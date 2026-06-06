from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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