# CityPulse Frontend Implementation Plan

## Project Overview
Comprehensive implementation plan for building a mobile-first React/Next.js frontend with glass morphism design, dark/light mode, and seamless integration with CityPulse backend APIs.

---

## 📁 Project Structure

```
CityPulseBackend/
├── frontend/                           # Next.js 14 Application
│   ├── public/
│   │   ├── icons/                      # App icons and favicons
│   │   ├── images/                     # Static images and NYC borough assets
│   │   └── manifest.json               # PWA manifest
│   │
│   ├── src/
│   │   ├── app/                        # App Router Structure
│   │   │   ├── globals.css             # Global styles with Tailwind
│   │   │   ├── layout.tsx              # Root layout with providers
│   │   │   ├── page.tsx                # Landing/Welcome page
│   │   │   ├── feed/
│   │   │   │   └── page.tsx            # Main video feed
│   │   │   ├── upload/
│   │   │   │   └── page.tsx            # Single-page upload flow
│   │   │   ├── ask/
│   │   │   │   └── page.tsx            # Ask NYC Q&A interface
│   │   │   ├── profile/
│   │   │   │   └── page.tsx            # User taste profile
│   │   │   └── api/                    # API proxy routes
│   │   │       └── [...proxy].ts       # Proxy to backend
│   │   │
│   │   ├── components/                 # React Components
│   │   │   ├── ui/                     # Base UI Components
│   │   │   │   ├── GlassButton.tsx     # Glass-styled button
│   │   │   │   ├── GlassCard.tsx       # Glass morphism card
│   │   │   │   ├── GlassInput.tsx      # Glass input field
│   │   │   │   ├── GlassModal.tsx      # Glass modal overlay
│   │   │   │   ├── LoadingSpinner.tsx  # Glass loading spinner
│   │   │   │   └── ThemeToggle.tsx     # Dark/light mode toggle
│   │   │   │
│   │   │   ├── layout/                 # Layout Components
│   │   │   │   ├── AppLayout.tsx       # Main app structure
│   │   │   │   ├── MobileNavigation.tsx # Bottom tab navigation
│   │   │   │   ├── Header.tsx          # App header
│   │   │   │   └── RubberBand.tsx      # Elastic scroll effects
│   │   │   │
│   │   │   ├── video/                  # Video Components
│   │   │   │   ├── VideoPlayer.tsx     # Custom glass video player
│   │   │   │   ├── VideoCard.tsx       # Feed video cards
│   │   │   │   ├── VideoModal.tsx      # Full-screen video modal
│   │   │   │   └── VideoControls.tsx   # Glass player controls
│   │   │   │
│   │   │   ├── feed/                   # Feed Components
│   │   │   │   ├── VideoFeed.tsx       # Main feed container
│   │   │   │   ├── FeedFilters.tsx     # Feed filtering options
│   │   │   │   ├── InfiniteScroll.tsx  # Infinite scroll logic
│   │   │   │   └── PullToRefresh.tsx   # Pull-to-refresh component
│   │   │   │
│   │   │   ├── interactions/           # User Interaction Components
│   │   │   │   ├── GlassLikeButton.tsx # Animated like button
│   │   │   │   ├── LikeAnimation.tsx   # Heart animation effects
│   │   │   │   └── HapticFeedback.tsx  # Mobile haptic feedback
│   │   │   │
│   │   │   ├── upload/                 # Upload Components
│   │   │   │   ├── UploadForm.tsx      # Single-page upload form
│   │   │   │   ├── GlassDropzone.tsx   # Drag & drop area
│   │   │   │   ├── FilePreview.tsx     # Video preview component
│   │   │   │   ├── UploadProgress.tsx  # Progress indicators
│   │   │   │   └── BoroughSelector.tsx # Borough selection
│   │   │   │
│   │   │   ├── ask/                    # Ask NYC Components
│   │   │   │   ├── AskInterface.tsx    # Main Q&A interface
│   │   │   │   ├── GlassSearchBar.tsx  # Glass search input
│   │   │   │   ├── QuerySuggestions.tsx # Contextual suggestions
│   │   │   │   ├── ResponseCard.tsx    # AI response display
│   │   │   │   └── SourceVideos.tsx    # Source attribution
│   │   │   │
│   │   │   └── profile/                # Profile Components
│   │   │       ├── TasteProfile.tsx    # User taste dashboard
│   │   │       ├── TasteStats.tsx      # Statistics display
│   │   │       └── SettingsPanel.tsx   # User preferences
│   │   │
│   │   ├── lib/                        # Utility Libraries
│   │   │   ├── api.ts                  # Type-safe API client
│   │   │   ├── constants.ts            # App constants
│   │   │   ├── utils.ts                # Helper functions
│   │   │   ├── animations.ts           # Framer Motion presets
│   │   │   └── glass-effects.ts        # Glass morphism utilities
│   │   │
│   │   ├── hooks/                      # Custom React Hooks
│   │   │   ├── useAPI.ts               # API interaction hooks
│   │   │   ├── useFeed.ts              # Feed management
│   │   │   ├── useUser.ts              # User state management
│   │   │   ├── useUpload.ts            # Upload functionality
│   │   │   ├── useTheme.tsx            # Theme management
│   │   │   ├── useRubberBand.ts        # Elastic scroll effects
│   │   │   └── useHaptic.ts            # Mobile haptic feedback
│   │   │
│   │   ├── store/                      # Zustand State Management
│   │   │   ├── index.ts                # Store configuration
│   │   │   ├── userStore.ts            # User state slice
│   │   │   ├── feedStore.ts            # Feed state slice
│   │   │   ├── themeStore.ts           # Theme state slice
│   │   │   └── uploadStore.ts          # Upload state slice
│   │   │
│   │   ├── types/                      # TypeScript Definitions
│   │   │   ├── api.ts                  # API response types
│   │   │   ├── components.ts           # Component prop types
│   │   │   └── store.ts                # Store state types
│   │   │
│   │   └── styles/                     # Styling
│   │       ├── glass-morphism.css      # Glass effect styles
│   │       └── animations.css          # Custom animations
│   │
│   ├── package.json                    # Dependencies
│   ├── next.config.js                  # Next.js configuration
│   ├── tailwind.config.js              # Tailwind CSS config
│   ├── tsconfig.json                   # TypeScript config
│   └── README.md                       # Frontend documentation
│
└── app/                                # Existing FastAPI backend
```

