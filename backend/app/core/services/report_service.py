import io
import base64
import datetime
import logging

from fpdf import FPDF

from app.core.exceptions import ReportGenerationError

try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT_REGULAR = f"{FONT_DIR}/Arial.ttf"
FONT_BOLD = f"{FONT_DIR}/Arial Bold.ttf"
FONT_ITALIC = f"{FONT_DIR}/Arial Italic.ttf"
FONT_BOLD_ITALIC = f"{FONT_DIR}/Arial Bold Italic.ttf"

logger = logging.getLogger(__name__)


class ReportService:

    def __init__(self):
        self._font_registered = False

    def _ensure_font(self, pdf: FPDF) -> None:
        if not self._font_registered:
            pdf.add_font("ArialUni", "", FONT_REGULAR, uni=True)
            pdf.add_font("ArialUni", "B", FONT_BOLD, uni=True)
            pdf.add_font("ArialUni", "I", FONT_ITALIC, uni=True)
            pdf.add_font("ArialUni", "BI", FONT_BOLD_ITALIC, uni=True)
            self._font_registered = True

    def _font(self, pdf: FPDF, style: str = "", size: int = 11) -> None:
        self._ensure_font(pdf)
        pdf.set_font("ArialUni", style, size)

    DEF_L_MARGIN = 15
    DEF_R_MARGIN = 15
    DEF_T_MARGIN = 15
    DEF_B_MARGIN = 20

    def generar_pdf_en_memoria(
        self,
        datos_ui: dict,
        recomendacion_ia: str,
        graficos: list[str] | None = None,
    ) -> io.BytesIO:
        try:
            pdf = FPDF()
            pdf.set_margins(self.DEF_L_MARGIN, self.DEF_T_MARGIN, self.DEF_R_MARGIN)
            pdf.set_auto_page_break(True, self.DEF_B_MARGIN)
            pdf.add_page()

            self._add_header(pdf, datos_ui)
            self._add_kpis_section(pdf, datos_ui)

            tiene_grafico = bool(graficos)
            if tiene_grafico:
                self._add_charts_section(pdf, graficos)

            num_seccion = "3" if tiene_grafico else "2"
            self._add_ia_recommendations(pdf, recomendacion_ia, num_seccion)

            pdf_bytes = pdf.output(dest="S")
            return io.BytesIO(pdf_bytes)

        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            raise ReportGenerationError(f"Error al generar el PDF: {e}") from e

    def _add_header(self, pdf: FPDF, datos_ui: dict) -> None:
        config = datos_ui.get("Configuracion", {})
        alcance = config.get("Alcance", "Proyecto")
        titulo = f"Informe Ejecutivo de {alcance} (IA)"
        self._font(pdf, "B", 18)
        pdf.cell(0, 12, txt=titulo, ln=True, align="C")
        self._font(pdf, "", 9)
        pdf.cell(
            0,
            8,
            txt=f"Generado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            ln=True,
            align="C",
        )
        pdf.ln(8)

    def _add_kpis_section(self, pdf: FPDF, datos_ui: dict) -> None:
        self._font(pdf, "B", 13)
        pdf.cell(0, 9, txt="1. Metricas Operativas Globales", ln=True)
        pdf.ln(2)
        self._font(pdf, "", 10)

        items = []

        kpis = datos_ui.get("UI_Header_KPIs", {})
        for nombre, valor in kpis.items():
            label = nombre.replace("_", " ")
            if nombre in ("Riesgo_Promedio", "Retraso_Promedio"):
                if valor is not None:
                    items.append((label, f"{float(valor) * 100:.0f}%"))
                else:
                    items.append((label, "---"))
            elif nombre == "Tasa_Completado_Pct":
                if valor is not None:
                    items.append(("Tasa Completado", f"{float(valor):.0f}%"))
                else:
                    items.append(("Tasa Completado", "---"))
            else:
                items.append((label, str(valor)))

        contexto = datos_ui.get("LLM_Tab_2_Contexto", {})
        metricas_neg = contexto.get("Metricas_Globales_Negocio", {})
        esf_riesgo = metricas_neg.get("Esfuerzo_Total_Comprometido_En_Riesgo")
        if esf_riesgo is not None:
            items.append(("Esf. en Riesgo", str(esf_riesgo)))

        margin = pdf.l_margin
        usable = pdf.w - pdf.l_margin - pdf.r_margin
        for label, valor in items:
            pdf.cell(usable, 7, txt=f"- {label}: {valor}", ln=True)
        pdf.ln(6)

    def _add_charts_section(self, pdf: FPDF, graficos: list[str]) -> None:
        from PIL import Image as PILImage

        margin = pdf.l_margin
        usable = pdf.w - pdf.l_margin - pdf.r_margin

        self._font(pdf, "B", 13)
        pdf.cell(usable, 9, txt="2. Evolucion del Riesgo y Retraso", ln=True)
        pdf.ln(2)
        for grafico in graficos:
            try:
                image_bytes = self._decode_base64_image(grafico)

                pil_img = PILImage.open(io.BytesIO(image_bytes))
                img_w_px, img_h_px = pil_img.size

                display_w = usable
                display_h = display_w * img_h_px / img_w_px

                if pdf.get_y() + display_h > pdf.h - pdf.b_margin:
                    pdf.add_page()

                pdf.image(
                    io.BytesIO(image_bytes),
                    x=margin,
                    y=pdf.get_y(),
                    w=display_w,
                    h=display_h,
                )
                pdf.set_y(pdf.get_y() + display_h + 6)

            except Exception as e:
                logger.warning(f"Error insertando grafico en PDF: {e}")
                continue

    def _decode_base64_image(self, grafico_base64: str) -> bytes:
        if "," in grafico_base64:
            grafico_base64 = grafico_base64.split(",", 1)[1]
        try:
            raw = base64.b64decode(grafico_base64)
            if raw.lstrip().startswith(b"<svg") or raw.lstrip().startswith(b"<?xml"):
                if HAS_CAIROSVG:
                    return cairosvg.svg2png(bytestring=raw)
                else:
                    raise ReportGenerationError(
                        "El grafico es SVG pero cairosvg no esta instalado. "
                        "Ejecute: pip install cairosvg"
                    )
            return raw
        except ReportGenerationError:
            raise
        except Exception as e:
            raise ReportGenerationError(
                f"Error decodificando imagen base64: {e}"
            ) from e

    def _add_ia_recommendations(
        self, pdf: FPDF, recomendacion_ia: str, num_seccion: str
    ) -> None:
        usable = pdf.w - pdf.l_margin - pdf.r_margin
        self._font(pdf, "B", 13)
        pdf.cell(usable, 9, txt=f"{num_seccion}. Recomendaciones Estrategicas (LLM)", ln=True)
        pdf.ln(2)
        self._font(pdf, "", 10)
        pdf.multi_cell(usable, 5.5, txt=recomendacion_ia)


report_service = ReportService()

