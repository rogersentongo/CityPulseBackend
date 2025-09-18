'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { GlassCard } from '@/components/ui/GlassCard';
import { GlassDropzone } from './GlassDropzone';
import { UploadProgress } from './UploadProgress';
import { BoroughSelector } from './BoroughSelector';
import { useAppStore } from '@/store';
import { useUpload } from '@/hooks/useUpload';

export function UploadForm() {
  const router = useRouter();
  const { selectedBorough } = useAppStore();
  const {
    uploadFile,
    uploadProgress,
    isUploading,
    uploadResult,
    uploadError,
    resetUpload
  } = useUpload();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadBorough, setUploadBorough] = useState(selectedBorough || 'Manhattan');

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  const handleUpload = () => {
    if (selectedFile) {
      uploadFile(selectedFile, uploadBorough);
    }
  };

  const handleNewUpload = () => {
    setSelectedFile(null);
    resetUpload();
  };

  const handleBackToFeed = () => {
    router.push('/feed');
  };

  if (uploadResult) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <GlassCard className="p-8">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-2xl font-bold text-white mb-4">
              Upload Successful!
            </h2>
            <p className="text-white/70 mb-6">
              Your video has been uploaded and will appear in the {uploadBorough} feed shortly.
            </p>

            <div className="flex gap-3 justify-center">
              <button
                onClick={handleNewUpload}
                className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl border border-white/20 transition-colors"
              >
                Upload Another
              </button>
              <button
                onClick={handleBackToFeed}
                className="px-6 py-3 bg-blue-500/20 hover:bg-blue-500/30 text-white rounded-xl border border-blue-500/30 transition-colors"
              >
                Back to Feed
              </button>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl font-bold text-white mb-2">
          Share Your NYC Moment
        </h1>
        <p className="text-white/60">
          Upload a video to share what's happening in your borough
        </p>
      </motion.div>

      <GlassCard className="p-6">
        {!isUploading ? (
          <div className="space-y-6">
            {/* File selection */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-3">
                Select Video
              </h3>
              <GlassDropzone
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
              />
            </div>

            {/* Borough selection */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-3">
                Choose Borough
              </h3>
              <BoroughSelector
                selectedBorough={uploadBorough}
                onBoroughSelect={setUploadBorough}
              />
            </div>

            {/* Upload button */}
            {selectedFile && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <button
                  onClick={handleUpload}
                  className="w-full px-6 py-4 bg-blue-500/20 hover:bg-blue-500/30 text-white rounded-xl border border-blue-500/30 transition-colors font-medium"
                >
                  Upload Video
                </button>
              </motion.div>
            )}

            {/* Error display */}
            {uploadError && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 bg-red-500/20 border border-red-500/30 rounded-xl"
              >
                <p className="text-red-300 text-sm">{uploadError}</p>
              </motion.div>
            )}
          </div>
        ) : (
          <UploadProgress
            progress={uploadProgress}
            fileName={selectedFile?.name || ''}
          />
        )}
      </GlassCard>
    </div>
  );
}