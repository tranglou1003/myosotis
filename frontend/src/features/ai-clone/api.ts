import axios from 'axios';
import type {
  CreateVideoFullTextPayload,
  CreateVideoFromTopicPayload,
  CreateVideoResponse,
  UserVideosResponse,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL;

export async function createVideoWithFullText(
  payload: CreateVideoFullTextPayload
): Promise<CreateVideoResponse> {
  const formData = new FormData();
  
  formData.append('user_id', payload.user_id.toString());
  formData.append('image', payload.image);
  formData.append('reference_audio', payload.reference_audio);
  formData.append('reference_text', payload.reference_text);
  formData.append('target_text', payload.target_text);
  
  if (payload.language) {
    formData.append('language', payload.language);
  }
  
  if (payload.dynamic_scale) {
    formData.append('dynamic_scale', payload.dynamic_scale.toString());
  }

  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/ai-clone/create-video-full-text-form`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 600000, 
      }
    );

    return response.data;
  } catch (error: unknown) {
    
    const axiosError = error as { response?: { status?: number }; code?: string };
    if (axiosError.response?.status === 504 || axiosError.code === 'ECONNABORTED') {
      return {
        success: true,
        video_id: Date.now(), 
        status: 'processing',
        message: 'Video generation started successfully. It will be available in your history soon.',
        timeout: true
      } as CreateVideoResponse & { timeout: boolean };
    }
    throw error;
  }
}

export async function createVideoFromTopic(
  payload: CreateVideoFromTopicPayload
): Promise<CreateVideoResponse> {
  const formData = new FormData();
  
  formData.append('user_id', payload.user_id.toString());
  formData.append('image', payload.image);
  formData.append('reference_audio', payload.reference_audio);
  formData.append('reference_text', payload.reference_text);
  formData.append('topic', payload.topic);
  
  if (payload.keywords) {
    formData.append('keywords', payload.keywords);
  }
  
  if (payload.description) {
    formData.append('description', payload.description);
  }
  
  if (payload.language) {
    formData.append('language', payload.language);
  }

  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/ai-clone/create-video-from-topic-form`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 600000,
      }
    );

    return response.data;
  } catch (error: unknown) {
    
    const axiosError = error as { response?: { status?: number }; code?: string };
    if (axiosError.response?.status === 504 || axiosError.code === 'ECONNABORTED') {
      return {
        success: true,
        video_id: Date.now(), 
        status: 'processing',
        message: 'Video generation started successfully. It will be available in your history soon.',
        timeout: true
      } as CreateVideoResponse & { timeout: boolean };
    }
    throw error;
  }
}

export async function getUserVideos(userId: number): Promise<UserVideosResponse> {
  const response = await axios.get(
    `${API_BASE_URL}/api/v1/ai-clone/user-videos/${userId}`
  );

  return response.data;
}

export function getVideoUrl(videoFilename: string): string {
  if (videoFilename.startsWith('http')) {
    return videoFilename;
  }
  
  const filename = videoFilename.split('/').pop() || videoFilename;
  return `${API_BASE_URL}/api/v1/ai-clone/human-clone/view/${filename}.mp4`;
}
