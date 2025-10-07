// API Types
export interface User {
  id: string
  email: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Client {
  id: string
  first_name: string
  last_name: string
  date_of_birth?: string
  email?: string
  phone?: string
  external_ids: Record<string, any>
  created_at: string
  updated_at: string
  tags: Tag[]
  contact_methods: ContactMethod[]
  consents: Consent[]
  membership_status?: 'active' | 'expiring' | 'expired' | null
  membership_end_date?: string | null
  membership_plan?: string | null
  // POS fields
  parent_guardian_name?: string | null
  pos_number?: string | null
  service_coordinator?: string | null
  pos_start_date?: string | null
  pos_end_date?: string | null
  notes?: string | null
  language?: string | null
}

export interface Tag {
  id: string
  name: string
  description?: string
  color?: string
  created_at: string
}

export interface ContactMethod {
  id: string
  type: 'sms' | 'email' | 'discord'
  value: string
  verified: boolean
  created_at: string
}

export interface Consent {
  id: string
  kind: 'sms' | 'email' | 'photo' | 'tos' | 'waiver'
  granted: boolean
  granted_at?: string
  source?: string
  created_at: string
}

export interface Membership {
  id: string
  client_id: string
  plan_code: string
  starts_on: string
  ends_on: string
  status: 'active' | 'expired' | 'pending'
  notes?: string
  created_at: string
  updated_at: string
}

export interface CheckIn {
  id: string
  client_id: string
  method: 'kiosk' | 'staff'
  station?: string
  happened_at: string
  notes?: string
  created_at: string
  client_name?: string
  client_first_name?: string
  client_last_name?: string
  client_email?: string
  client_phone?: string
}

// Form Types
export interface LoginForm {
  email: string
  password: string
}

export interface ClientForm {
  first_name: string
  last_name: string
  date_of_birth?: string
  email?: string
  phone?: string
  external_ids?: Record<string, any>
  parent_guardian_name?: string
  pos_number?: string
  service_coordinator?: string
  pos_start_date?: string
  pos_end_date?: string
  notes?: string
  language?: string
}

export interface MembershipForm {
  plan_code: string
  starts_on: string
  ends_on: string
  notes?: string
}

export interface CheckInForm {
  client_id?: string
  phone?: string
  code?: string
  station?: string
  method: 'kiosk' | 'staff'
  notes?: string
}

export interface KioskCheckInForm {
  phone?: string
  code?: string
  station?: string
}

// API Response Types
export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface ApiError {
  error: string
  type?: string
  details?: any
}

// Stats Types
export interface MembershipStats {
  total_active: number
  total_expired: number
  total_pending: number
  expiring_30_days: number
  expiring_7_days: number
  plans: Record<string, number>
}

export interface CheckInStats {
  today: number
  this_week: number
  this_month: number
  unique_clients_today: number
  unique_clients_week: number
  unique_clients_month: number
  popular_stations: Record<string, number>
}