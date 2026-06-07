from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Literal
import numpy as np

# Imports corregidos para apuntar a las clases exactas
from app.data.ingestion.file_reader import JiraFileReader
from app.data.transformation.data_transformer import JiraTransformer
from app.api.schemas.pydantic_models import AnalysisRequest, AnalysisResponse

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/process", response_model=AnalysisResponse)
async def procesar_analisis(
    file: UploadFile = File(...),
    alcance: str = Form(...), # 'sprint' o 'proyecto'
    rol: str = Form(...)      # 'PM' o 'PMO'
):
    try:
        # 1. INGESTA: Lectura cruda (CSV/Excel)
        df_raw = await JiraFileReader.leer_archivo(file)
        
        # 2. TRANSFORMACIÓN: Limpieza y creación de features
        df_clean = JiraTransformer.transformar_exportacion(df_raw)
        
        # 3. VALIDACIÓN Y LIMPIEZA DE NULOS
        # Reemplazamos los NaN de Pandas por None para que JSON y Pydantic no fallen
        df_clean = df_clean.replace({np.nan: None})
        tareas_dict = df_clean.to_dict(orient="records")
        
        # Esto lanzará el ValueError si el model_validator falla (ej: mezcla de sprints)
        request_data = AnalysisRequest(
            alcance=alcance, 
            rol=rol, 
            tareas=tareas_dict
        )
        
        # 4. ORQUESTACIÓN FUTURA (Aquí llamarás a tu modelo ML y luego al LLM)
        # predicciones = predictor.predict(request_data)
        # recomendacion = llm_service.generar_informe(predicciones)
        
        return AnalysisResponse(
            proyecto=tareas_dict[0].get("Project_Name", "Desconocido") if tareas_dict else "Desconocido",
            alcance=alcance,
            tareas_analizadas=len(tareas_dict),
            predicciones=[], # Placeholder hasta conectar el modelo
            recomendacion_ia="Pendiente de integrar IA"
        )

    except ValueError as ve:
        # Errores de validación de negocio (ej: mezcla de sprints)
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Errores inesperados del sistema
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(e)}")