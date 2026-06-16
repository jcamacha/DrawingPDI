import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { triggerAnalysis } from '../services/analysisService';
import ImageGrid from '../components/ImageGrid';
import ColorHistogram from '../components/ColorHistogram';
import MetricsPanel from '../components/MetricsPanel';
import VADMeter from '../components/VADMeter';
import SpatialPhenotypeMap from '../components/SpatialPhenotypeMap';
import { ArrowLeft, SpinnerGap } from '@phosphor-icons/react';

const STATES = {
  ANALYZING: 'ANALYZING',
  DONE: 'DONE',
  ERROR: 'ERROR',
};

export default function AnalysisPage({ analysisId, onReset }) {
  const [status, setStatus] = useState(STATES.ANALYZING);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!analysisId) return;
    setStatus(STATES.ANALYZING);
    setError('');

    triggerAnalysis(analysisId)
      .then((data) => {
        setResult(data);
        setStatus(STATES.DONE);
      })
      .catch((err) => {
        setError(err.response?.data?.detail?.message || 'Error al analizar la imagen.');
        setStatus(STATES.ERROR);
      });
  }, [analysisId]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen bg-zinc-50"
    >
      <div className="max-w-6xl mx-auto px-6 md:px-12 py-8">
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <p className="text-xs font-medium tracking-widest uppercase text-indigo-500 mb-1">
              Resultados del Análisis
            </p>
            <h1 className="text-2xl font-bold tracking-tight text-zinc-900">
              Arteterapia PDI
            </h1>
          </div>
          <motion.button
            onClick={onReset}
            whileHover={{ y: -1 }}
            whileTap={{ scale: 0.97 }}
            className="btn-ghost"
          >
            <ArrowLeft size={18} weight="duotone" />
            Nueva imagen
          </motion.button>
        </motion.div>

        <AnimatePresence mode="wait">
          {status === STATES.ANALYZING && (
            <motion.div
              key="analyzing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="flex flex-col items-center justify-center py-24 gap-4"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              >
                <SpinnerGap size={48} weight="duotone" className="text-indigo-500" />
              </motion.div>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-zinc-500 font-medium"
              >
                Procesando imagen con técnicas PDI...
              </motion.p>
            </motion.div>
          )}

          {status === STATES.ERROR && (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="flex flex-col items-center justify-center py-16 gap-4"
            >
              <p className="text-red-500 font-medium">{error}</p>
              <motion.button
                whileTap={{ scale: 0.97 }}
                onClick={() => {
                  setStatus(STATES.ANALYZING);
                  triggerAnalysis(analysisId)
                    .then((data) => { setResult(data); setStatus(STATES.DONE); })
                    .catch((err) => {
                      setError(err.response?.data?.detail?.message || 'Error al analizar.');
                      setStatus(STATES.ERROR);
                    });
                }}
                className="btn-primary"
              >
                Reintentar
              </motion.button>
            </motion.div>
          )}

          {status === STATES.DONE && result && (
            <motion.div
              key="done"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-5"
            >
              <div className="flex flex-col gap-5">
                <ImageGrid images={result.images} />
                <ColorHistogram histogram={result.histogram} />
              </div>
              <div className="flex flex-col gap-5">
                <MetricsPanel
                  colorDistribution={result.color_distribution}
                  strokeMetrics={result.stroke_metrics}
                  enrichedFeatures={result.enriched_features}
                  analysisId={analysisId}
                />
                <VADMeter vad={result.enriched_features?.computational_vad} />
                <SpatialPhenotypeMap
                  spatialPhenotype={result.enriched_features?.spatial_phenotype}
                  canvasUtilization={result.enriched_features?.canvas_utilization}
                  visualComplexity={result.enriched_features?.visual_complexity}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}