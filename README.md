# TFG-AI-PM

Sistema Inteligente de Apoyo a la Decisión para la Dirección de Proyectos Ágiles.

TFG de **Pablo Romero Gómez** — Universidad de Sevilla.

## Descripción

Analiza datos de Jira (CSV exportado) mediante modelos ML (XGBoost) y LLM (Ollama) para predecir riesgos, retrasos y generar recomendaciones estratégicas para Project Managers.

## Arquitectura

```
Frontend (React + Vite)  →  Backend (FastAPI)  →  ML models (XGBoost) + LLM (Ollama)
```

## Inicio rápido

```bash
# Local (desarrollo)
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev        # → http://localhost:5173

# Docker (producción)
docker compose up --build         # → http://localhost
```

## Documentación

- [`DEPLOYMENT.md`](DEPLOYMENT.md) — despliegue local, Docker y notebooks
- [`USAGE.md`](USAGE.md) — manual de uso del prototipo

## Requisitos

- Python 3.11+, Node 20+
- Ollama (para recomendaciones IA, opcional)
- Docker (opcional, para despliegue contenedorizado)
