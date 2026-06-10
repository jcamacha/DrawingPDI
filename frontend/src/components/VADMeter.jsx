import { motion } from 'framer-motion';

const VAD_CONFIG = [
  {
    key: 'valence_estimate',
    label: 'Valencia',
    description: 'Emoción positiva vs. negativa',
    gradient: 'from-emerald-400 to-red-400',
    color: '#22c55e',
  },
  {
    key: 'arousal_estimate',
    label: 'Activación',
    description: 'Nivel de energía emocional',
    gradient: 'from-zinc-300 to-orange-400',
    color: '#f97316',
  },
  {
    key: 'dominance_estimate',
    label: 'Dominancia',
    description: 'Grado de control percibido',
    gradient: 'from-zinc-300 to-indigo-500',
    color: '#6366f1',
  },
];

export default function VADMeter({ vad }) {
  if (!vad) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="card-glass rounded-2xl overflow-hidden"
    >
      <div className="px-5 pt-5 pb-4">
        <h3 className="text-xs font-medium tracking-widest uppercase text-zinc-400 mb-5">
          Dimensiones Emocionales (VAD)
        </h3>
        <div className="flex flex-col gap-5">
          {VAD_CONFIG.map(({ key, label, description, color }) => {
            const value = vad[key] ?? 0;
            const percentage = Math.min(Math.max(value * 100, 0), 100);
            return (
              <div key={key}>
                <div className="flex items-baseline justify-between mb-1.5">
                  <div>
                    <span className="text-sm font-medium text-zinc-700">{label}</span>
                    <span className="text-xs text-zinc-400 ml-2">{description}</span>
                  </div>
                  <span className="text-sm font-mono text-zinc-500">
                    {value.toFixed(2)}
                  </span>
                </div>
                <div className="h-2 bg-zinc-100 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ background: color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}