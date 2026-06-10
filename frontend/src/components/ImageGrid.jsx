import { motion } from 'framer-motion';

const grid = [
  { key: 'original_b64', title: 'Imagen Original' },
  { key: 'filtered_b64', title: 'Filtro Bilateral' },
  { key: 'canny_b64', title: 'Bordes Canny' },
  { key: 'hsv_mask_b64', title: 'Máscara HSV' },
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 300, damping: 24 },
  },
};

export default function ImageGrid({ images }) {
  if (!images) return null;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="card-glass p-4 rounded-[2rem]"
    >
      <div className="grid grid-cols-2 gap-3">
        {grid.map(({ key, title }) => (
          <motion.div
            key={key}
            variants={itemVariants}
            whileHover={{ y: -2 }}
            transition={{ type: 'spring', stiffness: 300, damping: 24 }}
            className="relative rounded-[1.5rem] overflow-hidden group"
          >
            {images[key] ? (
              <>
                <img
                  src={`data:image/png;base64,${images[key]}`}
                  alt={title}
                  className="w-full block object-cover"
                />
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/40 to-transparent pt-8 pb-2 px-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <span className="text-white text-xs font-medium tracking-wide">
                    {title}
                  </span>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-32 text-zinc-400 text-sm">
                No disponible
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}