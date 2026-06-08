from typing import List, Literal
from pydantic import BaseModel, Field, model_validator


class TaskRecord(BaseModel):
    Issue_Key: str = Field(..., description="Identificador único de la tarea")
    Title: str = Field(..., description="Título o resumen de la tarea")
    Issue_Type: str = Field(..., description="Tipo de tarea (Bug, Story, Enhancement, etc.)")
    Project_ID: int = Field(..., description="ID numérico del proyecto")
    Project_Name: str = Field(..., description="Nombre comercial del proyecto")
    Sprint_ID: int = Field(..., description="ID del sprint")
    Sprint_State: str = Field(..., description="Estado actual del sprint (ej. ACTIVE)")
    Story_Point: float = Field(..., description="Puntos de historia estimados")
    Total_Effort_Minutes: float = Field(..., description="Esfuerzo total registrado en minutos")
    In_Progress_Minutes: float = Field(..., description="Tiempo en la columna In Progress")
    Resolution_Time_Minutes: float = Field(..., description="Tiempo total hasta la resolución")
    Title_Changed_After_Estimation: int = Field(..., description="0 o 1 si el título cambió")
    Description_Changed_After_Estimation: int = Field(..., description="0 o 1 si la descripción cambió")
    Story_Point_Changed_After_Estimation: int = Field(..., description="0 o 1 si la estimación cambió")
    Blocker_Count: int = Field(..., description="Número de impedimentos/bloqueos registrados")
    Status: str = Field(default="Open", description="Estado actual de la tarea (ej. Open, Closed, Done)")
    Created_Date: str | None = Field(default=None, description="Fecha de creación (YYYY-MM-DD)")


class TaskPrediction(BaseModel):
    Issue_Key: str
    Title: str
    Issue_Type: str
    Status: str
    Story_Points: float
    Blocker_Count: int
    Created_Date: str | None = None
    Prob_Riesgo: float = Field(..., ge=0.0, le=1.0)
    Prob_Retraso: float = Field(..., ge=0.0, le=1.0)
    Gravedad: str


class AnalysisResponse(BaseModel):
    datos_ui: dict
    recomendacion_ia: str


class ReportRequest(BaseModel):
    datos_ui: dict
    recomendacion_ia: str = Field(..., min_length=1)
    grafico_base64: str | None = None


class AnalysisRequest(BaseModel):
    alcance: Literal["Sprint", "Proyecto"] = Field(..., description="Alcance del análisis")
    rol: Literal["Project Manager", "PMO"] = Field(..., description="Rol del analista")
    tareas: List[TaskRecord] = Field(..., description="Lista de filas extraídas del archivo")

    @model_validator(mode="after")
    def validar_coherencia_alcance(self):
        if not self.tareas:
            raise ValueError("El archivo está vacío o no se pudieron extraer las tareas.")

        sprints_unicos = {tarea.Sprint_ID for tarea in self.tareas}
        proyectos_unicos = {tarea.Project_ID for tarea in self.tareas}

        if self.alcance == "Sprint":
            if len(sprints_unicos) > 1:
                raise ValueError(
                    f"Incongruencia detectada: Has seleccionado análisis de Sprint, "
                    f"pero el archivo contiene tareas de múltiples sprints: {sprints_unicos}. "
                    "Por favor, sube un archivo filtrado para un solo sprint."
                )
        elif self.alcance == "Proyecto":
            if len(proyectos_unicos) > 1:
                raise ValueError(
                    f"Incongruencia detectada: Has seleccionado análisis de Proyecto, "
                    f"pero el archivo mezcla tareas de varios proyectos: {proyectos_unicos}. "
                    "Por favor, sube el histórico de un único proyecto."
                )

        return self