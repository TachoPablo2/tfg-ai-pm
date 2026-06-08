import logging
from typing import Optional

from app.ai.ml_models.predictor import MLPredictor
from app.ai.llm_engine.llm_service import LLMService
from app.api.schemas.pydantic_models import AnalysisRequest
from app.core.exceptions import ModelInferenceError, LLMInferenceError

logger = logging.getLogger(__name__)


class AnalysisService:

    def __init__(
        self,
        ml_predictor: Optional[MLPredictor] = None,
        llm_service: Optional[LLMService] = None,
    ):
        self._ml_predictor = ml_predictor or MLPredictor()
        self._llm_service = llm_service or LLMService()

    async def ejecutar_analisis_completo(self, request_data: AnalysisRequest) -> dict:
        logger.info(f"Iniciando orquestación de análisis para rol: {request_data.rol}")

        try:
            predicciones = self._ml_predictor.predict(request_data)
        except ModelInferenceError:
            logger.error("Error en inferencia ML")
            raise

        try:
            resultado_final = await self._llm_service.generar_informe(
                predicciones=predicciones,
                rol=request_data.rol,
                alcance=request_data.alcance,
            )
        except LLMInferenceError as e:
            logger.warning(f"LLM no disponible, devolviendo solo métricas: {e}")
            datos_ui = self._llm_service.construir_payload(
                predicciones, request_data.rol, request_data.alcance
            )
            resultado_final = {
                "datos_ui": datos_ui,
                "recomendacion_ia": (
                    "Sistema de recomendaciones temporalmente no disponible. "
                    "El dashboard de métricas sigue operativo. Por favor, revise los "
                    "semáforos de riesgo manualmente."
                ),
            }

        return resultado_final


analysis_service = AnalysisService()
