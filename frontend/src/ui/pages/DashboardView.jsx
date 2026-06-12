import { useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  BarChart, Bar,
} from "recharts";
import {
  AlertTriangle, Shield, Clock, TrendingUp, MessageSquareText,
  ArrowDown, AlertCircle,
} from "lucide-react";
import KpiCard from "../components/KpiCard";

function kpiColor(value) {
  if (value == null) return "#0F172A";
  if (value >= 0.6) return "#EF4444";
  if (value >= 0.3) return "#F59E0B";
  return "#10B981";
}

function formatPct(v) {
  if (v == null) return "---";
  return `${(v * 100).toFixed(0)}%`;
}

function formatNum(v) {
  if (v == null) return "---";
  return Number(v).toLocaleString("es-ES", { maximumFractionDigits: 1 });
}

function gravedadColor(g) {
  if (!g) return "#64748B";
  if (g.includes("Alto") || g.includes("Rojo")) return "#EF4444";
  if (g.includes("Medio") || g.includes("Amarillo")) return "#F59E0B";
  return "#10B981";
}

function severityFromProb(v) {
  if (v >= 0.75) return "Alto";
  if (v >= 0.55) return "Medio";
  return "Bajo";
}

function TareaCard({ tarea, icon: Icon, label, valueKey, colorKey }) {
  const rawSeverity = colorKey ? tarea[colorKey] : null;
  const severity = rawSeverity || severityFromProb(tarea[valueKey]);
  return (
    <div className="flex items-start gap-3 p-4 bg-white border border-slate-200 rounded-lg">
      <div className="p-2 rounded-full bg-slate-100 shrink-0">
        <Icon className="w-4 h-4 text-slate-500" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-xs text-slate-400 font-mono">{tarea.Issue_Key}</div>
        <div className="text-sm font-medium text-slate-800 truncate">{tarea.Title}</div>
        <div className="flex items-center gap-3 mt-1">
          <span className="text-xs text-slate-500">{label}: {formatPct(tarea[valueKey])}</span>
          <span
            className="text-xs font-semibold px-2 py-0.5 rounded-full"
            style={{
              backgroundColor: `${gravedadColor(severity)}18`,
              color: gravedadColor(severity),
            }}
          >
            {severity}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function DashboardView({ data, chartRef }) {
  const [tab, setTab] = useState("metrics");

  const kpis = data?.datos_ui?.UI_Header_KPIs || {};
  const estado = data?.datos_ui?.UI_Tab_1_Estado || {};
  const contexto = data?.datos_ui?.LLM_Tab_2_Contexto || {};
  const recomendacion = data?.recomendacion_ia || "";
  const riesgoPorTipo = estado.Grafico_Riesgo_por_Tipo || {};
  const evolucionRiesgo = estado.Grafico_Evolucion_Riesgo || {};
  const evolucionRetraso = estado.Grafico_Evolucion_Retraso || {};
  const topRiesgos = contexto.Top_Tareas_Riesgo_Bloqueos || [];
  const topRetrasos = contexto.Top_Tareas_Retraso_Cronograma || [];
  const metricasNegocio = contexto.Metricas_Globales_Negocio || {};

  const evolucionRiesgoData = Object.entries(evolucionRiesgo).map(([date, val]) => ({
    date,
    riesgo: Number(val),
  }));

  const evolucionRetrasoData = Object.entries(evolucionRetraso).map(([date, val]) => ({
    date,
    retraso: Number(val),
  }));

  const tipoData = Object.entries(riesgoPorTipo).map(([type, val]) => ({
    type,
    riesgo: Number(val),
  }));

  const semaforoColor =
    estado.Semaforo_Riesgo_Global === "Rojo"
      ? "#EF4444"
      : estado.Semaforo_Riesgo_Global === "Amarillo"
        ? "#F59E0B"
        : "#10B981";

  const alertaActiva = estado.Alerta_Retraso_Global === "Activada";

  return (
    <div className="max-w-6xl mx-auto pt-6 pb-12 space-y-6">
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-4">
        <KpiCard label="Total Tareas" value={formatNum(kpis.Total_Tareas)} color="#0F172A" />
        <KpiCard
          label="Completado"
          value={kpis.Tasa_Completado_Pct != null ? `${Number(kpis.Tasa_Completado_Pct).toFixed(0)}%` : "---"}
          color="#0F172A"
        />
        <KpiCard
          label="Esfuerzo Total"
          value={kpis.Esfuerzo_Total != null ? formatNum(kpis.Esfuerzo_Total) : "---"}
          subtitle="Story Points"
          color="#0F172A"
        />
        <KpiCard
          label="Esf. en Riesgo"
          value={metricasNegocio.Esfuerzo_Total_Comprometido_En_Riesgo != null ? formatNum(metricasNegocio.Esfuerzo_Total_Comprometido_En_Riesgo) : "---"}
          subtitle="Story Points"
          color={
            kpis.Esfuerzo_Total > 0 && metricasNegocio.Esfuerzo_Total_Comprometido_En_Riesgo / kpis.Esfuerzo_Total > 0.5
              ? "#EF4444"
              : metricasNegocio.Esfuerzo_Total_Comprometido_En_Riesgo > 0
                ? "#F59E0B"
                : "#10B981"
          }
        />
        <KpiCard
          label="Bloqueadas"
          value={formatNum(kpis.Tareas_Bloqueadas_Activas)}
          subtitle={kpis.Tareas_Bloqueadas_Activas != null ? `de ${formatNum(kpis.Total_Tareas)} tareas` : undefined}
          color={kpis.Tareas_Bloqueadas_Activas > 0 ? "#EF4444" : "#10B981"}
        />
        <KpiCard
          label="Riesgo Promedio"
          value={formatPct(kpis.Riesgo_Promedio)}
          color={kpiColor(kpis.Riesgo_Promedio)}
        />
        <KpiCard
          label="Retraso Promedio"
          value={formatPct(kpis.Retraso_Promedio)}
          color={kpiColor(kpis.Retraso_Promedio)}
        />
      </div>

      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg">
          <Shield aria-hidden="true" className="w-5 h-5" style={{ color: semaforoColor }} />
          <span className="text-sm text-slate-600">
            Riesgo:{" "}
            <span className="font-semibold" style={{ color: semaforoColor }}>
              {estado.Semaforo_Riesgo_Global || "---"}
            </span>
          </span>
        </div>
        <div className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg">
          <Clock aria-hidden="true" className="w-5 h-5" style={{ color: alertaActiva ? "#F59E0B" : "#10B981" }} />
          <span className="text-sm text-slate-600">
            Alerta de retraso:{" "}
            <span className="font-semibold" style={{ color: alertaActiva ? "#F59E0B" : "#10B981" }}>
              {alertaActiva ? "Activada" : "Desactivada"}
            </span>
          </span>
        </div>
        {metricasNegocio.Total_Bloqueos_Activos > 0 && (
          <div className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg">
            <AlertCircle aria-hidden="true" className="w-5 h-5 text-alert-red" />
            <span className="text-sm text-slate-600">
              Bloqueos totales:{" "}
              <span className="font-semibold text-alert-red">{metricasNegocio.Total_Bloqueos_Activos}</span>
            </span>
          </div>
        )}
      </div>

      <div className="border-b border-slate-200" role="tablist">
        <div className="flex gap-6">
          <button
            onClick={() => setTab("metrics")}
            role="tab"
            aria-selected={tab === "metrics"}
            className={`pb-2 text-sm font-medium transition-colors border-b-2 ${
              tab === "metrics"
                ? "text-corporate-blue border-corporate-blue"
                : "text-slate-400 border-transparent hover:text-slate-600"
            }`}
          >
            Metricas y Alertas
          </button>
          <button
            onClick={() => setTab("llm")}
            role="tab"
            aria-selected={tab === "llm"}
            className={`pb-2 text-sm font-medium transition-colors border-b-2 ${
              tab === "llm"
                ? "text-corporate-blue border-corporate-blue"
                : "text-slate-400 border-transparent hover:text-slate-600"
            }`}
          >
            Recomendaciones
          </button>
        </div>
      </div>

      <div className={tab !== "metrics" ? "hidden" : ""} role="tabpanel">
        <div className="space-y-6" ref={chartRef}>
          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
              <AlertTriangle aria-hidden="true" className="w-4 h-4 text-alert-red" />
              Tareas en Riesgo
            </h3>
            {topRiesgos.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {topRiesgos.map((t, i) => (
                  <TareaCard key={`${t.Issue_Key}-${i}`} tarea={t} icon={AlertTriangle} label="Riesgo" valueKey="Prob_Riesgo" colorKey="Gravedad" />
                ))}
              </div>
            ) : (
              <div className="bg-white border border-slate-200 rounded-xl p-6 text-center">
                <p className="text-sm text-slate-400">No se detectaron tareas con riesgo significativo.</p>
              </div>
            )}
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
              <ArrowDown aria-hidden="true" className="w-4 h-4 text-alert-yellow" />
              Tareas con Retraso
            </h3>
            {topRetrasos.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {topRetrasos.map((t, i) => (
                  <TareaCard key={`${t.Issue_Key}-${i}`} tarea={t} icon={ArrowDown} label="Retraso" valueKey="Prob_Retraso" />
                ))}
              </div>
            ) : (
              <div className="bg-white border border-slate-200 rounded-xl p-6 text-center">
                <p className="text-sm text-slate-400">No se detectaron tareas con retraso significativo.</p>
              </div>
            )}
          </div>

          {evolucionRiesgoData.length > 0 && (
            <div data-chart-wrapper className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2">
                <TrendingUp aria-hidden="true" className="w-4 h-4" />
                Evolucion del Riesgo
              </h3>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={evolucionRiesgoData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#94A3B8" }} angle={-45} textAnchor="end" height={60} interval="preserveStartEnd" />
                  <YAxis
                    domain={[0, 1]}
                    tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                    tick={{ fontSize: 11, fill: "#94A3B8" }}
                  />
                  <Tooltip
                    formatter={(v) => [`${(v * 100).toFixed(1)}%`, "Riesgo"]}
                    contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #E2E8F0", boxShadow: "0 2px 8px rgba(0,0,0,0.08)" }}
                  />
                  <Line
                    type="monotone"
                    dataKey="riesgo"
                    stroke="#0A2540"
                    strokeWidth={2}
                    dot={{ r: 3, fill: "#fff", stroke: "#0A2540", strokeWidth: 2 }}
                    activeDot={{ r: 5, fill: "#0A2540", stroke: "#fff", strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {evolucionRetrasoData.length > 0 && (
            <div data-chart-wrapper className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2">
                <TrendingUp aria-hidden="true" className="w-4 h-4" />
                Evolucion del Retraso
              </h3>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={evolucionRetrasoData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#94A3B8" }} angle={-45} textAnchor="end" height={60} interval="preserveStartEnd" />
                  <YAxis
                    domain={[0, 1]}
                    tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                    tick={{ fontSize: 11, fill: "#94A3B8" }}
                  />
                  <Tooltip
                    formatter={(v) => [`${(v * 100).toFixed(1)}%`, "Retraso"]}
                    contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #E2E8F0", boxShadow: "0 2px 8px rgba(0,0,0,0.08)" }}
                  />
                  <Line
                    type="monotone"
                    dataKey="retraso"
                    stroke="#0A2540"
                    strokeWidth={2}
                    dot={{ r: 3, fill: "#fff", stroke: "#0A2540", strokeWidth: 2 }}
                    activeDot={{ r: 5, fill: "#0A2540", stroke: "#fff", strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {tipoData.length > 0 && (
            <div data-chart-wrapper className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="text-sm font-semibold text-slate-700 mb-4">
                Riesgo Promedio por Tipo de Tarea
              </h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={tipoData} barSize={40}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                  <XAxis dataKey="type" tick={{ fontSize: 11, fill: "#94A3B8" }} />
                  <YAxis
                    domain={[0, 1]}
                    tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                    tick={{ fontSize: 11, fill: "#94A3B8" }}
                  />
                  <Tooltip
                    formatter={(v) => [`${(v * 100).toFixed(1)}%`, "Riesgo"]}
                    contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #E2E8F0", boxShadow: "0 2px 8px rgba(0,0,0,0.08)" }}
                  />
                  <Bar dataKey="riesgo" radius={[6, 6, 0, 0]} fill="#0A2540" fillOpacity={0.85} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {evolucionRiesgoData.length === 0 && evolucionRetrasoData.length === 0 && tipoData.length === 0 && (
            <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
              <TrendingUp aria-hidden="true" className="w-6 h-6 text-slate-300 mx-auto mb-2" />
              <p className="text-sm text-slate-400">No hay datos temporales para mostrar graficos.</p>
            </div>
          )}
        </div>
      </div>

      <div className={tab !== "llm" ? "hidden" : ""} role="tabpanel">
        <div className="bg-white border border-slate-200 rounded-xl p-8">
          {recomendacion ? (
            <div className="prose prose-sm max-w-none text-slate-700 leading-relaxed whitespace-pre-line">
              {recomendacion}
            </div>
          ) : (
            <div className="text-center py-12">
              <MessageSquareText aria-hidden="true" className="w-8 h-8 text-slate-300 mx-auto mb-3" />
              <p className="text-sm text-slate-400">
                No hay recomendaciones disponibles.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
