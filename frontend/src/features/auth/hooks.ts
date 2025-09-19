import { useEffect } from 'react';
import { useAuthStore } from './store';


export function useAuthInitialization() {
  const { user, isAuthenticated, setLoading } = useAuthStore();

  useEffect(() => {
    const initAuth = async () => {
      
      if (user && isAuthenticated) {
        setLoading(false);
      } else {
        
        useAuthStore.setState({
          user: null,
          loginData: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    };

    initAuth();
  }, [user, isAuthenticated, setLoading]);
}

export function useAuth() {
  const auth = useAuthStore();

  return {
    ...auth,
    isLoggedIn: auth.isAuthenticated && !!auth.user,
  };
}

export function useRequireAuth() {
  const { isAuthenticated, isLoading, user } = useAuthStore();

  return {
    isAuthenticated,
    isLoading,
    user,
    isReady: !isLoading && (isAuthenticated ? !!user : true),
  };
}
