import { motion } from 'framer-motion';

const ZONES = [
  { key: 'top_left_pct', label: 'PASADO', x: 0, y: 0 },
  { key: 'top_right_pct', label: 'FUTURO', x: 1, y: 0 },
  { key: 'bottom_left_pct', label: 'MATERIAL', x: 0, y: 1 },
  { key: 'bottom_right_pct', label: 'IDEAL', x: 1, y: 1 },
];

const ZONE_COLORS = {
  PASADO: '#818cf8',
  FUTURO: '#f59e0b',
  MATERIAL: '#22c55e',
  IDEAL: '#ec4899',
};

export default function SpatialPhenotypeMap({ spatialPhenotype, canvasUtilization, visualComplexity }) {
  if (!spatialPhenotype) return null;

  const centroid = spatialPhenotype.predominant_color_centroid || { x_norm: 0.5, y_norm: 0.5 };
  const quadrantDist = spatialPhenotype.quadrant_mass_distribution || {};
  const dominantGroup = spatialPhenotype.dominant_group || 'unknown';

  const dominantLabels = {
    warm: 'Cálidos',
    cool: 'Fríos',
    neutral: 'Neutros',
    unknown: '—',
  };

  const currentZone = centroid.x_norm < 0.5
    ? (centroid.y_norm < 0.5 ? 'PASADO' : 'MATERIAL')
    : (centroid.y_norm < 0.5 ? 'FUTURO' : 'IDEAL');

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="card-glass rounded-2xl overflow-hidden"
    >
      <div className="px-5 pt-5 pb-4">
        <h3 className="text-xs font-medium tracking-widest uppercase text-zinc-400 mb-4">
          Fenotipado Espacial
        </h3>

        <div className="flex flex-col items-center gap-3">
          <div className="relative w-[200px] h-[200px] grid grid-cols-2 grid-rows-2 rounded-xl overflow-hidden border border-zinc-200/60">
            {ZONES.map(({ key, label }) => {
              const val = quadrantDist[key] || 0;
              const opacity = Math.max(0.08, Math.min(val * 3, 0.35));
              const isActive = label === currentZone;
              return (
                <div
                  key={key}
                  className="flex flex-col items-center justify-center text-center p-1.5 transition-all"
                  style={{
                    background: isActive
                      ? `rgba(99, 102, 241, ${opacity + 0.15})`
                      : `rgba(244, 244, 245, ${opacity + 0.3})`,
                  }}
                >
                  <span className={`text-[10px] font-medium tracking-wider ${isActive ? 'text-indigo-600' : 'text-zinc-400'}`}>
                    {label}
                  </span>
                  <span className={`text-xs font-mono ${isActive ? 'text-indigo-700 font-semibold' : 'text-zinc-500'}`}>
                    {(val * 100).toFixed(1)}%
                  </span>
                </div>
              );
            })}

            <motion.div
              className="absolute w-3 h-3 rounded-full bg-indigo-500 border-2 border-white shadow-lg"
              style={{
                left: `${Math.min(Math.max(centroid.x_norm * 100, 5), 95)}%`,
                top: `${Math.min(Math.max(centroid.y_norm * 100, 5), 95)}%`,
                transform: 'translate(-50%, -50%)',
              }}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20, delay: 0.5 }}
            >
              <motion.div
                className="absolute inset-0 rounded-full bg-indigo-400"
                animate={{ scale: [1, 1.8, 1], opacity: [0.6, 0, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </motion.div>
          </div>

          <div className="flex items-center gap-2 text-xs text-zinc-500">
            <span className="inline-block w-2 h-2 rounded-full bg-indigo-500" />
            <span>Cuadrante: <strong className="text-zinc-700">{currentZone}</strong></span>
            <span className="text-zinc-300">|</span>
            <span>Perfil: <strong className="text-zinc-700">{dominantLabels[dominantGroup]}</strong></span>
          </div>

          {canvasUtilization && (
            <div className="w-full grid grid-cols-2 gap-2 text-xs">
              <div className="text-center p-2 rounded-lg bg-zinc-50">
                <div className="font-mono font-medium text-zinc-700">
                  {((canvasUtilization.total_used_pct ?? 0) * 100).toFixed(1)}%
                </div>
                <div className="text-zinc-400">Ocupación</div>
              </div>
              <div className="text-center p-2 rounded-lg bg-zinc-50">
                <div className="font-mono font-medium text-zinc-700">
                  {((canvasUtilization.symmetry_index ?? 0) * 100).toFixed(0)}%
                </div>
                <div className="text-zinc-400">Simetría I-D</div>
              </div>
            </div>
          )}

          {visualComplexity && visualComplexity.image_entropy > 0 && (
            <div className="w-full grid grid-cols-2 gap-2 text-xs">
              <div className="text-center p-2 rounded-lg bg-zinc-50">
                <div className="font-mono font-medium text-zinc-700">
                  {(visualComplexity.image_entropy ?? 0).toFixed(2)}
                </div>
                <div className="text-zinc-400">Entropía</div>
              </div>
              <div className="text-center p-2 rounded-lg bg-zinc-50">
                <div className="font-mono font-medium text-zinc-700">
                  {(visualComplexity.fractal_dimension ?? 0).toFixed(2)}
                </div>
                <div className="text-zinc-400">Dim. Fractal</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}