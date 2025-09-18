'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart } from 'lucide-react';
import { useAppStore } from '@/store';
import { apiClient } from '@/lib/api';

interface GlassLikeButtonProps {
  videoId: string;
  initialLiked: boolean;
  likeCount: number;
}

export function GlassLikeButton({ videoId, initialLiked, likeCount }: GlassLikeButtonProps) {
  const [isLiked, setIsLiked] = useState(initialLiked);
  const [currentLikeCount, setCurrentLikeCount] = useState(likeCount);
  const [isAnimating, setIsAnimating] = useState(false);
  const { userId } = useAppStore();

  const handleLike = async () => {
    if (!userId || isAnimating) return;

    setIsAnimating(true);

    // Optimistic update
    const newLikedState = !isLiked;
    setIsLiked(newLikedState);
    setCurrentLikeCount(prev => newLikedState ? prev + 1 : prev - 1);

    try {
      if (newLikedState) {
        await apiClient.likeVideo(userId, videoId);
      } else {
        // Note: API doesn't have unlike endpoint, so we'll keep the optimistic update
        console.log('Unlike functionality not implemented in API');
      }
    } catch (error) {
      console.error('Error liking video:', error);
      // Revert optimistic update on error
      setIsLiked(!newLikedState);
      setCurrentLikeCount(prev => newLikedState ? prev - 1 : prev + 1);
    } finally {
      setTimeout(() => setIsAnimating(false), 300);
    }
  };

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={handleLike}
      className="flex items-center space-x-2 p-2 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-colors"
    >
      <div className="relative">
        <motion.div
          animate={isLiked ? { scale: [1, 1.3, 1] } : { scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Heart
            className={`w-5 h-5 transition-colors ${
              isLiked ? 'text-red-500 fill-red-500' : 'text-white/70'
            }`}
          />
        </motion.div>

        {/* Heart particles animation */}
        <AnimatePresence>
          {isAnimating && isLiked && (
            <>
              {[...Array(3)].map((_, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 1, scale: 0.5, x: 0, y: 0 }}
                  animate={{
                    opacity: 0,
                    scale: 1,
                    x: (Math.random() - 0.5) * 40,
                    y: -20 - Math.random() * 20,
                  }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.8, delay: i * 0.1 }}
                  className="absolute top-0 left-0 pointer-events-none"
                >
                  <Heart className="w-3 h-3 text-red-500 fill-red-500" />
                </motion.div>
              ))}
            </>
          )}
        </AnimatePresence>
      </div>

      <span className="text-sm text-white/80 font-medium">
        {currentLikeCount}
      </span>
    </motion.button>
  );
}