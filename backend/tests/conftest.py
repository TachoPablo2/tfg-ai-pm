import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

os.environ["OLLAMA_HOST"] = "http://localhost:11434"
os.environ["LLM_MODEL"] = "test-model"
os.environ["LLM_TIMEOUT"] = "5"
os.environ["LLM_TEMPERATURE"] = "0.0"
os.environ["LLM_CONTEXT_SIZE"] = "1024"


@pytest.fixture
def sample_task_record():
    from app.api.schemas.pydantic_models import TaskRecord
    return TaskRecord(
        Issue_Key="PRO-101",
        Title="Test task",
        Issue_Type="Bug",
        Project_ID=999,
        Project_Name="Test Project",
        Sprint_ID=1,
        Sprint_State="ACTIVE",
        Story_Point=5.0,
        Total_Effort_Minutes=1200.0,
        In_Progress_Minutes=480.0,
        Resolution_Time_Minutes=1440.0,
        Title_Changed_After_Estimation=0,
        Description_Changed_After_Estimation=0,
        Story_Point_Changed_After_Estimation=0,
        Blocker_Count=0,
        Status="Open",
        Created_Date="2024-01-15",
    )


@pytest.fixture
def sample_tasks(sample_task_record):
    return [sample_task_record]


@pytest.fixture
def analysis_request(sample_tasks):
    from app.api.schemas.pydantic_models import AnalysisRequest
    return AnalysisRequest(alcance="Sprint", rol="Project Manager", tareas=sample_tasks)


@pytest.fixture
def sample_prediction():
    from app.api.schemas.pydantic_models import TaskPrediction
    return TaskPrediction(
        Issue_Key="PRO-101",
        Title="Test task",
        Issue_Type="Bug",
        Status="Open",
        Story_Points=5.0,
        Blocker_Count=0,
        Sprint_ID=1,
        Created_Date="2024-01-15",
        Prob_Riesgo=0.85,
        Prob_Retraso=0.35,
        Gravedad="Alto",
    )


@pytest.fixture
def mock_pipeline():
    import joblib
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import FunctionTransformer
    import numpy as np

    def predict_proba(X):
        n = X.shape[0]
        return np.column_stack([1 - np.ones(n) * 0.5, np.ones(n) * 0.5])

    pipeline = Pipeline([
        ("identity", FunctionTransformer(lambda x: x)),
    ])
    pipeline.predict_proba = predict_proba
    return pipeline


@pytest.fixture(autouse=True)
def mock_joblib(mocker, mock_pipeline):
    mocker.patch("joblib.load", return_value=mock_pipeline)


@pytest.fixture(autouse=True)
def mock_ollama(mocker):
    mock_response = {
        "message": {
            "content": "• Recomendación 1 de prueba.\n• Recomendación 2 de prueba.\n• Recomendación 3 de prueba."
        }
    }
    mocker.patch("ollama.chat", return_value=mock_response)


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def csv_bytes():
    return b"Issue key,Summary,Issue Type,Status,Created,Resolved,Custom field (Story Points),Blocker_Count\nPRO-101,Test task,Bug,Open,2024-01-15,2024-01-16,5,1\nPRO-102,Another task,Story,Closed,2024-01-10,2024-01-14,3,0\n"


@pytest.fixture
def sample_df():
    import pandas as pd
    return pd.DataFrame({
        "Issue_Key": ["PRO-101", "PRO-102"],
        "Title": ["Test task", "Another task"],
        "Issue_Type": ["Bug", "Story"],
        "Status": ["Open", "Closed"],
        "Story_Point": [5.0, 3.0],
        "Blocker_Count": [1, 0],
        "Project_ID": [999, 999],
        "Sprint_ID": [1, 1],
        "Sprint_State": ["ACTIVE", "ACTIVE"],
        "Created_Date": ["2024-01-15", "2024-01-10"],
        "Total_Effort_Minutes": [1200.0, 600.0],
        "In_Progress_Minutes": [480.0, 240.0],
        "Resolution_Time_Minutes": [1440.0, 720.0],
        "Title_Changed_After_Estimation": [0, 0],
        "Description_Changed_After_Estimation": [0, 0],
        "Story_Point_Changed_After_Estimation": [0, 0],
        "Project_Name": ["Test", "Test"],
    })


@pytest.fixture
def mock_cairosvg(mocker):
    mocker.patch("app.core.services.report_service.HAS_CAIROSVG", True)
    mocker.patch("cairosvg.svg2png", return_value=b"fake_png_data")
