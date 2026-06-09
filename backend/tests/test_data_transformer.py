import pytest
import pandas as pd
from app.data.transformation.data_transformer import JiraTransformer


class TestTransformarExportacion:
    def test_basic_transformation(self):
        df = pd.DataFrame({
            "Issue key": ["PRO-101"],
            "Summary": ["Test task"],
            "Issue Type": ["Bug"],
            "Status": ["Open"],
            "Created": ["2024-01-15"],
            "Resolved": ["2024-01-16"],
            "Custom field (Story Points)": [5],
            "Blocker_Count": [1],
        })
        result = JiraTransformer.transformar_exportacion(df)
        assert "Issue_Key" in result.columns
        assert "Title" in result.columns
        assert "Story_Point" in result.columns
        assert result["Issue_Key"].iloc[0] == "PRO-101"
        assert result["Story_Point"].iloc[0] == 5.0

    def test_alternative_story_point_column(self):
        df = pd.DataFrame({
            "Issue key": ["PRO-101"],
            "Summary": ["Test"],
            "Issue Type": ["Bug"],
            "Status": ["Open"],
            "Created": ["2024-01-15"],
            "Resolved": ["2024-01-16"],
            "Custom field (10002)": [3],
            "Blocker_Count": [0],
        })
        result = JiraTransformer.transformar_exportacion(df)
        assert result["Story_Point"].iloc[0] == 3.0

    def test_missing_blocker_count_infers_from_block_columns(self):
        df = pd.DataFrame({
            "Issue key": ["PRO-101"],
            "Summary": ["Test"],
            "Issue Type": ["Bug"],
            "Status": ["Open"],
            "Created": ["2024-01-15"],
            "Resolved": ["2024-01-16"],
            "Custom field (Story Points)": [5],
            "is_blocked": [1],
        })
        result = JiraTransformer.transformar_exportacion(df)
        assert "Blocker_Count" in result.columns

    def test_missing_blocker_count_defaults_zero(self):
        df = pd.DataFrame({
            "Issue key": ["PRO-101"],
            "Summary": ["Test"],
            "Issue Type": ["Bug"],
            "Status": ["Open"],
            "Created": ["2024-01-15"],
            "Resolved": ["2024-01-16"],
            "Custom field (Story Points)": [5],
        })
        result = JiraTransformer.transformar_exportacion(df)
        assert result["Blocker_Count"].iloc[0] == 0

    def test_missing_created_resolved(self):
        df = pd.DataFrame({
            "Issue key": ["PRO-101"],
            "Summary": ["Test"],
            "Issue Type": ["Bug"],
            "Status": ["Open"],
        })
        result = JiraTransformer.transformar_exportacion(df)
        assert result["Resolution_Time_Minutes"].iloc[0] == 0.0
        assert result["Created_Date"].iloc[0] is None

    def test_in_progress_ratio_fallback(self):
        df = pd.DataFrame({
            "Issue key": ["PRO-101"],
            "Summary": ["Test"],
            "Issue Type": ["Bug"],
            "Status": ["Open"],
            "Created": ["2024-01-15"],
            "Resolved": ["2024-01-16"],
            "Custom field (Story Points)": [5],
        })
        result = JiraTransformer.transformar_exportacion(df)
        expected_in_progress = 1440.0 * 0.4
        assert result["In_Progress_Minutes"].iloc[0] == expected_in_progress

    def test_sprint_id_coercion(self):
        df = pd.DataFrame({
            "Issue key": ["PRO-101"],
            "Summary": ["Test"],
            "Issue Type": ["Bug"],
            "Status": ["Open"],
            "Sprint_ID": ["invalid"],
        })
        result = JiraTransformer.transformar_exportacion(df)
        assert result["Sprint_ID"].iloc[0] == 1

    def test_all_audit_columns_added(self):
        df = pd.DataFrame({
            "Issue key": ["PRO-101"],
            "Summary": ["Test"],
            "Issue Type": ["Bug"],
            "Status": ["Open"],
        })
        result = JiraTransformer.transformar_exportacion(df)
        assert result["Project_ID"].iloc[0] == 999
        assert result["Sprint_State"].iloc[0] == "ACTIVE"
        assert result["Title_Changed_After_Estimation"].iloc[0] == 0
        assert result["Description_Changed_After_Estimation"].iloc[0] == 0
        assert result["Story_Point_Changed_After_Estimation"].iloc[0] == 0

    def test_total_effort_fallback(self):
        df = pd.DataFrame({
            "Issue key": ["PRO-101"],
            "Summary": ["Test"],
            "Issue Type": ["Bug"],
            "Status": ["Open"],
            "Created": ["2024-01-15"],
            "Resolved": ["2024-01-16"],
            "Custom field (Story Points)": [5],
        })
        result = JiraTransformer.transformar_exportacion(df)
        assert result["Total_Effort_Minutes"].iloc[0] == 1440.0

    def test_project_name_default(self):
        df = pd.DataFrame({
            "Issue key": ["PRO-101"],
            "Summary": ["Test"],
            "Issue Type": ["Bug"],
            "Status": ["Open"],
        })
        result = JiraTransformer.transformar_exportacion(df)
        assert result["Project_Name"].iloc[0] == "Default Project"


class TestDataframeToRecords:
    def test_basic_conversion(self, sample_df):
        records = JiraTransformer.dataframe_to_records(sample_df)
        assert len(records) == 2
        assert records[0]["Issue_Key"] == "PRO-101"
        assert isinstance(records[0], dict)

    def test_null_fill(self):
        import numpy as np
        df = pd.DataFrame({
            "Issue_Key": ["PRO-101"],
            "Title": ["Test"],
            "NumericCol": [np.nan],
            "TextCol": [None],
        })
        records = JiraTransformer.dataframe_to_records(df)
        assert records[0]["NumericCol"] == 0
        assert records[0]["TextCol"] == ""
