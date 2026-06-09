import { useState, useCallback, useRef } from "react";
import Header from "./ui/components/Header";
import IngestaView from "./ui/pages/IngestaView";
import LoadingView from "./ui/pages/LoadingView";
import DashboardView from "./ui/pages/DashboardView";
import { uploadAndAnalyze, exportPdf } from "./ui/services/api";

const PHASES = { INGESTA: 0, LOADING: 1, DASHBOARD: 2 };

function svgToBase64(svgEl) {
  const rect = svgEl.getBoundingClientRect();
  const w = rect.width || 800;
  const h = rect.height || 400;
  const clone = svgEl.cloneNode(true);
  clone.setAttribute("width", String(w));
  clone.setAttribute("height", String(h));
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");

  const allEls = svgEl.querySelectorAll("*");
  const clonedEls = clone.querySelectorAll("*");
  allEls.forEach((el, i) => {
    const computed = window.getComputedStyle(el);
    const target = clonedEls[i];
    if (target) {
      const importantStyles = ["fill", "stroke", "color", "font-family", "font-size", "font-weight"];
      importantStyles.forEach((prop) => {
        const val = computed.getPropertyValue(prop);
        if (val && val !== "none" && target.style) {
          target.style.setProperty(prop, val);
        }
      });
    }
  });

  const xml = new XMLSerializer().serializeToString(clone);
  const encoded = new TextEncoder().encode(xml);
  let binary = "";
  encoded.forEach((b) => (binary += String.fromCharCode(b)));
  return "data:image/svg+xml;base64," + btoa(binary);
}

export default function App() {
  const [phase, setPhase] = useState(PHASES.INGESTA);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const chartRef = useRef(null);

  const handleStartAnalysis = useCallback(async (params) => {
    setError(null);
    setPhase(PHASES.LOADING);

    try {
      const result = await uploadAndAnalyze(params);
      setAnalysisData(result);
      setPhase(PHASES.DASHBOARD);
    } catch (err) {
      setError(err.message || "Error desconocido al procesar el análisis.");
      setPhase(PHASES.INGESTA);
    }
  }, []);

  const handleNewAnalysis = useCallback(() => {
    setAnalysisData(null);
    setError(null);
    setPhase(PHASES.INGESTA);
  }, []);

  const handleExportPdf = useCallback(async () => {
    if (!analysisData || pdfLoading) return;
    setPdfLoading(true);
    try {
      const graficos = [];
      if (chartRef.current) {
        const svgs = chartRef.current.querySelectorAll("svg.recharts-surface");
        for (const svg of svgs) {
          graficos.push(svgToBase64(svg));
        }
      }
      await exportPdf({
        datos_ui: analysisData.datos_ui,
        recomendacion_ia: analysisData.recomendacion_ia,
        graficos,
      });
    } catch (err) {
      setError(err.message || "Error al exportar el PDF.");
    } finally {
      setPdfLoading(false);
    }
  }, [analysisData, pdfLoading]);

  return (
    <div className="min-h-screen flex flex-col bg-[#F8F9FA] font-sans">
      <Header
        showActions={phase === PHASES.DASHBOARD}
        onExportPdf={handleExportPdf}
        onNewAnalysis={handleNewAnalysis}
        pdfLoading={pdfLoading}
      />

      {error && phase !== PHASES.LOADING && (
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
          <DashboardView data={analysisData} chartRef={chartRef} />
        )}
      </main>

      <footer className="px-8 py-5 text-xs text-slate-300 flex justify-between items-center border-t border-slate-200 mt-auto shrink-0">
        <span>&copy; {new Date().getFullYear()} IDSS PMO Solutions. Todos los derechos reservados.</span>
        <span>Cumplimiento de Seguridad</span>
      </footer>
    </div>
  );
}
