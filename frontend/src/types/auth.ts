export type Role = "owner" | "admin" | "analyst" | "viewer";

export interface Organization {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
}

export interface User {
  id: string;
  organization_id: string;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  user: User;
  organization: Organization;
  tokens: TokenResponse;
}

export interface LoginPayload {
  organization_slug: string;
  email: string;
  password: string;
}

export interface SignupPayload {
  organization_name: string;
  organization_slug: string;
  email: string;
  full_name: string;
  password: string;
}

export interface CreateApiKeyPayload {
  name: string;
}

export interface CreateApiKeyResponse {
  id: string;
  api_key: string;
  key_prefix: string;
  name: string;
  webhook_signing_secret?: string | null;
}

export interface ApiKeyListItem {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
  has_webhook_signing_secret: boolean;
}
