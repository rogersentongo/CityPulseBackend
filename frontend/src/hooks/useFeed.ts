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
    addVideos,
    setLoading,
    setHasMore,
    setCurrentPage,
    setError,
    userId,
    selectedBorough,
  } = useAppStore();

  console.log('🔍 useFeed state:', {
    videosCount: videos.length,
    isLoading,
    hasMore,
    currentPage,
    userId,
    selectedBorough
  });

  const loadMore = useCallback(async () => {
    console.log('📄 loadMore called:', { isLoading, hasMore, userId, selectedBorough });

    if (isLoading || !hasMore || !userId || !selectedBorough) {
      console.log('❌ loadMore early return:', { isLoading, hasMore, userId, selectedBorough });
      return;
    }

    console.log('🚀 Starting loadMore API call...');
    setLoading(true);
    setError(null);

    try {
      const requestParams = {
        borough: selectedBorough,
        user_id: userId,
        limit: 20,
        skip: currentPage * 20,
      };
      console.log('📡 API request params:', requestParams);

      const response = await apiClient.getFeed(requestParams);
      console.log('✅ API response:', response);

      const newVideos = response.videos || [];
      console.log('📹 New videos received:', newVideos.length);

      if (newVideos.length === 0) {
        console.log('🔚 No more videos available');
        setHasMore(false);
      } else {
        console.log('➕ Adding videos to feed');
        addVideos(newVideos);
        setCurrentPage(currentPage + 1);
        console.log('📊 Updated page to:', currentPage + 1);
      }
    } catch (error) {
      console.error('❌ Error loading feed:', error);
      setError(error instanceof Error ? error.message : 'Failed to load videos');
    } finally {
      setLoading(false);
      console.log('✨ loadMore completed');
    }
  }, [
    isLoading,
    hasMore,
    userId,
    selectedBorough,
    currentPage,
    videos,
    setVideos,
    addVideos,
    setLoading,
    setHasMore,
    setCurrentPage,
    setError,
  ]);

  const refresh = useCallback(async () => {
    console.log('🔄 refresh called:', { userId, selectedBorough });

    if (!userId || !selectedBorough) {
      console.log('❌ refresh early return: missing userId or selectedBorough');
      return;
    }

    console.log('🚀 Starting refresh API call...');
    setLoading(true);
    setCurrentPage(1); // Reset to page 1
    setHasMore(true);
    setError(null);

    try {
      const requestParams = {
        borough: selectedBorough,
        user_id: userId,
        limit: 20,
        skip: 0,
      };
      console.log('📡 Refresh API request params:', requestParams);

      const response = await apiClient.getFeed(requestParams);
      console.log('✅ Refresh API response:', response);

      const newVideos = response.videos || [];
      console.log('📹 Fresh videos received:', newVideos.length);

      setVideos(newVideos);

      if (newVideos.length < 20) {
        console.log('🔚 Less than 20 videos, marking hasMore as false');
        setHasMore(false);
      }
    } catch (error) {
      console.error('❌ Error refreshing feed:', error);
      setError(error instanceof Error ? error.message : 'Failed to refresh videos');
      setVideos([]);
    } finally {
      setLoading(false);
      console.log('✨ refresh completed');
    }
  }, [userId, selectedBorough, setVideos, setLoading, setCurrentPage, setHasMore, setError]);

  // Load initial feed on mount
  const initialize = useCallback(async () => {
    console.log('🚀 initialize called:', { videosLength: videos.length, isLoading });
    if (videos.length === 0 && !isLoading) {
      console.log('📱 Initializing feed with refresh...');
      await refresh();
    } else {
      console.log('⏭️ Skipping initialize: videos already exist or loading');
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