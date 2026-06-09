import pytest
from app.core.exceptions import (
    AnalysisError,
    FileValidationError,
    ModelInferenceError,
    LLMInferenceError,
    ReportGenerationError,
)


class TestExceptions:
    def test_analysis_error(self):
        err = AnalysisError("test error")
        assert str(err) == "test error"
        assert isinstance(err, Exception)

    def test_file_validation_error(self):
        err = FileValidationError("invalid file")
        assert str(err) == "invalid file"
        assert isinstance(err, AnalysisError)

    def test_model_inference_error(self):
        err = ModelInferenceError("model failed")
        assert str(err) == "model failed"
        assert isinstance(err, AnalysisError)

    def test_llm_inference_error(self):
        err = LLMInferenceError("llm failed")
        assert str(err) == "llm failed"
        assert isinstance(err, AnalysisError)

    def test_report_generation_error(self):
        err = ReportGenerationError("report failed")
        assert str(err) == "report failed"
        assert isinstance(err, AnalysisError)

    def test_inheritance_chain(self):
        assert issubclass(FileValidationError, AnalysisError)
        assert issubclass(ModelInferenceError, AnalysisError)
        assert issubclass(LLMInferenceError, AnalysisError)
        assert issubclass(ReportGenerationError, AnalysisError)
