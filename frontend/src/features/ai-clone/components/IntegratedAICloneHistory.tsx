import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../auth';
import { LoadingSpinner } from '../../../components';
import { getUserVideos, getVideoUrl } from '../api';
import type { AICloneVideo } from '../types';

export default function IntegratedAICloneHistory() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [videos, setVideos] = useState<AICloneVideo[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchVideos = async () => {
      if (!user?.id) return;

      try {
        setLoading(true);
        const response = await getUserVideos(user.id);
        if (response.success) {
          const successfulVideos = response.videos.filter(video => video.status !== 'failed');
          setVideos(successfulVideos);
          setCurrentIndex(0); // Reset to first video
        } else {
          setError('Failed to load video history');
        }
      } catch (err) {
        console.error('Failed to fetch videos:', err);
        setError('Failed to load video history');
      } finally {
        setLoading(false);
      }
    };

    fetchVideos();
  }, [user?.id]);

  const handlePrevious = () => {
    setCurrentIndex(prev => (prev > 0 ? prev - 1 : videos.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex(prev => (prev < videos.length - 1 ? prev + 1 : 0));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'processing':
        return 'Processing';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  if (!user) {
    return null;
  }

  return (
    <>
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <LoadingSpinner text="Loading videos..." />
        </div>
      ) : error ? (
        <div className="p-8 text-center">
          <div className="text-red-600 mb-4">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="text-cyan-600 hover:text-cyan-700"
          >
            Try Again
          </button>
        </div>
      ) : videos.length === 0 ? (
        <div className="p-8 text-center">
          <div className="max-w-md mx-auto">
            <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Videos Yet</h2>
            <p className="text-gray-600 mb-6">Create your first AI clone video to see it here</p>
            <button
              onClick={() => navigate('/ai-clone')}
              className="bg-cyan-600 hover:bg-cyan-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
            >
              Create First Video
            </button>
          </div>
        </div>
      ) : (
        <div className="overflow-hidden">
          {/* Video Navigation */}
          <div className="relative">
            {/* Current Video */}
            <div className="aspect-w-16 aspect-h-9 bg-gray-100">
              <video
                src={videos[currentIndex]?.video_url ? getVideoUrl(videos[currentIndex].video_url) : ''}
                controls
                className="w-full h-full object-cover"
              />
            </div>

            {/* Navigation Arrows */}
            <div className="absolute inset-y-0 left-0 flex items-center">
              <button
                onClick={handlePrevious}
                className="p-2 m-4 rounded-full bg-black/50 hover:bg-black/70 text-white transition-colors"
                aria-label="Previous video"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            </div>
            <div className="absolute inset-y-0 right-0 flex items-center">
              <button
                onClick={handleNext}
                className="p-2 m-4 rounded-full bg-black/50 hover:bg-black/70 text-white transition-colors"
                aria-label="Next video"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          {/* Video Info */}
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-gray-600">
                {formatDate(videos[currentIndex].created_at)}
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(videos[currentIndex].status)}`}>
                {getStatusText(videos[currentIndex].status)}
              </span>
            </div>
            {videos[currentIndex].description && (
              <p className="text-gray-700">
                {videos[currentIndex].description}
              </p>
            )}
          </div>

          {/* Video Counter */}
          <div className="px-6 pb-6 flex items-center justify-center space-x-2">
            {videos.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-2 h-2 rounded-full transition-all ${
                  index === currentIndex ? 'bg-cyan-600 w-4' : 'bg-gray-300 hover:bg-gray-400'
                }`}
                aria-label={`Go to video ${index + 1}`}
              />
            ))}
          </div>
        </div>
      )}
    </>
  );
}
