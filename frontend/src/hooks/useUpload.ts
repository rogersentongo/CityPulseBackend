import { useState, useCallback } from 'react';
import { useAppStore } from '@/store';
import { apiClient } from '@/lib/api';
import { Borough, UploadResponse } from '@/types/api';

export function useUpload() {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [uploadError, setUploadError] = useState<string>('');

  const { userId } = useAppStore();

  const uploadFile = useCallback(async (file: File, borough: Borough, title?: string, description?: string) => {
    if (!userId) {
      setUploadError('User ID is required');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setUploadError('');
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', userId);
      formData.append('borough', borough);

      if (title) formData.append('title', title);
      if (description) formData.append('description', description);

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.random() * 10;
        });
      }, 200);

      const response = await apiClient.uploadVideo(formData);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setTimeout(() => {
        setUploadResult(response);
        setIsUploading(false);
      }, 500);

    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(error instanceof Error ? error.message : 'Upload failed');
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, [userId]);

  const resetUpload = useCallback(() => {
    setUploadProgress(0);
    setIsUploading(false);
    setUploadResult(null);
    setUploadError('');
  }, []);

  return {
    uploadFile,
    uploadProgress,
    isUploading,
    uploadResult,
    uploadError,
    resetUpload,
  };
}