import { motion } from 'framer-motion';
import ImageUploader from '../components/ImageUploader';

export default function HomePage({ onAnalysisStart }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="min-h-screen bg-zinc-50 flex items-center"
    >
      <div className="w-full max-w-6xl mx-auto px-6 md:px-12">
        <div className="flex flex-col md:flex-row items-center gap-12 md:gap-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="flex-1 md:max-w-[40%] space-y-6"
          >
            <div className="space-y-2">
              <p className="text-xs font-medium tracking-widest uppercase text-indigo-500">
                Procesamiento Digital de Imágenes
              </p>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-zinc-900 leading-tight">
                Arteterapia<span className="text-indigo-500">.</span>
              </h1>
            </div>
            <p className="text-zinc-500 text-lg leading-relaxed">
              Análisis visual avanzado para interpretación terapéutica.
              Carga una imagen y obtén métricas cromáticas, de trazos y emocionales
              basadas en procesamiento digital de imágenes.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="flex-1 md:max-w-[60%] w-full"
          >
            <ImageUploader onSuccess={onAnalysisStart} />
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}