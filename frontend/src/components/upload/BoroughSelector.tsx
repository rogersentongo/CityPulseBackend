'use client';

import { motion } from 'framer-motion';
import { MapPin } from 'lucide-react';
import { VALID_BOROUGHS, BOROUGH_COLORS, Borough } from '@/types/api';

interface BoroughSelectorProps {
  selectedBorough: Borough;
  onBoroughSelect: (borough: Borough) => void;
}

export function BoroughSelector({ selectedBorough, onBoroughSelect }: BoroughSelectorProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {VALID_BOROUGHS.map((borough, index) => (
        <motion.button
          key={borough}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
          onClick={() => onBoroughSelect(borough)}
          className={`p-4 rounded-xl border transition-all duration-300 text-left ${
            selectedBorough === borough
              ? 'bg-white/20 border-white/40 ring-2 ring-white/30'
              : 'bg-white/5 border-white/20 hover:bg-white/10'
          }`}
        >
          <div className="flex items-center space-x-3">
            <div
              className="w-4 h-4 rounded-full flex-shrink-0"
              style={{ backgroundColor: BOROUGH_COLORS[borough] }}
            />
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <MapPin className="w-4 h-4 text-white/60" />
                <span className="font-medium text-white">{borough}</span>
              </div>
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
        </motion.button>
      ))}
    </div>
  );
}