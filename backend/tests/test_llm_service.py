import pytest
from app.ai.llm_engine.llm_service import LLMService


class TestConstruirPayload:
    def test_basic_payload(self, sample_prediction):
        service = LLMService()
        payload = service.construir_payload(
            [sample_prediction], rol="Project Manager", alcance="Sprint"
        )
        assert payload["Configuracion"]["Alcance"] == "Sprint"
        assert payload["Configuracion"]["Rol"] == "Project Manager"
        assert payload["UI_Header_KPIs"]["Total_Tareas"] == 1
        assert payload["UI_Tab_1_Estado"]["Semaforo_Riesgo_Global"] == "Rojo"
        assert payload["LLM_Tab_2_Contexto"]["Metricas_Globales_Negocio"]["Riesgo_General"] == 0.85

    def test_semaforo_verde(self, sample_prediction):
        from copy import deepcopy
        p = deepcopy(sample_prediction)
        p.Prob_Riesgo = 0.2
        service = LLMService()
        payload = service.construir_payload([p], rol="PMO", alcance="Proyecto")
        assert payload["UI_Tab_1_Estado"]["Semaforo_Riesgo_Global"] == "Verde"

    def test_semaforo_amarillo(self, sample_prediction):
        from copy import deepcopy
        p = deepcopy(sample_prediction)
        p.Prob_Riesgo = 0.45
        service = LLMService()
        payload = service.construir_payload([p], rol="PMO", alcance="Proyecto")
        assert payload["UI_Tab_1_Estado"]["Semaforo_Riesgo_Global"] == "Amarillo"

    def test_alerta_retraso_activada(self, sample_prediction):
        from copy import deepcopy
        p = deepcopy(sample_prediction)
        p.Prob_Retraso = 0.6
        service = LLMService()
        payload = service.construir_payload([p], rol="Project Manager", alcance="Sprint")
        assert payload["UI_Tab_1_Estado"]["Alerta_Retraso_Global"] == "Activada"

    def test_top_riesgos_filtered(self, sample_prediction):
        from copy import deepcopy
        predictions = []
        for i in range(5):
            p = deepcopy(sample_prediction)
            p.Issue_Key = f"PRO-{i}"
            p.Prob_Riesgo = 0.5 + i * 0.1
            p.Blocker_Count = i
            predictions.append(p)
        service = LLMService()
        payload = service.construir_payload(predictions, rol="Project Manager", alcance="Sprint")
        top = payload["LLM_Tab_2_Contexto"]["Top_Tareas_Riesgo_Bloqueos"]
        assert len(top) <= 3

    def test_tasa_completado(self, sample_prediction):
        from copy import deepcopy
        abierta = deepcopy(sample_prediction)
        abierta.Status = "Open"
        cerrada = deepcopy(sample_prediction)
        cerrada.Issue_Key = "PRO-102"
        cerrada.Status = "Closed"
        service = LLMService()
        payload = service.construir_payload([abierta, cerrada], rol="Project Manager", alcance="Sprint")
        assert payload["UI_Header_KPIs"]["Tasa_Completado_Pct"] == 50.0

    def test_tasa_completado_with_done_resolved_cerrada(self, sample_prediction):
        from copy import deepcopy
        states = ["Done", "Resolved", "cerrada", "Closed"]
        predictions = []
        for i, s in enumerate(states):
            p = deepcopy(sample_prediction)
            p.Issue_Key = f"PRO-{i}"
            p.Status = s
            predictions.append(p)
        predictions.append(deepcopy(sample_prediction))
        predictions[-1].Issue_Key = "PRO-99"
        predictions[-1].Status = "Open"
        service = LLMService()
        payload = service.construir_payload(predictions, rol="Project Manager", alcance="Sprint")
        assert payload["UI_Header_KPIs"]["Tasa_Completado_Pct"] == 80.0

    def test_proyecto_evolution(self, sample_prediction):
        from copy import deepcopy
        predictions = []
        for sprint_id in [1, 2, 3]:
            for _ in range(2):
                p = deepcopy(sample_prediction)
                p.Sprint_ID = sprint_id
                predictions.append(p)
        service = LLMService()
        payload = service.construir_payload(predictions, rol="PMO", alcance="Proyecto")
        evolucion = payload["UI_Tab_1_Estado"]["Grafico_Evolucion_Riesgo"]
        assert len(evolucion) == 3

    def test_esfuerzo_en_riesgo(self, sample_prediction):
        from copy import deepcopy
        p = deepcopy(sample_prediction)
        p.Prob_Riesgo = 0.95
        p.Story_Points = 10.0
        service = LLMService()
        payload = service.construir_payload([p], rol="Project Manager", alcance="Sprint")
        assert payload["LLM_Tab_2_Contexto"]["Metricas_Globales_Negocio"]["Esfuerzo_Total_Comprometido_En_Riesgo"] == 10.0

    def test_grafico_por_tipo(self, sample_prediction):
        from copy import deepcopy
        predictions = []
        for t in ["Bug", "Story", "Enhancement"]:
            p = deepcopy(sample_prediction)
            p.Issue_Key = f"PRO-{t}"
            p.Issue_Type = t
            predictions.append(p)
        service = LLMService()
        payload = service.construir_payload(predictions, rol="Project Manager", alcance="Sprint")
        tipos = payload["UI_Tab_1_Estado"]["Grafico_Riesgo_por_Tipo"]
        assert len(tipos) == 3


