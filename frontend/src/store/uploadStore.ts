import { StateCreator } from 'zustand';
import { UploadStore } from '@/types/store';

export const createUploadSlice: StateCreator<UploadStore> = (set) => ({
  // State
  isUploading: false,
  uploadProgress: 0,
  uploadError: null,
  uploadResult: null,
  selectedFile: null,

  // Actions
  setUploading: (isUploading) => {
    set({ isUploading });
  },

  setUploadProgress: (uploadProgress) => {
    set({ uploadProgress });
  },

  setUploadError: (uploadError) => {
    set({ uploadError, isUploading: false });
  },

  setUploadResult: (uploadResult) => {
    set({
      uploadResult,
      isUploading: false,
      uploadProgress: 100
    });
  },

  setSelectedFile: (selectedFile) => {
    set({ selectedFile, uploadError: null });
  },

  resetUpload: () => {
    set({
      isUploading: false,
      uploadProgress: 0,
      uploadError: null,
      uploadResult: null,
      selectedFile: null
    });
  },
});