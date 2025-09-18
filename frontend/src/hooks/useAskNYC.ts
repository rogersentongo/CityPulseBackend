import { useState, useCallback } from 'react';
import { useAppStore } from '@/store';
import { apiClient } from '@/lib/api';
import { AskResponse } from '@/types/api';

export function useAskNYC() {
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const { selectedBorough } = useAppStore();

  // Default suggestions based on current context
  const suggestions = [
    "What's happening in Manhattan today?",
    "Show me popular videos from Brooklyn",
    "What events are trending in Queens?",
    "What's new in the Bronx this week?",
    "Tell me about Staten Island activities",
    "What's the vibe in Central Park?",
    "Show me street art from Brooklyn",
    "What food trends are popular?",
  ];

  const askQuestion = useCallback(async (query: string, borough?: string) => {
    if (!query.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      const response = await apiClient.askNYC({
        query: query.trim(),
        borough: borough || selectedBorough || undefined,
        window_hours: 24, // Default to last 24 hours
      });

      setResponse(response);
    } catch (err) {
      console.error('Ask NYC error:', err);
      setError(err instanceof Error ? err.message : 'Failed to get response');
    } finally {
      setIsLoading(false);
    }
  }, [selectedBorough]);

  const clearResponse = useCallback(() => {
    setResponse(null);
    setError('');
  }, []);

  return {
    askQuestion,
    response,
    isLoading,
    error,
    suggestions,
    clearResponse,
  };
}