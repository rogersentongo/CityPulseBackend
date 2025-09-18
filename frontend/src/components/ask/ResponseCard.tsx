'use client';

import { motion } from 'framer-motion';
import { Bot, ExternalLink, PlayCircle } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { SourceVideos } from './SourceVideos';
import { AskResponse } from '@/types/api';

interface ResponseCardProps {
  response: AskResponse;
}

export function ResponseCard({ response }: ResponseCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* AI Response */}
      <GlassCard className="p-6">
        <div className="flex items-start space-x-4">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
            <Bot className="w-5 h-5 text-white" />
          </div>

          <div className="flex-1">
            <h3 className="font-semibold text-white mb-3">
              NYC AI Response
            </h3>

            <div className="prose prose-invert max-w-none">
              <p className="text-white/90 leading-relaxed whitespace-pre-wrap">
                {response.answer}
              </p>
            </div>

            {/* Query info */}
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="flex items-center justify-between text-sm text-white/60">
                <span>Query: "{response.query}"</span>
                {response.borough && (
                  <span>Borough: {response.borough}</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Source Videos */}
      {response.source_videos && response.source_videos.length > 0 && (
        <SourceVideos videos={response.source_videos} />
      )}

      {/* External Sources */}
      {response.sources && response.sources.length > 0 && (
        <GlassCard className="p-6">
          <h4 className="font-semibold text-white mb-4 flex items-center">
            <ExternalLink className="w-5 h-5 mr-2" />
            Additional Sources
          </h4>

          <div className="space-y-3">
            {response.sources.map((source, index) => (
              <motion.a
                key={index}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="block p-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg transition-colors group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium text-white group-hover:text-blue-300 transition-colors">
                      {source.title}
                    </h5>
                    {source.description && (
                      <p className="text-sm text-white/70 mt-1">
                        {source.description}
                      </p>
                    )}
                  </div>
                  <ExternalLink className="w-4 h-4 text-white/60 group-hover:text-blue-300 transition-colors" />
                </div>
              </motion.a>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Response Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <GlassCard className="p-4 text-center">
          <div className="text-2xl font-bold text-white">
            {response.source_videos?.length || 0}
          </div>
          <div className="text-sm text-white/60">Source Videos</div>
        </GlassCard>

        <GlassCard className="p-4 text-center">
          <div className="text-2xl font-bold text-white">
            {response.window_hours || 24}h
          </div>
          <div className="text-sm text-white/60">Time Window</div>
        </GlassCard>

        <GlassCard className="p-4 text-center">
          <div className="text-2xl font-bold text-white">
            {response.confidence_score ? Math.round(response.confidence_score * 100) : 'N/A'}%
          </div>
          <div className="text-sm text-white/60">Confidence</div>
        </GlassCard>

        <GlassCard className="p-4 text-center">
          <div className="text-2xl font-bold text-white">
            {response.borough || 'All'}
          </div>
          <div className="text-sm text-white/60">Borough</div>
        </GlassCard>
      </div>
    </motion.div>
  );
}