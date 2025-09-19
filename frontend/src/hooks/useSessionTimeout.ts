
import { useEffect, useRef, useCallback } from 'react';
import { useAuthStore } from '../features/auth/store';

interface UseSessionTimeoutOptions {
  timeoutMinutes?: number;
  warningMinutes?: number;
  onWarning?: () => void;
  onTimeout?: () => void;
}

export const useSessionTimeout = ({
  timeoutMinutes = 1440,
  warningMinutes = 30,
  onWarning,
  onTimeout
}: UseSessionTimeoutOptions = {}) => {
  const { user, logout } = useAuthStore();
  const warningShownRef = useRef(false);
  const timeoutRef = useRef<number | null>(null);
  const warningRef = useRef<number | null>(null);

  const resetTimers = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    if (warningRef.current) {
      clearTimeout(warningRef.current);
      warningRef.current = null;
    }
    warningShownRef.current = false;
  }, []);

  const handleTimeout = useCallback(() => {
    resetTimers();
    if (onTimeout) {
      onTimeout();
    } else {
      alert('Your session has expired for security purposes.\n\nPlease sign in again.');
      logout();
    }
  }, [onTimeout, logout, resetTimers]);

  const startTimers = useCallback(() => {
    if (!user) return;

    resetTimers();

    const timeoutMs = timeoutMinutes * 60 * 1000;
    const warningMs = (timeoutMinutes - warningMinutes) * 60 * 1000;

    
    warningRef.current = window.setTimeout(() => {
      if (!warningShownRef.current) {
        warningShownRef.current = true;
        if (onWarning) {
          onWarning();
        } else {
          const shouldContinue = window.confirm(
            `Your session will expire in ${warningMinutes} minutes.\n\nWould you like to continue using the app?`
          );
          if (shouldContinue) {
            startTimers();
          } else {
            handleTimeout();
          }
        }
      }
    }, warningMs);

    
    timeoutRef.current = window.setTimeout(() => {
      handleTimeout();
    }, timeoutMs);
  }, [user, timeoutMinutes, warningMinutes, onWarning, handleTimeout, resetTimers]);

  const extendSession = useCallback(() => {
    startTimers();
  }, [startTimers]);

  useEffect(() => {
    if (user) {
      startTimers();
    } else {
      resetTimers();
    }

    
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    const resetTimer = () => {
      if (user && !warningShownRef.current) {
        startTimers();
      }
    };

    events.forEach(event => {
      document.addEventListener(event, resetTimer, true);
    });

    return () => {
      resetTimers();
      events.forEach(event => {
        document.removeEventListener(event, resetTimer, true);
      });
    };
  }, [user, startTimers, resetTimers]);

  return {
    extendSession,
    resetTimers
  };
};
