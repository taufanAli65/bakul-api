# Bakul API

This is a FastAPI-based backend application for the Bakul project

## Prerequisites

- **Python 3.9+**
- **PostgreSQL**: Ensure you have a running PostgreSQL instance.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/taufanAli65/bakul-api.git
    cd bakul-api
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration:**
    Copy the example environment file and update it with your configuration (e.g., database credentials).
    ```bash
    cp .env.example .env
    ```
    Typically, you will need to set `DATABASE_URL` and `SECRET_KEY`.
    
## Database

This project uses **Alembic** for database migrations.

1.  **Apply migrations:**
    ```bash
    alembic upgrade head
    ```

## Running the Application

Start the development server with hot-reload:

```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:

-   **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
-   **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
