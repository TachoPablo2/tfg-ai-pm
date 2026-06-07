from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse

from app.core.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/export-pdf")
async def exportar_informe_pdf(
    datos_ui: dict = Body(...),
    recomendacion_ia: str = Body(...),
    grafico_base64: str = Body(None)
):
    try:
        buffer_pdf = report_service.generar_pdf_en_memoria(
            datos_ui, 
            recomendacion_ia, 
            grafico_base64
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
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {str(e)}")