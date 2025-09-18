'use client';

import { motion } from 'framer-motion';
import { Home, Upload, MessageCircle, User } from 'lucide-react';
import { useRouter, usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const navItems = [
  { icon: Home, label: 'Feed', path: '/feed' },
  { icon: Upload, label: 'Upload', path: '/upload' },
  { icon: MessageCircle, label: 'Ask NYC', path: '/ask' },
  { icon: User, label: 'Profile', path: '/profile' },
];

export function MobileNavigation() {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <motion.nav
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed bottom-0 left-0 right-0 z-50 p-4 pb-safe"
    >
      <div className="backdrop-blur-glass bg-glass-dark border border-glass-border rounded-2xl p-2 mx-auto max-w-md">
        <div className="flex items-center justify-around">
          {navItems.map(({ icon: Icon, label, path }) => {
            const isActive = pathname === path;

            return (
              <motion.button
                key={path}
                whileTap={{ scale: 0.9 }}
                onClick={() => router.push(path)}
                className={cn(
                  'flex flex-col items-center p-3 rounded-xl transition-all duration-300',
                  'min-w-touch min-h-touch',
                  'focus:outline-none focus:ring-2 focus:ring-white/20',
                  isActive
                    ? 'bg-white/20 text-white'
                    : 'text-white/60 hover:bg-white/10 hover:text-white/80'
                )}
              >
                <motion.div
                  animate={{ scale: isActive ? 1.1 : 1 }}
                  transition={{ duration: 0.2 }}
                >
                  <Icon className="w-6 h-6 mb-1" />
                </motion.div>
                <span className="text-xs font-medium">{label}</span>

                {/* Active indicator */}
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-white rounded-full"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
              </motion.button>
            );
          })}
        </div>
      </div>
    </motion.nav>
  );
}