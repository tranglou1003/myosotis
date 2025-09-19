import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import DashboardHeader from './DashboardHeader';
import { AICloneHistoryContent } from '../components';
import { useTranslation } from 'react-i18next';

export default function AICloneContent() {
  const { t } = useTranslation(['aiClone']);
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState<'overview' | 'history'>('overview');
  const navigate = useNavigate();

  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab === 'history') {
      setActiveTab('history');
    }
  }, [searchParams]);

  return (
    <div className="space-y-6">
      <DashboardHeader 
        title={t('aiClone:title')}
        description={t('aiClone:description')}
      />
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="px-6 pt-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'overview'
                    ? 'border-cyan-500 text-cyan-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  {t('aiClone:tabs.overview')}
                </div>
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'history'
                    ? 'border-cyan-500 text-cyan-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  {t('aiClone:tabs.memoryGallery')}
                </div>
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6 lg:p-8">
          {activeTab === 'overview' && (
            <div className="space-y-8">
              {/* Create New Section */}
              <div className="text-center max-w-2xl mx-auto">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">{t('aiClone:createNew.title')}</h2>
                <p className="text-gray-600 mb-8">
                  {t('aiClone:createNew.description')}
                </p>
                <button
                  onClick={() => navigate('/ai-clone/create')}
                  className="inline-flex items-center bg-cyan-600 hover:bg-cyan-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  {t('aiClone:createNew.startButton')}
                </button>
              </div>

              {/* Features Grid */}
              <div className="grid md:grid-cols-3 gap-6">
                <div className="text-center p-6 rounded-lg border border-gray-200">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">{t('aiClone:features.uploadPhotos.title')}</h3>
                  <p className="text-sm text-gray-600">{t('aiClone:features.uploadPhotos.description')}</p>
                </div>

                <div className="text-center p-6 rounded-lg border border-gray-200">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">{t('aiClone:features.recordVoice.title')}</h3>
                  <p className="text-sm text-gray-600">{t('aiClone:features.recordVoice.description')}</p>
                </div>

                <div className="text-center p-6 rounded-lg border border-gray-200">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">{t('aiClone:features.generateVideo.title')}</h3>
                  <p className="text-sm text-gray-600">{t('aiClone:features.generateVideo.description')}</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'history' && <AICloneHistoryContent />}
        </div>
      </div>
    </div>
  );
}
