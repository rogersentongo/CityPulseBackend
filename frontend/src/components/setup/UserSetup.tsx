'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { User, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/store';
import { GlassCard } from '@/components/ui/GlassCard';
import { GlassInput } from '@/components/ui/GlassInput';
import { GlassButton } from '@/components/ui/GlassButton';

export function UserSetup() {
  const [userId, setUserId] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();
  const { setUserId: setStoreUserId } = useAppStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!userId.trim()) {
      setError('Please enter a user ID');
      return;
    }

    if (userId.length < 3) {
      setError('User ID must be at least 3 characters');
      return;
    }

    setStoreUserId(userId.trim());
    router.push('/setup/borough');
  };

  const suggestedUserIds = [
    'demo-user-1',
    'test-user-ai',
    'nyc-explorer',
    'video-hunter',
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="text-center space-y-3">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring' }}
          className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center"
        >
          <User className="w-10 h-10 text-white" />
        </motion.div>

        <h2 className="text-2xl font-bold text-white">
          Welcome to CityPulse
        </h2>

        <p className="text-white/70 max-w-md mx-auto">
          Enter a user ID to get started with your personalized NYC video feed experience
        </p>
      </div>

      <GlassCard className="p-6 space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <GlassInput
            label="User ID"
            placeholder="Enter your user ID (e.g., demo-user-1)"
            value={userId}
            onChange={(e) => {
              setUserId(e.target.value);
              setError('');
            }}
            error={error}
            icon={<User className="w-5 h-5" />}
          />

          <GlassButton type="submit" fullWidth>
            Continue
            <ArrowRight className="w-5 h-5 ml-2" />
          </GlassButton>
        </form>

        <div className="space-y-3">
          <p className="text-sm text-white/60 text-center">
            Quick start with suggested IDs:
          </p>

          <div className="grid grid-cols-2 gap-2">
            {suggestedUserIds.map((id) => (
              <motion.button
                key={id}
                whileTap={{ scale: 0.95 }}
                onClick={() => setUserId(id)}
                className="p-2 text-sm bg-white/5 border border-white/10 rounded-lg text-white/80 hover:bg-white/10 transition-colors"
              >
                {id}
              </motion.button>
            ))}
          </div>
        </div>
      </GlassCard>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="text-center text-xs text-white/50"
      >
        Your user ID helps us personalize your video feed based on your likes and preferences
      </motion.div>
    </motion.div>
  );
}