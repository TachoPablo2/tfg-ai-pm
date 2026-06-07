import io
import base64
import tempfile
import datetime
from fpdf import FPDF

class ReportService:
    def generar_pdf_en_memoria(self, datos_ui: dict, recomendacion_ia: str, grafico_base64: str = None) -> io.BytesIO:
        pdf = FPDF()
        pdf.add_page()
        
        # --- ENCABEZADO ---
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Informe Ejecutivo de Proyecto (IA)", ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, txt=f"Generado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
        pdf.ln(5)
        
        # --- SECCIÓN 1: KPIs ---
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt="1. Métricas Operativas Globales", ln=True)
        pdf.set_font("Arial", size=11)
        kpis = datos_ui.get("UI_Header_KPIs", {})
        for kpi_nombre, kpi_valor in kpis.items():
            nombre_limpio = kpi_nombre.replace("_", " ")
            pdf.cell(0, 8, txt=f"• {nombre_limpio}: {kpi_valor}", ln=True)
        pdf.ln(5)
        
        # --- SECCIÓN 2: GRÁFICO VISUAL (NUEVO) ---
        if grafico_base64:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, txt="2. Evolución del Riesgo y Retraso", ln=True)
            
            # React suele enviar la cabecera 'data:image/png;base64,'. Se la quitamos.
            if "," in grafico_base64:
                grafico_base64 = grafico_base64.split(",")[1]
                
            # Decodificamos el texto a bytes puros
            image_bytes = base64.b64decode(grafico_base64)
            
            # Creamos un archivo temporal que se autodestruirá al salir del bloque 'with'
            with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as tmp:
                tmp.write(image_bytes)
                tmp.flush() # Forzamos la escritura en RAM
                
                # Pegamos la imagen en el PDF. Ajustamos el ancho (w=190) para que ocupe la página
                pdf.image(tmp.name, x=10, y=pdf.get_y(), w=190)
                
            pdf.ln(100) # Damos un salto de línea grande para no escribir encima del gráfico
            
        # --- SECCIÓN 3: TEXTO IA ---
        pdf.set_font("Arial", 'B', 14)
        seccion_ia = "3. Recomendaciones Estratégicas (LLM)" if grafico_base64 else "2. Recomendaciones Estratégicas (LLM)"
        pdf.cell(0, 10, txt=seccion_ia, ln=True)
        pdf.set_font("Arial", size=11)
        texto_limpio = recomendacion_ia.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, txt=texto_limpio)
        
        # --- FINALIZACIÓN ---
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        return io.BytesIO(pdf_bytes)

report_service = ReportService()


'''
¿Qué tendrás que hacer en React?
Cuando vayas a programar el botón en la interfaz gráfica, usarás una librería estándar como html2canvas. 
El código de React será algo tan sencillo como:
Apuntar al componente del gráfico: const canvas = await html2canvas(document.getElementById('grafico-evolucion'));
Sacar el texto Base64: const imagenBase64 = canvas.toDataURL('image/png');
Enviarlo en el JSON (junto con datos_ui y recomendacion_ia) al endpoint /export.
'''
