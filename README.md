# FastAPI Base Skeleton

This project serves as a **base skeleton** designed to facilitate and accelerate the creation of new projects or microservices using FastAPI.

The main idea behind this repository is to provide the fundamental pieces, configurations, and a clean, pre-built architecture that includes generic CRUD repositories, database migrations, and standard response handling. This allows the development team to focus solely on business logic rather than boilerplate code from day one.

## Project Structure

The code is organized modularly and intentionally separated into different layers to ensure scalability:

- `alembic/` & `alembic.ini`: Files and migration history for the database using [Alembic](https://alembic.sqlalchemy.org/).
- `api/`: Contains the route files and endpoints (controllers), usually grouped and separated by versions (e.g., `v1/`).
- `configurations/`: Environment configuration management (database connections, environment variables, and core FastAPI settings).
- `core/`: Core classes and logic of the project such as the **Generic Router (GenericCRUDRouter)**, exceptions, standard response models, and shared application dependencies.
- `models/`: ORM models (SQLModel/SQLAlchemy) that map directly to the database tables.
- `repositories/`: Data abstraction layer. Here resides the `BaseRepository` containing CRUD operations and any other complex database queries, separated from the rest of the application.
- `schemas/`: Pydantic models used for data validation and serialization of incoming (Requests) and outgoing (Responses) data, keeping them independent of the database models.
- `services/`: Layer for the application's business logic. If an endpoint needs to calculate complex data or call third-party services before saving a model, it should live in a Service rather than a controller.
- `main.py`: The entry point or "bootstrap" file of the application; it handles app initialization, middleware configuration (like CORS), and router inclusion.
- `Dockerfile` & `docker-compose.yml`: Configuration files to easily and reproducibly containerize the application locally.
- `Makefile`: A collection of quick terminal commands to facilitate local deployment or the execution of repetitive tasks.
- `.env_dev` / `.env_example`: Example environment variable files. Remember to create your `.env` with your secrets to run locally.

## Getting Started

### Google OAuth Setup

If you want to use the Google OAuth route provided in this skeleton:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2. Create a Project, then configure your **OAuth consent screen**.
3. Go to **Credentials** -> **Create Credentials** -> **OAuth client ID**.
4. Choose **Web application** as the application type.
5. In **Authorized redirect URIs**, add `http://localhost:8000/api/v1/auth/google/callback` (and optionally `http://127.0.0.1:8000/api/v1/auth/google/callback`).
6. Copy the generated **Client ID** and **Client Secret** into your `.env` file under `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.

### Initial Setup

1. Clone or use this repository as the base for a new project.
2. Copy `.env_example` to `.env` and configure your local credentials.
3. Install dependencies or spin it up using predefined commands (via Docker or locally using `uvicorn main:app --reload`).
4. Add new models in `models/`, run Alembic to reflect them, and add your APIs in the `api/` folder.
