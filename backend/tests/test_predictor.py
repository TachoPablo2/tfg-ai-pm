import pytest
import numpy as np
from app.ai.ml_models.predictor import MLPredictor
from app.core.exceptions import ModelInferenceError


class TestMLPredictor:
    def test_predict_returns_list(self, analysis_request, mocker):
        predictor = MLPredictor()

        def mock_predict_proba(X):
            n = X.shape[0]
            return np.column_stack([1 - np.ones(n) * 0.3, np.ones(n) * 0.3])

        mock_pipeline = mocker.MagicMock()
        mock_pipeline.predict_proba = mock_predict_proba
        predictor.pipeline_retraso = mock_pipeline
        predictor.pipeline_riesgo = mock_pipeline
        predictor._loaded = True

        result = predictor.predict(analysis_request)
        assert len(result) == 1
        assert result[0].Issue_Key == "PRO-101"
        assert result[0].Prob_Riesgo == 0.3
        assert result[0].Prob_Retraso == 0.3

    def test_gravedad_alto_for_high_risk(self, analysis_request, mocker):
        predictor = MLPredictor()

        def high_proba(X):
            n = X.shape[0]
            return np.column_stack([1 - np.ones(n) * 0.9, np.ones(n) * 0.9])

        mock_pipeline = mocker.MagicMock()
        mock_pipeline.predict_proba = high_proba
        predictor.pipeline_retraso = mock_pipeline
        predictor.pipeline_riesgo = mock_pipeline
        predictor._loaded = True

        result = predictor.predict(analysis_request)
        assert result[0].Gravedad == "Alto"

    def test_gravedad_medio(self, analysis_request, mocker):
        predictor = MLPredictor()

        def mid_proba(X):
            n = X.shape[0]
            return np.column_stack([1 - np.ones(n) * 0.65, np.ones(n) * 0.65])

        mock_pipeline = mocker.MagicMock()
        mock_pipeline.predict_proba = mid_proba
        predictor.pipeline_retraso = mock_pipeline
        predictor.pipeline_riesgo = mock_pipeline
        predictor._loaded = True

        result = predictor.predict(analysis_request)
        assert result[0].Gravedad == "Medio"

    def test_gravedad_bajo(self, analysis_request, mocker):
        predictor = MLPredictor()

        def low_proba(X):
            n = X.shape[0]
            return np.column_stack([1 - np.ones(n) * 0.3, np.ones(n) * 0.3])

        mock_pipeline = mocker.MagicMock()
        mock_pipeline.predict_proba = low_proba
        predictor.pipeline_retraso = mock_pipeline
        predictor.pipeline_riesgo = mock_pipeline
        predictor._loaded = True

        result = predictor.predict(analysis_request)
        assert result[0].Gravedad == "Bajo"

    def test_gravedad_high_blocker_count(self, analysis_request, mocker):
        from copy import deepcopy
        req = deepcopy(analysis_request)
        req.tareas[0].Blocker_Count = 2

        predictor = MLPredictor()

        def low_proba(X):
            n = X.shape[0]
            return np.column_stack([1 - np.ones(n) * 0.1, np.ones(n) * 0.1])

        mock_pipeline = mocker.MagicMock()
        mock_pipeline.predict_proba = low_proba
        predictor.pipeline_retraso = mock_pipeline
        predictor.pipeline_riesgo = mock_pipeline
        predictor._loaded = True

        result = predictor.predict(req)
        assert result[0].Gravedad == "Alto"

    def test_empty_input_raises_error(self, mocker):
        from app.api.schemas.pydantic_models import AnalysisRequest, TaskRecord
        predictor = MLPredictor()

        mock_pipeline = mocker.MagicMock()
        predictor.pipeline_retraso = mock_pipeline
        predictor.pipeline_riesgo = mock_pipeline
        predictor._loaded = True

        req = AnalysisRequest(alcance="Sprint", rol="Project Manager", tareas=[
            TaskRecord(
                Issue_Key="PRO-0",
                Title="",
                Issue_Type="",
                Project_ID=1,
                Project_Name="",
                Sprint_ID=1,
                Sprint_State="",
                Story_Point=0.0,
                Total_Effort_Minutes=0.0,
                In_Progress_Minutes=0.0,
                Resolution_Time_Minutes=0.0,
                Title_Changed_After_Estimation=0,
                Description_Changed_After_Estimation=0,
                Story_Point_Changed_After_Estimation=0,
                Blocker_Count=0,
            )
        ])
        df_input = __import__("pandas").DataFrame([t.model_dump() for t in req.tareas])
        mocker.patch("pandas.DataFrame.empty", True)
        with pytest.raises(ModelInferenceError, match="No hay tareas"):
            predictor.predict(req)

    def test_predict_proba_failure(self, analysis_request, mocker):
        predictor = MLPredictor()

        mock_pipeline = mocker.MagicMock()
        mock_pipeline.predict_proba.side_effect = RuntimeError("predict_proba failed")
        predictor.pipeline_retraso = mock_pipeline
        predictor.pipeline_riesgo = mock_pipeline
        predictor._loaded = True

        with pytest.raises(ModelInferenceError):
            predictor.predict(analysis_request)

    def test_model_load_error(self, mocker):
        mocker.patch("joblib.load", side_effect=FileNotFoundError("model not found"))
        predictor = MLPredictor()
        with pytest.raises(ModelInferenceError, match="modelos ML"):
            predictor._ensure_loaded()
