'use client';

import { motion } from 'framer-motion';
import { MessageSquare, TrendingUp, MapPin, Calendar } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';

interface QuerySuggestionsProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
}

const defaultSuggestions = [
  {
    category: 'Trending',
    icon: TrendingUp,
    color: 'from-red-500 to-pink-500',
    questions: [
      "What's trending in Manhattan today?",
      "Show me popular videos from Brooklyn",
      "What are people sharing in Queens?",
    ]
  },
  {
    category: 'Location',
    icon: MapPin,
    color: 'from-blue-500 to-cyan-500',
    questions: [
      "What's happening in Central Park?",
      "Show me videos from Times Square",
      "What's new in the Bronx?",
    ]
  },
  {
    category: 'Events',
    icon: Calendar,
    color: 'from-purple-500 to-indigo-500',
    questions: [
      "Are there any events this weekend?",
      "What festivals are happening?",
      "Show me street performances",
    ]
  },
  {
    category: 'General',
    icon: MessageSquare,
    color: 'from-green-500 to-emerald-500',
    questions: [
      "What makes each borough unique?",
      "Best food spots in NYC",
      "Hidden gems in Staten Island",
    ]
  },
];

export function QuerySuggestions({ suggestions, onSelect }: QuerySuggestionsProps) {
  const displaySuggestions = suggestions.length > 0 ?
    [{ category: 'Suggestions', icon: MessageSquare, color: 'from-gray-500 to-gray-600', questions: suggestions }] :
    defaultSuggestions;

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h3 className="text-lg font-semibold text-white mb-2">
          Try asking about...
        </h3>
        <p className="text-white/60 text-sm">
          Click on any suggestion to get started
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {displaySuggestions.map((category, categoryIndex) => (
          <motion.div
            key={category.category}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: categoryIndex * 0.1 }}
          >
            <GlassCard className="p-6 h-full">
              <div className="flex items-center space-x-3 mb-4">
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-r ${category.color} flex items-center justify-center`}>
                  <category.icon className="w-5 h-5 text-white" />
                </div>
                <h4 className="font-semibold text-white">{category.category}</h4>
              </div>

              <div className="space-y-2">
                {category.questions.map((question, questionIndex) => (
                  <motion.button
                    key={questionIndex}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => onSelect(question)}
                    className="w-full p-3 text-left text-sm bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/80 transition-colors"
                  >
                    {question}
                  </motion.button>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>
    </div>
  );
}