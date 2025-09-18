'use client';

import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, AlertCircle } from 'lucide-react';
import { VideoCard } from './VideoCard';
import { PullToRefresh } from './PullToRefresh';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useAppStore } from '@/store';
import { useFeed } from '@/hooks/useFeed';
import { useRubberBand } from '@/hooks/useRubberBand';

export function VideoFeed() {
  const { userId, selectedBorough, error } = useAppStore();
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

  // Error state
  if (error && videos.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center justify-center min-h-[60vh] px-4"
      >
        <AlertCircle className="w-16 h-16 text-red-400 mb-4" />
        <h3 className="text-xl font-semibold text-white mb-2">
          Something went wrong
        </h3>
        <p className="text-white/60 mb-6 text-center">
          {error}
        </p>
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={() => refresh()}
          className="flex items-center space-x-2 px-4 py-2 bg-nyc-blue rounded-lg text-white font-medium hover:bg-nyc-blue/80 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Try Again</span>
        </motion.button>
      </motion.div>
    );
  }

  // Loading state
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

        {/* Error indicator when loading more */}
        {error && videos.length > 0 && !isLoading && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center py-8"
          >
            <AlertCircle className="w-8 h-8 text-red-400 mb-2" />
            <p className="text-white/60 text-sm text-center mb-3">
              Failed to load more videos
            </p>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => loadMore()}
              className="flex items-center space-x-2 px-3 py-1 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm hover:bg-red-500/30 transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Retry</span>
            </motion.button>
          </motion.div>
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