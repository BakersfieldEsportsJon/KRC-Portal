import axios, { AxiosInstance, AxiosResponse } from 'axios'
import toast from 'react-hot-toast'
import {
  User,
  Client,
  Membership,
  CheckIn,
  LoginForm,
  LoginResponse,
  ClientForm,
  MembershipForm,
  CheckInForm,
  KioskCheckInForm,
  MembershipStats,
  CheckInStats,
  Tag,
  ApiError
} from '../types'

class ApiService {
  private api: AxiosInstance

  constructor() {
    const apiUrl = import.meta.env.VITE_API_URL || ''
    this.api = axios.create({
      baseURL: apiUrl ? `${apiUrl}/api/v1` : '/api/v1',
      timeout: 10000,
    })

    // Request interceptor to add auth token
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        } else if (error.response?.data?.error) {
          toast.error(error.response.data.error)
        } else {
          toast.error('An unexpected error occurred')
        }
        return Promise.reject(error)
      }
    )
  }

  // Authentication
  async login(credentials: LoginForm): Promise<LoginResponse> {
    const response = await this.api.post<LoginResponse>('/auth/login', credentials)
    return response.data
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/auth/me')
    return response.data
  }

  async logout(): Promise<void> {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  // Clients
  async getClients(params?: {
    query?: string
    tags?: string[]
    limit?: number
    offset?: number
  }): Promise<Client[]> {
    const response = await this.api.get<Client[]>('/clients', { params })
    return response.data
  }

  async getClient(id: string): Promise<Client> {
    const response = await this.api.get<Client>(`/clients/${id}`)
    return response.data
  }

  async createClient(data: ClientForm): Promise<Client> {
    const response = await this.api.post<Client>('/clients', data)
    return response.data
  }

  async updateClient(id: string, data: Partial<ClientForm>): Promise<Client> {
    const response = await this.api.patch<Client>(`/clients/${id}`, data)
    return response.data
  }

  async deleteClient(id: string): Promise<void> {
    await this.api.delete(`/clients/${id}`)
  }

  async addTagsToClient(id: string, tagNames: string[]): Promise<Client> {
    const response = await this.api.post<Client>(`/clients/${id}/tags`, {
      tag_names: tagNames
    })
    return response.data
  }

  async removeTagFromClient(id: string, tagName: string): Promise<Client> {
    const response = await this.api.delete<Client>(`/clients/${id}/tags/${tagName}`)
    return response.data
  }

  // Tags
  async getTags(): Promise<Tag[]> {
    const response = await this.api.get<Tag[]>('/tags')
    return response.data
  }

  // Memberships
  async createMembership(clientId: string, data: MembershipForm): Promise<Membership> {
    const response = await this.api.post<Membership>(`/clients/${clientId}/membership`, data)
    return response.data
  }

  async getClientMembership(clientId: string): Promise<Membership | null> {
    try {
      const response = await this.api.get<Membership>(`/clients/${clientId}/membership`)
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null
      }
      throw error
    }
  }

  async getClientMemberships(clientId: string): Promise<Membership[]> {
    const response = await this.api.get<Membership[]>(`/clients/${clientId}/memberships`)
    return response.data
  }

  async updateMembership(id: string, data: Partial<MembershipForm>): Promise<Membership> {
    const response = await this.api.patch<Membership>(`/memberships/${id}`, data)
    return response.data
  }

  async deleteMembership(id: string): Promise<void> {
    await this.api.delete(`/memberships/${id}`)
  }

  async getExpiringMemberships(days: number = 30): Promise<Membership[]> {
    const response = await this.api.get<Membership[]>('/memberships/expiring', {
      params: { days }
    })
    return response.data
  }

  async getMembershipStats(): Promise<MembershipStats> {
    const response = await this.api.get<MembershipStats>('/memberships/stats')
    return response.data
  }

  // Check-ins
  async createCheckIn(data: CheckInForm): Promise<CheckIn> {
    const response = await this.api.post<CheckIn>('/checkins', data)
    return response.data
  }

  async kioskCheckIn(data: KioskCheckInForm): Promise<CheckIn> {
    const response = await this.api.post<CheckIn>('/checkins/kiosk', data)
    return response.data
  }

  async lookupClient(phone?: string, code?: string): Promise<any> {
    const response = await this.api.get('/checkins/lookup', {
      params: { phone, code }
    })
    return response.data
  }

  async getCheckIns(params?: {
    limit?: number
    offset?: number
  }): Promise<CheckIn[]> {
    const response = await this.api.get<CheckIn[]>('/clients/checkins', { params })
    return response.data
  }

  async getClientCheckIns(clientId: string, params?: {
    limit?: number
    offset?: number
  }): Promise<CheckIn[]> {
    const response = await this.api.get<CheckIn[]>(`/clients/${clientId}/checkins`, { params })
    return response.data
  }

  async getCheckInStats(): Promise<CheckInStats> {
    const response = await this.api.get<CheckInStats>('/checkins/stats')
    return response.data
  }

  // Users/Staff Management (Admin only)
  async getUsers(): Promise<User[]> {
    const response = await this.api.get<User[]>('/users')
    return response.data
  }

  async createUser(data: { email: string; password: string; role: string; is_active: boolean }): Promise<User> {
    const response = await this.api.post<User>('/users', data)
    return response.data
  }

  async updateUser(id: string, data: { email?: string; password?: string; role?: string; is_active?: boolean }): Promise<User> {
    const response = await this.api.patch<User>(`/users/${id}`, data)
    return response.data
  }

  async deleteUser(id: string): Promise<void> {
    await this.api.delete(`/users/${id}`)
  }
}

export const apiService = new ApiService()
export default apiService