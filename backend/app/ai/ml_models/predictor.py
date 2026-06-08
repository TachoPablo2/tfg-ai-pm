import pandas as pd
import joblib
import os
import logging
from typing import List

from app.api.schemas.pydantic_models import AnalysisRequest, TaskPrediction
from app.core.exceptions import ModelInferenceError

logger = logging.getLogger(__name__)

class MLPredictor:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        models_dir = os.path.join(base_dir, "models")
        
        retrasos_path = os.path.join(models_dir, "modelo_retrasos_xgb.pkl")
        riesgos_path = os.path.join(models_dir, "modelo_riesgos_xgb.pkl")
        
        logger.info("Cargando pipelines de Machine Learning (XGBoost) en memoria...")
        try:
            self.pipeline_riesgo = joblib.load(riesgos_path)
            
            retrasos_data = joblib.load(retrasos_path)
            self.pipeline_retraso = retrasos_data['pipeline']
            self.umbral_retraso = retrasos_data.get('optimal_threshold', 0.5)
            
            logger.info("✅ Modelos ML cargados correctamente.")
        except Exception as e:
            logger.error(f"Error crítico al cargar los modelos: {str(e)}")
            raise ModelInferenceError(f"Error al cargar los modelos ML: {str(e)}")

    def predict(self, request_data: AnalysisRequest) -> List[TaskPrediction]:
        df_input = pd.DataFrame([tarea.model_dump() for tarea in request_data.tareas])
        
        if df_input.empty:
            raise ModelInferenceError("No hay tareas válidas para predecir tras el preprocesamiento.")
        
        # 2. PREVENCIÓN DE DATA LEAKAGE (Exactamente como en el Notebook 5)
        cols_to_drop_global = [
            'Issue_Key', 'Project_ID', 'Project_Name', 'Sprint_ID', 
            'Resolution_Time_Minutes', 'Target_Retraso', 'Target_Riesgo'
        ]
        X_ret = df_input.drop(columns=cols_to_drop_global, errors='ignore')
        
        cols_leakage_riesgo = [
            'Blocker_Count', 'Story_Point_Changed_After_Estimation', 'Description_Changed_After_Estimation'
        ]
        X_rsg = X_ret.drop(columns=cols_leakage_riesgo, errors='ignore')
        
        # 3. Inferencia matemática
        prob_retrasos = self.pipeline_retraso.predict_proba(X_ret)[:, 1]
        prob_riesgos = self.pipeline_riesgo.predict_proba(X_rsg)[:, 1]
        
        # 4. Ensamblar la respuesta estructurada arrastrando el contexto operativo
        predicciones = []
        for i, tarea in enumerate(request_data.tareas):
            p_riesgo = float(prob_riesgos[i])
            p_retraso = float(prob_retrasos[i])
            
            # Extraemos atributos de forma segura para evitar errores de clave
            bloqueos = int(getattr(tarea, 'Blocker_Count', 0))
            
            # Lógica de semáforo de Riesgo (Notebook 5)
            gravedad = self._calcular_gravedad_riesgo(p_riesgo, bloqueos)
            
            prediccion = TaskPrediction(
                Issue_Key=tarea.Issue_Key,
                Title=tarea.Title,
                Issue_Type=getattr(tarea, 'Issue_Type', 'Task'),
                Status=getattr(tarea, 'Status', 'Open'),
                Story_Points=float(getattr(tarea, 'Story_Point', 0.0)),
                Blocker_Count=bloqueos,
                Created_Date=getattr(tarea, 'Created_Date', None),
                Prob_Riesgo=round(p_riesgo, 4),
                Prob_Retraso=round(p_retraso, 4),
                Gravedad=gravedad
            )
            predicciones.append(prediccion)
            
        return predicciones

    def _calcular_gravedad_riesgo(self, prob_riesgo: float, bloqueos: int) -> str:
        """Réplica del semáforo híbrido del cuaderno."""
        if prob_riesgo >= 0.75 or bloqueos > 1:
            return "🔴 Alto"
        elif prob_riesgo >= 0.55 or bloqueos == 1:
            return "🟡 Medio"
        else:
            return "🟢 Bajo"

ml_predictor = MLPredictor()