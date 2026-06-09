# Manual de Uso

## Flujo básico

```
Ingesta → Análisis ML → Dashboard → Recomendaciones IA → Exportar PDF
```

---

## 1. Pantalla de ingesta

### 1.1 Subir archivo

Arrastra un archivo CSV, XLSX o XLS al área de carga, o haz clic para seleccionarlo.

**Formato esperado:** Exportación plana de Jira con columnas como `Issue key`, `Summary`, `Issue Type`, `Status`, `Created`, `Resolved`, `Custom field (Story Points)`, etc.

### 1.2 Seleccionar alcance

| Opción | Descripción |
|---|---|
| **Sprint** | Analiza tareas de una iteración específica (valida que todas pertenezcan al mismo Sprint_ID) |
| **Proyecto Completo** | Evalúa el histórico de varios sprints y muestra tendencias temporales |

### 1.3 Seleccionar rol

| Opción | Descripción |
|---|---|
| **Director de Proyecto (PM)** | Recomendaciones tácticas y operativas |
| **Gestión de Proyectos (PMO)** | Recomendaciones estratégicas y estructurales |

### 1.4 Iniciar análisis

Haz clic en *Iniciar Análisis*. El sistema:
1. Lee y transforma los datos
2. Ejecuta los modelos predictivos (XGBoost)
3. Genera recomendaciones vía IA (Ollama + llama3)

---

## 2. Datos de demostración

Ejecuta el notebook 02 para generar CSVs sintéticos. Los escenarios disponibles:

| Dataset | Alcance | Semáforo esperado | Qué demuestra |
|---|---|---|---|
| `sprint_perfecto.csv` | Sprint | Verde | Todo bajo control |
| `sprint_normal.csv` | Sprint | Verde | KPIs normales |
| `sprint_riesgo_moderado.csv` | Sprint | Amarillo | Riesgo moderado |
| `sprint_catastrofico.csv` | Sprint | Rojo | Alertas máximas |
| `sprint_solo_bloqueos.csv` | Sprint | Rojo | Impacto de bloqueos |
| `sprint_retraso_critico.csv` | Sprint | Verde/Rojo | Retraso con riesgo bajo |
| `proyecto_completo.csv` | Proyecto | Amarillo/Rojo (S3) | 4 sprints, tendencias |
| `proyecto_mejora_progresiva.csv` | Proyecto | Rojo→Verde | Mejora continua |
| `proyecto_crisis_progresiva.csv` | Proyecto | Verde→Rojo | Crisis progresiva |

---

## 3. Dashboard

### 3.1 KPIs globales

| KPI | Descripción |
|---|---|
| **Total Tareas** | Número de tareas en el análisis |
| **Completado** | Porcentaje de tareas cerradas (status: closed, done, resolved, cerrada) |
| **Esfuerzo Total** | Suma de Story Points |
| **Esf. en Riesgo** | Story Points en tareas con Prob_Riesgo > 0.7, Prob_Retraso > 0.7 o bloqueos |
| **Bloqueadas** | Tareas con Blocker_Count > 0 |
| **Riesgo Promedio** | Media de Prob_Riesgo (0-1) |
| **Retraso Promedio** | Media de Prob_Retraso (0-1) |

### 3.2 Indicadores de alerta

- **Semáforo de riesgo global:** Rojo (≥0.60), Amarillo (≥0.30), Verde (<0.30)
- **Alerta de retraso:** Activada si el retraso promedio > 0.50
- **Bloqueos totales:** Número de tareas bloqueadas

### 3.3 Tareas críticas

Dos secciones muestran hasta 3 tareas cada una:

- **Tareas en Riesgo** — ordenadas por `Blocker_Count` + `Prob_Riesgo` descendente. Gravedad calculada:

| Condición | Gravedad |
|---|---|
| Prob_Riesgo ≥ 0.75 o Blocker_Count > 1 | Alto |
| Prob_Riesgo ≥ 0.55 o Blocker_Count = 1 | Medio |
| Resto | Bajo |

- **Tareas con Retraso** — ordenadas por `Prob_Retraso` descendente.

### 3.4 Gráficos

- **Evolución del Riesgo/Retraso:** Línea temporal. Para Sprint se agrupa por día, para Proyecto por Sprint_ID.
- **Riesgo por Tipo de Tarea:** Barras con la media de riesgo por Issue_Type.

### 3.5 Recomendaciones IA

La pestaña *Recomendaciones* muestra 3 viñetas generadas por el LLM con sugerencias contextuales basadas en las predicciones.

### 3.6 Exportar PDF

Haz clic en *Exportar PDF* para descargar un informe ejecutivo con KPIs, gráficos y recomendaciones.

---

## 4. Interpretación de probabilidades

| Probabilidad | Interpretación |
|---|---|
| 0.00 – 0.29 | Baja |
| 0.30 – 0.59 | Media |
| 0.60 – 0.74 | Alta |
| 0.75 – 1.00 | Crítica |

**Importante:** Una probabilidad de retraso de 0.06 es BAJA. Una de 0.94 es ALTA. El LLM traduce automáticamente los decimales a porcentajes (0.06 → "6%", 0.94 → "94%").

---

## 5. Solución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| Error 422 al subir archivo | Columnas insuficientes o formato incorrecto | Verifica que el CSV tenga las columnas esperadas |
| Error 503 en análisis | Modelo ML no cargado | Ejecuta NB04 para regenerar los `.pkl` |
| "LLM no disponible" | Ollama no está corriendo | Ejecuta `ollama serve` |
| Semáforo siempre Verde | Datos sin variabilidad | Prueba con `sprint_catastrofico.csv` |
| Gráficos sin datos | Alcance Proyecto sin Sprint_ID | Usa un dataset con múltiples Sprint_ID |
