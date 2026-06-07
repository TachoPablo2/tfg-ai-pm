import { useState } from 'react';
import IngestaView from './ui/pages/IngestaView';

function App() {
  const [appState, setAppState] = useState('INGESTA'); 

  const handleStartAnalysis = () => {
    setAppState('DASHBOARD'); 
  };

  return (
    <div className="min-h-screen font-sans bg-white flex flex-col">
      {/* Cabecera idéntica al mockup */}
      <header className="border-b border-gray-200 px-8 py-4 flex items-center justify-between bg-white">
        <div className="flex items-center space-x-3">
          <div className="bg-gray-100 text-corporate-blue font-bold px-2 py-1 rounded text-sm">IDSS</div>
          <span className="text-gray-300">|</span>
          <h1 className="text-sm font-semibold tracking-widest text-gray-500">
            PROJECT MANAGEMENT
          </h1>
        </div>
      </header>

      {/* Contenedor principal expandido */}
      <main className="flex-grow p-8">
        {appState === 'INGESTA' && (
          <IngestaView onStartAnalysis={handleStartAnalysis} />
        )}

        {appState === 'DASHBOARD' && (
          <div className="text-center mt-20">
            <h2 className="text-2xl font-semibold text-corporate-blue mb-4">
              (Próximamente) Dashboard Ejecutivo
            </h2>
            <button 
              onClick={() => setAppState('INGESTA')}
              className="border-2 border-corporate-blue text-corporate-blue px-6 py-2 rounded-md hover:bg-corporate-blue hover:text-white transition-colors"
            >
              Volver a Ingesta
            </button>
          </div>
        )}
      </main>

      {/* Pie de página idéntico al mockup */}
      <footer className="px-8 py-6 text-xs text-gray-400 flex justify-between items-center border-t border-gray-100 mt-auto">
        <span>© 2024 IDSS PMO Solutions. Todos los derechos reservados.</span>
        <span>Cumplimiento de Seguridad</span>
      </footer>
    </div>
  );
}

export default App;