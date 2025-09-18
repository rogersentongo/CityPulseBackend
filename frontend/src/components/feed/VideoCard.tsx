'use client';

import { useState, memo } from 'react';
import { motion } from 'framer-motion';
import { Play, MapPin, Clock } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { GlassLikeButton } from '@/components/interactions/GlassLikeButton';
import { VideoModal } from '../video/VideoModal';
import { VideoResponse } from '@/types/api';
import { formatDistanceToNow } from '@/lib/utils';

interface VideoCardProps {
  video: VideoResponse;
}

export const VideoCard = memo(function VideoCard({ video }: VideoCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handlePlay = () => {
    setIsModalOpen(true);
  };

  const thumbnailUrl = `http://localhost:8000/media/thumbnails/${video.video_id}.jpg`;
  const fallbackThumbnail = '/placeholder-thumbnail.svg';

  return (
    <>
      <GlassCard hoverable className="overflow-hidden">
        {/* Thumbnail with play overlay */}
        <div className="relative aspect-video bg-gray-800">
          <img
            src={imageError ? fallbackThumbnail : thumbnailUrl}
            alt={video.title || 'Video thumbnail'}
            className="w-full h-full object-cover"
            onError={() => setImageError(true)}
          />

          {/* Play button overlay */}
          <button
            onClick={handlePlay}
            className="absolute inset-0 flex items-center justify-center bg-black/20 hover:bg-black/40 transition-all duration-200 group hover:scale-105 active:scale-95"
          >
            <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm border border-white/30 flex items-center justify-center group-hover:bg-white/30 transition-colors">
              <Play className="w-8 h-8 text-white ml-1" />
            </div>
          </button>

          {/* Gradient overlay for better text readability */}
          <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-black/60 to-transparent" />
        </div>

        {/* Video info */}
        <div className="p-4">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <h3 className="font-semibold text-white line-clamp-2 mb-1">
                {video.title || 'Untitled Video'}
              </h3>

              <div className="flex items-center text-sm text-white/70 space-x-4">
                <div className="flex items-center">
                  <MapPin className="w-4 h-4 mr-1" />
                  {video.borough}
                </div>

                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  {formatDistanceToNow(video.uploaded_at || video.created_at)}
                </div>
              </div>
            </div>

            <GlassLikeButton
              videoId={video.video_id}
              initialLiked={video.user_liked || false}
              likeCount={video.like_count || 0}
            />
          </div>

          {/* Description */}
          {video.description && (
            <p className="text-sm text-white/80 line-clamp-3">
              {video.description}
            </p>
          )}

          {/* Tags */}
          {video.tags && video.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {video.tags.slice(0, 3).map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs bg-white/10 text-white/80 rounded-full"
                >
                  #{tag}
                </span>
              ))}
              {video.tags.length > 3 && (
                <span className="px-2 py-1 text-xs text-white/60">
                  +{video.tags.length - 3} more
                </span>
              )}
            </div>
          )}
        </div>
      </GlassCard>

      {/* Video modal */}
      <VideoModal
        video={video}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  );
});