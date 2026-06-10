import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CloudArrowUp, CheckCircle, WarningCircle } from '@phosphor-icons/react';
import { uploadImage } from '../services/imageService';

const STATES = {
  IDLE: 'IDLE',
  UPLOADING: 'UPLOADING',
  SUCCESS: 'SUCCESS',
  ERROR: 'ERROR',
};

const stateVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
};

export default function ImageUploader({ onSuccess }) {
  const [status, setStatus] = useState(STATES.IDLE);
  const [errorMsg, setErrorMsg] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file) return;
    setStatus(STATES.UPLOADING);
    setErrorMsg('');
    try {
      const analysisId = await uploadImage(file);
      setStatus(STATES.SUCCESS);
      onSuccess(analysisId);
    } catch (err) {
      setStatus(STATES.ERROR);
      const detail = err.response?.data?.detail;
      setErrorMsg(detail?.message || 'Error al subir la imagen.');
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => setIsDragging(false);

  const onFileChange = (e) => {
    handleFile(e.target.files[0]);
  };

  return (
    <motion.div
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onClick={() => inputRef.current?.click()}
      whileTap={{ scale: 0.98 }}
      className={`
        relative rounded-[2rem] p-10 text-center cursor-pointer
        transition-colors duration-150
        ${isDragging
          ? 'bg-indigo-50 border-2 border-indigo-300'
          : 'card-glass'
        }
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".jpg,.jpeg,.png"
        onChange={onFileChange}
        className="hidden"
      />

      <AnimatePresence mode="wait">
        {status === STATES.IDLE && (
          <motion.div
            key="idle"
            variants={stateVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col items-center gap-3"
          >
            <motion.div
              whileHover={{ y: -2 }}
              transition={{ type: 'spring', stiffness: 300, damping: 24 }}
            >
              <CloudArrowUp size={40} weight="duotone" className="text-zinc-400" />
            </motion.div>
            <p className="text-zinc-600 text-lg font-medium">
              Arrastra una imagen aquí o haz clic para seleccionar
            </p>
            <p className="text-zinc-400 text-sm">
              JPG, JPEG, PNG — máx 10MB
            </p>
          </motion.div>
        )}

        {status === STATES.UPLOADING && (
          <motion.div
            key="uploading"
            variants={stateVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col items-center gap-4"
          >
            <div className="w-64 h-2 bg-zinc-200 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full bg-indigo-500"
                initial={{ width: '0%' }}
                animate={{ width: '70%' }}
                transition={{ duration: 3, ease: 'easeOut' }}
              />
            </div>
            <p className="text-indigo-500 font-medium">Procesando imagen...</p>
          </motion.div>
        )}

        {status === STATES.SUCCESS && (
          <motion.div
            key="success"
            variants={stateVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col items-center gap-3"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            >
              <CheckCircle size={40} weight="duotone" className="text-emerald-500" />
            </motion.div>
            <p className="text-emerald-600 font-medium">Imagen cargada correctamente</p>
          </motion.div>
        )}

        {status === STATES.ERROR && (
          <motion.div
            key="error"
            variants={stateVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col items-center gap-3"
            onClick={(e) => e.stopPropagation()}
          >
            <WarningCircle size={40} weight="duotone" className="text-red-400" />
            <p className="text-red-500 font-medium">{errorMsg}</p>
            <motion.button
              whileTap={{ scale: 0.97 }}
              onClick={(e) => { e.stopPropagation(); setStatus(STATES.IDLE); }}
              className="btn-ghost text-sm"
            >
              Reintentar
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}