class TestBuildPrompt:
    def test_sprint_prompt_contains_sprint(self, sample_prediction):
        service = LLMService()
        payload = service.construir_payload([sample_prediction], rol="Project Manager", alcance="Sprint")
        system_p, user_p = service._build_prompt(
            payload["LLM_Tab_2_Contexto"], "Project Manager", "Sprint"
        )
        assert "ALCANCE SPRINT" in system_p
        assert "ROL PM" in system_p

    def test_proyecto_prompt_contains_proyecto(self, sample_prediction):
        service = LLMService()
        payload = service.construir_payload([sample_prediction], rol="PMO", alcance="Proyecto")
        system_p, user_p = service._build_prompt(
            payload["LLM_Tab_2_Contexto"], "PMO", "Proyecto"
        )
        assert "ALCANCE PROYECTO" in system_p
        assert "ROL PMO" in system_p


class TestGenerarInforme:
    @pytest.mark.asyncio
    async def test_generar_informe_success(self, sample_prediction, mocker):
        mock_chat = mocker.patch("ollama.chat")
        mock_chat.return_value = {
            "message": {"content": "• Recomendación de prueba."}
        }
        service = LLMService()
        result = await service.generar_informe(
            [sample_prediction], rol="Project Manager", alcance="Sprint"
        )
        assert "datos_ui" in result
        assert "recomendacion_ia" in result
        assert result["recomendacion_ia"] == "• Recomendación de prueba."

    @pytest.mark.asyncio
    async def test_generar_informe_empty_predictions(self):
        service = LLMService()
        result = await service.generar_informe([], rol="Project Manager", alcance="Sprint")
        assert "recomendacion_ia" in result
        assert "No hay datos" in result["recomendacion_ia"]

    @pytest.mark.asyncio
    async def test_generar_informe_timeout(self, sample_prediction, mocker):
        import asyncio
        from app.core.exceptions import LLMInferenceError
        mocker.patch("ollama.chat", side_effect=asyncio.TimeoutError())
        service = LLMService()
        with pytest.raises(LLMInferenceError, match="no respondió"):
            await service.generar_informe(
                [sample_prediction], rol="Project Manager", alcance="Sprint"
            )

    @pytest.mark.asyncio
    async def test_generar_informe_connection_error(self, sample_prediction, mocker):
        from app.core.exceptions import LLMInferenceError
        mocker.patch("ollama.chat", side_effect=ConnectionError("Ollama offline"))
        service = LLMService()
        with pytest.raises(LLMInferenceError, match="no disponible"):
            await service.generar_informe(
                [sample_prediction], rol="Project Manager", alcance="Sprint"
            )
