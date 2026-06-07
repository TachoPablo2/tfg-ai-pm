from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


# 1. ESQUEMA DE ENTRADA (Validación de los datos del CSV fila por fila)
class TaskRecord(BaseModel):
    Issue_Key: str = Field(..., description="Identificador único de la tarea")
    Title: str = Field(..., description="Título o resumen de la tarea")
    Issue_Type: str = Field(..., description="Tipo de tarea (Bug, Story, Enhancement, etc.)")
    Project_ID: int = Field(..., description="ID numérico del proyecto")
    Project_Name: str = Field(..., description="Nombre comercial del proyecto")
    Sprint_ID: int = Field(..., description="ID del sprint")
    Sprint_State: str = Field(..., description="Estado actual del sprint (ej. ACTIVE)")
    
    # Métricas core para los modelos XGBoost
    Story_Point: float = Field(..., description="Puntos de historia estimados")
    Total_Effort_Minutes: float = Field(..., description="Esfuerzo total registrado en minutos")
    In_Progress_Minutes: float = Field(..., description="Tiempo en la columna In Progress")
    Resolution_Time_Minutes: float = Field(..., description="Tiempo total hasta la resolución")
    
    # Variables binarias y conteos
    Title_Changed_After_Estimation: int = Field(..., description="0 o 1 si el título cambió")
    Description_Changed_After_Estimation: int = Field(..., description="0 o 1 si la descripción cambió")
    Story_Point_Changed_After_Estimation: int = Field(..., description="0 o 1 si la estimación cambió")
    Blocker_Count: int = Field(..., description="Número de impedimentos/bloqueos registrados")

# 2. ESQUEMA DE RESPUESTA (Lo que devolverá la API al Frontend React)
class TaskPrediction(BaseModel):
    Issue_Key: str
    Title: str
    Riesgo_Probabilidad: float
    Retraso_Probabilidad: float
    Alerta: str  # Ej: "Crítico", "Moderado", "Controlado"

class AnalysisResponse(BaseModel):
    proyecto: str
    alcance: str
    tareas_analizadas: int
    predicciones: List[TaskPrediction]
    recomendacion_ia: str
    

class AnalysisRequest(BaseModel):
    """
    Esquema que agrupa la petición completa: Los metadatos del frontend + las filas del CSV.
    """
    alcance: str = Field(..., description="Debe ser 'sprint' o 'proyecto'")
    rol: str = Field(..., description="Debe ser 'PM' o 'PMO'")
    tareas: List[TaskRecord] = Field(..., description="Lista de filas extraídas del archivo")

    @model_validator(mode='after')
    def validar_coherencia_alcance(self):
        # 1. Comprobar que hay datos
        if not self.tareas:
            raise ValueError("El archivo está vacío o no se pudieron extraer las tareas.")

        # 2. Extraer los IDs únicos usando conjuntos (sets)
        sprints_unicos = {tarea.Sprint_ID for tarea in self.tareas}
        proyectos_unicos = {tarea.Project_ID for tarea in self.tareas}

        # 3. Aplicar las reglas de negocio según el alcance
        if self.alcance.lower() == 'sprint':
            if len(sprints_unicos) > 1:
                raise ValueError(
                    f"Incongruencia detectada (Fail-Fast): Has seleccionado análisis de 'sprint', "
                    f"pero el archivo contiene tareas de múltiples sprints distintos: {sprints_unicos}. "
                    "Por favor, sube un archivo filtrado para un solo sprint."
                )
                
        elif self.alcance.lower() == 'proyecto':
            if len(proyectos_unicos) > 1:
                raise ValueError(
                    f"Incongruencia detectada (Fail-Fast): Has seleccionado análisis de 'proyecto', "
                    f"pero el archivo mezcla tareas de varios proyectos diferentes: {proyectos_unicos}. "
                    "Por favor, sube el histórico de un único proyecto."
                )
        else:
            raise ValueError("El alcance especificado no es válido. Usa 'sprint' o 'proyecto'.")

        return self