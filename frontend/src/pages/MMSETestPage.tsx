import { ProtectedRoute } from '../features/auth';
import MMSETestContent from '../components/MMSETestContent';
import { useTranslation } from 'react-i18next';

export default function MMSETestPage() {
  const { t } = useTranslation('mmse');
  
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white border-b border-gray-200">
          <div className="px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <img src="/test-icon.png" alt="MMSE Test" className="w-6 h-6" />
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">{t('testContent.title')}</h1>
                  <p className="text-sm text-gray-500">{t('testContent.subtitle')}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="px-4 sm:px-6 lg:px-8 py-8">
          <MMSETestContent />
        </div>
      </div>
    </ProtectedRoute>
  );
}
