import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAICloneStore } from '../store';
import { useAuthStore } from '../../auth/store';
import { createVideoWithFullText, createVideoFromTopic, getVideoUrl } from '../api';
import GenerationNotificationModal from './GenerationNotificationModal';

export default function Step3Preview() {
  const { t } = useTranslation('aiClone');
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const {
    characterPhoto,
    characterPhotoPreview,
    referenceAudio,
    referenceText,
    scriptMode,
    manualScript,
    topic,
    keywords,
    description,
    finalScript,
    generatedVideoUrl,
    isGenerating,
    updateData,
    prevStep,
    reset,
  } = useAICloneStore();

  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [showNotificationModal, setShowNotificationModal] = useState(false);
  const [currentScript, setCurrentScript] = useState<string>(
    finalScript || (scriptMode === 'manual' ? manualScript || '' : '')
  );

  
  useEffect(() => {
    if (!characterPhoto && !finalScript && !manualScript && !topic) {
      setError('');
      setCurrentScript('');
    }
  }, [characterPhoto, finalScript, manualScript, topic]);

  
  useEffect(() => {
    if (scriptMode === 'manual') {
      const newScript = finalScript || manualScript || '';
      setCurrentScript(newScript);
    } else if (scriptMode === 'ai-generated' && finalScript) {
      setCurrentScript(finalScript);
    }
  }, [finalScript, manualScript, scriptMode]);

  const generateVideo = useCallback(async () => {
    if (!characterPhoto || !referenceAudio || !referenceText) {
      setError(t('step3.errors.missingData'));
      return;
    }

    if (!user?.id) {
      setError(t('step3.errors.notAuthenticated'));
      return;
    }

    setError('');
    setSuccessMessage('');
    updateData({ isGenerating: true });

    try {
      let response;
      
      if (scriptMode === 'manual') {
        response = await createVideoWithFullText({
          user_id: user.id,
          image: characterPhoto,
          reference_audio: referenceAudio,
          reference_text: referenceText,
          target_text: currentScript,
          language: 'english',
        });
      } else {
        response = await createVideoFromTopic({
          user_id: user.id,
          image: characterPhoto,
          reference_audio: referenceAudio,
          reference_text: referenceText,
          topic: topic || '',
          keywords,
          description,
          language: 'english',
        });
        
        if (response.generated_target_text) {
          setCurrentScript(response.generated_target_text);
          updateData({ finalScript: response.generated_target_text });
        }
      }

      if (response.success && (response.video_filename || response.video_url)) {
        const videoUrl = response.video_filename 
          ? getVideoUrl(response.video_filename)
          : response.video_url;
        
        updateData({
          generatedVideoUrl: videoUrl,
          finalScript: currentScript,
        });
      } else if (response.timeout) {
        
        setSuccessMessage(t('step3.success.generationStarted'));
        setShowNotificationModal(true);
        updateData({ finalScript: currentScript });
      } else {
        setError(response.error || t('step3.errors.generationFailed'));
      }
    } catch (err) {
      console.error('Video generation error:', err);
      setError(t('step3.errors.generalError'));
    } finally {
      updateData({ isGenerating: false });
    }
  }, [characterPhoto, referenceAudio, referenceText, user?.id, scriptMode, currentScript, topic, keywords, description, updateData, t]);

  
  useEffect(() => {
    if (scriptMode === 'ai-generated' && !isGenerating && !generatedVideoUrl && !error) {
      generateVideo();
    }
  }, [scriptMode, isGenerating, generatedVideoUrl, error, generateVideo]);

  const saveMemory = () => {
    
    alert(t('step3.success.memorySaved'));
    reset();
  };

  const handleScriptEdit = (text: string) => {
    setCurrentScript(text);
    updateData({ finalScript: text });
  };

  const handleGoToGallery = () => {
    setShowNotificationModal(false);
    navigate('/dashboard/ai-clone?tab=history');
  };

  const handleWaitOnPage = () => {
    setShowNotificationModal(false);
    updateData({ isGenerating: false }); // Stop showing loading state
    // Continue waiting - the user can manually check history later or refresh
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          {scriptMode === 'ai-generated' ? t('step3.titles.generating') : t('step3.titles.preview')}
        </h2>
        <p className="text-lg text-gray-600">
          {scriptMode === 'ai-generated' 
            ? t('step3.descriptions.generating')
            : t('step3.descriptions.preview')
          }
        </p>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="lg:w-1/2">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('step3.characterPreview.title')}</h3>
            
            <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
              {generatedVideoUrl ? (
                <video
                  src={generatedVideoUrl}
                  controls
                  className="w-full h-full object-cover"
                  poster={characterPhotoPreview}
                >
                  {t('step3.video.notSupported')}
                </video>
              ) : isGenerating ? (
                <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                  <div className="text-center text-white">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                    <p className="text-lg font-medium">{t('step3.generating.title')}</p>
                    <p className="text-sm text-gray-300 mt-2">{t('step3.generating.subtitle')}</p>
                  </div>
                </div>
              ) : characterPhotoPreview ? (
                <div className="relative h-full">
                  <img
                    src={characterPhotoPreview}
                    alt={t('step3.characterPreview.imageAlt')}
                    className="w-full h-full object-cover"
                  />
                  {scriptMode === 'manual' && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40">
                      <button
                        onClick={generateVideo}
                        disabled={isGenerating || !currentScript.trim()}
                        className="w-20 h-20 bg-cyan-600 hover:bg-cyan-700 text-white rounded-full flex items-center justify-center transition-colors disabled:opacity-50"
                      >
                        <svg className="w-8 h-8 ml-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  )}
                  {scriptMode === 'ai-generated' && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40">
                      <div className="text-center text-white">
                        <div className="w-20 h-20 bg-cyan-600 rounded-full flex items-center justify-center mx-auto mb-4">
                          <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <p className="text-sm">{t('step3.aiMode.autoGenerate')}</p>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-400">
                  <p>{t('step3.characterPreview.noImage')}</p>
                </div>
              )}
            </div>

            {/* Character Info */}
            {characterPhoto && (
              <div className="mt-4 text-sm text-gray-600">
                <p><span className="font-bold">{t('step3.characterInfo.image')}:</span> {characterPhoto.name}</p>
                {referenceAudio && (
                  <p><span className="font-bold">{t('step3.characterInfo.voice')}:</span> {referenceAudio.name}</p>
                )}
              </div>
            )}
          </div>

          {(scriptMode === 'manual' || (scriptMode === 'ai-generated' && currentScript)) && (
            <div className="lg:w-1/2">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{t('step3.script.title')}</h3>
                {scriptMode === 'ai-generated' && (
                  <span className="text-xs bg-cyan-100 text-cyan-800 px-2 py-1 rounded">
                    {t('step3.script.aiGenerated')}
                  </span>
                )}
              </div>
              
              <textarea
                value={currentScript}
                onChange={(e) => handleScriptEdit(e.target.value)}
                readOnly={scriptMode === 'ai-generated' && isGenerating}
                className={`w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none ${
                  scriptMode === 'ai-generated' && isGenerating ? 'bg-gray-50 cursor-not-allowed' : ''
                }`}
                placeholder={scriptMode === 'ai-generated' ? t('step3.script.placeholders.generating') : t('step3.script.placeholders.manual')}
              />
              
              <div className="flex justify-between items-center mt-2 text-sm text-gray-500">
                <span>
                  {scriptMode === 'manual' 
                    ? t('step3.script.tips.manual')
                    : t('step3.script.tips.aiGenerated')
                  }
                </span>
                <span>{t('step3.script.characterCount', { count: currentScript.length })}</span>
              </div>
            </div>
          )}

          {scriptMode === 'ai-generated' && !currentScript && !error && (
            <div className="lg:w-1/2">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{t('step3.aiGeneration.title')}</h3>
                <span className="text-xs bg-cyan-100 text-cyan-800 px-2 py-1 rounded">
                  {t('step3.aiGeneration.inProgress')}
                </span>
              </div>
              
              <div className="h-64 border-2 border-dashed border-cyan-300 rounded-lg flex items-center justify-center bg-cyan-50">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600 mx-auto mb-4"></div>
                  <p className="text-cyan-800 font-medium">{t('step3.aiGeneration.generating')}</p>
                  <p className="text-cyan-600 text-sm mt-2">
                    {t('step3.aiGeneration.topic')}: <span className="font-semibold">{topic}</span>
                  </p>
                  {keywords && (
                    <p className="text-cyan-600 text-sm">
                      {t('step3.aiGeneration.keywords')}: <span className="font-semibold">{keywords}</span>
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-green-800">{successMessage}</p>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between">
        <button
          onClick={prevStep}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          {t('step3.buttons.editScript')}
        </button>

        <div className="space-x-4">
          {scriptMode === 'manual' && !generatedVideoUrl && !isGenerating && (
            <button
              onClick={generateVideo}
              disabled={!currentScript.trim() || isGenerating}
              className={`px-8 py-3 rounded-lg font-medium transition-colors ${
                currentScript.trim() && !isGenerating
                  ? 'bg-cyan-600 hover:bg-cyan-700 text-white'
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              }`}
            >
              {t('step3.buttons.generateVideo')}
            </button>
          )}

          {scriptMode === 'ai-generated' && !generatedVideoUrl && isGenerating && (
            <div className="px-8 py-3 bg-cyan-100 text-cyan-800 rounded-lg font-medium">
              {t('step3.buttons.aiGenerating')}
            </div>
          )}

          {generatedVideoUrl && (
            <button
              onClick={saveMemory}
              className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
            >
              {t('step3.buttons.saveMemory')}
            </button>
          )}
        </div>
      </div>

      {isGenerating && (
        <div className="mt-6 bg-cyan-50 border border-cyan-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-cyan-600"></div>
            </div>
            <div className="ml-3">
              <p className="text-sm text-cyan-800">
                {t('step3.generatingStatus.message')}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Generation Notification Modal */}
      <GenerationNotificationModal
        isOpen={showNotificationModal}
        onGoToGallery={handleGoToGallery}
        onWaitOnPage={handleWaitOnPage}
      />
    </div>
  );
}
