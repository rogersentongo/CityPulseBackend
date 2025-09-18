'use client';

import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { VideoCard } from './VideoCard';
import { PullToRefresh } from './PullToRefresh';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useAppStore } from '@/store';
import { useFeed } from '@/hooks/useFeed';
import { useRubberBand } from '@/hooks/useRubberBand';

export function VideoFeed() {
  const { userId, selectedBorough } = useAppStore();
  const { videos, isLoading, hasMore, loadMore, refresh, initialize } = useFeed();
  const { isAtTop, isAtBottom, pullDistance, isRefreshing, setIsRefreshing } = useRubberBand();

  // Initialize feed on mount
  useEffect(() => {
    initialize();
  }, [initialize]);

  useEffect(() => {
    if (isRefreshing) {
      refresh().finally(() => setIsRefreshing(false));
    }
  }, [isRefreshing, refresh, setIsRefreshing]);

  // Infinite scroll handler
  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + document.documentElement.scrollTop >=
        document.documentElement.offsetHeight - 1000 &&
        !isLoading &&
        hasMore
      ) {
        loadMore();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isLoading, hasMore, loadMore]);

  if (isLoading && videos.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="relative min-h-screen">
      {/* Pull to refresh indicator */}
      <PullToRefresh pullDistance={pullDistance} isRefreshing={isRefreshing} />

      {/* Video feed */}
      <motion.div
        style={{ paddingTop: `${pullDistance}px` }}
        className="px-4 py-6 space-y-6"
      >
        <AnimatePresence>
          {videos.map((video, index) => (
            <motion.div
              key={video.video_id}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ delay: index * 0.1 }}
            >
              <VideoCard video={video} />
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading more indicator */}
        {isLoading && videos.length > 0 && (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        )}

        {/* Bottom rubber band effect */}
        {isAtBottom && !hasMore && videos.length > 0 && (
          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 0.5, repeat: Infinity }}
            className="text-center py-8 text-white/60"
          >
            You've reached the end! 🎬
          </motion.div>
        )}

        {/* Empty state */}
        {!isLoading && videos.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-16"
          >
            <div className="text-6xl mb-4">🎥</div>
            <h3 className="text-xl font-semibold text-white mb-2">
              No videos yet
            </h3>
            <p className="text-white/60 mb-6">
              Be the first to share something from {selectedBorough}!
            </p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}