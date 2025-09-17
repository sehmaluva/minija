const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api"

export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}

export interface PaginatedResponse<T> {
  results: T[]
  count: number
  next: string | null
  previous: string | null
}

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null
  }

  setToken(token: string) {
    this.token = token
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token")
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // Auth endpoints
  async login(email: string, password: string) {
    return this.request<{ access: string; refresh: string; user: any }>("/auth/login/", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })
  }

  async register(userData: any) {
    return this.request<{ access: string; refresh: string; user: any }>("/auth/register/", {
      method: "POST",
      body: JSON.stringify(userData),
    })
  }

  async refreshToken(refresh: string) {
    return this.request<{ access: string }>("/auth/refresh/", {
      method: "POST",
      body: JSON.stringify({ refresh }),
    })
  }

  // Farm endpoints
  async getFarms() {
    return this.request<PaginatedResponse<any>>("/farms/")
  }

  async createFarm(farmData: any) {
    return this.request<any>("/farms/", {
      method: "POST",
      body: JSON.stringify(farmData),
    })
  }

  async updateFarm(id: number, farmData: any) {
    return this.request<any>(`/farms/${id}/`, {
      method: "PUT",
      body: JSON.stringify(farmData),
    })
  }

  // Flock endpoints
  async getFlocks(farmId?: number) {
    const endpoint = farmId ? `/flocks/?farm=${farmId}` : "/flocks/"
    return this.request<PaginatedResponse<any>>(endpoint)
  }

  async createFlock(flockData: any) {
    return this.request<any>("/flocks/", {
      method: "POST",
      body: JSON.stringify(flockData),
    })
  }

  // Health endpoints
  async getHealthRecords(flockId?: number) {
    const endpoint = flockId ? `/health/records/?flock=${flockId}` : "/health/records/"
    return this.request<PaginatedResponse<any>>(endpoint)
  }

  async createHealthRecord(recordData: any) {
    return this.request<any>("/health/records/", {
      method: "POST",
      body: JSON.stringify(recordData),
    })
  }

  // Production endpoints
  async getProductionRecords(flockId?: number) {
    const endpoint = flockId ? `/production/records/?flock=${flockId}` : "/production/records/"
    return this.request<PaginatedResponse<any>>(endpoint)
  }

  async createProductionRecord(recordData: any) {
    return this.request<any>("/production/records/", {
      method: "POST",
      body: JSON.stringify(recordData),
    })
  }

  // Reports endpoints
  async getDashboardStats() {
    return this.request<any>("/reports/dashboard/")
  }

  async getProductionReport(params: any) {
    const queryString = new URLSearchParams(params).toString()
    return this.request<any>(`/reports/production/?${queryString}`)
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
