# Manual de Despliegue

## Requisitos del sistema

- **Python** 3.11+
- **Node.js** 22+
- **Docker** y **Docker Compose** (opcional, para despliegue containerizado)
- **Ollama** con modelo `llama3` (opcional, necesario para recomendaciones IA)

---

## 1. Ejecución local (sin Docker)

### 1.1 Backend (FastAPI)

```bash
# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r backend/requirements.txt

# 3. Generar modelos ML (si no existen en backend/models/)
#    Ejecutar el notebook:
#    notebooks/04_modelado_machine_learning.ipynb

# 4. Iniciar el servidor
cd backend
uvicorn app.main:app --reload --port 8000
```

El backend queda disponible en `http://localhost:8000`.

### 1.2 Frontend (React + Vite)

```bash
# 1. Instalar dependencias
cd frontend
npm install

# 2. Iniciar en modo desarrollo
npm run dev
```

El frontend queda disponible en `http://localhost:5173`.
Las peticiones `/api/*` se redirigen automáticamente al backend gracias al proxy de Vite.

### 1.3 Ollama (para recomendaciones IA)

```bash
# Instalar Ollama: https://ollama.com
ollama pull llama3
ollama serve
```

Sin Ollama, el prototipo funciona pero devuelve:
> *"Sistema de recomendaciones temporalmente no disponible"*

### 1.4 Generar datos de prueba

Los modelos ML ya están pre-entrenados en `backend/models/`. Para generar datasets de demostración:

```bash
# Ejecutar el notebook 02 desde Jupyter
jupyter notebook notebooks/02_generacion_datos_sinteticos.ipynb
```

Los CSV se guardan en `data/synthetic/`.

---

## 2. Ejecución con Docker

```bash
# Construir y levantar servicios
docker compose up --build

# En segundo plano
docker compose up --build -d
```

| Servicio  | URL                       |
|-----------|---------------------------|
| Frontend  | `http://localhost:80`     |
| Backend   | `http://localhost:8000`   |

Para detener:

```bash
docker compose down
```

**Nota sobre Ollama:** El contenedor del backend se conecta a `host.docker.internal:11434` para llegar al proceso de Ollama en la máquina host. Asegúrate de que `ollama serve` esté corriendo.

---

## 3. Notebooks (Jupyter)

```bash
# Instalar dependencias de notebooks
pip install -r requirements.txt

# Iniciar Jupyter
jupyter notebook
```

### Orden de ejecución recomendado

| Notebook | Propósito | Obligatorio |
|---|---|---|
| `01_extraccion_tawos.ipynb` | Extraer datos de MySQL (TAWOS) | Solo si tienes la BD |
| `02_generacion_datos_sinteticos.ipynb` | Generar CSVs de demostración | Para datos de prueba |
| `03_analisis_exploratorio_EDA.ipynb` | Análisis exploratorio | Solo lectura |
| `04_modelado_machine_learning.ipynb` | Entrenar modelos ML | Si faltan los `.pkl` |
| `05_generacion_recomendaciones_llm.ipynb` | Verificar pipeline LLM | Solo lectura |

---

## 4. Tests

```bash
source venv/bin/activate

# Ejecutar tests del backend con cobertura
python -m pytest backend/tests/ -v --cov=app --cov-report=term

# Solo tests (más rápido)
python -m pytest backend/tests/ -v
```

---

## 5. Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | URL del servidor Ollama |
| `LLM_MODEL` | `llama3` | Modelo de lenguaje |
| `LLM_TIMEOUT` | `120` | Timeout en segundos para el LLM |
| `LLM_TEMPERATURE` | `0.3` | Temperatura del modelo |
| `LLM_CONTEXT_SIZE` | `4096` | Tamaño del contexto |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Orígenes permitidos CORS |
| `DB_USER` | `root` | Usuario MySQL (notebook 01) |
| `DB_PASS` | `root` | Contraseña MySQL (notebook 01) |
| `DB_HOST` | `localhost` | Host MySQL (notebook 01) |
| `DB_PORT` | `3306` | Puerto MySQL (notebook 01) |
| `DB_NAME` | `tawos` | Base de datos MySQL (notebook 01) |
