import pandas as pd
import logging

# Configuramos un logger básico para tener trazabilidad en consola
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraTransformer:
    """
    Transformador de datos para Jira.
    Convierte exportaciones crudas (CSV/Excel) en tensores de entrada para XGBoost.
    
    Implementa:
    1. Mapeo semántico de columnas.
    2. Heurística de dependencias (Blocker_Count).
    3. Patrón Fallback para datos faltantes (Degradación Elegante).
    """
    
    @staticmethod
    def transformar_exportacion(df_crudo: pd.DataFrame) -> pd.DataFrame:
        logger.info("Iniciando transformación de datos Jira...")
        df = df_crudo.copy()
        
        # 1. Renombrar variables Jira a la nomenclatura del modelo
        mapeo_columnas = {
            "Issue key": "Issue_Key",
            "Summary": "Title",
            "Issue Type": "Issue_Type",
            "Custom field (Story Points)": "Story_Point",
            "Status": "Sprint_State",
            "Project key": "Project_Name"
        }
        df = df.rename(columns={k: v for k, v in mapeo_columnas.items() if k in df.columns})
        
        # 2. Ingeniería de Características (Tiempos)
        if 'Created' in df.columns and 'Resolved' in df.columns:
            df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
            df['Resolved'] = pd.to_datetime(df['Resolved'], errors='coerce')
            df['Resolution_Time_Minutes'] = (df['Resolved'] - df['Created']).dt.total_seconds() / 60
            # FIX: Evitar NaNs por fechas inválidas o nulas
            df['Resolution_Time_Minutes'] = df['Resolution_Time_Minutes'].fillna(0.0)
        else:
            df['Resolution_Time_Minutes'] = 0.0

        if 'In_Progress_Minutes' not in df.columns:
            df['In_Progress_Minutes'] = df['Resolution_Time_Minutes'] * 0.4 
            
        # 3. Limpieza de Story Points
        df['Story_Point'] = df.get('Story_Point', 0.0).fillna(0.0)
            
        # 4. Cálculo heurístico de Blocker_Count (Extracción dinámica)
        columnas_bloqueo = [
            col for col in df.columns 
            if any(x in col.lower() for x in ['block', 'depend', 'flagged', 'impediment'])
        ]
        df['Blocker_Count'] = df[columnas_bloqueo].notna().sum(axis=1) if columnas_bloqueo else 0

        # 5. Patrón Fallback (Degradación Elegante) para variables históricas de auditoría
        columnas_auditoria = {
            'Project_ID': 999,
            'Sprint_ID': 1,
            'Total_Effort_Minutes': df.get('Resolution_Time_Minutes', 0),
            'Title_Changed_After_Estimation': 0,
            'Description_Changed_After_Estimation': 0,
            'Story_Point_Changed_After_Estimation': 0
        }
        
        for col, valor_defecto in columnas_auditoria.items():
            if col not in df.columns:
                df[col] = valor_defecto
                
        # FIX: Forzar el tipado a entero para curarnos en salud con Pydantic
        df['Sprint_ID'] = df['Sprint_ID'].fillna(0).astype(int)
        df['Project_ID'] = df['Project_ID'].fillna(0).astype(int)
                
        logger.info(f"Transformación completada. Columnas procesadas: {df.shape[1]}")
        return df