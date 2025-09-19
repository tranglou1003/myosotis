import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { ProtectedRoute } from '../../features/auth';
import { useAuthStore } from '../../features/auth/store';
import { useSessionTimeout } from '../../hooks/useSessionTimeout';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher';

export default function DashboardLayout() {
  const { t } = useTranslation(['dashboard']);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [showNotification, setShowNotification] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useSessionTimeout({
    timeoutMinutes: 1440,
    warningMinutes: 30,
  });

  const firstName = user?.email?.split('@')[0] || 'User';
  const displayName = user?.profile?.full_name || firstName.charAt(0).toUpperCase() + firstName.slice(1);

  const handleLogout = () => {
    logout();
  };

  const handleCreateSchedule = () => {
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  const navigationItems = [
    {
      key: 'dashboard',
      label: t('dashboard:navigation.dashboard'),
      icon: '/dashboard.png',
      path: '/dashboard',
    },
    {
      key: 'account',
      label: t('dashboard:navigation.myAccount'),
      icon: '/personal-information.png',
      path: '/dashboard/account',
    },
    {
      key: 'discover',
      label: t('dashboard:navigation.discover'),
      icon: '/discover.png',
      path: '/dashboard/discover',
    },
    {
      key: 'faq',
      label: t('dashboard:navigation.faq'),
      icon: '/faq.png',
      path: '/dashboard/faq',
    },
  ];

  
  const getCurrentActiveKey = () => {
    const path = location.pathname;
    
    
    if (path === '/dashboard' || path === '/dashboard/') {
      return 'dashboard';
    }
    if (path.startsWith('/dashboard/account')) {
      return 'account';
    }
    if (path.startsWith('/dashboard/discover')) {
      return 'discover';
    }
    if (path.startsWith('/dashboard/faq')) {
      return 'faq';
    }

    if (path.startsWith('/dashboard/')) {
      return 'dashboard';
    }
    
    return 'dashboard';
  };

  const activeKey = getCurrentActiveKey();

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#F9F9FB] antialiased text-[#333333] flex">
        {showNotification && (
          <div className="fixed top-4 right-4 z-50 bg-blue-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{t('dashboard:notifications.scheduleComingSoon')}</span>
          </div>
        )}

        <div className="hidden lg:block lg:w-2/12 bg-white">
          <div className="p-4 lg:p-6 h-screen flex flex-col sticky top-0">
            <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-gray-100">
              <img src="/apple-touch-icon.png" alt="Myosotis Logo" className="h-8 w-8" />
              <div className="text-2xl font-bold text-[#5A6DD0]">{t('dashboard:branding.myosotis')}</div>
            </div>

            <button
              onClick={handleCreateSchedule}
              className="w-full bg-[#5A6DD0] text-white rounded-[16px] py-4 mb-6 font-semibold hover:bg-[#5A6DD0]/90 transition-colors flex items-center justify-center space-x-2"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <span>{t('dashboard:buttons.createNewSchedule')}</span>
            </button>

            <nav className="space-y-2 flex-1 lg:overflow-y-auto mb-6">
              {navigationItems.map((item) => (
                <button
                  key={item.key}
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center space-x-3 p-3 rounded-[12px] transition-colors ${
                    activeKey === item.key
                      ? 'bg-[#5A6DD0]/10 text-[#5A6DD0] hover:bg-[#5A6DD0]/20'
                      : 'text-[#888888] hover:bg-gray-50'
                  }`}
                >
                  <img src={item.icon} alt={item.label} className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              ))}
            </nav>

            <div className="pt-4 mt-auto border-t border-gray-100">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-[#5A6DD0] rounded-full flex items-center justify-center text-white font-semibold">
                  {displayName.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div className="font-medium text-[#333333]">{displayName}</div>
                  <button
                    onClick={handleLogout}
                    className="text-sm text-[#888888] hover:text-[#5A6DD0]"
                  >
                    {t('dashboard:buttons.signOut')}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {isMobileMenuOpen && (
          <div className="lg:hidden fixed inset-0 z-50 flex">
            <div className="fixed inset-0 bg-white-50 bg-opacity-50" onClick={() => setIsMobileMenuOpen(false)}></div>
            <div className="relative w-64 bg-white h-full shadow-xl">
              <div className="p-4 h-full flex flex-col">
                <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
                  <div className="flex items-center space-x-3">
                    <img src="/apple-touch-icon.png" alt="Myosotis Logo" className="h-8 w-8" />
                    <div className="text-xl font-bold text-[#5A6DD0]">{t('dashboard:branding.myosotis')}</div>
                  </div>
                  <button
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="p-2 rounded-lg hover:bg-gray-100"
                  >
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <button
                  onClick={handleCreateSchedule}
                  className="w-full bg-[#5A6DD0] text-white rounded-[16px] py-4 mb-6 font-semibold hover:bg-[#5A6DD0]/90 transition-colors flex items-center justify-center space-x-2"
                >
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>{t('dashboard:buttons.createNewSchedule')}</span>
                </button>

                <nav className="space-y-2 flex-1 overflow-y-auto mb-6">
                  {navigationItems.map((item) => (
                    <button
                      key={item.key}
                      onClick={() => {
                        navigate(item.path);
                        setIsMobileMenuOpen(false);
                      }}
                      className={`w-full flex items-center space-x-3 p-3 rounded-[12px] transition-colors ${
                        activeKey === item.key
                          ? 'bg-[#5A6DD0]/10 text-[#5A6DD0] hover:bg-[#5A6DD0]/20'
                          : 'text-[#888888] hover:bg-gray-50'
                      }`}
                    >
                      <img src={item.icon} alt={item.label} className="h-5 w-5" />
                      <span className="font-medium">{item.label}</span>
                    </button>
                  ))}
                </nav>

                <div className="pt-4 mt-auto border-t border-gray-100">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-[#5A6DD0] rounded-full flex items-center justify-center text-white font-semibold">
                      {displayName.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="font-medium text-[#333333]">{displayName}</div>
                      <button
                        onClick={handleLogout}
                        className="text-sm text-[#888888] hover:text-[#5A6DD0]"
                      >
                        {t('dashboard:buttons.signOut')}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col w-full lg:w-10/12">
          <header className="bg-white py-4 border-l-0 lg:border-l border-gray-100 sticky top-0 z-30">
            <div className="w-full flex items-center justify-end px-4 sm:px-6 lg:px-8">
              {/* Mobile menu button */}
              <button
                onClick={() => setIsMobileMenuOpen(true)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors absolute left-4"
              >
                <svg className="h-6 w-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>

              <div className="flex items-center space-x-2">
                <button className="md:hidden p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors">
                  <svg className="h-5 w-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>

                <LanguageSwitcher />

                <button className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors relative mr-4">
                  <img src="/bell.png" alt="Notifications" className="h-5 w-5" />
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <div className="flex-1 px-4 sm:px-6 lg:px-8 py-6 bg-white border-l-0 lg:border-l border-gray-100">
            <Outlet />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
