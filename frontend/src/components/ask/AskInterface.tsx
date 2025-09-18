'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Sparkles, MessageCircle } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { GlassButton } from '@/components/ui/GlassButton';
import { GlassInput } from '@/components/ui/GlassInput';
import { QuerySuggestions } from './QuerySuggestions';
import { ResponseCard } from './ResponseCard';
import { useAskNYC } from '@/hooks/useAskNYC';

export function AskInterface() {
  const [query, setQuery] = useState('');
  const { askQuestion, response, isLoading, suggestions, clearResponse } = useAskNYC();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      await askQuestion(query);
    }
  };

  const handleSuggestionSelect = (suggestion: string) => {
    setQuery(suggestion);
  };

  const handleNewQuestion = () => {
    setQuery('');
    clearResponse();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center">
          <MessageCircle className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">
          Ask NYC
        </h1>
        <p className="text-white/60">
          Get AI-powered insights about what's happening in New York City
        </p>
      </motion.div>

      {/* Search interface */}
      <GlassCard className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <GlassInput
            label="What would you like to know about NYC?"
            placeholder="e.g., What's happening in Brooklyn today?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            icon={<Search className="w-5 h-5" />}
          />

          <div className="flex space-x-3">
            <GlassButton
              type="submit"
              disabled={!query.trim() || isLoading}
              isLoading={isLoading}
              className="flex-1"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Ask NYC
            </GlassButton>

            {response && (
              <GlassButton
                type="button"
                variant="ghost"
                onClick={handleNewQuestion}
              >
                New Question
              </GlassButton>
            )}
          </div>
        </form>
      </GlassCard>

      {/* Query suggestions */}
      {!response && (
        <QuerySuggestions
          suggestions={suggestions}
          onSelect={handleSuggestionSelect}
        />
      )}

      {/* Response */}
      {response && (
        <ResponseCard response={response} />
      )}

      {/* Empty state */}
      {!response && !isLoading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-center py-12"
        >
          <div className="text-6xl mb-4">🗽</div>
          <h3 className="text-xl font-semibold text-white mb-2">
            Ask me anything about NYC
          </h3>
          <p className="text-white/60 max-w-md mx-auto">
            I can help you discover what's happening in different boroughs, find events,
            explore local trends, and much more.
          </p>
        </motion.div>
      )}
    </div>
  );
}