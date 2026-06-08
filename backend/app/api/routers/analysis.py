import logging

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.data.ingestion.file_reader import JiraFileReader
from app.data.transformation.data_transformer import JiraTransformer
from app.api.schemas.pydantic_models import AnalysisRequest, AnalysisResponse
from app.core.services.analysis_service import analysis_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/process", response_model=AnalysisResponse)
async def procesar_analisis(
    file: UploadFile = File(...),
    alcance: str = Form(...),
    rol: str = Form(...)
):
    try:
        df_raw = await JiraFileReader.leer_archivo(file)
        
        df_clean = JiraTransformer.transformar_exportacion(df_raw)
        
        tareas_dict = JiraTransformer.dataframe_to_records(df_clean)
        
        request_data = AnalysisRequest(
            alcance=alcance, 
            rol=rol, 
            tareas=tareas_dict
        )
        
        resultado_final = await analysis_service.ejecutar_analisis_completo(request_data)
        
        return resultado_final

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error inesperado en /analyze/process: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor. Inténtelo de nuevo más tarde.")
