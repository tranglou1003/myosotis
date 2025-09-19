import { createBrowserRouter } from 'react-router-dom';
import { LoginPage, RegisterPage } from '../features/auth';
import { DashboardLayout } from '../components/layout';
import {
  DashboardHomePage,
  DashboardAccountPage,
  DashboardDiscoverPage,
  DashboardContactsPage,
  DashboardMMSETestPage,
  DashboardMMSEHistoryPage,
  DashboardAIClonePage,
  DashboardMemoryFilmPage,
  DashboardChatbotPage,
  DashboardMemoryMapPage,
  DashboardMiniGamesPage,
  DashboardSudokuGamePage,
  DashboardPictureRecallPage,
} from '../pages/dashboard';
import ForgotPasswordPage from '../pages/ForgotPasswordPage';
import LandingPage from '../pages/LandingPage';
import CaregiverGuidePage from '../pages/CaregiverGuidePage';
import MMSETestPage from '../pages/MMSETestPage';
import MMSEHistoryPage from '../pages/MMSEHistoryPage';
import MemoryFilmPage from '../pages/MemoryBookPage';
import AICloneCreatePage from '../pages/AICloneCreatePage';
import FAQPage from '../pages/FAQPage';
import RootRedirect from '../components/RootRedirect';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootRedirect />,
  },
  {
    path: '/landing',
    element: <LandingPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/forgot-password',
    element: <ForgotPasswordPage />,
  },
  {
    path: '/caregiver-guide',
    element: <CaregiverGuidePage />,
  },
  {
    path: '/dashboard',
    element: <DashboardLayout />,
    children: [
      {
        index: true,
        element: <DashboardHomePage />,
      },
      {
        path: 'account',
        element: <DashboardAccountPage />,
      },
      {
        path: 'discover',
        element: <DashboardDiscoverPage />,
      },
      {
        path: 'faq',
        element: <FAQPage />,
      },
      {
        path: 'contacts',
        element: <DashboardContactsPage />,
      },
      {
        path: 'ai-clone',
        element: <DashboardAIClonePage />,
      },
      {
        path: 'mmse-test',
        element: <DashboardMMSETestPage />,
      },
      {
        path: 'mmse-history',
        element: <DashboardMMSEHistoryPage />,
      },
      {
        path: 'memory-film',
        element: <DashboardMemoryFilmPage />,
      },
      {
        path: 'chatbot',
        element: <DashboardChatbotPage />,
      },
      {
        path: 'memory-map',
        element: <DashboardMemoryMapPage />,
      },
      {
        path: 'mini-games',
        element: <DashboardMiniGamesPage />,
      },
      {
        path: 'mini-games/sudoku',
        element: <DashboardSudokuGamePage />,
      },
      {
        path: 'mini-games/picture-recall',
        element: <DashboardPictureRecallPage />,
      },
    ],
  },
  {
    path: '/mmse-test',
    element: <MMSETestPage />,
  },
  {
    path: '/mmse-history',
    element: <MMSEHistoryPage />,
  },
  {
    path: '/memory-film',
    element: <MemoryFilmPage />,
  },
  {
    path: '/ai-clone/create',
    element: <AICloneCreatePage />,
  },
  {
    path: '*',
    element: (
      <div className="min-h-screen bg-cyan-50 antialiased text-[18px] flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-semibold text-gray-900 mb-4">404</h1>
          <p className="text-lg text-gray-600">Page not found</p>
        </div>
      </div>
    ),
  },
]);
