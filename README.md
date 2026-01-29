# Knowledge Graph + LLM Book Recommendation System

## Project Structure

- `frontend/`: Vue 3 + TypeScript + Tailwind CSS application
- `backend/`: FastAPI + Neo4j driver application
- `docker-compose.yml`: Orchestration for Frontend, Backend, and Neo4j

## Prerequisites

- Docker and Docker Compose

## Getting Started

1.  **Clone the repository** (if you haven't already).
2.  **Start the application**:
    ```bash
    docker-compose up --build
    ```
3.  **Access the services**:
    - Frontend: http://localhost:5173
    - Backend API: http://localhost:8000/docs
    - Neo4j Browser: http://localhost:7474 (User: neo4j, Password: password)

## Development

- **Frontend**:
    ```bash
    cd frontend
    pnpm install
    pnpm dev
    ```
- **Backend**:
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```
    Note: You need a running Neo4j instance for the backend to connect to.
