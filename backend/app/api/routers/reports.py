import logging

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse

from app.api.schemas.pydantic_models import ReportRequest
from app.core.services.report_service import report_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/export-pdf")
async def exportar_informe_pdf(request: ReportRequest):
    try:
        buffer_pdf = report_service.generar_pdf_en_memoria(
            request.datos_ui,
            request.recomendacion_ia,
            request.grafico_base64
        )
        
        buffer_pdf.seek(0)
        
        return StreamingResponse(
            buffer_pdf, 
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=informe_ejecutivo_ia.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error generando PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al generar el informe. Inténtelo de nuevo más tarde.")
