export type User = {
  id: number;
  email: string;
  full_name: string;
  is_admin: boolean;
  subscription_tier: string;
  skill_profile?: Record<string, any>;
  created_at?: string;
};

export type UserProfile = {
  id: number;
  email: string;
  full_name: string;
  is_admin: boolean;
};

export type AuthToken = {
  access_token: string;
  token_type: string;
};

export type ChangePasswordRequest = {
  current_password: string;
  new_password: string;
};
