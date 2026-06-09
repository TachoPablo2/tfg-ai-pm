from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.analysis import router as analysis_router
from app.api.routers.reports import router as reports_router

# Inicializamos la API
app = FastAPI(
    title="AI Project Management Assistant",
    description="Sistema Inteligente de Apoyo a la Decisión para la Gestión de Proyectos Ágiles",
    version="1.0.0"
)

# Configuración CORS para permitir peticiones desde el frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de salud para comprobar que el servidor está vivo
@app.get("/")
def health_check():
    return {
        "status": "online", 
        "mensaje": "El motor de inferencia de IA está listo para recibir proyectos."
    }

#2. ENGANCHE: Conectamos las rutas a la API
app.include_router(analysis_router, prefix="/api")
app.include_router(reports_router, prefix="/api")