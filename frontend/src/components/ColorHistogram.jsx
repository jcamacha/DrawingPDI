import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { motion } from 'framer-motion';

const HUE_COLORS = [
  '#ff0000','#ff1a00','#ff3300','#ff4d00','#ff6600',
  '#ff8000','#ff9900','#ffb300','#ffcc00','#ffe600',
  '#ffff00','#ccff00','#99ff00','#66ff00','#33ff00',
  '#00ff00','#00ff33','#00ff66','#00ff99','#00ffcc',
  '#00ffff','#00ccff','#0099ff','#0066ff','#0033ff',
  '#0000ff','#3300ff','#6600ff','#9900ff','#cc00ff',
  '#ff00ff','#ff00cc','#ff0099','#ff0066','#ff0033',
];

function hueToColor(hueBin) {
  if (hueBin <= 30) return HUE_COLORS[hueBin] || '#ff0000';
  if (hueBin <= 60) return '#ccff00';
  if (hueBin <= 90) return '#00ff00';
  if (hueBin <= 120) return '#00ffff';
  if (hueBin <= 150) return '#0066ff';
  return '#9900ff';
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const { hue, count } = payload[0].payload;
  return (
    <div className="card-glass px-3 py-2 text-xs">
      <p className="font-medium text-zinc-900">Bin {hue}°</p>
      <p className="text-zinc-500">{count} píxeles</p>
    </div>
  );
}

export default function ColorHistogram({ histogram }) {
  if (!histogram || !histogram.hue) return null;

  const data = histogram.hue
    .map((count, i) => ({ hue: i, count, color: hueToColor(i) }))
    .filter((_, i) => i % 2 === 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="card-glass p-5 rounded-2xl"
    >
      <h3 className="text-sm font-medium tracking-wide uppercase text-zinc-400 mb-4">
        Histograma de Tono (H)
      </h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
          <XAxis
            dataKey="hue"
            tick={{ fontSize: 9, fill: '#a1a1aa' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 9, fill: '#a1a1aa' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={false} />
          <Bar dataKey="count" isAnimationActive={false} radius={[2, 2, 0, 0]}>
            {data.map((entry, idx) => (
              <Cell key={idx} fill={entry.color} fillOpacity={0.85} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}