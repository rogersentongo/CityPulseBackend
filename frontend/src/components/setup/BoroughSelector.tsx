'use client';

import { motion } from 'framer-motion';
import { MapPin, ArrowLeft, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/store';
import { GlassCard } from '@/components/ui/GlassCard';
import { GlassButton } from '@/components/ui/GlassButton';
import { Borough, VALID_BOROUGHS, BOROUGH_COLORS } from '@/types/api';

export function BoroughSelector() {
  const router = useRouter();
  const { selectedBorough, setBorough, completeSetup } = useAppStore();

  const handleBoroughSelect = (borough: Borough) => {
    setBorough(borough);
  };

  const handleContinue = () => {
    if (selectedBorough) {
      completeSetup();
      router.push('/feed');
    }
  };

  const handleBack = () => {
    router.push('/');
  };

  const boroughDescriptions = {
    Manhattan: 'The heart of NYC - Times Square, Central Park, and endless energy',
    Brooklyn: 'Creative hub with amazing food, art, and waterfront views',
    Queens: 'Most diverse borough with authentic global cuisines',
    Bronx: 'Home of Yankees, vibrant culture, and amazing street art',
    'Staten Island': 'Peaceful suburban vibes with beautiful parks and ferries',
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="space-y-6"
    >
      <div className="text-center space-y-3">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring' }}
          className="w-20 h-20 mx-auto bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center"
        >
          <MapPin className="w-10 h-10 text-white" />
        </motion.div>

        <h2 className="text-2xl font-bold text-white">
          Choose Your Borough
        </h2>

        <p className="text-white/70 max-w-md mx-auto">
          Select a NYC borough to discover what's happening in that area
        </p>
      </div>

      <div className="space-y-3">
        {VALID_BOROUGHS.map((borough, index) => (
          <motion.div
            key={borough}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <GlassCard
              hoverable
              onClick={() => handleBoroughSelect(borough)}
              className={`p-4 cursor-pointer transition-all duration-300 ${
                selectedBorough === borough
                  ? 'ring-2 ring-white/30 bg-white/20'
                  : ''
              }`}
            >
              <div className="flex items-center space-x-4">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: BOROUGH_COLORS[borough] }}
                />

                <div className="flex-1">
                  <h3 className="font-semibold text-white">{borough}</h3>
                  <p className="text-sm text-white/70">
                    {boroughDescriptions[borough]}
                  </p>
                </div>

                {selectedBorough === borough && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-6 h-6 bg-white rounded-full flex items-center justify-center"
                  >
                    <div className="w-2 h-2 bg-black rounded-full" />
                  </motion.div>
                )}
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      <div className="flex space-x-3">
        <GlassButton variant="ghost" onClick={handleBack}>
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back
        </GlassButton>

        <GlassButton
          onClick={handleContinue}
          disabled={!selectedBorough}
          className="flex-1"
        >
          Start Exploring
          <ArrowRight className="w-5 h-5 ml-2" />
        </GlassButton>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="text-center text-xs text-white/50"
      >
        You can change your borough anytime from the feed page
      </motion.div>
    </motion.div>
  );
}