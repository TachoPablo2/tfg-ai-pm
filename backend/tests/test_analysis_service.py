import pytest
from app.core.services.analysis_service import AnalysisService
from app.core.exceptions import ModelInferenceError


class TestAnalysisService:
    @pytest.mark.asyncio
    async def test_ejecutar_analisis_completo_success(self, analysis_request, mocker):
        mock_predictor = mocker.MagicMock()
        mock_predictor.predict.return_value = []

        mock_llm = mocker.AsyncMock()
        mock_llm.generar_informe.return_value = {
            "datos_ui": None,
            "recomendacion_ia": "Test recommendation",
        }

        service = AnalysisService(ml_predictor=mock_predictor, llm_service=mock_llm)
        result = await service.ejecutar_analisis_completo(analysis_request)
        assert result["recomendacion_ia"] == "Test recommendation"
        mock_predictor.predict.assert_called_once_with(analysis_request)
        mock_llm.generar_informe.assert_called_once()

    @pytest.mark.asyncio
    async def test_ml_prediction_failure(self, analysis_request, mocker):
        mock_predictor = mocker.MagicMock()
        mock_predictor.predict.side_effect = ModelInferenceError("ML failed")

        mock_llm = mocker.MagicMock()

        service = AnalysisService(ml_predictor=mock_predictor, llm_service=mock_llm)
        with pytest.raises(ModelInferenceError):
            await service.ejecutar_analisis_completo(analysis_request)

    @pytest.mark.asyncio
    async def test_llm_fallback_when_unavailable(self, analysis_request, mocker):
        from app.core.exceptions import LLMInferenceError

        mock_predictor = mocker.MagicMock()
        mock_predictor.predict.return_value = []

        mock_llm = mocker.MagicMock()
        mock_llm.generar_informe.side_effect = LLMInferenceError("LLM offline")
        mock_llm.construir_payload.return_value = {
            "Configuracion": {"Alcance": "Sprint", "Rol": "Project Manager"},
            "UI_Header_KPIs": {},
            "UI_Tab_1_Estado": {},
            "LLM_Tab_2_Contexto": {},
        }

        service = AnalysisService(ml_predictor=mock_predictor, llm_service=mock_llm)
        result = await service.ejecutar_analisis_completo(analysis_request)
        assert "temporalmente no disponible" in result["recomendacion_ia"]
        assert "datos_ui" in result

    def test_default_constructor(self):
        service = AnalysisService()
        assert service._ml_predictor is not None
        assert service._llm_service is not None
