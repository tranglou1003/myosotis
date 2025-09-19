export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  profile: {
    full_name: string;
  };
}

export interface Profile {
  id: number;
  user_id: number;
  full_name: string;
  date_of_birth?: string;
  gender?: 'male' | 'female';
  phone?: string;
  address?: string;
  avatar_url?: string;
  emergency_contact?: string;
  city?: string;
  hometown?: string;
  country?: string;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  phone?: string;
  created_at: string;
  updated_at?: string | null;
  profile?: Profile;
  emergency_contacts?: unknown;
}

export interface LoginResponseData {
  user_id: number;
  email: string;
  full_name: string;
  message?: string;
}

export interface RegisterResponseData {
  id: number;
  email: string;
  phone?: string;
  created_at: string;
  updated_at?: string | null;
  profile?: Profile;
  emergency_contacts?: unknown;
}

export interface ApiResponse<T> {
  http_code: number;
  success: boolean;
  message: string | null;
  metadata: unknown;
  data: T;
}

export interface AuthState {
  user: User | null;
  loginData: LoginResponseData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthActions {
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  updateUser: (user: User) => void;
}
