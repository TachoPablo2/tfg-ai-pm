import pandas as pd
import io
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
import logging

from app.core.exceptions import FileValidationError

logger = logging.getLogger(__name__)

class JiraFileReader:
    
    @staticmethod
    async def leer_archivo(archivo: UploadFile) -> pd.DataFrame:
        logger.info(f"Ingestando archivo: {archivo.filename}")
        
        extension = archivo.filename.split('.')[-1].lower()
        if extension not in ['csv', 'xlsx', 'xls']:
            raise FileValidationError("Formato no admitido. Usa .csv, .xlsx o .xls")
            
        try:
            contenido = await archivo.read()
            buffer = io.BytesIO(contenido)
            
            if extension == 'csv':
                df = await run_in_threadpool(pd.read_csv, buffer)
            else:
                df = await run_in_threadpool(pd.read_excel, buffer)
            
            if df.empty:
                raise FileValidationError("El archivo está vacío.")
                
            logger.info(f"Archivo {extension} procesado. Filas: {len(df)}")
            return df
                
        except FileValidationError:
            raise
        except Exception as e:
            logger.error(f"Error crítico durante la lectura: {str(e)}")
            raise FileValidationError(f"No se pudo procesar el archivo: {str(e)}")
