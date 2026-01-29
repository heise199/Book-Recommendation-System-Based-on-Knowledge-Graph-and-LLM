from typing import List, Dict, Any
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Define output structure for the LLM
class RecommendedBook(BaseModel):
    book_title: str = Field(description="The title of the recommended book")
    reason: str = Field(description="A personalized, engaging explanation (1-2 sentences) in Chinese")
    score: float = Field(description="Relevance score between 0.0 and 1.0")

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendedBook]

class LLMService:
    def __init__(self):
        # Initialize ChatOllama with the specified model
        # Ensure Ollama is running (default: http://localhost:11434)
        # Added timeout to prevent hanging requests
        self.llm = ChatOllama(
            model="gpt-oss:20b",
            temperature=0.7,
            timeout=15 # 15 seconds timeout
        )

    def generate_explanation(self, book_title: str, user_history_titles: List[str], reason_type: str) -> str:
        """
        Legacy method: Generate a single explanation.
        Refactored to use LangChain.
        """
        if not self.llm:
            return self._fallback_explanation(book_title, reason_type)

        try:
            history_str = ", ".join(user_history_titles[:5])
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a knowledgeable librarian assistant. Your goal is to provide brief, engaging book recommendations in Chinese."),
                ("user", """
                User has read: {history}
                Recommend book: {book}
                Reasoning logic: {reason_type}
                
                Please write a short, engaging recommendation reason (1 sentence) in Chinese.
                """)
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({
                "history": history_str,
                "book": book_title,
                "reason_type": reason_type
            })
            
            return response.content.strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._fallback_explanation(book_title, reason_type)

    def refine_recommendations(self, user_history_titles: List[str], candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        New Agent-like method: Takes a list of candidates and returns a refined list with LLM-generated reasons.
        """
        if not self.llm:
            return []

        try:
            # Prepare data for prompt
            history_str = ", ".join(user_history_titles[:10])
            candidates_str = ""
            for cand in candidates:
                candidates_str += f"- Title: {cand['title']}, Author: {cand.get('author', 'Unknown')}, Category: {cand.get('category', 'Unknown')}, Graph Reason: {cand.get('reason_val', 'None')}\n"

            parser = JsonOutputParser(pydantic_object=RecommendationResponse)

            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert book recommender system. You are given a user's reading history and a list of candidate books identified by a knowledge graph."),
                ("user", """
                User's Reading History: {history}

                Candidate Books (retrieved from Knowledge Graph):
                {candidates}

                Task:
                1. Analyze the candidates and select the best matches for the user.
                2. You can re-rank them based on how well they fit the user's history.
                3. Provide a personalized reason for each selected book in Chinese.
                4. Assign a confidence score (0.0 to 1.0).

                {format_instructions}
                """)
            ])

            chain = prompt | self.llm | parser

            response = chain.invoke({
                "history": history_str,
                "candidates": candidates_str,
                "format_instructions": parser.get_format_instructions()
            })

            # Map back to the original candidate objects or return the structured data
            # We return the LLM's output directly, the caller will merge it.
            return response['recommendations']

        except Exception as e:
            print(f"LLM Refine Error: {e}")
            return []

    def _fallback_explanation(self, book_title: str, reason_type: str) -> str:
        if reason_type == "author":
            return f"因为您之前读过该作者的其他作品，这本《{book_title}》延续了其一贯的风格，值得一读。"
        elif reason_type == "category":
            return f"基于您对相关主题的兴趣，为您精选了这本《{book_title}》，深入探讨了类似的话题。"
        elif reason_type == "collab":
            return f"许多和您口味相似的读者都收藏了这本《{book_title}》，相信您也会喜欢。"
        else:
            return f"根据您的阅读偏好，智能算法为您推荐《{book_title}》。"

llm_service = LLMService()
