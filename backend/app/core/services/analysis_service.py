import logging
from app.api.schemas.pydantic_models import AnalysisRequest
from app.ai.ml_models.predictor import ml_predictor
from app.ai.llm_engine.llm_service import llm_service

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Capa de Lógica de Negocio. Orquesta el flujo de datos desde que están 
    validados por Pydantic hasta la generación del informe final por la IA.
    """
    
    async def ejecutar_analisis_completo(self, request_data: AnalysisRequest) -> dict:
        logger.info(f"Iniciando orquestación de análisis para rol: {request_data.rol}")
        
        # 1. Inferencia Matemática (Machine Learning)
        # El predictor devuelve la lista de TaskPrediction ya diagnosticadas (🔴, 🟡, 🟢)
        predicciones = ml_predictor.predict(request_data)
        
        # 2. Inferencia de Lenguaje Natural (LLM)
        # El servicio LLM calcula KPIs, extrae el Top 3 y genera el texto de Llama 3
        resultado_final = await llm_service.generar_informe(
            predicciones=predicciones,
            rol=request_data.rol,
            alcance=request_data.alcance
        )
        
        # El resultado final es un diccionario híbrido con:
        # { "datos_ui": {...}, "recomendacion_ia": "..." }
        return resultado_final

# Instancia Singleton para usarla en los routers
analysis_service = AnalysisService()