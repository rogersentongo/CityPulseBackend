'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, MapPin, Clock } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { VideoModal } from '@/components/video/VideoModal';
import { VideoResponse } from '@/types/api';
import { formatDistanceToNow } from '@/lib/utils';

interface SourceVideosProps {
  videos: VideoResponse[];
}

export function SourceVideos({ videos }: SourceVideosProps) {
  const [selectedVideo, setSelectedVideo] = useState<VideoResponse | null>(null);

  const handleVideoClick = (video: VideoResponse) => {
    setSelectedVideo(video);
  };

  const closeModal = () => {
    setSelectedVideo(null);
  };

  return (
    <>
      <GlassCard className="p-6">
        <h4 className="font-semibold text-white mb-4 flex items-center">
          <Play className="w-5 h-5 mr-2" />
          Source Videos ({videos.length})
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {videos.map((video, index) => (
            <motion.div
              key={video.video_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => handleVideoClick(video)}
              className="cursor-pointer group"
            >
              <div className="relative aspect-video bg-gray-800 rounded-lg overflow-hidden">
                <img
                  src={`http://localhost:8000/media/thumbnails/${video.video_id}.jpg`}
                  alt={video.title || 'Video thumbnail'}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = '/api/placeholder/300/200';
                  }}
                />

                {/* Play overlay */}
                <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors flex items-center justify-center">
                  <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm border border-white/30 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Play className="w-6 h-6 text-white ml-0.5" />
                  </div>
                </div>

                {/* Gradient overlay */}
                <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-black/60 to-transparent" />
              </div>

              <div className="p-3">
                <h5 className="font-medium text-white text-sm line-clamp-2 mb-2">
                  {video.title || 'Untitled Video'}
                </h5>

                <div className="flex items-center justify-between text-xs text-white/60">
                  <div className="flex items-center">
                    <MapPin className="w-3 h-3 mr-1" />
                    {video.borough}
                  </div>

                  <div className="flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {formatDistanceToNow(video.uploaded_at)}
                  </div>
                </div>

                {video.description && (
                  <p className="text-xs text-white/50 mt-2 line-clamp-2">
                    {video.description}
                  </p>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {videos.length === 0 && (
          <div className="text-center py-8 text-white/60">
            No source videos available for this query
          </div>
        )}
      </GlassCard>

      {/* Video modal */}
      {selectedVideo && (
        <VideoModal
          video={selectedVideo}
          isOpen={!!selectedVideo}
          onClose={closeModal}
        />
      )}
    </>
  );
}