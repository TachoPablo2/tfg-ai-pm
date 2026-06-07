import { useState } from 'react';
import { CloudUpload, CheckCircle2, ArrowRight } from 'lucide-react';

export default function IngestaView({ onStartAnalysis }) {
  const [file, setFile] = useState(null);
  const [scope, setScope] = useState('sprint');
  const [role, setRole] = useState('pm');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div className="max-w-5xl mx-auto mt-6">
      
      {/* Títulos centrados */}
      <div className="text-center mb-12">
        <h2 className="text-3xl font-medium text-gray-800 mb-3">Ingesta de Datos</h2>
        <p className="text-gray-500 text-sm max-w-2xl mx-auto leading-relaxed">
          Sube tus datos brutos del proyecto para comenzar la matriz de análisis. Formatos<br/>
          soportados: .CSV, .XLSX. Aplicamos el principio 'Fail-Fast' mediante validación inmediata.
        </p>
      </div>

      {/* Área de Drag & Drop */}
      <div className="mb-10">
        <div className="border border-dashed border-gray-300 rounded-lg p-16 flex flex-col items-center justify-center bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer relative">
          <input 
            type="file" 
            accept=".csv, .xlsx" 
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          {file ? (
            <div className="flex flex-col items-center text-alert-green">
              <CheckCircle2 className="w-10 h-10 mb-3 text-alert-green" strokeWidth={1.5} />
              <span className="font-medium text-gray-800">{file.name}</span>
            </div>
          ) : (
            <div className="flex flex-col items-center text-gray-500">
              <div className="bg-white p-3 rounded-full shadow-sm border border-gray-200 mb-4">
                <CloudUpload className="w-6 h-6 text-gray-600" strokeWidth={1.5} />
              </div>
              <span className="font-medium text-gray-800">Arrastra y suelta archivos aquí</span>
              <span className="text-sm mt-1">o haz clic para buscar en tu ordenador</span>
            </div>
          )}
        </div>
      </div>

      {/* Selectores convertidos en tarjetas horizontales */}
      <div className="space-y-8">
        
        {/* Alcance */}
        <div>
          <div className="flex items-center mb-4">
            <h3 className="text-sm font-semibold text-gray-800">Alcance del Análisis</h3>
            <div className="ml-4 flex-grow border-t border-gray-200"></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div 
              onClick={() => setScope('sprint')}
              className={`p-4 border rounded-md cursor-pointer transition-all ${scope === 'sprint' ? 'border-corporate-blue shadow-sm' : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="font-medium text-gray-800">Sprint</span>
                {scope === 'sprint' && <CheckCircle2 className="w-4 h-4 text-corporate-blue" />}
              </div>
              <p className="text-xs text-gray-500">Analizar las tareas activas correspondientes a una iteración específica.</p>
            </div>
            
            <div 
              onClick={() => setScope('proyecto')}
              className={`p-4 border rounded-md cursor-pointer transition-all ${scope === 'proyecto' ? 'border-corporate-blue shadow-sm' : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="font-medium text-gray-800">Proyecto Completo</span>
                {scope === 'proyecto' && <CheckCircle2 className="w-4 h-4 text-corporate-blue" />}
              </div>
              <p className="text-xs text-gray-500">Analizar el conjunto de tareas agrupadas a lo largo del tiempo.</p>
            </div>
          </div>
        </div>

        {/* Rol */}
        <div>
          <div className="flex items-center mb-4">
            <h3 className="text-sm font-semibold text-gray-800">Rol de Usuario</h3>
            <div className="ml-4 flex-grow border-t border-gray-200"></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div 
              onClick={() => setRole('pm')}
              className={`p-4 border rounded-md cursor-pointer transition-all ${role === 'pm' ? 'border-corporate-blue shadow-sm' : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="font-medium text-gray-800">Director de Proyecto (PM)</span>
                {role === 'pm' && <CheckCircle2 className="w-4 h-4 text-corporate-blue" />}
              </div>
              <p className="text-xs text-gray-500">Recibir consejos de la IA centrados en la ejecución de tareas y el equipo.</p>
            </div>
            
            <div 
              onClick={() => setRole('pmo')}
              className={`p-4 border rounded-md cursor-pointer transition-all ${role === 'pmo' ? 'border-corporate-blue shadow-sm' : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className="font-medium text-gray-800">Gestión de Proyectos (PMO)</span>
                {role === 'pmo' && <CheckCircle2 className="w-4 h-4 text-corporate-blue" />}
              </div>
              <p className="text-xs text-gray-500">Recibir consejos de la IA orientados a procesos y estándares metodológicos.</p>
            </div>
          </div>
        </div>

      </div>

      {/* Botón inferior alineado a la derecha */}
      <div className="mt-10 mb-8 flex justify-end">
        <button 
          onClick={onStartAnalysis}
          disabled={!file}
          className={`flex items-center px-6 py-2.5 rounded text-sm font-medium transition-all ${file ? 'bg-corporate-blue text-white hover:bg-opacity-90' : 'bg-corporate-blue text-white opacity-50 cursor-not-allowed'}`}
        >
          Iniciar Análisis <ArrowRight className="ml-2 w-4 h-4" />
        </button>
      </div>
      
    </div>
  );
}