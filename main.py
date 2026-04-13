from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.api_router import v1_router

app = FastAPI(title="FastAPI Structure")

# Configuración de CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes en desarrollo. Modificar para producción.
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
def read_root():
    return {"status": "running"}
