from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import numpy as np

from app.data.ingestion.file_reader import JiraFileReader
from app.data.transformation.data_transformer import JiraTransformer
from app.api.schemas.pydantic_models import AnalysisRequest
from app.core.services.analysis_service import analysis_service

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/process")
async def procesar_analisis(
    file: UploadFile = File(...),
    alcance: str = Form(...), # 'Sprint' o 'Proyecto'
    rol: str = Form(...)      # 'PM' o 'PMO'
):
    try:
        # 1. INGESTA: Lectura cruda
        df_raw = await JiraFileReader.leer_archivo(file)
        
        # 2. TRANSFORMACIÓN Y LIMPIEZA
        df_clean = JiraTransformer.transformar_exportacion(df_raw)
        
        # Reemplazamos NaN por None para compatibilidad estricta con JSON/Pydantic
        df_clean = df_clean.replace({np.nan: None})
        tareas_dict = df_clean.to_dict(orient="records")
        
        # 3. VALIDACIÓN (Frontera de Seguridad Pydantic)
        request_data = AnalysisRequest(
            alcance=alcance, 
            rol=rol, 
            tareas=tareas_dict
        )
        
        # 4. ORQUESTACIÓN (Lógica de Negocio)
        resultado_final = await analysis_service.ejecutar_analisis_completo(request_data)
        
        # Devolvemos el payload directamente para que React dibuje el Dashboard
        return resultado_final

    except ValueError as ve:
        # Errores de validación de negocio (ej: mezcla de sprints o campos faltantes)
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Errores inesperados (Fallback RNF-07)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")