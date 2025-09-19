

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthState, AuthActions, LoginPayload, RegisterPayload, User } from './types';
import { loginUser, registerUser, logoutUser } from './api';

interface AuthStore extends AuthState, AuthActions {}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      
      user: null,
      loginData: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      
      login: async (payload: LoginPayload) => {
        try {
          set({ isLoading: true, error: null });
          
          const response = await loginUser(payload);
          
          
          const user: User = {
            id: response.user_id,
            email: response.email,
            created_at: new Date().toISOString(),
            profile: {
              id: response.user_id,
              user_id: response.user_id,
              full_name: response.full_name,
              created_at: new Date().toISOString(),
            }
          };
          
          set({
            user,
            loginData: response,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: unknown) {
          const errorMessage = error instanceof Error 
            ? error.message 
            : (error as { response?: { data?: { message?: string } } })?.response?.data?.message || 'Đăng nhập thất bại';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      register: async (payload: RegisterPayload) => {
        try {
          set({ isLoading: true, error: null });
          
          const response = await registerUser(payload);
          
          
          const user: User = {
            id: response.id,
            email: response.email,
            phone: response.phone,
            created_at: response.created_at,
            updated_at: response.updated_at,
            profile: response.profile || {
              id: response.id,
              user_id: response.id,
              full_name: payload.profile.full_name,
              created_at: response.created_at,
            },
            emergency_contacts: response.emergency_contacts,
          };
          
          set({
            user,
            loginData: null,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: unknown) {
          const errorMessage = error instanceof Error 
            ? error.message 
            : (error as { response?: { data?: { message?: string } } })?.response?.data?.message || 'Đăng ký thất bại';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await logoutUser();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          // Clear auth state
          set({
            user: null,
            loginData: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
          
          // Clear chatbot data when logging out
          // Import is done dynamically to avoid circular dependency
          const { useChatbotStore } = await import('../chatbot/store');
          useChatbotStore.getState().clearUserData();
          
          // Clear memory map data when logging out
          const { useMemoryMapStore } = await import('../memory-map/store');
          useMemoryMapStore.getState().clearAllMemories();
        }
      },

      clearError: () => set({ error: null }),
      
      setLoading: (loading: boolean) => set({ isLoading: loading }),

      updateUser: (user: User) => set({ user }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        loginData: state.loginData,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
