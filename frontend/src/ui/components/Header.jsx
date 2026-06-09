import { FileDown, Plus, Loader2 } from "lucide-react";

export default function Header({ onExportPdf, onNewAnalysis, showActions, pdfLoading }) {
  return (
    <header className="border-b border-corporate-border bg-white px-8 py-4 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <div className="bg-corporate-blue text-white font-bold px-2.5 py-1 rounded text-sm tracking-wide">
          IDSS
        </div>
        <span className="text-corporate-border">|</span>
        <span className="text-sm font-semibold tracking-widest text-slate-400">
          PROJECT MANAGEMENT
        </span>
      </div>

      {showActions && (
        <div className="flex items-center gap-3">
          <button
            onClick={onExportPdf}
            disabled={pdfLoading}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-corporate-blue border border-corporate-blue rounded-lg hover:bg-corporate-blue hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {pdfLoading ? (
              <Loader2 aria-hidden="true" className="w-4 h-4 animate-spin" />
            ) : (
              <FileDown aria-hidden="true" className="w-4 h-4" />
            )}
            {pdfLoading ? "Generando..." : "Exportar PDF"}
          </button>
          <button
            onClick={onNewAnalysis}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-corporate-blue rounded-lg hover:opacity-90 transition-opacity"
          >
            <Plus aria-hidden="true" className="w-4 h-4" />
            Nuevo Análisis
          </button>
        </div>
      )}
    </header>
  );
}
