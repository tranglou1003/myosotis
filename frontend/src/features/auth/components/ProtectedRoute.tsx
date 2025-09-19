import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useRequireAuth } from '../hooks';

interface ProtectedRouteProps {
  children: ReactNode;
  redirectTo?: string;
}

export default function ProtectedRoute({ 
  children, 
  redirectTo = '/login' 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, isReady } = useRequireAuth();
  const location = useLocation();

  if (!isReady || isLoading) {
    return (
      <div className="min-h-screen bg-cyan-50 antialiased text-[18px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location }} 
        replace 
      />
    );
  }

  return <>{children}</>;
}
