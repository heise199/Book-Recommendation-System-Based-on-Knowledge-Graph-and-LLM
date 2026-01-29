from neo4j import GraphDatabase
import os

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def init_db():
    print(f"Connecting to {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            # Create constraints
            print("Creating constraints...")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (b:Book) REQUIRE b.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
            
            # Create some sample data
            print("Inserting sample data...")
            cypher = """
            MERGE (u:User {id: 'user1', name: 'Alice'})
            MERGE (b1:Book {id: '1', title: 'The Great Gatsby', author: 'F. Scott Fitzgerald'})
            MERGE (b2:Book {id: '2', title: '1984', author: 'George Orwell'})
            MERGE (c1:Category {name: 'Classic Literature'})
            MERGE (c2:Category {name: 'Fiction'})
            
            MERGE (b1)-[:BELONGS_TO]->(c1)
            MERGE (b2)-[:BELONGS_TO]->(c2)
            MERGE (b2)-[:BELONGS_TO]->(c1)
            
            MERGE (u)-[:CLICKED]->(b1)
            """
            session.run(cypher)
            print("Database initialized with sample data.")
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    init_db()