---

## 🚀 Implementation Phases

### Phase 1: Project Foundation (Day 1 - 2 hours)

#### 1.1 Project Setup
```bash
# Navigate to project root
cd /Users/rogersentongo/Dev/CityPulseBackend

# Create Next.js application
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir

# Install additional dependencies
cd frontend
npm install zustand framer-motion lucide-react react-hook-form @hookform/resolvers/zod zod swr react-hot-toast

# Install dev dependencies
npm install -D @types/react @types/node
```

#### 1.2 Basic Configuration Files

**next.config.js**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
    ];
  },
  images: {
    domains: ['localhost'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/media/**',
      },
    ],
  },
};

module.exports = nextConfig;
```

**tailwind.config.js**
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        glass: {
          light: 'rgba(255, 255, 255, 0.1)',
          dark: 'rgba(0, 0, 0, 0.3)',
          border: 'rgba(255, 255, 255, 0.2)',
        },
        nyc: {
          blue: '#1E40AF',
          orange: '#EA580C',
          green: '#059669',
        },
      },
      backdropBlur: {
        'glass': '20px',
      },
      animation: {
        'rubber-band': 'rubberBand 1s ease-out',
        'heart-beat': 'heartBeat 0.5s ease-out',
      },
    },
  },
  plugins: [],
};
```

#### 1.3 TypeScript Configuration
```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/hooks/*": ["./src/hooks/*"],
      "@/store/*": ["./src/store/*"],
      "@/types/*": ["./src/types/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

### Phase 2: Core State Management & API (Day 1-2 - 3 hours)

#### 2.1 Zustand Store Setup

**store/index.ts**
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserStore, createUserSlice } from './userStore';
import { FeedStore, createFeedSlice } from './feedStore';
import { ThemeStore, createThemeSlice } from './themeStore';
import { UploadStore, createUploadSlice } from './uploadStore';

export type AppStore = UserStore & FeedStore & ThemeStore & UploadStore;

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      ...createUserSlice(set, get),
      ...createFeedSlice(set, get),
      ...createThemeSlice(set, get),
      ...createUploadSlice(set, get),
    }),
    {
      name: 'citypulse-storage',
      partialize: (state) => ({
        userId: state.userId,
        selectedBorough: state.selectedBorough,
        theme: state.theme,
      }),
    }
  )
);
```

**store/userStore.ts**
```typescript
import { StateCreator } from 'zustand';
import { Borough } from '@/types/api';

export interface UserStore {
  // State
  userId: string | null;
  selectedBorough: Borough | null;
  isSetupComplete: boolean;

  // Actions
  setUserId: (userId: string) => void;
  setBorough: (borough: Borough) => void;
  completeSetup: () => void;
  resetUser: () => void;
}

export const createUserSlice: StateCreator<UserStore> = (set) => ({
  userId: null,
  selectedBorough: null,
  isSetupComplete: false,

  setUserId: (userId) => set({ userId }),
  setBorough: (borough) => set({ selectedBorough: borough }),
  completeSetup: () => set({ isSetupComplete: true }),
  resetUser: () => set({
    userId: null,
    selectedBorough: null,
    isSetupComplete: false
  }),
});
```

#### 2.2 API Client Setup

**lib/api.ts**
```typescript
import {
  FeedResponse,
  UploadResponse,
  LikeResponse,
  AskResponse
} from '@/types/api';

const API_BASE_URL = process.env.NODE_ENV === 'development'
  ? 'http://localhost:8000/api/v1'
  : '/api/v1';

class APIClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // Feed endpoints
  async getFeed(params: {
    borough: string;
    user_id: string;
    limit?: number;
    skip?: number;
  }): Promise<FeedResponse> {
    const searchParams = new URLSearchParams({
      borough: params.borough,
      user_id: params.user_id,
      limit: String(params.limit || 20),
      skip: String(params.skip || 0),
    });

    return this.request(`/feed?${searchParams}`);
  }

  // Like endpoints
  async likeVideo(userId: string, videoId: string): Promise<LikeResponse> {
    return this.request('/like', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, video_id: videoId }),
    });
  }

  // Upload endpoint
  async uploadVideo(formData: FormData): Promise<UploadResponse> {
    return fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    }).then(res => res.json());
  }

  // Ask NYC endpoint
  async askNYC(params: {
    query: string;
    borough?: string;
    window_hours?: number;
  }): Promise<AskResponse> {
    return this.request('/ask', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }
}

export const apiClient = new APIClient();
```

---

### Phase 3: Glass Morphism UI Components (Day 2 - 4 hours)

#### 3.1 Base Glass Components

**components/ui/GlassCard.tsx**
```typescript
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  variant?: 'light' | 'dark';
  hoverable?: boolean;
}

export function GlassCard({
  children,
  className,
  variant = 'dark',
  hoverable = false
}: GlassCardProps) {
  return (
    <div
      className={cn(
        'backdrop-blur-glass border rounded-2xl transition-all duration-300',
        variant === 'dark'
          ? 'bg-glass-dark border-glass-border'
          : 'bg-glass-light border-white/30',
        hoverable && 'hover:scale-[1.02] hover:shadow-xl hover:shadow-white/10',
        className
      )}
    >
      {children}
    </div>
  );
}
```

**components/ui/GlassButton.tsx**
```typescript
import { ButtonHTMLAttributes, ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface GlassButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export function GlassButton({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  className,
  ...props
}: GlassButtonProps) {
  const variants = {
    primary: 'bg-glass-dark border-glass-border text-white hover:bg-white/20',
    secondary: 'bg-glass-light border-white/30 text-gray-900 hover:bg-white/30',
    ghost: 'bg-transparent border-transparent text-white hover:bg-white/10',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      whileHover={{ scale: 1.05 }}
      className={cn(
        'backdrop-blur-glass border rounded-xl font-medium transition-all duration-300',
        'min-h-[44px] min-w-[44px]', // Mobile touch targets
        variants[variant],
        sizes[size],
        isLoading && 'opacity-50 cursor-not-allowed',
        className
      )}
      disabled={isLoading}
      {...props}
    >
      {isLoading ? (
        <div className="flex items-center justify-center">
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        </div>
      ) : (
        children
      )}
    </motion.button>
  );
}
```

#### 3.2 Theme Toggle Component

**components/ui/ThemeToggle.tsx**
```typescript
import { motion } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import { useAppStore } from '@/store';

export function ThemeToggle() {
  const { theme, toggleTheme } = useAppStore();

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={toggleTheme}
      className="relative p-3 rounded-xl backdrop-blur-glass bg-glass-dark border border-glass-border"
    >
      <motion.div
        initial={false}
        animate={{ rotate: theme === 'dark' ? 0 : 180 }}
        transition={{ duration: 0.3 }}
      >
        {theme === 'dark' ? (
          <Moon className="w-6 h-6 text-white" />
        ) : (
          <Sun className="w-6 h-6 text-yellow-400" />
        )}
      </motion.div>
    </motion.button>
  );
}
```

---

### Phase 4: Video Feed with Rubber Band Effects (Day 3 - 5 hours)

#### 4.1 Rubber Band Hook

**hooks/useRubberBand.ts**
```typescript
import { useState, useEffect, useCallback } from 'react';

export function useRubberBand() {
  const [isAtTop, setIsAtTop] = useState(false);
  const [isAtBottom, setIsAtBottom] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleScroll = useCallback(() => {
    const scrollTop = window.scrollY;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;

    setIsAtTop(scrollTop === 0);
    setIsAtBottom(scrollTop + windowHeight >= documentHeight - 10);
  }, []);

  const handleTouchStart = useCallback((e: TouchEvent) => {
    if (isAtTop) {
      const startY = e.touches[0].clientY;

      const handleTouchMove = (moveEvent: TouchEvent) => {
        const currentY = moveEvent.touches[0].clientY;
        const distance = Math.max(0, currentY - startY);
        setPullDistance(Math.min(distance / 3, 100)); // Damping
      };

      const handleTouchEnd = () => {
        if (pullDistance > 50) {
          setIsRefreshing(true);
          // Trigger refresh
        }
        setPullDistance(0);
        document.removeEventListener('touchmove', handleTouchMove);
        document.removeEventListener('touchend', handleTouchEnd);
      };

      document.addEventListener('touchmove', handleTouchMove);
      document.addEventListener('touchend', handleTouchEnd);
    }
  }, [isAtTop, pullDistance]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    document.addEventListener('touchstart', handleTouchStart);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      document.removeEventListener('touchstart', handleTouchStart);
    };
  }, [handleScroll, handleTouchStart]);

  return {
    isAtTop,
    isAtBottom,
    pullDistance,
    isRefreshing,
    setIsRefreshing,
  };
}
```

#### 4.2 Video Feed Component

**components/feed/VideoFeed.tsx**
```typescript
import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { VideoCard } from './VideoCard';
import { PullToRefresh } from './PullToRefresh';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { useAppStore } from '@/store';
import { useFeed } from '@/hooks/useFeed';
import { useRubberBand } from '@/hooks/useRubberBand';

export function VideoFeed() {
  const { userId, selectedBorough } = useAppStore();
  const { videos, isLoading, hasMore, loadMore, refresh } = useFeed();
  const { isAtTop, isAtBottom, pullDistance, isRefreshing, setIsRefreshing } = useRubberBand();

  useEffect(() => {
    if (isRefreshing) {
      refresh().finally(() => setIsRefreshing(false));
    }
  }, [isRefreshing, refresh, setIsRefreshing]);

  return (
    <div className="relative min-h-screen">
      {/* Pull to refresh indicator */}
      <PullToRefresh pullDistance={pullDistance} isRefreshing={isRefreshing} />

      {/* Video feed */}
      <motion.div
        style={{ paddingTop: `${pullDistance}px` }}
        className="px-4 py-6 space-y-6"
      >
        <AnimatePresence>
          {videos.map((video, index) => (
            <motion.div
              key={video.video_id}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ delay: index * 0.1 }}
            >
              <VideoCard video={video} />
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading more indicator */}
        {isLoading && (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        )}

        {/* Bottom rubber band effect */}
        {isAtBottom && !hasMore && (
          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 0.5, repeat: Infinity }}
            className="text-center py-8 text-white/60"
          >
            You've reached the end! 🎬
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
```

---

### Phase 5: Upload & Ask NYC Features (Day 4 - 4 hours)

#### 5.1 Single Page Upload

**app/upload/page.tsx**
```typescript
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { GlassCard } from '@/components/ui/GlassCard';
import { GlassDropzone } from '@/components/upload/GlassDropzone';
import { UploadProgress } from '@/components/upload/UploadProgress';
import { BoroughSelector } from '@/components/upload/BoroughSelector';
import { useAppStore } from '@/store';
import { useUpload } from '@/hooks/useUpload';

export default function UploadPage() {
  const { userId, selectedBorough } = useAppStore();
  const {
    uploadFile,
    uploadProgress,
    isUploading,
    uploadResult
  } = useUpload();

  return (
    <div className="min-h-screen p-4 pt-20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl mx-auto space-y-6"
      >
        <GlassCard className="p-6">
          <h1 className="text-2xl font-bold text-white mb-6">
            Share Your NYC Moment
          </h1>

          {!isUploading ? (
            <div className="space-y-6">
              <GlassDropzone onFileSelect={uploadFile} />
              <BoroughSelector />
            </div>
          ) : (
            <UploadProgress
              progress={uploadProgress}
              result={uploadResult}
            />
          )}
        </GlassCard>
      </motion.div>
    </div>
  );
}
```

#### 5.2 Ask NYC Interface

**components/ask/AskInterface.tsx**
```typescript
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Sparkles } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { GlassButton } from '@/components/ui/GlassButton';
import { QuerySuggestions } from './QuerySuggestions';
import { ResponseCard } from './ResponseCard';
import { useAskNYC } from '@/hooks/useAskNYC';

