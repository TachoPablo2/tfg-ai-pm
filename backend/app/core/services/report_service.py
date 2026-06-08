import io
import base64
import datetime
import logging

from fpdf import FPDF

from app.core.exceptions import ReportGenerationError


def _sanitize(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")

logger = logging.getLogger(__name__)


class ReportService:

    def generar_pdf_en_memoria(
        self,
        datos_ui: dict,
        recomendacion_ia: str,
        grafico_base64: str | None = None,
    ) -> io.BytesIO:
        try:
            pdf = FPDF()
            pdf.add_page()

            self._add_header(pdf, datos_ui)
            self._add_kpis_section(pdf, datos_ui)

            tiene_grafico = bool(grafico_base64)
            if tiene_grafico:
                self._add_chart_section(pdf, grafico_base64)

            num_seccion = "3" if tiene_grafico else "2"
            self._add_ia_recommendations(pdf, recomendacion_ia, num_seccion)

            # fpdf2 built-in fonts solo soportan Latin-1.
            # Para Unicode completo (tildes, eñes), registrar una TTF:
            #   pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
            #   pdf.set_font("DejaVu", size=11)
            pdf_bytes = pdf.output(dest="S").encode("latin-1", errors="replace")
            return io.BytesIO(pdf_bytes)

        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            raise ReportGenerationError(f"Error al generar el PDF: {e}") from e

    def _add_header(self, pdf: FPDF, datos_ui: dict) -> None:
        config = datos_ui.get("Configuracion", {})
        alcance = config.get("Alcance", "Proyecto")
        titulo = f"Informe Ejecutivo de {alcance} (IA)"
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, txt=_sanitize(titulo), ln=True, align="C")
        pdf.set_font("Arial", "I", 10)
        pdf.cell(
            0,
            10,
            txt=_sanitize(f"Generado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"),
            ln=True,
            align="C",
        )
        pdf.ln(5)

    def _add_kpis_section(self, pdf: FPDF, datos_ui: dict) -> None:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, txt=_sanitize("1. Metricas Operativas Globales"), ln=True)
        pdf.set_font("Arial", size=11)
        kpis = datos_ui.get("UI_Header_KPIs", {})
        for nombre, valor in kpis.items():
            pdf.cell(0, 8, txt=_sanitize(f"- {nombre.replace('_', ' ')}: {valor}"), ln=True)
        pdf.ln(5)

    def _add_chart_section(self, pdf: FPDF, grafico_base64: str) -> None:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, txt=_sanitize("2. Evolución del Riesgo y Retraso"), ln=True)
        image_bytes = self._decode_base64_image(grafico_base64)
        pdf.image(io.BytesIO(image_bytes), x=10, y=pdf.get_y(), w=190)
        pdf.ln(100)

    def _decode_base64_image(self, grafico_base64: str) -> bytes:
        if "," in grafico_base64:
            grafico_base64 = grafico_base64.split(",", 1)[1]
        try:
            return base64.b64decode(grafico_base64)
        except Exception as e:
            raise ReportGenerationError(
                f"Error decodificando imagen base64: {e}"
            ) from e

    def _add_ia_recommendations(
        self, pdf: FPDF, recomendacion_ia: str, num_seccion: str
    ) -> None:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, txt=_sanitize(f"{num_seccion}. Recomendaciones Estratégicas (LLM)"), ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, txt=_sanitize(recomendacion_ia))


report_service = ReportService()

