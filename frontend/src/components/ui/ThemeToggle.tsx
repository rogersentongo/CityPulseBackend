'use client';

import { motion } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import { useAppStore } from '@/store';

export function ThemeToggle() {
  const { theme, toggleTheme } = useAppStore();

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={toggleTheme}
      className="relative p-3 rounded-xl backdrop-blur-glass bg-glass-dark border border-glass-border hover:bg-white/10 transition-colors duration-300"
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      <motion.div
        initial={false}
        animate={{
          rotate: theme === 'dark' ? 0 : 180,
          scale: theme === 'dark' ? 1 : 0.8
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="relative"
      >
        <motion.div
          animate={{ opacity: theme === 'dark' ? 1 : 0 }}
          transition={{ duration: 0.2 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <Moon className="w-6 h-6 text-blue-200" />
        </motion.div>

        <motion.div
          animate={{ opacity: theme === 'light' ? 1 : 0 }}
          transition={{ duration: 0.2 }}
          className="flex items-center justify-center"
        >
          <Sun className="w-6 h-6 text-yellow-400" />
        </motion.div>
      </motion.div>

      {/* Glow effect */}
      <motion.div
        className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/20 to-yellow-500/20 opacity-0"
        animate={{ opacity: theme === 'light' ? 0.3 : 0 }}
        transition={{ duration: 0.3 }}
      />
    </motion.button>
  );
}