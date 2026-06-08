import { useState, useCallback, useRef } from 'react';
import Header from './ui/components/Header';
import IngestaView from './ui/pages/IngestaView';
import LoadingView from './ui/pages/LoadingView';
import DashboardView from './ui/pages/DashboardView';
import { uploadAndAnalyze, exportPdf } from './ui/services/api';

const PHASES = { INGESTA: 0, LOADING: 1, DASHBOARD: 2 };

export default function App() {
  const [phase, setPhase] = useState(PHASES.INGESTA);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);
  const chartRef = useRef(null);

  const handleStartAnalysis = useCallback(async (params) => {
    setError(null);
    setPhase(PHASES.LOADING);

    try {
      const result = await uploadAndAnalyze(params);
      setAnalysisData(result);
      setPhase(PHASES.DASHBOARD);
    } catch (err) {
      setError(err.message);
      setPhase(PHASES.INGESTA);
    }
  }, []);

  const handleNewAnalysis = useCallback(() => {
    setAnalysisData(null);
    setError(null);
    setPhase(PHASES.INGESTA);
  }, []);

  const handleExportPdf = useCallback(async () => {
    if (!analysisData) return;
    try {
      let grafico_base64 = null;
      if (chartRef.current) {
        const svg = chartRef.current.querySelector('svg.recharts-surface');
        if (svg) {
          const xml = new XMLSerializer().serializeToString(svg);
          grafico_base64 = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(xml)));
        }
      }
      await exportPdf({
        datos_ui: analysisData.datos_ui,
        recomendacion_ia: analysisData.recomendacion_ia,
        grafico_base64,
      });
    } catch (err) {
      setError(err.message);
    }
  }, [analysisData]);

  return (
    <div className="min-h-screen flex flex-col bg-[#F8F9FA] font-sans">
      <Header
        showActions={phase === PHASES.DASHBOARD}
        onExportPdf={handleExportPdf}
        onNewAnalysis={handleNewAnalysis}
      />

      {error && (
        <div className="px-8 pt-4 max-w-6xl mx-auto w-full">
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 flex items-center gap-2">
            <span className="font-medium">Error:</span> {error}
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-400 hover:text-red-600 font-bold text-lg leading-none"
              aria-label="Cerrar"
            >
              &times;
            </button>
          </div>
        </div>
      )}

      <main className="flex-1 px-8">
        {phase === PHASES.INGESTA && (
          <IngestaView onStartAnalysis={handleStartAnalysis} />
        )}
        {phase === PHASES.LOADING && <LoadingView />}
        {phase === PHASES.DASHBOARD && (
          <DashboardView data={analysisData} onExportPdf={handleExportPdf} chartRef={chartRef} />
        )}
      </main>

      <footer className="px-8 py-5 text-xs text-slate-300 flex justify-between items-center border-t border-slate-200 mt-auto shrink-0">
        <span>© 2024 IDSS PMO Solutions. Todos los derechos reservados.</span>
        <span>Cumplimiento de Seguridad</span>
      </footer>
    </div>
  );
}
