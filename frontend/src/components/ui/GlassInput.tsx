'use client';

import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface GlassInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

export const GlassInput = forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, label, error, icon, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="block text-sm font-medium text-white/80">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/60">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            className={cn(
              'w-full backdrop-blur-glass bg-glass-dark border border-glass-border',
              'rounded-xl px-4 py-3 text-white placeholder-white/60',
              'transition-all duration-300',
              'focus:outline-none focus:ring-2 focus:ring-white/30 focus:border-white/40',
              'hover:border-white/30',
              'min-h-touch', // Mobile touch target
              icon && 'pl-12',
              error && 'border-red-500/50 focus:ring-red-500/30',
              className
            )}
            {...props}
          />
        </div>
        {error && (
          <p className="text-sm text-red-400">{error}</p>
        )}
      </div>
    );
  }
);

GlassInput.displayName = 'GlassInput';