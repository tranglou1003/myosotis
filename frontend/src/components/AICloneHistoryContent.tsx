import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../features/auth';
import { LoadingSpinner } from '../components';
import { getUserVideos, getVideoUrl } from '../features/ai-clone/api';
import type { AICloneVideo } from '../features/ai-clone/types';

export default function AICloneHistoryContent() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [videos, setVideos] = useState<AICloneVideo[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const fetchVideos = async () => {
      if (!user?.id) return;

      try {
        setLoading(true);
        const response = await getUserVideos(user.id);
        if (response.success) {
          const successfulVideos = response.videos.filter(video => video.status !== 'failed');
          setVideos(successfulVideos);
          setCurrentIndex(0);
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

  // Reset video state when changing videos
  useEffect(() => {
    setIsPlaying(false);
    setCurrentTime(0);
    setDuration(0);
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
    }
  }, [currentIndex]);

  const handlePrevious = () => {
    setCurrentIndex(prev => (prev > 0 ? prev - 1 : videos.length - 1));
    setIsPlaying(false);
  };

  const handleNext = () => {
    setCurrentIndex(prev => (prev < videos.length - 1 ? prev + 1 : 0));
    setIsPlaying(false);
  };

  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
        setIsPlaying(false);
      } else {
        videoRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handleVideoEnd = () => {
    setIsPlaying(false);
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (videoRef.current && duration > 0) {
      const rect = e.currentTarget.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const newTime = (clickX / rect.width) * duration;
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
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

  if (!user) {
    return null;
  }

  return (
    <div className="space-y-6">
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <LoadingSpinner text="Loading videos..." />
        </div>
      ) : error ? (
        <div className="bg-red-50 rounded-lg p-6 text-center">
          <div className="text-red-600 mb-4">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="text-cyan-600 hover:text-cyan-700 font-medium"
          >
            Try Again
          </button>
        </div>
      ) : videos.length === 0 ? (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Videos Yet</h2>
            <p className="text-gray-600 mb-6">Create your first AI clone video to see it here</p>
            <button
              onClick={() => navigate('/ai-clone/create')}
              className="bg-cyan-600 hover:bg-cyan-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
            >
              Create First Video
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-gray-50 rounded-xl overflow-hidden max-w-2xl mx-auto">
            <div className="relative">
              <div className="aspect-w-16 aspect-h-9 bg-gray-100">
                <video
                  ref={videoRef}
                  src={videos[currentIndex]?.video_url ? getVideoUrl(videos[currentIndex].video_url) : ''}
                  className="w-full h-full object-cover rounded-t-xl"
                  style={{ maxHeight: '700px' }}
                  onTimeUpdate={handleTimeUpdate}
                  onLoadedMetadata={handleLoadedMetadata}
                  onEnded={handleVideoEnd}
                  onClick={togglePlayPause}
                />
                
                <div className="absolute inset-0 flex items-center justify-center">
                  <button
                    onClick={togglePlayPause}
                    className={`p-4 rounded-full bg-black/50 hover:bg-black/70 text-white transition-all ${
                      isPlaying ? 'opacity-0 hover:opacity-100' : 'opacity-100'
                    }`}
                  >
                    {isPlaying ? (
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6" />
                      </svg>
                    ) : (
                      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                      </svg>
                    )}
                  </button>
                </div>

                {/* Custom Progress Bar */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-4">
                  <div className="flex items-center space-x-2 text-white text-sm">
                    <span>{formatTime(currentTime)}</span>
                    <div 
                      className="flex-1 h-2 bg-white/30 rounded-full cursor-pointer"
                      onClick={handleSeek}
                    >
                      <div 
                        className="h-full bg-white rounded-full transition-all"
                        style={{ width: duration > 0 ? `${(currentTime / duration) * 100}%` : '0%' }}
                      />
                    </div>
                    <span>{formatTime(duration)}</span>
                  </div>
                </div>
              </div>

              {videos.length > 1 && (
                <>
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
                </>
              )}
            </div>

            <div className="p-6 bg-white">
              <div className="flex items-center justify-between mb-4">
                <div className="text-sm text-gray-600">
                  Created: {formatDate(videos[currentIndex].created_at)}
                </div>
              </div>
              {videos[currentIndex].description && (
                <p className="text-gray-700">
                  {videos[currentIndex].description}
                </p>
              )}
            </div>

            {videos.length > 1 && (
              <div className="px-6 pb-6 bg-white flex items-center justify-center space-x-2">
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
            )}
          </div>
        </div>
      )}
    </div>
  );
}
