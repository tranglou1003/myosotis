import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import type { LifeEvent, LifeEventInput } from '../types/memory';

interface LifeEventModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (event: LifeEventInput, file?: File) => void;
  event?: LifeEvent | null;
}

export default function LifeEventModal({ isOpen, onClose, onSave, event }: LifeEventModalProps) {
  const { t } = useTranslation('modals');
  const [formData, setFormData] = useState<LifeEventInput>({
    title: '',
    type: 'image',
    description: '',
    file_path: '',
    start_time: '',
    end_time: '',
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');

  useEffect(() => {
    if (event) {
      setFormData({
        title: event.title,
        type: event.type,
        description: event.description,
        file_path: event.file_path || '',
        start_time: event.start_time,
        end_time: event.end_time || '',
      });
      if (event.file_path && event.type === 'image') {
        setPreviewUrl(event.file_path);
      }
    } else {
      setFormData({
        title: '',
        type: 'image',
        description: '',
        file_path: '',
        start_time: '',
        end_time: '',
      });
      setPreviewUrl('');
      setSelectedFile(null);
    }
  }, [event, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.title.trim() && formData.start_time && formData.description.trim()) {
      onSave(formData, selectedFile || undefined);
      onClose();
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      
      
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = () => {
          setPreviewUrl(reader.result as string);
        };
        reader.readAsDataURL(file);
        
        
        setFormData(prev => ({
          ...prev,
          type: 'image',
        }));
      } else if (file.type.startsWith('video/')) {
        setFormData(prev => ({
          ...prev,
          type: 'video',
        }));
        setPreviewUrl('');
      } else if (file.type.startsWith('audio/')) {
        setFormData(prev => ({
          ...prev,
          type: 'audio',
        }));
        setPreviewUrl('');
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4 text-center sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />
        
        <div className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-4 sm:w-full sm:max-w-2xl">
          <form onSubmit={handleSubmit}>
            <div className="bg-white px-6 pb-6 pt-8 sm:p-8">
              <div className="sm:flex sm:items-start">
                <div className="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
                  <h3 className="text-2xl font-bold leading-8 text-gray-900 mb-2">
                    {event ? t('lifeEvent.title.edit') : t('lifeEvent.title.add')}
                  </h3>
                  
                  <div className="space-y-3">
                    <div>
                      <label htmlFor="title" className="block text-lg font-semibold text-gray-700 mb-2">
                        {t('lifeEvent.fields.title.label')} <span className="text-red-500">{t('lifeEvent.required')}</span>
                      </label>
                      <input
                        type="text"
                        id="title"
                        value={formData.title}
                        onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                        className="w-full rounded-lg border-2 border-gray-300 px-4 py-3 text-lg focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-200"
                        placeholder={t('lifeEvent.fields.title.placeholder')}
                        required
                      />
                    </div>

                    <div>
                      <label htmlFor="type" className="block text-lg font-semibold text-gray-700 mb-2">
                        {t('lifeEvent.fields.type.label')} <span className="text-red-500">{t('lifeEvent.required')}</span>
                      </label>
                      <select
                        id="type"
                        value={formData.type}
                        onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as 'image' | 'video' | 'audio' }))}
                        className="w-full rounded-lg border-2 border-gray-300 px-4 py-3 text-lg focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-200"
                        required
                      >
                        <option value="image">{t('lifeEvent.fields.type.options.image')}</option>
                        <option value="video">{t('lifeEvent.fields.type.options.video')}</option>
                        <option value="audio">{t('lifeEvent.fields.type.options.audio')}</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="start_time" className="block text-lg font-semibold text-gray-700 mb-2">
                        {t('lifeEvent.fields.startDate.label')} <span className="text-red-500">{t('lifeEvent.required')}</span>
                      </label>
                      <input
                        type="date"
                        id="start_time"
                        value={formData.start_time}
                        onChange={(e) => setFormData(prev => ({ ...prev, start_time: e.target.value }))}
                        className="w-full rounded-lg border-2 border-gray-300 px-4 py-3 text-lg focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-200"
                        required
                      />
                    </div>

                    <div>
                      <label htmlFor="end_time" className="block text-lg font-semibold text-gray-700 mb-2">
                        {t('lifeEvent.fields.endDate.label')}
                      </label>
                      <input
                        type="date"
                        id="end_time"
                        value={formData.end_time}
                        onChange={(e) => setFormData(prev => ({ ...prev, end_time: e.target.value }))}
                        className="w-full rounded-lg border-2 border-gray-300 px-4 py-3 text-lg focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-200"
                      />
                    </div>

                    <div>
                      <label htmlFor="description" className="block text-lg font-semibold text-gray-700 mb-2">
                        {t('lifeEvent.fields.description.label')} <span className="text-red-500">{t('lifeEvent.required')}</span>
                      </label>
                      <textarea
                        id="description"
                        rows={4}
                        value={formData.description}
                        onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                        className="w-full rounded-lg border-2 border-gray-300 px-4 py-3 text-lg focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-200"
                        placeholder={t('lifeEvent.fields.description.placeholder')}
                        required
                      />
                    </div>

                    {(formData.type === 'image' || formData.type === 'video' || formData.type === 'audio') && (
                      <div>
                        <label htmlFor="file" className="block text-lg font-semibold text-gray-700 mb-2">
                          {formData.type === 'image' ? t('lifeEvent.fields.file.photo') : 
                           formData.type === 'video' ? t('lifeEvent.fields.file.video') : 
                           t('lifeEvent.fields.file.audio')}
                        </label>
                        <input
                          type="file"
                          id="file"
                          accept={
                            formData.type === 'image' ? 'image/*' : 
                            formData.type === 'video' ? 'video/*' : 
                            'audio/*'
                          }
                          onChange={handleFileUpload}
                          className="w-full rounded-lg border-2 border-gray-300 px-4 py-3 text-lg focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-200"
                        />
                        {previewUrl && formData.type === 'image' && (
                          <div className="mt-3">
                            <img
                              src={previewUrl}
                              alt={t('lifeEvent.preview.alt')}
                              className="h-32 w-32 rounded-lg object-cover shadow-md"
                            />
                          </div>
                        )}
                        {selectedFile && formData.type !== 'image' && (
                          <div className="mt-3 text-lg text-gray-600 bg-gray-50 p-3 rounded-lg">
                            {t('lifeEvent.fields.file.selected', { fileName: selectedFile.name })}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 px-6 py-6 sm:flex sm:flex-row-reverse sm:px-8">
              <button
                type="submit"
                className="inline-flex w-full justify-center rounded-lg bg-cyan-600 px-6 py-4 text-lg font-bold text-white shadow-lg hover:bg-cyan-500 transition-colors focus:outline-none focus:ring-4 focus:ring-cyan-300 sm:ml-4 sm:w-auto"
              >
                {event ? t('lifeEvent.buttons.update') : t('lifeEvent.buttons.add')}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="mt-4 inline-flex w-full justify-center rounded-lg bg-white px-6 py-4 text-lg font-bold text-gray-900 shadow-md ring-2 ring-inset ring-gray-300 hover:bg-gray-50 transition-colors focus:outline-none focus:ring-4 focus:ring-gray-300 sm:mt-0 sm:w-auto"
              >
                {t('lifeEvent.buttons.cancel')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
