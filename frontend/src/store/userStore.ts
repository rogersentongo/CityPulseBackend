import { StateCreator } from 'zustand';
import { UserStore } from '@/types/store';

export const createUserSlice: StateCreator<UserStore> = (set) => ({
  // State
  userId: null,
  selectedBorough: null,
  isSetupComplete: false,

  // Actions
  setUserId: (userId) => {
    set({ userId });
  },

  setBorough: (borough) => {
    set({ selectedBorough: borough });
  },

  completeSetup: () => {
    set({ isSetupComplete: true });
  },

  resetUser: () => {
    set({
      userId: null,
      selectedBorough: null,
      isSetupComplete: false,
    });
  },
});