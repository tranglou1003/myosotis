import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import { useAuthInitialization, useAuthStore } from '../features/auth';
import { ChatInterface, ChatFloatingActionButton } from '../features/chatbot';

export default function AppWithAuth() {
  useAuthInitialization();
  const { isAuthenticated } = useAuthStore();
  
  return (
    <>
      <RouterProvider router={router} />
      {/* Only show chatbot FAB and interface when user is authenticated */}
      {isAuthenticated && (
        <>
          <ChatFloatingActionButton />
          <ChatInterface />
        </>
      )}
    </>
  );
}
