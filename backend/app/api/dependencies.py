from typing import Annotated

from fastapi import Depends

from app.ai.ml_models.predictor import ml_predictor
from app.ai.llm_engine.llm_service import llm_service
from app.core.services.analysis_service import AnalysisService
from app.core.services.report_service import ReportService


async def get_analysis_service() -> AnalysisService:
    return AnalysisService(
        ml_predictor=ml_predictor,
        llm_service=llm_service,
    )


async def get_report_service() -> ReportService:
    return ReportService()


AnalysisServiceDep = Annotated[AnalysisService, Depends(get_analysis_service)]
ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]
