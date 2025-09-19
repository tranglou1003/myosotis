import axios from 'axios';
import type { LifeEvent, LifeEventInput, StoriesApiResponse } from '../types/memory';

const storiesAPI = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});


export const getStoriesByUserId = async (userId: number, skip = 0, limit = 10): Promise<StoriesApiResponse> => {
  try {
    const response = await storiesAPI.get(`/api/v1/stories/user/${userId}?skip=${skip}&limit=${limit}`);
    console.log('Stories response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching stories:', error);
    throw error;
  }
};


export const getStoryById = async (storyId: number): Promise<{ data: LifeEvent }> => {
  try {
    const response = await storiesAPI.get(`/api/v1/stories/${storyId}`);
    console.log('Story response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching story:', error);
    throw error;
  }
};


export const createStory = async (storyData: LifeEventInput & { user_id: number }, file?: File): Promise<{ data: LifeEvent }> => {
  try {
    const formData = new FormData();
    formData.append('user_id', storyData.user_id.toString());
    formData.append('title', storyData.title);
    formData.append('type', storyData.type);
    formData.append('description', storyData.description);
    formData.append('start_time', storyData.start_time);
    if (storyData.end_time) {
      formData.append('end_time', storyData.end_time);
    }
    if (file) {
      formData.append('file', file);
    }

    const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/v1/stories/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('Create story response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error creating story:', error);
    throw error;
  }
};


export const updateStory = async (storyId: number, storyData: Partial<LifeEventInput>): Promise<{ data: LifeEvent }> => {
  try {
    const response = await storiesAPI.put(`/api/v1/stories/${storyId}`, storyData);
    console.log('Update story response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error updating story:', error);
    throw error;
  }
};


export const updateStoryFile = async (storyId: number, file: File): Promise<{ data: LifeEvent }> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.put(`${import.meta.env.VITE_API_URL}/api/v1/stories/${storyId}/file`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('Update story file response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error updating story file:', error);
    throw error;
  }
};


export const deleteStory = async (storyId: number): Promise<{ success: boolean }> => {
  try {
    const response = await storiesAPI.delete(`/api/v1/stories/${storyId}`);
    console.log('Delete story response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error deleting story:', error);
    throw error;
  }
};


export const getMediaUrl = (filePath: string): string => {
  if (!filePath) return '';
  if (filePath.startsWith('http')) {
    return filePath;
  }
  const baseUrl = import.meta.env.VITE_API_URL;
  return `${baseUrl}/${filePath}`;
};


export const getStoryFileUrl = (storyId: number): string => {
  const baseUrl = import.meta.env.VITE_API_URL;
  return `${baseUrl}/api/v1/stories/${storyId}/file`;
};
