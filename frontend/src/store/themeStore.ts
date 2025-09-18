import { StateCreator } from 'zustand';
import { ThemeStore } from '@/types/store';

export const createThemeSlice: StateCreator<ThemeStore> = (set, get) => ({
  // State
  theme: 'dark',
  systemTheme: 'dark',

  // Actions
  setTheme: (theme) => {
    set({ theme });
    // Apply theme to document
    if (typeof window !== 'undefined') {
      const root = window.document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(theme);
    }
  },

  toggleTheme: () => {
    const currentTheme = get().theme;
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    get().setTheme(newTheme);
  },

  setSystemTheme: (systemTheme) => {
    set({ systemTheme });
  },
});