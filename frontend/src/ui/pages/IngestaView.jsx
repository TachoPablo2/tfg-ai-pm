import { useState, useRef } from "react";
import { CloudUpload, CheckCircle2, X, ArrowRight, Loader2 } from "lucide-react";

const VALID_EXTENSIONS = [".csv", ".xlsx", ".xls"];
const MAX_FILE_SIZE_MB = 50;

function isValidFile(f) {
  if (!f) return false;
  const ext = "." + f.name.split(".").pop().toLowerCase();
  return VALID_EXTENSIONS.includes(ext);
}

export default function IngestaView({ onStartAnalysis }) {
  const [file, setFile] = useState(null);
  const [scope, setScope] = useState("sprint");
  const [role, setRole] = useState("pm");
  const [submitting, setSubmitting] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const f = e.target.files?.[0];
    setValidationError(null);
    if (!f) return;
    if (!isValidFile(f)) {
      setValidationError("Formato no válido. Usa CSV, XLSX o XLS.");
      return;
    }
    if (f.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setValidationError(`El archivo supera ${MAX_FILE_SIZE_MB} MB.`);
      return;
    }
    setFile(f);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setValidationError(null);
    const f = e.dataTransfer?.files?.[0];
    if (!f) return;
    if (!isValidFile(f)) {
      setValidationError("Formato no válido. Usa CSV, XLSX o XLS.");
      return;
    }
    if (f.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setValidationError(`El archivo supera ${MAX_FILE_SIZE_MB} MB.`);
      return;
    }
    setFile(f);
  };

  const handleDiscard = () => {
    setFile(null);
    setValidationError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = async () => {
    if (!file || submitting) return;
    setSubmitting(true);
    try {
      await onStartAnalysis({ file, scope, role });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto pt-8">
      <div className="text-center mb-10">
        <h2 className="text-2xl font-semibold text-slate-800 mb-2">Ingesta de Datos</h2>
        <p className="text-sm text-slate-400 leading-relaxed max-w-lg mx-auto">
          Sube tu exportación de Jira en formato CSV o Excel para generar el
          análisis predictivo de tu proyecto o sprint.
        </p>
      </div>

      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="border-2 border-dashed border-slate-300 rounded-xl p-12 flex flex-col items-center justify-center bg-[#F8F9FA] hover:bg-white hover:border-slate-400 transition-colors cursor-pointer relative mb-6"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        {file ? (
          <div className="flex flex-col items-center gap-3">
            <div className="bg-green-50 p-3 rounded-full">
              <CheckCircle2 className="w-8 h-8 text-alert-green" strokeWidth={1.5} />
            </div>
            <span className="font-medium text-slate-800 text-sm">{file.name}</span>
            <span className="text-xs text-slate-400">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="bg-white p-3 rounded-full shadow-sm border border-slate-200">
              <CloudUpload className="w-6 h-6 text-slate-500" strokeWidth={1.5} />
            </div>
            <span className="font-medium text-slate-700">
              Arrastra y suelta tu archivo aquí
            </span>
            <span className="text-sm text-slate-400">
              o haz clic para buscar en tu ordenador
            </span>
            <span className="text-xs text-slate-300 mt-1">
              CSV, XLSX o XLS — Tamaño máximo {MAX_FILE_SIZE_MB} MB
            </span>
          </div>
        )}
      </div>

      {validationError && (
        <div className="mb-6 text-center text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          {validationError}
        </div>
      )}

      {file && (
        <div className="flex justify-center mb-8">
          <button
            onClick={handleDiscard}
            className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-red-500 transition-colors"
          >
            <X className="w-4 h-4" />
            Descartar archivo
          </button>
        </div>
      )}

      <div className="space-y-7">
        <div>
          <div className="flex items-center mb-3">
            <h3 className="text-sm font-semibold text-slate-700">Alcance del Análisis</h3>
            <div className="ml-4 flex-1 border-t border-slate-200" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            {[
              { key: "sprint", label: "Sprint", desc: "Analiza las tareas activas de una iteración específica." },
              { key: "proyecto", label: "Proyecto Completo", desc: "Evalúa el histórico de tareas a lo largo del tiempo." },
            ].map((opt) => (
              <button
                key={opt.key}
                type="button"
                onClick={() => setScope(opt.key)}
                className={`text-left p-4 border rounded-lg transition-all ${
                  scope === opt.key
                    ? "border-[#0A2540] shadow-sm bg-white"
                    : "border-slate-200 hover:border-slate-300 bg-white"
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="font-medium text-sm text-slate-800">{opt.label}</span>
                  {scope === opt.key && (
                    <CheckCircle2 className="w-4 h-4 text-[#0A2540] shrink-0" />
                  )}
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{opt.desc}</p>
              </button>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center mb-3">
            <h3 className="text-sm font-semibold text-slate-700">Rol del Analista</h3>
            <div className="ml-4 flex-1 border-t border-slate-200" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            {[
              { key: "pm", label: "Director de Proyecto (PM)", desc: "Recomendaciones tácticas centradas en la ejecución del equipo." },
              { key: "pmo", label: "Gestión de Proyectos (PMO)", desc: "Recomendaciones estratégicas sobre procesos y metodología." },
            ].map((opt) => (
              <button
                key={opt.key}
                type="button"
                onClick={() => setRole(opt.key)}
                className={`text-left p-4 border rounded-lg transition-all ${
                  role === opt.key
                    ? "border-[#0A2540] shadow-sm bg-white"
                    : "border-slate-200 hover:border-slate-300 bg-white"
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="font-medium text-sm text-slate-800">{opt.label}</span>
                  {role === opt.key && (
                    <CheckCircle2 className="w-4 h-4 text-[#0A2540] shrink-0" />
                  )}
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{opt.desc}</p>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-10 mb-8 flex justify-end">
        <button
          onClick={handleSubmit}
          disabled={!file || submitting}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${
            file && !submitting
              ? "bg-[#0A2540] text-white hover:opacity-90"
              : "bg-[#0A2540] text-white/50 cursor-not-allowed"
          }`}
        >
          {submitting ? (
            <>
              Procesando...
              <Loader2 className="w-4 h-4 animate-spin" />
            </>
          ) : (
            <>
              Iniciar Análisis
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
