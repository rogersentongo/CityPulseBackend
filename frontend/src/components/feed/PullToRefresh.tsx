'use client';

import { motion } from 'framer-motion';
import { RefreshCw } from 'lucide-react';

interface PullToRefreshProps {
  pullDistance: number;
  isRefreshing: boolean;
}

export function PullToRefresh({ pullDistance, isRefreshing }: PullToRefreshProps) {
  const opacity = Math.min(pullDistance / 50, 1);
  const scale = Math.min(pullDistance / 50, 1);

  if (pullDistance === 0 && !isRefreshing) {
    return null;
  }

  return (
    <motion.div
      className="fixed top-0 left-0 right-0 z-50 flex justify-center"
      style={{ opacity }}
    >
      <div className="mt-4 p-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full">
        <motion.div
          animate={isRefreshing ? { rotate: 360 } : { rotate: 0 }}
          transition={isRefreshing ? { duration: 1, repeat: Infinity, ease: 'linear' } : {}}
          style={{ scale }}
        >
          <RefreshCw className="w-6 h-6 text-white" />
        </motion.div>
      </div>
    </motion.div>
  );
}