import pandas as pd
import io
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

class JiraFileReader:
    """
    Responsable único de la extracción. Ahora polivalente para CSV y Excel.
    """
    
    @staticmethod
    async def leer_archivo(archivo: UploadFile) -> pd.DataFrame:
        """
        Detecta la extensión y lee el archivo (CSV o Excel) a DataFrame.
        """
        logger.info(f"Ingestando archivo: {archivo.filename}")
        
        # 1. Validación de extensión
        extension = archivo.filename.split('.')[-1].lower()
        if extension not in ['csv', 'xlsx', 'xls']:
            raise HTTPException(
                status_code=400, 
                detail="Formato no admitido. Usa .csv, .xlsx o .xls"
            )
            
        try:
            contenido = await archivo.read()
            buffer = io.BytesIO(contenido)
            
            # 2. Lógica de lectura condicional
            if extension == 'csv':
                df = pd.read_csv(buffer)
            else:
                # Pandas usa openpyxl internamente para xlsx
                df = pd.read_excel(buffer)
            
            if df.empty:
                raise HTTPException(status_code=400, detail="El archivo está vacío.")
                
            logger.info(f"Archivo {extension} procesado. Filas: {len(df)}")
            return df
                
        except Exception as e:
            logger.error(f"Error crítico durante la lectura: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {str(e)}")