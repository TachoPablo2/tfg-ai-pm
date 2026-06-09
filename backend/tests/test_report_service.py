import pytest
from app.core.services.report_service import ReportService
from app.core.exceptions import ReportGenerationError


class TestReportService:
    def test_generar_pdf_basic(self, mocker):
        mock_fpdf = mocker.patch("app.core.services.report_service.FPDF")
        mock_instance = mock_fpdf.return_value
        mock_instance.output.return_value = b"%PDF-1.4 mock content"
        service = ReportService()
        result = service.generar_pdf_en_memoria(
            datos_ui={
                "Configuracion": {"Alcance": "Sprint", "Rol": "PM"},
                "UI_Header_KPIs": {
                    "Total_Tareas": 5,
                    "Tasa_Completado_Pct": 60.0,
                    "Esfuerzo_Total": 20.0,
                    "Tareas_Bloqueadas_Activas": 1,
                    "Riesgo_Promedio": 0.3,
                    "Retraso_Promedio": 0.2,
                },
                "LLM_Tab_2_Contexto": {
                    "Metricas_Globales_Negocio": {
                        "Esfuerzo_Total_Comprometido_En_Riesgo": 5.0,
                    }
                },
            },
            recomendacion_ia="• Recomendación de prueba.",
            graficos=None,
        )
        assert result is not None

    def test_generar_pdf_with_graficos(self, mocker):
        mock_fpdf = mocker.patch("app.core.services.report_service.FPDF")
        mock_instance = mock_fpdf.return_value
        mock_instance.output.return_value = b"%PDF-1.4 mock content"
        service = ReportService()
        result = service.generar_pdf_en_memoria(
            datos_ui={"Configuracion": {}, "UI_Header_KPIs": {}},
            recomendacion_ia="• Test.",
            graficos=[],
        )
        assert result is not None

    def test_generar_pdf_failure(self, mocker):
        mocker.patch("app.core.services.report_service.FPDF", side_effect=RuntimeError("PDF lib failed"))
        service = ReportService()
        with pytest.raises(ReportGenerationError, match="PDF"):
            service.generar_pdf_en_memoria(
                datos_ui={},
                recomendacion_ia="• Test.",
                graficos=None,
            )


class TestDecodeBase64Image:
    def test_decode_png(self, mocker):
        import base64
        fake_png = b"fake_png_binary_data"
        b64 = base64.b64encode(fake_png).decode()
        mocker.patch("app.core.services.report_service.FPDF")

        service = ReportService()
        # La imagen no es SVG, pasa directo
        result = service._decode_base64_image(f"data:image/png;base64,{b64}")
        assert result == fake_png

    def test_decode_svg_with_cairosvg(self, mocker, mock_cairosvg):
        import base64
        svg_content = b"<svg><circle/></svg>"
        b64 = base64.b64encode(svg_content).decode()
        mocker.patch("app.core.services.report_service.FPDF")

        service = ReportService()
        result = service._decode_base64_image(f"data:image/svg+xml;base64,{b64}")
        assert result == b"fake_png_data"

    def test_decode_svg_without_cairosvg(self, mocker):
        import base64
        svg_content = b"<svg></svg>"
        b64 = base64.b64encode(svg_content).decode()
        mocker.patch("app.core.services.report_service.HAS_CAIROSVG", False)
        mocker.patch("app.core.services.report_service.FPDF")

        service = ReportService()
        with pytest.raises(ReportGenerationError, match="cairosvg"):
            service._decode_base64_image(f"data:image/svg+xml;base64,{b64}")

    def test_decode_invalid_base64(self, mocker):
        mocker.patch("app.core.services.report_service.FPDF")
        service = ReportService()
        with pytest.raises(ReportGenerationError, match="decodificando"):
            service._decode_base64_image("not-valid-base64!!!")


class TestFindFontDir:
    def test_find_font_returns_none_on_unknown_system(self, mocker):
        mocker.patch("app.core.services.report_service.platform.system", return_value="UnknownOS")
        from app.core.services.report_service import _find_font_dir
        result = _find_font_dir()
        assert result is None
