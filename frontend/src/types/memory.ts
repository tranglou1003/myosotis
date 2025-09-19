export interface LifeEvent {
  id: number;
  user_id: number;
  title: string;
  type: 'image' | 'video' | 'audio';
  description: string;
  file_path?: string;
  start_time: string;
  end_time?: string;
  created_at: string;
  updated_at: string;
}

export interface LifeEventInput {
  title: string;
  type: 'image' | 'video' | 'audio';
  description: string;
  file_path?: string;
  start_time: string;
  end_time?: string;
}

export interface StoriesApiResponse {
  http_code: number;
  success: boolean;
  message: string;
  metadata: {
    total: number;
    skip: number;
    limit: number;
    user_id: number;
  };
  data: LifeEvent[];
}
