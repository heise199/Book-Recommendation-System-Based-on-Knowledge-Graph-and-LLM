from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from neo4j import GraphDatabase
from app.core.config import settings

# MySQL Configuration (使用统一配置)
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_SERVER = settings.MYSQL_SERVER
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_DB = settings.MYSQL_DB

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Neo4j Configuration (使用统一配置)
NEO4J_URI = settings.NEO4J_URI
NEO4J_USER = settings.NEO4J_USER
NEO4J_PASSWORD = settings.NEO4J_PASSWORD

class Neo4jConnection:
    def __init__(self):
        self.driver = None

    def connect(self):
        if not self.driver:
            try:
                self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
                # Verify connection
                self.driver.verify_connectivity()
            except Exception as e:
                print(f"Failed to connect to Neo4j: {e}")
                # We don't raise here to allow app to start even if Neo4j is down,
                # but operations requiring Neo4j will fail.

    def close(self):
        if self.driver:
            self.driver.close()

    def get_session(self):
        if not self.driver:
            self.connect()
        if self.driver:
            # Explicitly connect to 'neo4j' database to avoid connecting to 'system' by default
            return self.driver.session(database="neo4j")
        else:
            raise Exception("Neo4j driver is not connected")

neo4j_conn = Neo4jConnection()

# Dependency for MySQL
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for Neo4j
def get_neo4j_session():
    session = neo4j_conn.get_session()
    try:
        yield session
    finally:
        session.close()
