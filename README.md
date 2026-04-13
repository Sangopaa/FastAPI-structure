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

### Prerequisites

Make sure you have the following installed on your machine:

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/)
- [Python 3.11+](https://www.python.org/downloads/)
- [Make](https://www.gnu.org/software/make/)

---

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Set up your environment variables

```bash
cp .env_example .env
```

Open `.env` and fill in the required values:

| Variable | Description |
|---|---|
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_DB` | Database name |
| `CONNECTION_STRING` | Full DB URL for Docker (uses `db` hostname) |
| `LOCAL_CONNECTION_STRING` | Full DB URL for local tools (uses `localhost:5433`) |
| `JWT_SECRET` | A secure random string for JWT signing |
| `GOOGLE_CLIENT_ID` | From Google Cloud Console (optional) |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console (optional) |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL (keep the default for local dev) |

### 3. Create your virtual environment and install dependencies

```bash
python -m venv .venv
make install-dev
```

This installs all production and development dependencies, and automatically registers the pre-commit git hooks (Black formatter, whitespace checks, etc.).

### 4. Start the project

```bash
make up
```

This starts the FastAPI app and the PostgreSQL database via Docker Compose. The API will be available at:

- **API:** `http://localhost:8000`
- **Swagger docs:** `http://localhost:8000/docs`

### 5. Run the database migrations

Once the containers are running, apply the initial migrations:

```bash
make run_migrations
```

---

### Makefile Commands Reference

| Command | Description |
|---|---|
| `make up` | Start the project (Docker Compose) |
| `make down` | Stop all containers |
| `make reset` | Tear down volumes and rebuild from scratch |
| `make run_migrations` | Apply pending Alembic migrations |
| `make create_migrations message=<name>` | Generate a new Alembic migration |
| `make install` | Install production dependencies into `.venv` |
| `make install-dev` | Install all dependencies + register pre-commit hooks |

---

### Google OAuth Setup (Optional)

If you want to use the built-in Google OAuth login route:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2. Create a Project, then configure your **OAuth consent screen**.
3. Go to **Credentials** -> **Create Credentials** -> **OAuth client ID**.
4. Choose **Web application** as the application type.
5. In **Authorized redirect URIs**, add `http://localhost:8000/api/v1/auth/google/callback`.
6. Copy the generated **Client ID** and **Client Secret** into your `.env` under `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
