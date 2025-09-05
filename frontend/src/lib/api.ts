import axios from 'axios'
import { API_BASE_URL } from '../config'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})

export const unwrap = <T>(data: unknown): T => {
  const maybePagedData = data as { results?: T }
  return maybePagedData?.results ?? (data as T)
}

export const get = async <T>(
  url: string,
  params?: Record<string, unknown>
): Promise<T> => {
  const { data } = await api.get(url, { params })
  return unwrap<T>(data)
}
export const post = async <T>(url: string, body?: unknown): Promise<T> => {
  const { data } = await api.post(url, body)
  return unwrap<T>(data)
}
export const put = async <T>(url: string, body?: unknown): Promise<T> => {
  const { data } = await api.put(url, body)
  return unwrap<T>(data)
}
export const del = async <T>(url: string): Promise<T> => {
  const { data } = await api.delete(url)
  return unwrap<T>(data)
}
