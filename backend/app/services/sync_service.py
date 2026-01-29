from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from app.models.sql import User, Book, Category, Interaction, Rating

class SyncService:
    def __init__(self, neo4j_session: Neo4jSession):
        self.neo4j = neo4j_session

    def sync_user(self, user: User):
        query = """
        MERGE (u:User {id: $id})
        SET u.username = $username,
            u.gender = $gender,
            u.age = $age,
            u.preferred_categories = $preferred_categories
        """
        self.neo4j.run(query, 
                       id=user.id, 
                       username=user.username,
                       gender=user.gender or "Unknown",
                       age=user.age or 0,
                       preferred_categories=user.preferred_categories or "")

    def sync_book(self, book: Book, category_name: str = None):
        # Create Book node
        # Create Author node and relationship
        # Create Category node and relationship
        query = """
        MERGE (b:Book {id: $id})
        SET b.title = $title, b.isbn = $isbn, b.description = $description
        
        WITH b
        MERGE (a:Author {name: $author})
        MERGE (b)-[:WRITTEN_BY]->(a)
        
        WITH b
        MERGE (c:Category {name: $category_name})
        MERGE (b)-[:BELONGS_TO]->(c)
        """
        self.neo4j.run(query, 
                       id=book.id, 
                       title=book.title, 
                       isbn=book.isbn, 
                       description=book.description or "",
                       author=book.author or "Unknown", 
                       category_name=category_name or "Uncategorized")

    def sync_interaction(self, user_id: int, book_id: int, interaction_type: str):
        # interaction_type: click, collect, etc.
        # Map types to relationship types: CLICKED, COLLECTED
        rel_type = interaction_type.upper()
        if rel_type not in ["CLICK", "COLLECT", "CART", "PURCHASE"]:
            rel_type = "INTERACTED"
        
        if rel_type == "CLICK":
            rel_type = "CLICKED"
        elif rel_type == "COLLECT":
            rel_type = "COLLECTED"
            
        query = f"""
        MATCH (u:User {{id: $user_id}})
        MATCH (b:Book {{id: $book_id}})
        MERGE (u)-[r:{rel_type}]->(b)
        SET r.timestamp = datetime()
        """
        self.neo4j.run(query, user_id=user_id, book_id=book_id)

    def sync_rating(self, user_id: int, book_id: int, rating: int):
        query = """
        MATCH (u:User {id: $user_id})
        MATCH (b:Book {id: $book_id})
        MERGE (u)-[r:RATED]->(b)
        SET r.score = $rating, r.timestamp = datetime()
        """
        self.neo4j.run(query, user_id=user_id, book_id=book_id, rating=rating)

    def sync_search(self, user_id: int, query_text: str):
        # 1. Create/Merge Keyword node
        # 2. Create SEARCHED relationship
        cypher = """
        MATCH (u:User {id: $user_id})
        MERGE (k:Keyword {text: $text})
        MERGE (u)-[r:SEARCHED]->(k)
        SET r.timestamp = datetime()
        """
        self.neo4j.run(cypher, user_id=user_id, text=query_text)

    def clear_graph(self):
        self.neo4j.run("MATCH (n) DETACH DELETE n")
