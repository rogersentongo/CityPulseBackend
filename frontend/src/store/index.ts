import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AppStore } from '@/types/store';
import { createUserSlice } from './userStore';
import { createThemeSlice } from './themeStore';
import { createFeedSlice } from './feedStore';
import { createUploadSlice } from './uploadStore';

export const useAppStore = create<AppStore>()(
  persist(
    (...a) => ({
      ...createUserSlice(...a),
      ...createThemeSlice(...a),
      ...createFeedSlice(...a),
      ...createUploadSlice(...a),
    }),
    {
      name: 'citypulse-storage',
      partialize: (state) => ({
        userId: state.userId,
        selectedBorough: state.selectedBorough,
        isSetupComplete: state.isSetupComplete,
        theme: state.theme,
      }),
    }
  )
);

// Initialize theme on store creation
if (typeof window !== 'undefined') {
  const store = useAppStore.getState();

  // Apply initial theme to document
  const root = window.document.documentElement;
  root.classList.remove('light', 'dark');
  root.classList.add(store.theme);

  // Listen for system theme changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const handleSystemThemeChange = (e: MediaQueryListEvent) => {
    store.setSystemTheme(e.matches ? 'dark' : 'light');
  };

  mediaQuery.addEventListener('change', handleSystemThemeChange);
  store.setSystemTheme(mediaQuery.matches ? 'dark' : 'light');
}