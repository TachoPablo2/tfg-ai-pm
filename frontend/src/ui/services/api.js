const API_BASE = 'http://localhost:8000';

function mapScope(scope) {
  return scope === 'sprint' ? 'Sprint' : 'Proyecto';
}

function mapRole(role) {
  return role === 'pm' ? 'Project Manager' : 'PMO';
}

export async function uploadAndAnalyze({ file, scope, role }) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('alcance', mapScope(scope));
  formData.append('rol', mapRole(role));

  const response = await fetch(`${API_BASE}/api/analyze/process`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: 'Error de conexión con el servidor' }));
    throw new Error(detail.detail || `Error ${response.status}`);
  }

  return response.json();
}

export async function exportPdf({ datos_ui, recomendacion_ia, graficos }) {
  const response = await fetch(`${API_BASE}/api/reports/export-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      datos_ui,
      recomendacion_ia,
      graficos: graficos || [],
    }),
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: 'Error al generar el PDF' }));
    throw new Error(detail.detail || `Error ${response.status}`);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'informe_ejecutivo_ia.pdf';
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}
