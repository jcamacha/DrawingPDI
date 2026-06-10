import { useState } from 'react';
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';

function App() {
  const [analysisId, setAnalysisId] = useState(null);

  if (analysisId) {
    return (
      <AnalysisPage
        analysisId={analysisId}
        onReset={() => setAnalysisId(null)}
      />
    );
  }

  return <HomePage onAnalysisStart={setAnalysisId} />;
}

export default App;
