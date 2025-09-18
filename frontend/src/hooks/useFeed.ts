import { useCallback } from 'react';
import { useAppStore } from '@/store';
import { apiClient } from '@/lib/api';
import { VideoResponse } from '@/types/api';

export function useFeed() {
  const {
    videos,
    isLoading,
    hasMore,
    currentPage,
    setVideos,
    setLoading,
    setHasMore,
    setCurrentPage,
    userId,
    selectedBorough,
  } = useAppStore();

  const loadMore = useCallback(async () => {
    if (isLoading || !hasMore || !userId || !selectedBorough) return;

    setLoading(true);

    try {
      const response = await apiClient.getFeed({
        borough: selectedBorough,
        user_id: userId,
        limit: 20,
        skip: currentPage * 20,
      });

      const newVideos = response.videos || [];

      if (newVideos.length === 0) {
        setHasMore(false);
      } else {
        setVideos([...videos, ...newVideos]);
        setCurrentPage(currentPage + 1);
      }
    } catch (error) {
      console.error('Error loading feed:', error);
    } finally {
      setLoading(false);
    }
  }, [
    isLoading,
    hasMore,
    userId,
    selectedBorough,
    currentPage,
    videos,
    setVideos,
    setLoading,
    setHasMore,
    setCurrentPage,
  ]);

  const refresh = useCallback(async () => {
    if (!userId || !selectedBorough) return;

    setLoading(true);
    setCurrentPage(0);
    setHasMore(true);

    try {
      const response = await apiClient.getFeed({
        borough: selectedBorough,
        user_id: userId,
        limit: 20,
        skip: 0,
      });

      const newVideos = response.videos || [];
      setVideos(newVideos);

      if (newVideos.length < 20) {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error refreshing feed:', error);
      setVideos([]);
    } finally {
      setLoading(false);
    }
  }, [userId, selectedBorough, setVideos, setLoading, setCurrentPage, setHasMore]);

  // Load initial feed on mount
  const initialize = useCallback(async () => {
    if (videos.length === 0 && !isLoading) {
      await refresh();
    }
  }, [videos.length, isLoading, refresh]);

  return {
    videos,
    isLoading,
    hasMore,
    loadMore,
    refresh,
    initialize,
  };
}