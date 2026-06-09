import pytest
import io
from fastapi import UploadFile
from app.core.exceptions import (
    FileValidationError,
    ModelInferenceError,
    LLMInferenceError,
    AnalysisError,
)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "motor de inferencia" in data["mensaje"]


class TestAnalyzeEndpoint:
    @pytest.mark.asyncio
    async def test_analyze_success(self, client, csv_bytes, mocker):
        mocker.patch(
            "app.api.routers.analysis.JiraFileReader.leer_archivo",
            return_value=__import__("pandas").DataFrame({
                "Issue_Key": ["PRO-101"],
                "Title": ["Test"],
                "Issue_Type": ["Bug"],
                "Status": ["Open"],
                "Story_Point": [5.0],
            }),
        )

        response = client.post(
            "/api/analyze/process",
            files={"file": ("test.csv", csv_bytes, "text/csv")},
            data={"alcance": "Sprint", "rol": "Project Manager"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "datos_ui" in data
        assert "recomendacion_ia" in data

    def test_analyze_file_validation_error(self, client, mocker):
        mocker.patch(
            "app.api.routers.analysis.JiraFileReader.leer_archivo",
            side_effect=FileValidationError("Invalid file"),
        )

        response = client.post(
            "/api/analyze/process",
            files={"file": ("bad.csv", b"", "text/csv")},
            data={"alcance": "Sprint", "rol": "Project Manager"},
        )
        assert response.status_code == 400

    def test_analyze_model_error(self, client, mocker):
        mocker.patch(
            "app.api.routers.analysis.JiraFileReader.leer_archivo",
            return_value=__import__("pandas").DataFrame({
                "Issue key": ["PRO-101"],
                "Summary": ["Test"],
                "Issue Type": ["Bug"],
                "Status": ["Open"],
                "Created": ["2024-01-15"],
                "Resolved": ["2024-01-16"],
                "Custom field (Story Points)": [5],
            }),
        )
        mocker.patch(
            "app.api.routers.analysis.AnalysisService.ejecutar_analisis_completo",
            side_effect=ModelInferenceError("Model failed"),
        )

        response = client.post(
            "/api/analyze/process",
            files={"file": ("test.csv", b"a,b\n1,2", "text/csv")},
            data={"alcance": "Sprint", "rol": "Project Manager"},
        )
        assert response.status_code == 503

    def test_analyze_llm_error(self, client, mocker):
        mocker.patch(
            "app.api.routers.analysis.JiraFileReader.leer_archivo",
            return_value=__import__("pandas").DataFrame({
                "Issue key": ["PRO-101"],
                "Summary": ["Test"],
                "Issue Type": ["Bug"],
                "Status": ["Open"],
                "Created": ["2024-01-15"],
                "Resolved": ["2024-01-16"],
                "Custom field (Story Points)": [5],
            }),
        )
        mocker.patch(
            "app.api.routers.analysis.AnalysisService.ejecutar_analisis_completo",
            side_effect=LLMInferenceError("LLM failed"),
        )

        response = client.post(
            "/api/analyze/process",
            files={"file": ("test.csv", b"a,b\n1,2", "text/csv")},
            data={"alcance": "Sprint", "rol": "Project Manager"},
        )
        assert response.status_code == 503

    def test_analyze_validation_error(self, client, mocker):
        mocker.patch(
            "app.api.routers.analysis.JiraFileReader.leer_archivo",
            return_value=__import__("pandas").DataFrame({"Issue_Key": ["P1"]}),
        )

        response = client.post(
            "/api/analyze/process",
            files={"file": ("test.csv", b"a,b\n1,2", "text/csv")},
            data={"alcance": "Invalid", "rol": "Project Manager"},
        )
        assert response.status_code == 422

    def test_analyze_analysis_error(self, client, mocker):
        mocker.patch(
            "app.api.routers.analysis.JiraFileReader.leer_archivo",
            side_effect=AnalysisError("Analysis failed"),
        )

        response = client.post(
            "/api/analyze/process",
            files={"file": ("test.csv", b"a,b\n1,2", "text/csv")},
            data={"alcance": "Sprint", "rol": "Project Manager"},
        )
        assert response.status_code == 422

    def test_analyze_internal_error(self, client, mocker):
        mocker.patch(
            "app.api.routers.analysis.JiraFileReader.leer_archivo",
            side_effect=RuntimeError("Unexpected crash"),
        )

        response = client.post(
            "/api/analyze/process",
            files={"file": ("test.csv", b"a,b\n1,2", "text/csv")},
            data={"alcance": "Sprint", "rol": "Project Manager"},
        )
        assert response.status_code == 500


class TestReportsEndpoint:
    def test_export_pdf_success(self, client, mocker):
        mocker.patch(
            "app.api.routers.reports.ReportService.generar_pdf_en_memoria",
            return_value=io.BytesIO(b"%PDF-1.4 fake pdf content"),
        )

        response = client.post(
            "/api/reports/export-pdf",
            json={
                "datos_ui": {"key": "val"},
                "recomendacion_ia": "Test recommendation",
                "graficos": [],
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "informe_ejecutivo_ia" in response.headers["content-disposition"]

    def test_export_pdf_generation_error(self, client, mocker):
        from app.core.exceptions import ReportGenerationError
        mocker.patch(
            "app.api.routers.reports.ReportService.generar_pdf_en_memoria",
            side_effect=ReportGenerationError("PDF failed"),
        )

        response = client.post(
            "/api/reports/export-pdf",
            json={
                "datos_ui": {},
                "recomendacion_ia": "Test",
                "graficos": [],
            },
        )
        assert response.status_code == 500

    def test_export_pdf_internal_error(self, client, mocker):
        mocker.patch(
            "app.api.routers.reports.ReportService.generar_pdf_en_memoria",
            side_effect=RuntimeError("Unexpected"),
        )

        response = client.post(
            "/api/reports/export-pdf",
            json={
                "datos_ui": {},
                "recomendacion_ia": "Test",
                "graficos": [],
            },
        )
        assert response.status_code == 500
