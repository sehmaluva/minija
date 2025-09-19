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
      // Django TokenAuthentication expects 'Token <key>'
      headers.Authorization = `Token ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      // Try to build a useful message from possible error shapes
      let msg = errorData.message || ''
      if (!msg) {
        if (typeof errorData === 'string') msg = errorData
        else if (Array.isArray(errorData)) msg = errorData.join(' ')
        else if (typeof errorData === 'object' && errorData !== null) {
          // collect values (arrays or strings)
          const parts: string[] = []
          Object.values(errorData).forEach((v) => {
            if (Array.isArray(v)) parts.push(v.join(' '))
            else if (typeof v === 'string') parts.push(v)
            else if (typeof v === 'object') parts.push(JSON.stringify(v))
          })
          msg = parts.join(' ')
        }
      }

      throw new Error(msg || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // Auth endpoints
  // Backend returns { user, token, message }
  async login(email: string, password: string) {
    return this.request<{ user: any; token: string; message?: string }>("/auth/login/", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })
  }

  async register(userData: any) {
    return this.request<{ user: any; token: string; message?: string }>("/auth/register/", {
      method: "POST",
      body: JSON.stringify(userData),
    })
  }

  async refreshToken(refresh: string) {
    // If backend does not provide refresh endpoints, leave as placeholder
    return this.request<any>("/auth/refresh/", {
      method: "POST",
      body: JSON.stringify({ refresh }),
    })
  }

  // Farm endpoints
  // (Farms endpoints removed for broiler-focused product)

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
  // (Health endpoints removed — not part of broiler minimal product)

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

  // Accounting endpoints (basic)
  async getSales() {
    return this.request<PaginatedResponse<any>>("/accounting/sales/")
  }

  async getCosts() {
    return this.request<PaginatedResponse<any>>("/accounting/costs/")
  }

  // Orders endpoints (basic)
  async getOrders() {
    return this.request<PaginatedResponse<any>>("/orders/")
  }

  async createOrder(data: any) {
    return this.request<any>("/orders/", { method: "POST", body: JSON.stringify(data) })
  }

  // Forecast endpoints (basic)
  async getForecasts() {
    return this.request<any>("/forecast/predict/feed/")
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
