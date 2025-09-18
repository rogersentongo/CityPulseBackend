'use client';

import { motion } from 'framer-motion';
import { MapPin, Settings, LogOut, ChevronDown } from 'lucide-react';
import { useAppStore } from '@/store';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { BOROUGH_COLORS, Borough } from '@/types/api';
import { useState, useEffect } from 'react';

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
  const { userId, selectedBorough, resetUser, setBorough, clearFeed } = useAppStore();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showBoroughMenu, setShowBoroughMenu] = useState(false);

  const boroughs: Borough[] = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'];

  const handleLogout = () => {
    resetUser();
    setShowUserMenu(false);
  };

  const handleBoroughChange = (borough: Borough) => {
    setBorough(borough);
    clearFeed(); // Clear current feed when changing borough
    setShowBoroughMenu(false);
  };

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowUserMenu(false);
      setShowBoroughMenu(false);
    };

    if (showUserMenu || showBoroughMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showUserMenu, showBoroughMenu]);

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
                  <div className="relative">
                    <motion.button
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setShowBoroughMenu(!showBoroughMenu)}
                      className="flex items-center space-x-1 px-2 py-1 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                    >
                      <MapPin
                        className="w-3 h-3"
                        style={{ color: BOROUGH_COLORS[selectedBorough] }}
                      />
                      <span className="text-xs font-medium text-white/80">
                        {selectedBorough}
                      </span>
                      <ChevronDown className="w-3 h-3 text-white/60" />
                    </motion.button>

                    {/* Borough dropdown */}
                    {showBoroughMenu && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="absolute top-full left-0 mt-2 bg-glass-dark border border-glass-border rounded-lg overflow-hidden backdrop-blur-glass z-50"
                      >
                        {boroughs.map((borough) => (
                          <button
                            key={borough}
                            onClick={() => handleBoroughChange(borough)}
                            className={`w-full px-3 py-2 text-left text-sm hover:bg-white/10 transition-colors flex items-center space-x-2 ${
                              borough === selectedBorough ? 'bg-white/5' : ''
                            }`}
                          >
                            <MapPin
                              className="w-3 h-3"
                              style={{ color: BOROUGH_COLORS[borough] }}
                            />
                            <span className="text-white/80">{borough}</span>
                          </button>
                        ))}
                      </motion.div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right side - Controls */}
          <div className="flex items-center space-x-2">
            {/* User indicator with logout */}
            {userId && (
              <div className="relative">
                <motion.button
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="px-2 py-1 rounded-lg bg-nyc-blue/20 border border-nyc-blue/30 hover:bg-nyc-blue/30 transition-colors flex items-center space-x-1"
                >
                  <span className="text-xs font-medium text-white/80">
                    {userId}
                  </span>
                  <ChevronDown className="w-3 h-3 text-white/60" />
                </motion.button>

                {/* User menu */}
                {showUserMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute top-full right-0 mt-2 bg-glass-dark border border-glass-border rounded-lg overflow-hidden backdrop-blur-glass z-50"
                  >
                    <button
                      onClick={handleLogout}
                      className="w-full px-3 py-2 text-left text-sm hover:bg-white/10 transition-colors flex items-center space-x-2 text-red-400"
                    >
                      <LogOut className="w-3 h-3" />
                      <span>Logout</span>
                    </button>
                  </motion.div>
                )}
              </div>
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