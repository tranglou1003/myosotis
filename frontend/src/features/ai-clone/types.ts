export interface AICloneVideo {
  id: number;
  status: 'completed' | 'failed' | 'processing';
  video_url: string | null;
  video_filename: string | null;
  target_text: string;
  reference_text: string;
  is_ai_generated_text: boolean;
  topic: string | null;
  description: string | null;
  keywords: string | null;
  error_message: string | null;
  created_at: string;
}

export interface CreateVideoFullTextPayload {
  user_id: number;
  image: File;
  reference_audio: File;
  reference_text: string;
  target_text: string;
  language?: string;
  dynamic_scale?: number;
}

export interface CreateVideoFromTopicPayload {
  user_id: number;
  image: File;
  reference_audio: File;
  reference_text: string;
  topic: string;
  keywords?: string;
  description?: string;
  language?: string;
}

export interface CreateVideoResponse {
  success: boolean;
  video_id: number;
  video_url?: string;
  video_filename?: string;
  status: 'completed' | 'failed' | 'processing';
  message: string;
  generated_target_text?: string;
  error?: string;
  timeout?: boolean; // Added to handle 504 timeout responses
}

export interface UserVideosResponse {
  success: boolean;
  user_id: number;
  total_videos: number;
  videos: AICloneVideo[];
}

export interface WizardStepData {
  
  characterPhoto?: File;
  characterPhotoPreview?: string;
  referenceAudio?: File;
  referenceText: string;
  
  
  scriptMode: 'manual' | 'ai-generated';
  manualScript?: string;
  topic?: string;
  keywords?: string;
  description?: string;
  
  
  finalScript?: string;
  generatedVideoUrl?: string;
  isGenerating?: boolean;
}

export type WizardStep = 1 | 2 | 3;
