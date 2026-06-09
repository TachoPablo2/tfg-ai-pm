import io
import base64
import datetime
import logging
import platform
from pathlib import Path

from fpdf import FPDF

from app.core.exceptions import ReportGenerationError

try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

logger = logging.getLogger(__name__)


def _find_font_dir() -> Path | None:
    system = platform.system()
    candidates = {
        "Darwin": [
            Path("/System/Library/Fonts/Supplemental"),
            Path("/Library/Fonts"),
            Path.home() / "Library/Fonts",
        ],
        "Linux": [
            Path("/usr/share/fonts/truetype"),
            Path("/usr/local/share/fonts"),
        ],
        "Windows": [
            Path("C:/Windows/Fonts"),
        ],
    }
    for d in candidates.get(system, []):
        if d.is_dir():
            return d
    return None


def _find_font(name: str) -> str | None:
    font_dir = _find_font_dir()
    if not font_dir:
        return None
    for ext in ("ttf", "TTF"):
        p = font_dir / f"{name}.{ext}"
        if p.is_file():
            return str(p)
    for p in sorted(font_dir.glob(f"{name}*.[tT][tT][fF]")):
        return str(p)
    return None


FONT_REGULAR = _find_font("Arial")
FONT_BOLD = _find_font("Arial Bold") or _find_font("Arialbd")
FONT_ITALIC = _find_font("Arial Italic") or _find_font("Ariali")
FONT_BOLD_ITALIC = _find_font("Arial Bold Italic") or _find_font("Arialbi")

FALLBACK_FONT = "Helvetica"


class ReportService:

    def _register_fonts(self, pdf: FPDF) -> None:
        if FONT_REGULAR and FONT_BOLD:
            pdf.add_font("CustomFont", "", FONT_REGULAR, uni=True)
            if FONT_BOLD:
                pdf.add_font("CustomFont", "B", FONT_BOLD, uni=True)
            if FONT_ITALIC:
                pdf.add_font("CustomFont", "I", FONT_ITALIC, uni=True)
            if FONT_BOLD_ITALIC:
                pdf.add_font("CustomFont", "BI", FONT_BOLD_ITALIC, uni=True)
            pdf._custom_font_registered = True
        else:
            pdf._custom_font_registered = False

    def _font(self, pdf: FPDF, style: str = "", size: int = 11) -> None:
        if not hasattr(pdf, "_custom_font_registered"):
            self._register_fonts(pdf)
        if getattr(pdf, "_custom_font_registered", False):
            pdf.set_font("CustomFont", style, size)
        else:
            pdf.set_font(FALLBACK_FONT, style, size)

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
            if isinstance(pdf_bytes, str):
                pdf_bytes = pdf_bytes.encode("latin-1")
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
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        pdf.cell(0, 8, txt=f"Generado el: {now}", ln=True, align="C")
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
            head = raw[:500]
            if b"<svg" in head:
                if HAS_CAIROSVG:
                    return cairosvg.svg2png(bytestring=raw)
                else:
                    raise ReportGenerationError(
                        "El grafico es SVG pero cairosvg no esta instalado. "
                        "Ejecute: pip install cairosvg"
                    )
            return raw
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
