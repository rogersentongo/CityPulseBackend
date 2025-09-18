'use client';

import { motion } from 'framer-motion';
import { Upload, CheckCircle } from 'lucide-react';

interface UploadProgressProps {
  progress: number;
  fileName: string;
}

export function UploadProgress({ progress, fileName }: UploadProgressProps) {
  const isComplete = progress >= 100;

  return (
    <div className="space-y-6">
      <div className="text-center">
        <motion.div
          animate={isComplete ? { scale: [1, 1.1, 1] } : {}}
          transition={{ duration: 0.5 }}
          className="w-20 h-20 mx-auto mb-4 bg-blue-500/20 rounded-full flex items-center justify-center"
        >
          {isComplete ? (
            <CheckCircle className="w-10 h-10 text-green-400" />
          ) : (
            <Upload className="w-10 h-10 text-blue-400" />
          )}
        </motion.div>

        <h3 className="text-xl font-bold text-white mb-2">
          {isComplete ? 'Upload Complete!' : 'Uploading Video...'}
        </h3>

        <p className="text-white/60 text-sm">
          {fileName}
        </p>
      </div>

      {/* Progress bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-white/70">
          <span>Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>

        <div className="w-full h-3 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
          />
        </div>
      </div>

      {/* Processing stages */}
      <div className="space-y-3">
        <ProgressStep
          label="Uploading file"
          isActive={progress < 70}
          isComplete={progress >= 70}
        />
        <ProgressStep
          label="Processing video"
          isActive={progress >= 70 && progress < 90}
          isComplete={progress >= 90}
        />
        <ProgressStep
          label="Generating thumbnail"
          isActive={progress >= 90 && progress < 100}
          isComplete={progress >= 100}
        />
      </div>

      {isComplete && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-green-500/20 border border-green-500/30 rounded-xl text-center"
        >
          <p className="text-green-300 text-sm">
            Your video has been uploaded successfully!
          </p>
        </motion.div>
      )}
    </div>
  );
}

interface ProgressStepProps {
  label: string;
  isActive: boolean;
  isComplete: boolean;
}

function ProgressStep({ label, isActive, isComplete }: ProgressStepProps) {
  return (
    <div className="flex items-center space-x-3">
      <div className={`w-2 h-2 rounded-full transition-colors ${
        isComplete ? 'bg-green-400' : isActive ? 'bg-blue-400' : 'bg-white/30'
      }`} />
      <span className={`text-sm transition-colors ${
        isComplete ? 'text-green-300' : isActive ? 'text-white' : 'text-white/60'
      }`}>
        {label}
      </span>
      {isActive && (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-3 h-3 border border-white/30 border-t-white rounded-full"
        />
      )}
    </div>
  );
}