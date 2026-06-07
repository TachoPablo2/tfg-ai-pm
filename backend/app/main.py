from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 👇 1. NUEVA IMPORTACIÓN: Traemos las rutas desde la nueva estructura
from app.api.routers.analyze import router as api_router

# Inicializamos la API
app = FastAPI(
    title="AI Project Management Assistant",
    description="Motor predictivo de riesgos y retrasos para PMOs",
    version="1.0.0"
)

# Configuración CORS para permitir peticiones desde el frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo permitimos todo. En producción se restringe a la URL de React.
    allow_credentials=True,
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

# 👇 2. NUEVO ENGANCHE: Conectamos las rutas bajo el prefijo /api
app.include_router(api_router, prefix="/api")