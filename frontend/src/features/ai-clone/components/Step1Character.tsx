import { useState, useRef, useEffect } from 'react';
import { useAICloneStore } from '../store';
import FileUploadZone from './FileUploadZone';
import { useTranslation } from 'react-i18next';

export default function Step1Character() {
  const { t } = useTranslation(['aiClone']);
  const {
    characterPhoto,
    characterPhotoPreview,
    referenceAudio,
    referenceText,
    updateData,
    canProceedToStep2,
    nextStep,
  } = useAICloneStore();

  const SAMPLE_TEXT = t('aiClone:step1.sampleText');

  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeTab, setActiveTab] = useState<'record' | 'upload'>('record');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  
  useEffect(() => {
    if (!characterPhoto && !characterPhotoPreview && !referenceAudio) {
      setIsRecording(false);
      setRecordingTime(0);
      setRecordedBlob(null);
      setIsPlaying(false);
      setActiveTab('record');
      
      
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (audioRef.current) {
        audioRef.current.pause();
      }
    }
  }, [characterPhoto, characterPhotoPreview, referenceAudio, isRecording]);

  const handlePhotoSelect = (file: File) => {
    const preview = URL.createObjectURL(file);
    updateData({
      characterPhoto: file,
      characterPhotoPreview: preview,
    });
  };

  const handleAudioFileSelect = (file: File) => {
    updateData({
      referenceAudio: file,
    });
    setActiveTab('upload');
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];

      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setRecordedBlob(blob);
        
        
        const file = new File([blob], 'recorded-voice.wav', { type: 'audio/wav' });
        updateData({ referenceAudio: file });
        
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Error accessing microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const playRecording = () => {
    if (recordedBlob && !isPlaying) {
      const audio = new Audio(URL.createObjectURL(recordedBlob));
      audioRef.current = audio;
      
      audio.onended = () => {
        setIsPlaying(false);
      };
      
      audio.play();
      setIsPlaying(true);
    } else if (audioRef.current && isPlaying) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleReferenceTextChange = (text: string) => {
    updateData({ referenceText: text });
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">{t('aiClone:step1.title')}</h2>
        <p className="text-lg text-gray-600">{t('aiClone:step1.description')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-gray-900">{t('aiClone:step1.photo.title')}</h3>
          
          <FileUploadZone
            onFileSelect={handlePhotoSelect}
            accept={{ 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] }}
            currentFile={characterPhoto}
            preview={characterPhotoPreview}
            className="min-h-[300px]"
          >
            <div className="space-y-4">
              <div className="text-gray-400">
                <svg className="w-12 h-12 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {t('aiClone:step1.photo.uploadArea.dragDrop')}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  {t('aiClone:step1.photo.uploadArea.tip')}
                </p>
              </div>
            </div>
          </FileUploadZone>
        </div>

        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-gray-900">{t('aiClone:step1.voice.title')}</h3>
          
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('record')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'record'
                    ? 'border-cyan-500 text-cyan-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {t('aiClone:step1.voice.tabs.record')}
              </button>
              <button
                onClick={() => setActiveTab('upload')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'upload'
                    ? 'border-cyan-500 text-cyan-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {t('aiClone:step1.voice.tabs.upload')}
              </button>
            </nav>
          </div>

          {activeTab === 'record' ? (
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">{t('aiClone:step1.voice.recording.instruction')}</h4>
                <p className="text-gray-700 leading-relaxed">{SAMPLE_TEXT}</p>
              </div>

              <div className="text-center space-y-4">
                {!isRecording && !recordedBlob ? (
                  <button
                    onClick={startRecording}
                    className="w-20 h-20 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center transition-colors"
                  >
                    <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                    </svg>
                  </button>
                ) : isRecording ? (
                  <div className="space-y-4">
                    <div className="w-20 h-20 bg-red-600 text-white rounded-full flex items-center justify-center animate-pulse">
                      <span className="text-sm font-medium">{formatTime(recordingTime)}</span>
                    </div>
                    <button
                      onClick={stopRecording}
                      className="px-6 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                    >
                      {t('aiClone:step1.voice.record.stopRecording')}
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="text-green-600">
                      <svg className="w-12 h-12 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <p className="text-sm text-gray-600">{t('aiClone:step1.voice.record.completed')}</p>
                    <div className="flex justify-center space-x-4">
                      <button
                        onClick={playRecording}
                        className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors"
                      >
                        {isPlaying ? t('aiClone:step1.voice.record.stop') : t('aiClone:step1.voice.record.listen')}
                      </button>
                      <button
                        onClick={() => {
                          setRecordedBlob(null);
                          updateData({ referenceAudio: undefined });
                        }}
                        className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                      >
                        {t('aiClone:step1.voice.record.reRecord')}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <FileUploadZone
              onFileSelect={handleAudioFileSelect}
              accept={{ 'audio/*': ['.mp3', '.wav', '.m4a'] }}
              currentFile={referenceAudio}
              className="min-h-[200px]"
            >
              <div className="space-y-4">
                <div className="text-gray-400">
                  <svg className="w-12 h-12 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <p className="text-lg font-medium text-gray-900">
                    {t('aiClone:step1.voice.upload.title')}
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    {t('aiClone:step1.voice.upload.description')}
                  </p>
                </div>
              </div>
            </FileUploadZone>
          )}

          {(referenceAudio || recordedBlob) && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                {t('aiClone:step1.voice.transcription.label')}
              </label>
              <textarea
                value={referenceText}
                onChange={(e) => handleReferenceTextChange(e.target.value)}
                placeholder={t('aiClone:step1.voice.transcription.placeholder')}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={4}
              />
              {activeTab === 'record' && (
                <p className="text-xs text-gray-500">
                  {t('aiClone:step1.voice.transcription.tip')}
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-end mt-8">
        <button
          onClick={nextStep}
          disabled={!canProceedToStep2()}
          className={`px-8 py-3 rounded-lg font-medium transition-colors ${
            canProceedToStep2()
              ? 'bg-cyan-600 hover:bg-cyan-700 text-white'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          }`}
        >
          {t('aiClone:step1.nextButton')}
        </button>
      </div>
    </div>
  );
}
