import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAICloneStore } from '../store';

export default function Step2Script() {
  const { t } = useTranslation('aiClone');
  const {
    scriptMode,
    manualScript,
    topic,
    keywords,
    description,
    updateData,
    canProceedToStep3,
    nextStep,
    prevStep,
  } = useAICloneStore();

  const [selectedMode, setSelectedMode] = useState<'manual' | 'ai-generated'>(scriptMode);

  
  useEffect(() => {
    setSelectedMode(scriptMode);
  }, [scriptMode]);

  const handleModeSelect = (mode: 'manual' | 'ai-generated') => {
    setSelectedMode(mode);
    updateData({ scriptMode: mode });
  };

  const handleManualScriptChange = (text: string) => {
    updateData({ manualScript: text });
  };

  const handleTopicChange = (text: string) => {
    updateData({ topic: text });
  };

  const handleKeywordsChange = (text: string) => {
    updateData({ keywords: text });
  };

  const handleDescriptionChange = (text: string) => {
    updateData({ description: text });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">{t('step2.title')}</h2>
        <p className="text-lg text-gray-600">{t('step2.description')}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div
          onClick={() => handleModeSelect('manual')}
          className={`p-6 rounded-lg border-2 cursor-pointer transition-all ${
            selectedMode === 'manual'
              ? 'border-cyan-500 bg-cyan-50'
              : 'border-gray-200 hover:border-gray-300 bg-white'
          }`}
        >
          <div className="flex items-start space-x-4">
            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
              selectedMode === 'manual' ? 'border-cyan-500' : 'border-gray-300'
            }`}>
              {selectedMode === 'manual' && (
                <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
              )}
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{t('step2.modes.manual.title')}</h3>
              <p className="text-gray-600 mb-4">
                {t('step2.modes.manual.description')}
              </p>
              <div className="flex items-center text-sm text-gray-500">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h6a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
                {t('step2.modes.manual.feature')}
              </div>
            </div>
          </div>
        </div>

        <div
          onClick={() => handleModeSelect('ai-generated')}
          className={`p-6 rounded-lg border-2 cursor-pointer transition-all ${
            selectedMode === 'ai-generated'
              ? 'border-cyan-500 bg-cyan-50'
              : 'border-gray-200 hover:border-gray-300 bg-white'
          }`}
        >
          <div className="flex items-start space-x-4">
            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
              selectedMode === 'ai-generated' ? 'border-cyan-500' : 'border-gray-300'
            }`}>
              {selectedMode === 'ai-generated' && (
                <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
              )}
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{t('step2.modes.aiGenerated.title')}</h3>
              <p className="text-gray-600 mb-4">
                {t('step2.modes.aiGenerated.description')}
              </p>
              <div className="flex items-center text-sm text-gray-500">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {t('step2.modes.aiGenerated.feature')}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {selectedMode === 'manual' ? (
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-gray-900">{t('step2.manual.title')}</h4>
            <textarea
              value={manualScript || ''}
              onChange={(e) => handleManualScriptChange(e.target.value)}
              placeholder={t('step2.manual.placeholder')}
              className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <div className="flex justify-between items-center text-sm text-gray-500">
              <span>{t('step2.manual.tip')}</span>
              <span>{t('step2.manual.characterCount', { count: manualScript?.length || 0 })}</span>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <h4 className="text-lg font-semibold text-gray-900">{t('step2.aiGenerated.title')}</h4>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('step2.aiGenerated.topic.label')} <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={topic || ''}
                  onChange={(e) => handleTopicChange(e.target.value)}
                  placeholder={t('step2.aiGenerated.topic.placeholder')}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('step2.aiGenerated.keywords.label')}
                </label>
                <input
                  type="text"
                  value={keywords || ''}
                  onChange={(e) => handleKeywordsChange(e.target.value)}
                  placeholder={t('step2.aiGenerated.keywords.placeholder')}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">{t('step2.aiGenerated.keywords.help')}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('step2.aiGenerated.description.label')}
                </label>
                <textarea
                  value={description || ''}
                  onChange={(e) => handleDescriptionChange(e.target.value)}
                  placeholder={t('step2.aiGenerated.description.placeholder')}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
                <p className="text-xs text-gray-500 mt-1">{t('step2.aiGenerated.description.help')}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-between mt-8">
        <button
          onClick={prevStep}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          {t('step2.backButton')}
        </button>
        
        <button
          onClick={nextStep}
          disabled={!canProceedToStep3()}
          className={`px-8 py-3 rounded-lg font-medium transition-colors ${
            canProceedToStep3()
              ? 'bg-cyan-600 hover:bg-cyan-700 text-white'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          }`}
        >
          {t('step2.nextButton')}
        </button>
      </div>
    </div>
  );
}
