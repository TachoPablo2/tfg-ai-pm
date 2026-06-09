import json
import asyncio
import pandas as pd
import logging
import ollama
import time
from typing import List, Dict, Any

from app.api.schemas.pydantic_models import TaskPrediction
from app.core.exceptions import LLMInferenceError

logger = logging.getLogger(__name__)

EMPTY_PAYLOAD = {
    "Configuracion": {"Alcance": "", "Rol": ""},
    "UI_Header_KPIs": {},
    "UI_Tab_1_Estado": {},
    "LLM_Tab_2_Contexto": {},
}

LLM_TIMEOUT_SECONDS = 120


class LLMService:

    def __init__(self):
        self.llm_model = "llama3"

    async def generar_informe(self, predicciones: List[TaskPrediction], rol: str, alcance: str) -> dict:
        if not predicciones:
            from app.api.schemas.pydantic_models import DatosUI
            return {
                "datos_ui": DatosUI(**EMPTY_PAYLOAD),
                "recomendacion_ia": "No hay datos suficientes para generar recomendaciones.",
            }

        payload_sistema = self.construir_payload(predicciones, rol, alcance)

        context_data_llm = payload_sistema.get("LLM_Tab_2_Contexto", {})

        system_p, user_p = self._build_prompt(context_data_llm, rol, alcance)

        logger.info(f"Iniciando solicitud a Ollama ({self.llm_model}) para {rol} en {alcance}...")
        start_time = time.time()

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    ollama.chat,
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_p},
                        {"role": "user", "content": user_p},
                    ],
                    stream=False,
                    options={
                        "temperature": 0.3,
                        "num_ctx": 4096,
                    },
                ),
                timeout=LLM_TIMEOUT_SECONDS,
            )

            latencia = time.time() - start_time
            logger.info(f"Tiempo total LLM: {latencia:.2f} segundos")

            texto_recomendacion = response["message"]["content"]

        except asyncio.TimeoutError:
            latencia = time.time() - start_time
            logger.error(f"Timeout LLM tras {latencia:.2f}s")
            raise LLMInferenceError(
                f"El modelo LLM no respondió en {LLM_TIMEOUT_SECONDS}s. Inténtelo de nuevo."
            )
        except Exception as e:
            latencia = time.time() - start_time
            logger.error(f"ERROR DE CONEXIÓN CON EL LLM (Latencia: {latencia:.2f}s): {e}")
            raise LLMInferenceError(f"LLM no disponible: {e}")

        from app.api.schemas.pydantic_models import DatosUI
        return {
            "datos_ui": DatosUI(**payload_sistema),
            "recomendacion_ia": texto_recomendacion,
        }

    def _build_prompt(self, context_data_llm: dict, user_role: str, scope: str) -> tuple[str, str]:
        context_str = json.dumps(context_data_llm, indent=2, ensure_ascii=False)

        if scope == "Sprint":
            focus = "ALCANCE SPRINT: Evalúa las predicciones de riesgo y retraso correspondientes a las tareas de esta iteración única. Tu prioridad es mitigar el impacto operativo inmediato analizando la carga de trabajo y los bloqueos diarios activos."
        else:
            focus = "ALCANCE PROYECTO: Evalúa las predicciones de riesgo y retraso agregadas de múltiples iteraciones. Tu prioridad es identificar tendencias de desviación a largo plazo, evaluar la salud global del proyecto y detectar patrones de bloqueo recurrentes."

        if user_role == "Project Manager":
            instruccion_rol = "ROL PM: Eres un consultor táctico. Genera recomendaciones operativas a corto plazo (reasignación de tareas, resolución de bloqueos, repriorización del backlog, pair programming). Usa un tono directo y orientado a la ejecución del equipo."
        else:
            instruccion_rol = "ROL PMO: Eres un consultor estratégico. Genera recomendaciones estructurales (cambios metodológicos, reajuste de presupuesto, auditoría de procesos corporativos, balanceo de capacidad técnica). Usa un tono analítico, formal y directivo."

        system_prompt = f"""
        Eres un Sistema Inteligente de Apoyo a la Decisión para la gestión ágil de proyectos.

        {instruccion_rol}
        {focus}

        REGLAS ESTRICTAS DE NEGOCIO:
        1. IDIOMA ESTRICTO: Responde ÚNICA Y EXCLUSIVAMENTE en Español. No uses términos en inglés salvo los propios del contexto (ej. Issue_Key).
        2. ABORDA AMBAS DIMENSIONES: Propón soluciones tanto para RETRASO como para RIESGO. Agrupa tareas similares en una misma recomendación.
        3. JUSTIFICACIÓN Y CERO ALUCINACIONES: Justifica cada recomendación citando los valores del contexto. NUNCA inventes Issue_Keys, títulos ni métricas.
        4. NOMBRA LAS TAREAS: Cita siempre Issue_Key y Title juntos (ej. "PRO-301 'Error de validación en formulario'").
        5. ESTRUCTURA: Devuelve exactamente 3 recomendaciones en viñetas. Cada viñeta debe citar al menos una tarea distinta. Sin introducciones ni saludos. Empieza con •.

        <reglas_interpretacion>
        - NUNCA escribas probabilidades como decimales. 1.0 → "100%", 0.63 → "63%", 0.80 → "80%". Sin excepciones. Aplica a Prob_Riesgo, Prob_Retraso, Riesgo_General y Retraso_General.
        - Un valor de Prob_Riesgo de 0.06 significa riesgo BAJO. Un valor de 0.94 significa riesgo ALTO.
        - Una probabilidad de retraso superior al 50% es ALTA, no baja. Superior al 75% es CRÍTICA.
        - Toda viñeta debe mencionar el porcentaje explícitamente, nunca solo la etiqueta "Alto" o "Medio".
        - La gravedad de cada tarea viene en el campo "Gravedad". Cópialo tal cual, no lo recalcules.
        - Si Blocker_Count > 0, la tarea es urgente independientemente de su probabilidad.
        </reglas_interpretacion>

        <datos_ml>
        {context_str}
        </datos_ml>
        """

        user_prompt = "Redacta el reporte de recomendaciones estratégicas en perfecto español basándote estrictamente en las predicciones proporcionadas."
        return system_prompt, user_prompt

    def construir_payload(self, predicciones: List[TaskPrediction], rol: str, alcance: str) -> Dict[str, Any]:
        df_analisis = pd.DataFrame([p.model_dump() for p in predicciones])

        cond_riesgo = (df_analisis["Prob_Riesgo"] > 0.55) | (df_analisis["Blocker_Count"] > 0)
        top_riesgos_df = df_analisis[cond_riesgo].sort_values(
            by=["Blocker_Count", "Prob_Riesgo"], ascending=[False, False]
        ).head(3).copy()

        top_riesgos_df["Prob_Riesgo"] = top_riesgos_df["Prob_Riesgo"].round(2)
        lista_top_riesgos = top_riesgos_df[[
            "Issue_Key", "Issue_Type", "Title", "Blocker_Count", "Prob_Riesgo", "Gravedad"
        ]].to_dict(orient="records")

        cond_retraso = df_analisis["Prob_Retraso"] > 0.55
        top_retrasos_df = df_analisis[cond_retraso].sort_values(
            by="Prob_Retraso", ascending=False
        ).head(3).copy()

        top_retrasos_df["Prob_Retraso"] = top_retrasos_df["Prob_Retraso"].round(2)
        lista_top_retrasos = top_retrasos_df[[
            "Issue_Key", "Issue_Type", "Title", "Prob_Retraso"
        ]].to_dict(orient="records")

        kpi_riesgo_medio = float(df_analisis["Prob_Riesgo"].mean())
        kpi_retraso_medio = float(df_analisis["Prob_Retraso"].mean())
        tareas_bloqueadas_total = int((df_analisis["Blocker_Count"] > 0).sum())
        total_story_points = float(df_analisis["Story_Points"].sum())

        semaforo_global = "Rojo" if kpi_riesgo_medio >= 0.60 else "Amarillo" if kpi_riesgo_medio >= 0.30 else "Verde"

        if "Status" in df_analisis.columns:
            tareas_cerradas = len(df_analisis[df_analisis["Status"].str.lower().isin(["closed", "done", "resolved", "cerrada"])])
        else:
            tareas_cerradas = 0
        tasa_completado = round((tareas_cerradas / max(1, len(df_analisis))) * 100, 2)

        tareas_criticas = df_analisis[
            (df_analisis["Prob_Riesgo"] > 0.7)
            | (df_analisis["Prob_Retraso"] > 0.7)
            | (df_analisis["Blocker_Count"] > 0)
        ]
        esfuerzo_col = "Story_Points" if "Story_Points" in df_analisis.columns else "Total_Effort_Minutes"
        if esfuerzo_col in tareas_criticas.columns:
            esfuerzo_en_riesgo = float(tareas_criticas[esfuerzo_col].sum())
        else:
            esfuerzo_en_riesgo = 0.0

        evolucion_riesgo = {}
        evolucion_retraso = {}
        grafico_riesgo_tipo = {}

        if alcance == "Proyecto" and "Sprint_ID" in df_analisis.columns:
            evolucion_riesgo = df_analisis.groupby("Sprint_ID")["Prob_Riesgo"].mean().round(2).to_dict()
            evolucion_retraso = df_analisis.groupby("Sprint_ID")["Prob_Retraso"].mean().round(2).to_dict()
        elif "Created_Date" in df_analisis.columns and not df_analisis["Created_Date"].isnull().all():
            df_analisis = df_analisis.copy()
            df_analisis["Dia"] = pd.to_datetime(df_analisis["Created_Date"], errors="coerce").dt.date
            df_valido = df_analisis.dropna(subset=["Dia"])
            if not df_valido.empty:
                evolucion_riesgo = df_valido.groupby(df_valido["Dia"].astype(str))["Prob_Riesgo"].mean().round(2).to_dict()
                evolucion_retraso = df_valido.groupby(df_valido["Dia"].astype(str))["Prob_Retraso"].mean().round(2).to_dict()

        if "Issue_Type" in df_analisis.columns:
            grafico_riesgo_tipo = df_analisis.groupby("Issue_Type")["Prob_Riesgo"].mean().round(2).to_dict()

        return {
            "Configuracion": {"Alcance": alcance, "Rol": rol},
            "UI_Header_KPIs": {
                "Total_Tareas": int(len(df_analisis)),
                "Tasa_Completado_Pct": tasa_completado,
                "Esfuerzo_Total": total_story_points,
                "Tareas_Bloqueadas_Activas": tareas_bloqueadas_total,
                "Riesgo_Promedio": round(kpi_riesgo_medio, 2),
                "Retraso_Promedio": round(kpi_retraso_medio, 2),
            },
            "UI_Tab_1_Estado": {
                "Semaforo_Riesgo_Global": semaforo_global,
                "Alerta_Retraso_Global": "Activada" if kpi_retraso_medio > 0.50 else "Desactivada",
                "Grafico_Riesgo_por_Tipo": grafico_riesgo_tipo,
                "Grafico_Evolucion_Riesgo": evolucion_riesgo,
                "Grafico_Evolucion_Retraso": evolucion_retraso,
            },
            "LLM_Tab_2_Contexto": {
                "Metricas_Globales_Negocio": {
                    "Riesgo_General": round(kpi_riesgo_medio, 2),
                    "Retraso_General": round(kpi_retraso_medio, 2),
                    "Total_Bloqueos_Activos": tareas_bloqueadas_total,
                    "Esfuerzo_Total_Comprometido_En_Riesgo": esfuerzo_en_riesgo,
                },
                "Tendencias": {
                    "Evolucion_Riesgo": evolucion_riesgo,
                    "Evolucion_Retraso": evolucion_retraso,
                },
                "Top_Tareas_Riesgo_Bloqueos": lista_top_riesgos,
                "Top_Tareas_Retraso_Cronograma": lista_top_retrasos,
            },
        }


llm_service = LLMService()
