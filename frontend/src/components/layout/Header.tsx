'use client';

import { motion } from 'framer-motion';
import { MapPin, Settings } from 'lucide-react';
import { useAppStore } from '@/store';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { BOROUGH_COLORS } from '@/types/api';

interface HeaderProps {
  title?: string;
  showBorough?: boolean;
  showSettings?: boolean;
  onSettingsClick?: () => void;
}

export function Header({
  title,
  showBorough = true,
  showSettings = false,
  onSettingsClick
}: HeaderProps) {
  const { userId, selectedBorough } = useAppStore();

  return (
    <motion.header
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed top-0 left-0 right-0 z-40 p-4 pt-safe"
    >
      <div className="backdrop-blur-glass bg-glass-dark border border-glass-border rounded-2xl px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Left side - Title and borough */}
          <div className="flex items-center space-x-3">
            {title ? (
              <h1 className="text-xl font-bold text-white">{title}</h1>
            ) : (
              <div className="flex items-center space-x-2">
                <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  CityPulse
                </div>
                {showBorough && selectedBorough && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="flex items-center space-x-1 px-2 py-1 rounded-lg bg-white/10"
                  >
                    <MapPin
                      className="w-3 h-3"
                      style={{ color: BOROUGH_COLORS[selectedBorough] }}
                    />
                    <span className="text-xs font-medium text-white/80">
                      {selectedBorough}
                    </span>
                  </motion.div>
                )}
              </div>
            )}
          </div>

          {/* Right side - Controls */}
          <div className="flex items-center space-x-2">
            {/* User indicator */}
            {userId && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="px-2 py-1 rounded-lg bg-nyc-blue/20 border border-nyc-blue/30"
              >
                <span className="text-xs font-medium text-white/80">
                  {userId}
                </span>
              </motion.div>
            )}

            {/* Settings button */}
            {showSettings && (
              <motion.button
                whileTap={{ scale: 0.9 }}
                onClick={onSettingsClick}
                className="p-2 rounded-lg backdrop-blur-glass bg-glass-dark border border-glass-border hover:bg-white/10 transition-colors"
              >
                <Settings className="w-5 h-5 text-white/80" />
              </motion.button>
            )}

            {/* Theme toggle */}
            <ThemeToggle />
          </div>
        </div>
      </div>
    </motion.header>
  );
}