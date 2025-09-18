'use client';

import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'light' | 'dark';
  hoverable?: boolean;
  onClick?: () => void;
}

export function GlassCard({
  children,
  className,
  variant = 'default',
  hoverable = false,
  onClick
}: GlassCardProps) {
  const variants = {
    default: 'bg-glass-dark border-glass-border',
    light: 'bg-glass-light border-glass-border-light',
    dark: 'bg-black/30 border-white/10',
  };

  const Component = onClick ? motion.button : motion.div;

  return (
    <Component
      onClick={onClick}
      whileHover={hoverable ? { scale: 1.02, y: -2 } : {}}
      whileTap={onClick ? { scale: 0.98 } : {}}
      className={cn(
        'backdrop-blur-glass border rounded-glass transition-all duration-300',
        'shadow-lg shadow-black/10',
        variants[variant],
        hoverable && 'hover:shadow-xl hover:shadow-white/5 cursor-pointer',
        onClick && 'focus:outline-none focus:ring-2 focus:ring-white/20',
        className
      )}
    >
      {children}
    </Component>
  );
}