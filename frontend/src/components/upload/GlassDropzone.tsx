'use client';

import { useCallback, useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, File, X } from 'lucide-react';
import { validateVideoFile } from '@/lib/utils';

interface GlassDropzoneProps {
  onFileSelect: (file: File) => void;
  selectedFile?: File | null;
}

export function GlassDropzone({ onFileSelect, selectedFile }: GlassDropzoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string>('');

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    setError('');

    const files = Array.from(e.dataTransfer.files);
    const file = files[0];

    if (!file) return;

    const validation = validateVideoFile(file);
    if (!validation.valid) {
      setError(validation.error || 'Invalid file');
      return;
    }

    onFileSelect(file);
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setError('');
    const file = e.target.files?.[0];

    if (!file) return;

    const validation = validateVideoFile(file);
    if (!validation.valid) {
      setError(validation.error || 'Invalid file');
      return;
    }

    onFileSelect(file);
  }, [onFileSelect]);

  const removeFile = () => {
    onFileSelect(null as any);
    setError('');
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (selectedFile) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="p-6 bg-white/5 border-2 border-white/20 rounded-2xl"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
              <File className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h4 className="font-medium text-white">{selectedFile.name}</h4>
              <p className="text-sm text-white/60">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
          </div>
          <button
            onClick={removeFile}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-white/60" />
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <div>
      <motion.div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        animate={{
          scale: isDragOver ? 1.02 : 1,
          borderColor: isDragOver ? 'rgba(59, 130, 246, 0.5)' : 'rgba(255, 255, 255, 0.2)',
        }}
        className="relative p-8 border-2 border-dashed rounded-2xl bg-white/5 text-center cursor-pointer hover:bg-white/10 transition-colors"
      >
        <input
          type="file"
          accept="video/*"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <motion.div
          animate={{ y: isDragOver ? -5 : 0 }}
          className="space-y-4"
        >
          <div className="w-16 h-16 mx-auto bg-blue-500/20 rounded-full flex items-center justify-center">
            <Upload className="w-8 h-8 text-blue-400" />
          </div>

          <div>
            <h3 className="text-lg font-medium text-white mb-2">
              {isDragOver ? 'Drop your video here' : 'Upload Video'}
            </h3>
            <p className="text-white/60 text-sm">
              Drag & drop your video file or click to browse
            </p>
            <p className="text-white/40 text-xs mt-2">
              Supports MP4, WebM, OGG, MOV (max 100MB)
            </p>
          </div>
        </motion.div>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 p-3 bg-red-500/20 border border-red-500/30 rounded-lg"
        >
          <p className="text-red-300 text-sm">{error}</p>
        </motion.div>
      )}
    </div>
  );
}