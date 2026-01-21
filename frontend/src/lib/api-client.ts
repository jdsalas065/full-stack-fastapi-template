import axios, { type AxiosError } from "axios"
import { ApiError } from "./types"

// Create axios instance
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: false,
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status || 0
    const statusText = error.response?.statusText || "Unknown Error"
    const body = error.response?.data || null

    // Create ApiError for consistency with old client
    const apiError = new ApiError(status, statusText, body, error.message)

    return Promise.reject(apiError)
  },
)
