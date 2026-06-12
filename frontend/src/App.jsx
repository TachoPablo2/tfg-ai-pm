import { useState, useCallback, useRef } from "react";
import Header from "./ui/components/Header";
import IngestaView from "./ui/pages/IngestaView";
import LoadingView from "./ui/pages/LoadingView";
import DashboardView from "./ui/pages/DashboardView";
import { uploadAndAnalyze, exportPdf } from "./ui/services/api";

const PHASES = { INGESTA: 0, LOADING: 1, DASHBOARD: 2 };

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
        const wrappers = chartRef.current.querySelectorAll("[data-chart-wrapper]");
        for (const wrapper of wrappers) {
          const titleEl = wrapper.querySelector("h3");
          const title = titleEl ? titleEl.textContent.trim() : "";
          const svg = wrapper.querySelector("svg.recharts-surface");
          if (svg) {
            const clone = svg.cloneNode(true);
            const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
            const style = document.createElementNS("http://www.w3.org/2000/svg", "style");
            style.textContent = `
              .chart-title { font-family: system-ui, sans-serif; font-size: 14px;
                font-weight: 600; fill: #334155; }
            `;
            defs.appendChild(style);
            clone.insertBefore(defs, clone.firstChild);
            const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
            txt.setAttribute("x", "12");
            txt.setAttribute("y", "22");
            txt.setAttribute("class", "chart-title");
            txt.textContent = title;
            clone.insertBefore(txt, clone.firstChild);
            const vb = (clone.getAttribute("viewBox") || "").split(" ");
            if (vb.length === 4) {
              vb[1] = "0";
              vb[3] = String(parseInt(vb[3], 10) + 32);
              clone.setAttribute("viewBox", vb.join(" "));
            }
            const rect = svg.getBoundingClientRect();
            const w = rect.width || 800;
            const h = (rect.height || 400) + 32;
            clone.setAttribute("width", String(w));
            clone.setAttribute("height", String(h));
            const composer = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            composer.setAttribute("xmlns", "http://www.w3.org/2000/svg");
            composer.setAttribute("width", String(w));
            composer.setAttribute("height", String(h));
            composer.appendChild(clone);
            const xml = new XMLSerializer().serializeToString(composer);
            const encoded = new TextEncoder().encode(xml);
            let binary = "";
            encoded.forEach((b) => (binary += String.fromCharCode(b)));
            graficos.push("data:image/svg+xml;base64," + btoa(binary));
          }
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
    <div className="min-h-screen flex flex-col bg-corporate-light font-sans">
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

      <main className="flex-1 px-8 flex flex-col">
        {phase === PHASES.INGESTA && (
          <IngestaView onStartAnalysis={handleStartAnalysis} />
        )}
        {phase === PHASES.LOADING && <LoadingView />}
        {phase === PHASES.DASHBOARD && (
          <DashboardView data={analysisData} chartRef={chartRef} />
        )}
      </main>

      <footer className="px-8 py-5 text-xs text-slate-300 flex justify-between items-center border-t border-slate-200 mt-auto shrink-0 bg-white">
        <span>&copy; {new Date().getFullYear()} IDSS PMO Solutions. Todos los derechos reservados.</span>
        <span>Cumplimiento de Seguridad</span>
      </footer>
    </div>
  );
}
