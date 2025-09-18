'use client';

import { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { Header } from './Header';
import { MobileNavigation } from './MobileNavigation';
import { cn } from '@/lib/utils';

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();

  // Don't show layout on landing page
  if (pathname === '/') {
    return <>{children}</>;
  }

  const pageConfig = {
    '/feed': { title: undefined, showBorough: true },
    '/upload': { title: 'Upload Video', showBorough: false },
    '/ask': { title: 'Ask NYC', showBorough: true },
    '/profile': { title: 'Profile', showBorough: false },
  };

  const config = pageConfig[pathname as keyof typeof pageConfig] || {
    title: undefined,
    showBorough: false,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Background effects */}
      <div className="fixed inset-0 opacity-10">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20" />
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
        </div>
      </div>

      {/* Header */}
      <Header
        title={config.title}
        showBorough={config.showBorough}
        showSettings={pathname === '/profile'}
      />

      {/* Main content */}
      <motion.main
        key={pathname}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className={cn(
          'relative z-10 pt-20 pb-24',
          'min-h-screen'
        )}
      >
        {children}
      </motion.main>

      {/* Mobile Navigation */}
      <MobileNavigation />
    </div>
  );
}