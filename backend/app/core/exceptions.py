class AnalysisError(Exception):
    pass

class FileValidationError(AnalysisError):
    pass

class DataValidationError(AnalysisError):
    pass

class ModelInferenceError(AnalysisError):
    pass

class LLMInferenceError(AnalysisError):
    pass

class ReportGenerationError(AnalysisError):
    pass
