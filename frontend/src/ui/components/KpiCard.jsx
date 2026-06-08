export default function KpiCard({ label, value, subtitle, color }) {
  return (
    <div className="bg-white border border-corporate-border rounded-xl p-5 flex flex-col justify-between min-w-0">
      <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
        {label}
      </span>
      <span
        className="text-2xl font-bold mt-1.5 truncate"
        style={{ color: color || '#0F172A' }}
      >
        {value ?? '—'}
      </span>
      {subtitle && (
        <span className="text-xs text-slate-400 mt-0.5">{subtitle}</span>
      )}
    </div>
  );
}
