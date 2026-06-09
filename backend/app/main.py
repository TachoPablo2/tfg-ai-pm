import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.analysis import router as analysis_router
from app.api.routers.reports import router as reports_router

ALLOWED_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
).split(",")

app = FastAPI(
    title="AI Project Management Assistant",
    description="Sistema Inteligente de Apoyo a la Decisión para la Gestión de Proyectos Ágiles",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "online",
        "mensaje": "El motor de inferencia de IA está listo para recibir proyectos.",
    }


app.include_router(analysis_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
