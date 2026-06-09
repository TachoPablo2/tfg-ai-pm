import pytest
from pydantic import ValidationError
from app.api.schemas.pydantic_models import (
    TaskRecord,
    TaskPrediction,
    AnalysisRequest,
    AnalysisResponse,
    ConfiguracionUI,
    HeaderKPIs,
    Tab1Estado,
    MetricasNegocio,
    LLMContexto,
    DatosUI,
    ReportRequest,
)


class TestTaskRecord:
    def test_valid_task(self, sample_task_record):
        assert sample_task_record.Issue_Key == "PRO-101"
        assert sample_task_record.Story_Point == 5.0
        assert sample_task_record.Status == "Open"
        assert sample_task_record.Created_Date == "2024-01-15"

    def test_minimal_task(self):
        task = TaskRecord(
            Issue_Key="PRO-1",
            Title="Minimal",
            Issue_Type="Task",
            Project_ID=1,
            Project_Name="P",
            Sprint_ID=1,
            Sprint_State="ACTIVE",
            Story_Point=0.0,
            Total_Effort_Minutes=0.0,
            In_Progress_Minutes=0.0,
            Resolution_Time_Minutes=0.0,
            Title_Changed_After_Estimation=0,
            Description_Changed_After_Estimation=0,
            Story_Point_Changed_After_Estimation=0,
            Blocker_Count=0,
        )
        assert task.Status == "Open"
        assert task.Created_Date is None

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            TaskRecord()


class TestTaskPrediction:
    def test_valid_prediction(self, sample_prediction):
        assert sample_prediction.Prob_Riesgo == 0.85
        assert sample_prediction.Gravedad == "Alto"
        assert sample_prediction.Story_Points == 5.0

    def test_probability_bounds(self):
        with pytest.raises(ValidationError):
            TaskPrediction(
                Issue_Key="P-1",
                Title="T",
                Issue_Type="Bug",
                Status="Open",
                Story_Points=1.0,
                Blocker_Count=0,
                Sprint_ID=1,
                Created_Date=None,
                Prob_Riesgo=1.5,
                Prob_Retraso=0.5,
                Gravedad="Alto",
            )


class TestAnalysisRequest:
    def test_valid_sprint_request(self, sample_tasks):
        req = AnalysisRequest(alcance="Sprint", rol="Project Manager", tareas=sample_tasks)
        assert req.alcance == "Sprint"
        assert req.rol == "Project Manager"

    def test_empty_tareas(self):
        with pytest.raises(ValidationError, match="vacío"):
            AnalysisRequest(alcance="Sprint", rol="Project Manager", tareas=[])

    def test_multiple_sprints_raises_error(self, sample_task_record):
        from copy import deepcopy
        t1 = deepcopy(sample_task_record)
        t2 = deepcopy(sample_task_record)
        t2.Issue_Key = "PRO-102"
        t2.Sprint_ID = 2
        with pytest.raises(ValidationError, match="múltiples sprints"):
            AnalysisRequest(alcance="Sprint", rol="Project Manager", tareas=[t1, t2])

    def test_multiple_projects_raises_error(self, sample_task_record):
        from copy import deepcopy
        t1 = deepcopy(sample_task_record)
        t2 = deepcopy(sample_task_record)
        t2.Issue_Key = "PRO-102"
        t2.Project_ID = 100
        with pytest.raises(ValidationError, match="varios proyectos"):
            AnalysisRequest(alcance="Proyecto", rol="PMO", tareas=[t1, t2])

    def test_invalid_alcance(self, sample_tasks):
        with pytest.raises(ValidationError):
            AnalysisRequest(alcance="Invalid", rol="Project Manager", tareas=sample_tasks)


class TestConfiguracionUI:
    def test_defaults(self):
        c = ConfiguracionUI()
        assert c.Alcance == ""
        assert c.Rol == ""


class TestHeaderKPIs:
    def test_defaults(self):
        k = HeaderKPIs()
        assert k.Total_Tareas == 0
        assert k.Tasa_Completado_Pct == 0.0


class TestTab1Estado:
    def test_defaults(self):
        t = Tab1Estado()
        assert t.Semaforo_Riesgo_Global == "Verde"
        assert t.Alerta_Retraso_Global == "Desactivada"


class TestMetricasNegocio:
    def test_defaults(self):
        m = MetricasNegocio()
        assert m.Riesgo_General == 0.0
        assert m.Total_Bloqueos_Activos == 0


class TestLLMContexto:
    def test_defaults(self):
        ctx = LLMContexto()
        assert ctx.Metricas_Globales_Negocio.Riesgo_General == 0.0
        assert ctx.Top_Tareas_Riesgo_Bloqueos == []


class TestDatosUI:
    def test_defaults(self):
        d = DatosUI()
        assert d.Configuracion.Alcance == ""
        assert d.UI_Header_KPIs.Total_Tareas == 0

    def test_with_data(self):
        d = DatosUI(
            Configuracion=ConfiguracionUI(Alcance="Sprint", Rol="PM"),
            UI_Header_KPIs=HeaderKPIs(Total_Tareas=10),
        )
        assert d.Configuracion.Alcance == "Sprint"
        assert d.UI_Header_KPIs.Total_Tareas == 10


class TestAnalysisResponse:
    def test_valid(self):
        d = DatosUI()
        resp = AnalysisResponse(datos_ui=d, recomendacion_ia="Test recommendation")
        assert resp.recomendacion_ia == "Test recommendation"
        assert resp.datos_ui == d


class TestReportRequest:
    def test_valid(self):
        req = ReportRequest(datos_ui={"key": "val"}, recomendacion_ia="Test")
        assert req.datos_ui == {"key": "val"}
        assert req.graficos == []

    def test_with_graficos(self):
        req = ReportRequest(datos_ui={}, recomendacion_ia="Test", graficos=["img1", "img2"])
        assert len(req.graficos) == 2
