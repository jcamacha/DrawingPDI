import { motion } from 'framer-motion';
import { getPdfUrl, getJsonUrl } from '../services/analysisService';
import apiClient from '../services/api';
import { DownloadSimple, FilePdf, TextAlignLeft } from '@phosphor-icons/react';

const SPECIFIC_COLORS = [
  { key: 'red_pct', label: 'Rojo', color: '#ef4444' },
  { key: 'orange_pct', label: 'Naranja', color: '#f97316' },
  { key: 'yellow_pct', label: 'Amarillo', color: '#eab308' },
  { key: 'green_pct', label: 'Verde', color: '#22c55e' },
  { key: 'blue_pct', label: 'Azul', color: '#3b82f6' },
  { key: 'violet_pct', label: 'Violeta', color: '#8b5cf6' },
  { key: 'white_pct', label: 'Blanco', color: '#d1d5db' },
  { key: 'black_pct', label: 'Negro', color: '#374151' },
  { key: 'gray_pct', label: 'Gris', color: '#9ca3af' },
  { key: 'other_pct', label: 'Otro', color: '#6b7280' },
];

const THERAPEUTIC_GROUPS = [
  { key: 'warm_pct', label: 'Cálidos', color: '#f87171' },
  { key: 'cool_pct', label: 'Fríos', color: '#60a5fa' },
  { key: 'neutral_pct', label: 'Neutros', color: '#9ca3af' },
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.2 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 8 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 300, damping: 24 },
  },
};

function ProgressBar({ value, color, label }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-zinc-500 w-20 text-right">{label}</span>
      <div className="flex-1 h-2 bg-zinc-100 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${Math.min((value || 0) * 100, 100)}%` }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
      <span className="text-xs font-mono text-zinc-500 w-12 text-right">
        {((value || 0) * 100).toFixed(1)}%
      </span>
    </div>
  );
}

function interpretDensity(val) {
  if (val > 0.2) return 'Trazos enérgicos/tupidos';
  if (val > 0.1) return 'Trazos moderados';
  return 'Trazos suaves/dispersos';
}

function interpretFragmentation(val) {
  if (val > 0.6) return 'Muy fragmentado';
  if (val > 0.3) return 'Moderadamente fragmentado';
  return 'Trazo continuo';
}

export default function MetricsPanel({ colorDistribution, strokeMetrics, analysisId }) {
  const downloadJson = async () => {
    const res = await apiClient.get(getJsonUrl(analysisId));
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_${analysisId.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="flex flex-col gap-6"
    >
      {colorDistribution && (
        <motion.div variants={itemVariants} className="card-glass rounded-2xl overflow-hidden">
          <div className="px-5 pt-5 pb-3">
            <h3 className="text-xs font-medium tracking-widest uppercase text-zinc-400 mb-4">
              Distribución de Colores
            </h3>
            <div className="flex flex-col gap-1.5">
              {SPECIFIC_COLORS.map(({ key, label, color }) => (
                <ProgressBar
                  key={key}
                  value={colorDistribution.specific[key]}
                  color={color}
                  label={label}
                />
              ))}
            </div>
          </div>

          <div className="px-5 pb-5 pt-4 border-t border-zinc-100">
            <h4 className="text-xs font-medium tracking-widest uppercase text-zinc-400 mb-3">
              Grupos Terapéuticos
            </h4>
            <div className="flex flex-col gap-1.5">
              {THERAPEUTIC_GROUPS.map(({ key, label, color }) => (
                <ProgressBar
                  key={key}
                  value={colorDistribution.therapeutic_groups[key]}
                  color={color}
                  label={label}
                />
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {strokeMetrics && (
        <motion.div variants={itemVariants} className="card-glass rounded-2xl overflow-hidden">
          <div className="px-5 pt-5 pb-4">
            <h3 className="text-xs font-medium tracking-widest uppercase text-zinc-400 mb-5">
              Métricas de Trazo
            </h3>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <motion.div
                className="text-center"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, type: 'spring', stiffness: 300, damping: 24 }}
              >
                <div className="text-3xl font-light text-zinc-900">
                  {((strokeMetrics.edge_density_pct || 0) * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-zinc-400 mt-1">Densidad</div>
              </motion.div>
              <motion.div
                className="text-center"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.38, type: 'spring', stiffness: 300, damping: 24 }}
              >
                <div className="text-3xl font-light text-zinc-900">
                  {(strokeMetrics.mean_edge_intensity ?? 0).toFixed(1)}
                </div>
                <div className="text-xs text-zinc-400 mt-1">Intensidad</div>
              </motion.div>
              <motion.div
                className="text-center"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.46, type: 'spring', stiffness: 300, damping: 24 }}
              >
                <div className="text-3xl font-light text-zinc-900">
                  {(strokeMetrics.stroke_continuity ?? 0).toFixed(1)}
                </div>
                <div className="text-xs text-zinc-400 mt-1">Continuidad</div>
              </motion.div>
            </div>
            <p className="text-sm text-zinc-500 italic">
              {interpretDensity(strokeMetrics.edge_density_pct)}
            </p>
          </div>

          {strokeMetrics.fragmentation_ratio !== undefined && (
            <div className="px-5 py-4 border-t border-zinc-100">
              <h4 className="text-xs font-medium tracking-widest uppercase text-zinc-400 mb-3">
                Fragmentación
              </h4>
              <ProgressBar
                value={strokeMetrics.fragmentation_ratio}
                color="#6366f1"
                label="Ratio"
              />
              <p className="text-sm text-zinc-500 italic mt-2">
                {interpretFragmentation(strokeMetrics.fragmentation_ratio)}
              </p>
            </div>
          )}

          {strokeMetrics.spatial_distribution && (
            <div className="px-5 py-4 border-t border-zinc-100">
              <h4 className="text-xs font-medium tracking-widest uppercase text-zinc-400 mb-3">
                Distribución Espacial
              </h4>
              <div className="grid grid-cols-2 gap-1.5">
                {[
                  { key: 'top_left_pct', label: 'Sup. Izq.' },
                  { key: 'top_right_pct', label: 'Sup. Der.' },
                  { key: 'bottom_left_pct', label: 'Inf. Izq.' },
                  { key: 'bottom_right_pct', label: 'Inf. Der.' },
                ].map(({ key, label }) => {
                  const val = strokeMetrics.spatial_distribution[key] || 0;
                  const opacity = Math.max(0.15, Math.min(val * 5, 1));
                  return (
                    <motion.div
                      key={key}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.3, duration: 0.3 }}
                      className="rounded-lg p-2 text-center text-xs"
                      style={{
                        background: `rgba(99, 102, 241, ${opacity})`,
                      }}
                    >
                      <div className="font-mono text-zinc-700 font-medium">
                        {(val * 100).toFixed(1)}%
                      </div>
                      <div className="text-zinc-500 mt-0.5">{label}</div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          )}
        </motion.div>
      )}

      {analysisId && (
        <motion.div variants={itemVariants} className="flex gap-3">
          <motion.a
            href={getPdfUrl(analysisId)}
            target="_blank"
            rel="noreferrer"
            className="btn-primary flex-1"
            whileHover={{ y: -1 }}
            whileTap={{ scale: 0.97 }}
          >
            <FilePdf size={18} weight="duotone" />
            Reporte PDF
          </motion.a>
          <motion.button
            onClick={downloadJson}
            className="btn-ghost flex-1"
            whileHover={{ y: -1 }}
            whileTap={{ scale: 0.97 }}
          >
            <TextAlignLeft size={18} weight="duotone" />
            Exportar JSON
          </motion.button>
        </motion.div>
      )}
    </motion.div>
  );
}