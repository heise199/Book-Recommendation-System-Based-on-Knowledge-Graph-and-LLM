from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from typing import List, Dict, Any
import random
import json
from datetime import datetime, timedelta
from app.models.sql import Book, User, Interaction, SearchLog, RecommendationCache
from app.services.llm_service import llm_service
from sqlalchemy import func

class RecommendationService:
    def __init__(self, db: Session, neo4j: Neo4jSession):
        self.db = db
        self.neo4j = neo4j

    def get_recommendations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Hybrid Recommendation: Graph Paths + Popularity + Demographics + Preferences
        With 24-hour Caching
        """
        print(f"DEBUG: Starting recommendation for user_id={user_id}")
        
        # 0. Check Cache First
        cache = self.db.query(RecommendationCache).filter(RecommendationCache.user_id == user_id).first()
        now = datetime.now()
        
        if cache:
            cache_time = cache.updated_at if cache.updated_at else cache.created_at
            # Check if cache is within 24 hours
            if now - cache_time < timedelta(hours=24):
                print(f"DEBUG: Using cached recommendations for user_id={user_id} (Cache age: {now - cache_time})")
                try:
                    cached_data = json.loads(cache.recommendations)
                    recommendations = []
                    for item in cached_data:
                        book = self.db.query(Book).filter(Book.id == item["book_id"]).first()
                        if book:
                            recommendations.append({
                                "book": book,
                                "score": item["score"],
                                "reason": item["reason"],
                                "tags": item["tags"]
                            })
                    if recommendations:
                        return recommendations[:limit]
                except Exception as e:
                    print(f"DEBUG: Failed to load cache: {e}, regenerating...")

        # 1. Get User Info for Parameters
        user = self.db.query(User).filter(User.id == user_id).first()
        pref_cats = []
        if user and user.preferred_categories:
            pref_cats = [c.strip() for c in user.preferred_categories.split(",") if c.strip()]

        # 1. Get User's recent history from MySQL
        recent_interactions = self.db.query(Interaction).filter(
            Interaction.user_id == user_id
        ).order_by(Interaction.created_at.desc()).limit(5).all()
        
        history_book_ids = [i.book_id for i in recent_interactions]
        history_titles = [i.book.title for i in recent_interactions]

        recommendations = []
        seen_books = set(history_book_ids)
        
        # Initialize variables for the try-except block
        refined_list = []
        candidate_map = {}
        candidates_for_llm = []

        # 1.5. Search-based Retrieval (Immediate Intent)
        print("DEBUG: Checking search history...")
        recent_searches = self.db.query(SearchLog).filter(
            SearchLog.user_id == user_id
        ).order_by(SearchLog.created_at.desc()).limit(3).all()
        
        for search in recent_searches:
            if len(recommendations) >= limit:
                break
                
            # Simple keyword match
            query_str = f"%{search.query}%"
            matched_books = self.db.query(Book).filter(
                (Book.title.like(query_str)) |
                (Book.author.like(query_str))
            ).limit(2).all()
            
            for book in matched_books:
                if book.id in seen_books:
                    continue
                
                recommendations.append({
                    "book": book,
                    "score": 0.9, # High score for explicit search intent
                    "reason": f"基于您最近搜索关键词【{search.query}】的精准推荐。",
                    "tags": ["搜索关联"]
                })
                seen_books.add(book.id)

        # 2. Graph-based Retrieval (Cypher)
        print("DEBUG: Running Neo4j Cypher query...")
        
        cypher_query = """
        MATCH (u:User {id: $user_id})
        
        // 1. Content-based Path: Find similar books based on metadata
        OPTIONAL MATCH (u)-[:CLICKED|RATED|COLLECTED]->(b:Book)-[:BELONGS_TO|WRITTEN_BY]->(node)<-[:BELONGS_TO|WRITTEN_BY]-(rec_content:Book)
        WHERE NOT (u)-[:CLICKED|RATED|COLLECTED]->(rec_content)
        
        // 2. Collaborative Filtering Path: Find books read by similar users
        OPTIONAL MATCH (u)-[:CLICKED|RATED|COLLECTED]->(b2:Book)<-[:CLICKED|RATED|COLLECTED]-(peer:User)-[:CLICKED|RATED|COLLECTED]->(rec_collab:Book)
        WHERE NOT (u)-[:CLICKED|RATED|COLLECTED]->(rec_collab) AND peer.id <> u.id
        
        // 3. Search-based Path
        OPTIONAL MATCH (u)-[:SEARCHED]->(k:Keyword)
        OPTIONAL MATCH (rec_search:Book)-[:BELONGS_TO]->(c:Category)
        WHERE c.name CONTAINS k.text AND NOT (u)-[:CLICKED|RATED|COLLECTED]->(rec_search)
        
        // 4. Demographic Path: Similar Age (+/- 5) and Same Gender
        // Using OPTIONAL MATCH to find peers, then books
        OPTIONAL MATCH (peer_demog:User)
        WHERE peer_demog.id <> u.id 
          AND peer_demog.gender = u.gender 
          AND abs(peer_demog.age - u.age) <= 5
        OPTIONAL MATCH (peer_demog)-[:CLICKED|RATED|COLLECTED]->(rec_demog:Book)
        WHERE NOT (u)-[:CLICKED|RATED|COLLECTED]->(rec_demog)
        
        // 5. Explicit Preference Path
        OPTIONAL MATCH (rec_pref:Book)-[:BELONGS_TO]->(c_pref:Category)
        WHERE c_pref.name IN $pref_cats AND NOT (u)-[:CLICKED|RATED|COLLECTED]->(rec_pref)
        
        // Collect & Score
        WITH rec_content, rec_collab, rec_search, rec_demog, rec_pref, node, k, count(peer) as peer_strength, count(peer_demog) as demog_strength, c_pref
        
        WITH 
            CASE 
                WHEN rec_collab IS NOT NULL THEN rec_collab 
                WHEN rec_demog IS NOT NULL THEN rec_demog
                WHEN rec_search IS NOT NULL THEN rec_search
                WHEN rec_pref IS NOT NULL THEN rec_pref
                ELSE rec_content 
            END AS final_rec,
            CASE 
                WHEN rec_collab IS NOT NULL THEN 'collab'
                WHEN rec_demog IS NOT NULL THEN 'demog'
                WHEN rec_search IS NOT NULL THEN 'search'
                WHEN rec_pref IS NOT NULL THEN 'pref'
                ELSE 'content'
            END AS source_type,
            node, k, peer_strength, demog_strength, c_pref
        
        WHERE final_rec IS NOT NULL
        
        // Calculate Average Rating from Knowledge Graph
        OPTIONAL MATCH (final_rec)<-[r:RATED]-()
        WITH final_rec, source_type, node, k, peer_strength, demog_strength, c_pref, avg(r.score) as avg_rating
        
        RETURN final_rec.id AS book_id, 
               final_rec.title AS title,
               source_type,
               CASE 
                 WHEN source_type = 'content' THEN labels(node) 
                 WHEN source_type = 'search' THEN ["Keyword"]
                 WHEN source_type = 'pref' THEN ["Category"]
                 ELSE ["User"]
               END AS reason_node,
               CASE 
                 WHEN source_type = 'content' THEN node.name 
                 WHEN source_type = 'search' THEN k.text
                 WHEN source_type = 'pref' THEN c_pref.name
                 WHEN source_type = 'demog' THEN toString(demog_strength)
                 ELSE toString(peer_strength)
               END AS reason_val,
               // Scoring Logic:
               // Base Score: (Weighted Average Rating * 0.5) if available, else 0
               // Collab: Base 3 + peer_strength * 0.5
               // Demog: Base 2.5 + demog_strength * 0.3
               // Search: Base 4
               // Pref: Base 3.5
               // Content: Base 1
               1.0 + 
               (CASE WHEN avg_rating IS NOT NULL THEN avg_rating * 0.5 ELSE 0 END) +
               (CASE WHEN source_type = 'collab' THEN 3 + (peer_strength * 0.5) ELSE 0 END) +
               (CASE WHEN source_type = 'demog' THEN 2.5 + (demog_strength * 0.3) ELSE 0 END) +
               (CASE WHEN source_type = 'search' THEN 4 ELSE 0 END) +
               (CASE WHEN source_type = 'pref' THEN 3.5 ELSE 0 END)
               AS score
        ORDER BY score DESC
        LIMIT $limit
        """
        
        try:
            results = self.neo4j.run(cypher_query, user_id=user_id, pref_cats=pref_cats, limit=limit * 2)
            
            # Pre-fetch a batch of candidates
            fetched_records = list(results)
            print(f"DEBUG: Found {len(fetched_records)} graph candidates")
            
            for record in fetched_records:
                if len(candidates_for_llm) >= 10: # Only consider top 10 for LLM
                    break
                    
                b_id = record["book_id"]
                if b_id in seen_books:
                    continue
                    
                book_obj = self.db.query(Book).filter(Book.id == b_id).first()
                if not book_obj:
                    continue
                
                cat_name = book_obj.category.name if book_obj.category else "Unknown"
                
                cand_info = {
                    "title": book_obj.title,
                    "author": book_obj.author,
                    "category": cat_name,
                    "reason_val": str(record["reason_val"]),
                    "source_type": record["source_type"]
                }
                candidates_for_llm.append(cand_info)
                candidate_map[book_obj.title] = (book_obj, record)
                
            # Call LLM to refine and explain (Agent-based Re-ranking)
            if candidates_for_llm:
                print(f"DEBUG: Calling LLM refinement with {len(candidates_for_llm)} candidates...")
                try:
                    refined_list = llm_service.refine_recommendations(history_titles, candidates_for_llm)
                    print(f"DEBUG: LLM refinement complete, got {len(refined_list)} items")
                except Exception as e:
                    print(f"DEBUG: LLM refinement failed: {e}")
                    # Fallback to direct use of candidates
                    for title, (book_obj, record) in candidate_map.items():
                        refined_list.append({
                            "book_title": title,
                            "reason": f"根据您的兴趣为您推荐了这本书。",
                            "score": record["score"]
                        })
        except Exception as e:
            print(f"DEBUG: Neo4j Query failed: {e}")
            
        # Add LLM refined recommendations first
        print("DEBUG: Processing refined recommendations...")
        for item in refined_list:
            title = item.get("book_title")
            # Try to match title (handling potential slight variations from LLM)
            matched_key = next((k for k in candidate_map if k in title or title in k), None)
            
            if matched_key:
                book_obj, record = candidate_map[matched_key]
                if book_obj.id not in seen_books:
                    recommendations.append({
                        "book": book_obj,
                        "score": item.get("score", record["score"]),
                        "reason": item.get("reason", f"为您推荐 {book_obj.title}"),
                        "tags": ["AI 推荐", record["source_type"]]
                    })
                    seen_books.add(book_obj.id)

        # 3. Fallback: Popularity
        if len(recommendations) < limit:
            # If no personalized recommendations, use global popular books
            popular_books = self.db.query(Book).order_by(Book.average_rating.desc()).limit(limit).all()
            for book in popular_books:
                if book.id not in seen_books and len(recommendations) < limit:
                    recommendations.append({
                        "book": book,
                        "score": 0.5,
                        "reason": "为您推荐当前热门的高评分书籍。",
                        "tags": ["热门精选"]
                    })
                    seen_books.add(book.id)

        # 4. Save to Cache
        try:
            cache_data = []
            for rec in recommendations:
                cache_data.append({
                    "book_id": rec["book"].id,
                    "score": rec["score"],
                    "reason": rec["reason"],
                    "tags": rec["tags"]
                })
            
            if not cache:
                cache = RecommendationCache(user_id=user_id, recommendations=json.dumps(cache_data, ensure_ascii=False))
                self.db.add(cache)
            else:
                cache.recommendations = json.dumps(cache_data, ensure_ascii=False)
                cache.updated_at = datetime.now()
            
            self.db.commit()
            print(f"DEBUG: Saved {len(cache_data)} recommendations to cache for user_id={user_id}")
        except Exception as e:
            print(f"DEBUG: Failed to save cache: {e}")

        return recommendations[:limit]

    def get_cold_start_recommendations(self, categories: List[str], moods: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Cold Start Recommendation based on Questionnaire
        """
        recommendations = []
        seen_books = set()
        
        # 1. Category-based Retrieval from Neo4j
        # We find books in these categories, sorted by some heuristic (random for now to ensure variety, or rating if available in graph)
        # Assuming we don't have rating in graph node props yet, we fetch candidates and filter.
        # Actually, let's just fetch IDs from graph.
        
        cypher_query = """
        MATCH (b:Book)-[:BELONGS_TO]->(c:Category)
        WHERE c.name IN $categories
        RETURN b.id AS book_id, c.name AS category_name
        LIMIT $limit_candidate
        """
        
        # Fetch more candidates to randomize
        try:
            results = list(self.neo4j.run(cypher_query, categories=categories, limit_candidate=limit * 4))
            random.shuffle(results)
            
            for record in results:
                b_id = record["book_id"]
                category_name = record["category_name"]
                
                if b_id in seen_books:
                    continue
                    
                book_obj = self.db.query(Book).filter(Book.id == b_id).first()
                if not book_obj:
                    continue
                
                # Simple "Reason" generation based on mood
                mood_text = moods[0] if moods else "探索"
                explanation = f"根据您对【{category_name}】的兴趣以及【{mood_text}】的偏好，为您特别推荐。"
                
                recommendations.append({
                    "book": book_obj,
                    "score": 0.8, # Default high score for explicit user selection
                    "reason": explanation,
                    "tags": [category_name] + moods
                })
                seen_books.add(b_id)
                
                if len(recommendations) >= limit:
                    break
        except Exception as e:
            print(f"Cold start Neo4j query failed: {e}")
        
        # 2. Fallback if no categories selected or not enough books found -> Global Popular
        if len(recommendations) < limit:
            popular_books = self.db.query(Book).order_by(Book.average_rating.desc()).limit(limit - len(recommendations)).all()
            for book in popular_books:
                if book.id in seen_books:
                    continue
                recommendations.append({
                    "book": book,
                    "score": 0.5,
                    "reason": "新用户必读的高分经典。",
                    "tags": ["热门推荐"]
                })
                seen_books.add(book.id)
                
        return recommendations
