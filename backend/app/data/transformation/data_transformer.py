import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

IN_PROGRESS_RATIO = 0.4
SPRINT_ID_DEFAULT = 1
PROJECT_ID_DEFAULT = 999


class JiraTransformer:

    @staticmethod
    def transformar_exportacion(df_crudo: pd.DataFrame) -> pd.DataFrame:
        logger.info("Iniciando transformación de datos Jira...")

        # 1. Renombrar variables Jira a la nomenclatura del modelo
        mapeo_columnas = {
            "Issue key": "Issue_Key",
            "Summary": "Title",
            "Issue Type": "Issue_Type",
            "Custom field (Story Points)": "Story_Point",
            "Custom field (10002)": "Story_Point",
            "Status": "Status",
            "Project key": "Project_Name",
        }
        rename_map = {k: v for k, v in mapeo_columnas.items() if k in df_crudo.columns}
        df = df_crudo.rename(columns=rename_map)

        # Fallback si el CSV no tenía columna Project key
        if "Project_Name" not in df.columns:
            df["Project_Name"] = "Default Project"

        # 2. Ingeniería de Características (Tiempos)
        if "Created" in df.columns and "Resolved" in df.columns:
            df["Created"] = pd.to_datetime(df["Created"], errors="coerce")
            df["Resolved"] = pd.to_datetime(df["Resolved"], errors="coerce")
            df["Resolution_Time_Minutes"] = (
                (df["Resolved"] - df["Created"]).dt.total_seconds() / 60
            )
            df["Resolution_Time_Minutes"] = df["Resolution_Time_Minutes"].fillna(0.0)
            df["Created_Date"] = df["Created"].dt.strftime("%Y-%m-%d")
            df["Created_Date"] = df["Created_Date"].replace("NaT", None)
        else:
            if "Resolution_Time_Minutes" not in df.columns:
                df["Resolution_Time_Minutes"] = 0.0
            if "Created_Date" not in df.columns:
                df["Created_Date"] = None

        if "In_Progress_Minutes" not in df.columns:
            df["In_Progress_Minutes"] = df["Resolution_Time_Minutes"] * IN_PROGRESS_RATIO

        # 3. Limpieza de Story Points
        if "Story_Point" in df.columns:
            df["Story_Point"] = pd.to_numeric(df["Story_Point"], errors="coerce").fillna(0.0)
        else:
            df["Story_Point"] = 0.0

        # 4. Cálculo heurístico de Blocker_Count (solo si no existe ya)
        if "Blocker_Count" not in df.columns:
            columnas_bloqueo = [
                col
                for col in df.columns
                if col != "Blocker_Count"
                and any(x in col.lower() for x in ["block", "depend", "flagged", "impediment"])
            ]
            df["Blocker_Count"] = (
                df[columnas_bloqueo].notna().sum(axis=1).astype(int)
                if columnas_bloqueo
                else 0
            )

        # 5. Patrón Fallback para variables históricas de auditoría
        columnas_auditoria = {
            "Project_ID": PROJECT_ID_DEFAULT,
            "Sprint_ID": SPRINT_ID_DEFAULT,
            "Sprint_State": "ACTIVE",
            "Total_Effort_Minutes": df.get("Resolution_Time_Minutes", 0),
            "Title_Changed_After_Estimation": 0,
            "Description_Changed_After_Estimation": 0,
            "Story_Point_Changed_After_Estimation": 0,
        }

        for col, valor_defecto in columnas_auditoria.items():
            if col not in df.columns:
                df[col] = valor_defecto

        # 6. Tipado explícito con downcasting para ahorrar memoria
        df["Sprint_ID"] = (
            pd.to_numeric(df["Sprint_ID"], errors="coerce")
            .fillna(SPRINT_ID_DEFAULT)
            .astype(int)
        )
        df["Project_ID"] = (
            pd.to_numeric(df["Project_ID"], errors="coerce")
            .fillna(PROJECT_ID_DEFAULT)
            .astype(int)
        )

        logger.info(
            f"Transformación completada. Columnas procesadas: {df.shape[1]}"
        )
        return df

    @staticmethod
    def dataframe_to_records(df: pd.DataFrame) -> list:
        df_safe = df.replace({np.nan: None})
        return df_safe.to_dict(orient="records")