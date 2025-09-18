import { StateCreator } from 'zustand';
import { FeedStore } from '@/types/store';

export const createFeedSlice: StateCreator<FeedStore> = (set, get) => ({
  // State
  videos: [],
  isLoading: false,
  hasMore: true,
  error: null,
  lastRefresh: Date.now(),
  feedMode: 'personalized',
  currentPage: 1,

  // Actions
  setVideos: (videos) => {
    set({ videos, error: null });
  },

  addVideos: (newVideos) => {
    const currentVideos = get().videos;
    const existingIds = new Set(currentVideos.map(v => v.video_id));
    const uniqueNewVideos = newVideos.filter(v => !existingIds.has(v.video_id));
    set({
      videos: [...currentVideos, ...uniqueNewVideos],
      error: null
    });
  },

  setLoading: (isLoading) => {
    set({ isLoading });
  },

  setHasMore: (hasMore) => {
    set({ hasMore });
  },

  setError: (error) => {
    set({ error, isLoading: false });
  },

  setCurrentPage: (currentPage) => {
    set({ currentPage });
  },

  refreshFeed: () => {
    set({
      videos: [],
      hasMore: true,
      error: null,
      lastRefresh: Date.now(),
      currentPage: 1
    });
  },

  setFeedMode: (feedMode) => {
    set({ feedMode });
    // Clear current feed when switching modes
    get().refreshFeed();
  },

  clearFeed: () => {
    set({
      videos: [],
      hasMore: true,
      error: null,
      currentPage: 1
    });
  },
});