export interface EmergencyContact {
  id: number;
  user_id: number;
  contact_name: string;
  relation: string;
  phone: string;
  email: string;
  address: string;
  is_primary: boolean;
  created_at: string;
}

export interface EmergencyContactPayload {
  contact_name: string;
  relation: string;
  phone: string;
  email: string;
  address: string;
  is_primary?: boolean;
}

export interface UserProfile {
  id: number;
  user_id: number;
  full_name: string;
  date_of_birth: string;
  gender: string;
  phone: string;
  address: string;
  avatar_url: string;
  emergency_contact: string;
  city?: string;
  hometown?: string;
  country?: string;
  created_at: string;
}

export interface UserData {
  id: number;
  email: string;
  phone: string;
  created_at: string;
  updated_at: string;
  profile: UserProfile;
  emergency_contacts: EmergencyContact[];
}

export interface UserApiResponse {
  http_code: number;
  success: boolean;
  message: string | null;
  metadata: unknown;
  data: UserData;
}

export interface UserUpdatePayload {
  phone?: string;
  email?: string;
  full_name?: string;
  date_of_birth?: string;
  gender?: string;
  address?: string;
  avatar_url?: string;
  city?: string;
  hometown?: string;
  country?: string;
  profile?: {
    full_name?: string;
    date_of_birth?: string;
    gender?: string;
    address?: string;
    avatar_url?: string;
    city?: string;
    hometown?: string;
    country?: string;
  };
}
