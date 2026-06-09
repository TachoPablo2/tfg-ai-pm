import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas.pydantic_models import ReportRequest
from app.api.dependencies import ReportServiceDep
from app.core.exceptions import ReportGenerationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/export-pdf")
async def exportar_informe_pdf(
    request: ReportRequest,
    report_service: ReportServiceDep = None,
):
    try:
        buffer_pdf = report_service.generar_pdf_en_memoria(
            request.datos_ui,
            request.recomendacion_ia,
            request.graficos
        )
        
        buffer_pdf.seek(0)
        
        return StreamingResponse(
            buffer_pdf, 
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=informe_ejecutivo_ia.pdf"
            }
        )
    except ReportGenerationError as e:
        logger.error(f"Error generando PDF: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado en /reports/export-pdf: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el informe. Inténtelo de nuevo más tarde.")
