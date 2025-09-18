'use client';

import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, MapPin, Clock } from 'lucide-react';
import { GlassModal } from '@/components/ui/GlassModal';
import { VideoPlayer } from './VideoPlayer';
import { GlassLikeButton } from '@/components/interactions/GlassLikeButton';
import { VideoResponse } from '@/types/api';
import { formatDistanceToNow } from '@/lib/utils';

interface VideoModalProps {
  video: VideoResponse;
  isOpen: boolean;
  onClose: () => void;
}

export function VideoModal({ video, isOpen, onClose }: VideoModalProps) {
  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <GlassModal onClose={onClose}>
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="w-full max-w-4xl max-h-[90vh] overflow-hidden"
          >
            {/* Video player */}
            <div className="relative aspect-video bg-black rounded-t-2xl overflow-hidden">
              <VideoPlayer video={video} />

              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 z-10 p-2 bg-black/50 hover:bg-black/70 text-white rounded-full backdrop-blur-sm transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Video info */}
            <div className="p-6 bg-white/5 backdrop-blur-sm rounded-b-2xl">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-white mb-2">
                    {video.title || 'Untitled Video'}
                  </h2>

                  <div className="flex items-center text-sm text-white/70 space-x-4 mb-3">
                    <div className="flex items-center">
                      <MapPin className="w-4 h-4 mr-1" />
                      {video.borough}
                    </div>

                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      {formatDistanceToNow(video.uploaded_at)}
                    </div>
                  </div>

                  {video.description && (
                    <p className="text-white/80 leading-relaxed">
                      {video.description}
                    </p>
                  )}
                </div>

                <div className="ml-4">
                  <GlassLikeButton
                    videoId={video.video_id}
                    initialLiked={video.user_liked || false}
                    likeCount={video.like_count || 0}
                  />
                </div>
              </div>

              {/* Tags */}
              {video.tags && video.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {video.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 text-sm bg-white/10 text-white/80 rounded-full border border-white/20"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </GlassModal>
      )}
    </AnimatePresence>
  );
}