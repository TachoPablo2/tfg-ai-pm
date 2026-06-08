import { FileDown, Plus } from 'lucide-react';

export default function Header({ onExportPdf, onNewAnalysis, showActions }) {
  return (
    <header className="border-b border-corporate-border bg-white px-8 py-4 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <div className="bg-[#0A2540] text-white font-bold px-2.5 py-1 rounded text-sm tracking-wide">
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
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-[#0A2540] border border-[#0A2540] rounded-lg hover:bg-[#0A2540] hover:text-white transition-colors"
          >
            <FileDown className="w-4 h-4" />
            Exportar PDF
          </button>
          <button
            onClick={onNewAnalysis}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-[#0A2540] rounded-lg hover:opacity-90 transition-opacity"
          >
            <Plus className="w-4 h-4" />
            Nuevo Análisis
          </button>
        </div>
      )}
    </header>
  );
}
