'use client';

import { ButtonHTMLAttributes, ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface GlassButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  fullWidth?: boolean;
}

export function GlassButton({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  fullWidth = false,
  className,
  disabled,
  ...props
}: GlassButtonProps) {
  const variants = {
    primary: 'bg-nyc-blue/20 border-nyc-blue/30 text-white hover:bg-nyc-blue/30 focus:ring-nyc-blue/50',
    secondary: 'bg-glass-dark border-glass-border text-white hover:bg-white/20 focus:ring-white/30',
    ghost: 'bg-transparent border-transparent text-white hover:bg-white/10 focus:ring-white/20',
    danger: 'bg-red-500/20 border-red-500/30 text-white hover:bg-red-500/30 focus:ring-red-500/50',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      whileHover={{ scale: 1.02 }}
      className={cn(
        'backdrop-blur-glass border rounded-xl font-medium transition-all duration-300',
        'min-h-touch min-w-touch', // Mobile touch targets
        'focus:outline-none focus:ring-2 focus:ring-offset-0',
        'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100',
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        (isLoading || disabled) && 'pointer-events-none',
        className
      )}
      disabled={isLoading || disabled}
      {...props}
    >
      {isLoading ? (
        <div className="flex items-center justify-center">
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
          Loading...
        </div>
      ) : (
        children
      )}
    </motion.button>
  );
}