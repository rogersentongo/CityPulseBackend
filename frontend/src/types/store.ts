import { Borough, VideoResponse } from './api';

// User Store Types
export interface UserState {
  userId: string | null;
  selectedBorough: Borough | null;
  isSetupComplete: boolean;
}

export interface UserActions {
  setUserId: (userId: string) => void;
  setBorough: (borough: Borough) => void;
  completeSetup: () => void;
  resetUser: () => void;
}

export type UserStore = UserState & UserActions;

// Theme Store Types
export interface ThemeState {
  theme: 'dark' | 'light';
  systemTheme: 'dark' | 'light';
}

export interface ThemeActions {
  setTheme: (theme: 'dark' | 'light') => void;
  toggleTheme: () => void;
  setSystemTheme: (theme: 'dark' | 'light') => void;
}

export type ThemeStore = ThemeState & ThemeActions;

// Feed Store Types
export interface FeedState {
  videos: VideoResponse[];
  isLoading: boolean;
  hasMore: boolean;
  error: string | null;
  lastRefresh: number;
  feedMode: 'personalized' | 'recent';
}

export interface FeedActions {
  setVideos: (videos: VideoResponse[]) => void;
  addVideos: (videos: VideoResponse[]) => void;
  setLoading: (loading: boolean) => void;
  setHasMore: (hasMore: boolean) => void;
  setError: (error: string | null) => void;
  refreshFeed: () => void;
  setFeedMode: (mode: 'personalized' | 'recent') => void;
  clearFeed: () => void;
}

export type FeedStore = FeedState & FeedActions;

// Upload Store Types
export interface UploadState {
  isUploading: boolean;
  uploadProgress: number;
  uploadError: string | null;
  uploadResult: any | null;
  selectedFile: File | null;
}

export interface UploadActions {
  setUploading: (uploading: boolean) => void;
  setUploadProgress: (progress: number) => void;
  setUploadError: (error: string | null) => void;
  setUploadResult: (result: any) => void;
  setSelectedFile: (file: File | null) => void;
  resetUpload: () => void;
}

export type UploadStore = UploadState & UploadActions;

// Combined App Store
export type AppStore = UserStore & ThemeStore & FeedStore & UploadStore;