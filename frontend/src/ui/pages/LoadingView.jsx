import { useEffect, useState } from 'react';
import { Database, Cpu, MessageSquareText } from 'lucide-react';

const PHASES = [
  { key: 'data', label: 'Limpieza y preparación de datos', icon: Database },
  { key: 'ml', label: 'Inferencia predictiva (Machine Learning)', icon: Cpu },
  { key: 'llm', label: 'Generación de recomendaciones (LLM)', icon: MessageSquareText },
];

export default function LoadingView() {
  const [activePhase, setActivePhase] = useState(0);

  useEffect(() => {
    if (activePhase < PHASES.length - 1) {
      const timer = setTimeout(() => setActivePhase((p) => p + 1), 2500);
      return () => clearTimeout(timer);
    }
  }, [activePhase]);

  return (
    <div className="max-w-lg mx-auto pt-20 flex flex-col items-center">
      <h2 className="text-xl font-semibold text-slate-800 mb-2">
        Procesando análisis
      </h2>
      <p className="text-sm text-slate-400 mb-12">
        Los motores de IA están trabajando en tu solicitud...
      </p>

      <div className="w-full space-y-4">
        {PHASES.map((phase, i) => {
          const isActive = i === activePhase;
          const isDone = i < activePhase;
          const Icon = phase.icon;

          return (
            <div
              key={phase.key}
              className={`flex items-center gap-4 p-4 rounded-lg border transition-all duration-500 ${
                isActive
                  ? 'border-[#0A2540] bg-white shadow-sm'
                  : isDone
                    ? 'border-green-200 bg-green-50/50'
                    : 'border-slate-200 bg-white opacity-40'
              }`}
            >
              <div
                className={`p-2 rounded-full transition-colors ${
                  isDone
                    ? 'bg-green-100 text-alert-green'
                    : isActive
                      ? 'bg-[#0A2540]/10 text-[#0A2540]'
                      : 'bg-slate-100 text-slate-300'
                }`}
              >
                <Icon className="w-5 h-5" />
              </div>

              <div className="flex-1 min-w-0">
                <span
                  className={`text-sm font-medium block ${
                    isDone
                      ? 'text-green-700'
                      : isActive
                        ? 'text-slate-800'
                        : 'text-slate-300'
                  }`}
                >
                  {phase.label}
                </span>
              </div>

              <div className="shrink-0">
                {isDone ? (
                  <span className="text-alert-green text-sm font-medium">Completado</span>
                ) : isActive ? (
                  <span className="flex gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#0A2540] animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-[#0A2540] animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-[#0A2540] animate-bounce" style={{ animationDelay: '300ms' }} />
                  </span>
                ) : (
                  <span className="text-slate-300 text-sm">Pendiente</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <p className="text-xs text-slate-300 mt-10 text-center leading-relaxed">
        Esta operación puede tardar unos segundos.<br />
        No cierres ni recargues la página.
      </p>
    </div>
  );
}
