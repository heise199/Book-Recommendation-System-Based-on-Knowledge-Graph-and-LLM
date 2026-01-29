import sys
import os

# Add parent dir to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base, neo4j_conn
from app.models.sql import User, Book, Category, Interaction, Rating
from app.services.sync_service import SyncService
from scripts.data_generator import get_books_data
# Direct import bcrypt to avoid compatibility issues
import bcrypt

def get_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def init_db():
    print("Initializing Database...")
    
    # 1. Reset MySQL Tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("MySQL tables created.")

    session = SessionLocal()
    try:
        neo4j_session = neo4j_conn.get_session()
        sync_service = SyncService(neo4j_session)

        # 2. Reset Neo4j
        print("Clearing Neo4j Graph...")
        sync_service.clear_graph()

        # 3. Create Categories
        categories_data = ["科幻", "历史", "计算机", "经济管理", "心理学", "悬疑"]
        categories = {}
        for name in categories_data:
            cat = Category(name=name)
            session.add(cat)
            session.flush()
            categories[name] = cat
        print(f"Created {len(categories)} categories.")

        # 4. Create Books
        books_data = get_books_data()

        for b_data in books_data:
            book = Book(
                title=b_data["title"],
                author=b_data["author"],
                category_id=categories[b_data["cat"]].id,
                isbn=b_data["isbn"],
                description=b_data["desc"],
                cover_url="https://via.placeholder.com/150"
            )
            session.add(book)
            session.flush()
            
            # Sync to Neo4j
            sync_service.sync_book(book, b_data["cat"])
        print(f"Created {len(books_data)} books and synced to Neo4j.")

        # 5. Create Users
        users = []
        for i in range(1, 4):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                hashed_password=get_hash("123456")
            )
            session.add(user)
            session.flush()
            users.append(user)
            sync_service.sync_user(user)
        print(f"Created {len(users)} users and synced to Neo4j.")

        # 6. Create Interactions (Mock History)
        # User1 likes Sci-Fi
        user1 = users[0]
        sci_fi_books = session.query(Book).join(Category).filter(Category.name == "科幻").all()
        for b in sci_fi_books:
            # Click
            session.add(Interaction(user_id=user1.id, book_id=b.id, interaction_type="click"))
            sync_service.sync_interaction(user1.id, b.id, "click")
            # Rate
            session.add(Rating(user_id=user1.id, book_id=b.id, rating=5))
            sync_service.sync_rating(user1.id, b.id, 5)

        # User2 likes History
        user2 = users[1]
        hist_books = session.query(Book).join(Category).filter(Category.name == "历史").all()
        for b in hist_books:
            session.add(Interaction(user_id=user2.id, book_id=b.id, interaction_type="collect"))
            sync_service.sync_interaction(user2.id, b.id, "collect")

        session.commit()
        print("Data initialization completed successfully!")
        
        neo4j_session.close()

    except Exception as e:
        session.rollback()
        print(f"Error initializing data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
