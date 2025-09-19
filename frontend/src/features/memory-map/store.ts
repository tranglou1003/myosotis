import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { MemoryLocation } from '../../types/google-maps';

interface MemoryMapState {
  savedLocations: MemoryLocation[];
  currentMapCenter: { lat: number; lng: number };
}

interface MemoryMapActions {
  addMemoryLocation: (location: MemoryLocation) => void;
  removeMemoryLocation: (id: string) => void;
  clearAllMemories: () => void;
  updateMapCenter: (center: { lat: number; lng: number }) => void;
}

interface MemoryMapStore extends MemoryMapState, MemoryMapActions {}

export const useMemoryMapStore = create<MemoryMapStore>()(
  persist(
    (set, get) => ({
      
      savedLocations: [],
      currentMapCenter: {
        lat: 21.028511, 
        lng: 105.804817,
      },

      
      addMemoryLocation: (location: MemoryLocation) => {
        const { savedLocations } = get();
        set({
          savedLocations: [...savedLocations, location],
        });
      },

      removeMemoryLocation: (id: string) => {
        const { savedLocations } = get();
        set({
          savedLocations: savedLocations.filter(location => location.id !== id),
        });
      },

      clearAllMemories: () => {
        set({
          savedLocations: [],
          currentMapCenter: {
            lat: 21.028511,
            lng: 105.804817,
          },
        });
      },

      updateMapCenter: (center: { lat: number; lng: number }) => {
        set({ currentMapCenter: center });
      },
    }),
    {
      name: 'memory-map-storage',
      partialize: (state) => ({
        savedLocations: state.savedLocations,
        currentMapCenter: state.currentMapCenter,
      }),
    }
  )
);