export function AskInterface() {
  const [query, setQuery] = useState('');
  const { askQuestion, response, isLoading, suggestions } = useAskNYC();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      await askQuestion(query);
    }
  };

  return (
    <div className="space-y-6">
      <GlassCard className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about what's happening in NYC..."
              className="w-full p-4 pl-12 rounded-xl backdrop-blur-glass bg-glass-dark border border-glass-border text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30"
            />
            <Search className="absolute left-4 top-4 w-5 h-5 text-white/60" />
          </div>

          <GlassButton
            type="submit"
            disabled={!query.trim() || isLoading}
            isLoading={isLoading}
            className="w-full"
          >
            <Sparkles className="w-5 h-5 mr-2" />
            Ask NYC
          </GlassButton>
        </form>
      </GlassCard>

      <QuerySuggestions
        suggestions={suggestions}
        onSelect={setQuery}
      />

      {response && (
        <ResponseCard response={response} />
      )}
    </div>
  );
}
```

---

### Phase 6: Mobile Navigation & Polish (Day 5 - 3 hours)

#### 6.1 Mobile Navigation

**components/layout/MobileNavigation.tsx**
```typescript
import { motion } from 'framer-motion';
import { Home, Upload, MessageCircle, User } from 'lucide-react';
import { useRouter, usePathname } from 'next/navigation';

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
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      className="fixed bottom-0 left-0 right-0 z-50 p-4"
    >
      <div className="backdrop-blur-glass bg-glass-dark border border-glass-border rounded-2xl p-2">
        <div className="flex items-center justify-around">
          {navItems.map(({ icon: Icon, label, path }) => {
            const isActive = pathname === path;

            return (
              <motion.button
                key={path}
                whileTap={{ scale: 0.9 }}
                onClick={() => router.push(path)}
                className={`flex flex-col items-center p-3 rounded-xl transition-all duration-300 min-w-[60px] ${
                  isActive ? 'bg-white/20' : 'hover:bg-white/10'
                }`}
              >
                <Icon
                  className={`w-6 h-6 mb-1 ${
                    isActive ? 'text-white' : 'text-white/60'
                  }`}
                />
                <span
                  className={`text-xs ${
                    isActive ? 'text-white' : 'text-white/60'
                  }`}
                >
                  {label}
                </span>
              </motion.button>
            );
          })}
        </div>
      </div>
    </motion.nav>
  );
}
```

---

## 🎯 Development Timeline

### Week 1: Core Implementation
- **Day 1**: Project setup, state management, API client
- **Day 2**: Glass UI components, theme system
- **Day 3**: Video feed with rubber band effects
- **Day 4**: Upload flow and Ask NYC features
- **Day 5**: Mobile navigation and polish

### Week 2: Enhancement & Testing
- **Day 6-7**: Advanced features (taste profile, settings)
- **Day 8-9**: Performance optimization and testing
- **Day 10**: Final polish and deployment preparation

---

## 🔧 Development Commands

```bash
# Development setup
cd frontend
npm install
npm run dev

# Backend integration testing
npm run build
npm run start

# Code quality
npm run lint
npm run type-check
```

---

## 📱 Mobile-First Considerations

### Performance Optimizations
- Lazy load components and images
- Optimize glass effects for mobile performance
- Use Web Vitals monitoring
- Implement service worker for offline capability

### Touch Interactions
- Minimum 44px touch targets
- Haptic feedback on interactions
- Swipe gestures for navigation
- Pull-to-refresh mechanics

### Responsive Breakpoints
- Mobile: 320px - 768px (primary focus)
- Tablet: 768px - 1024px
- Desktop: 1024px+ (enhanced experience)

This comprehensive implementation plan provides a roadmap for building a premium mobile-first video platform with beautiful glass morphism design and seamless backend integration.