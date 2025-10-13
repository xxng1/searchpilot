import axios from 'axios'
import { SearchResponse, SearchParams, AutocompleteResponse, SearchStats, SuggestionResponse } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const searchAPI = {
  search: async (params: SearchParams): Promise<SearchResponse> => {
    const response = await apiClient.get<SearchResponse>('/api/search', { params })
    return response.data
  },

  autocomplete: async (q: string, limit: number = 10): Promise<AutocompleteResponse> => {
    const response = await apiClient.get<AutocompleteResponse>('/api/autocomplete', {
      params: { q, limit }
    })
    return response.data
  },

  getSuggestions: async (): Promise<SuggestionResponse> => {
    const response = await apiClient.get<SuggestionResponse>('/api/suggestions')
    return response.data
  },

  getStats: async (): Promise<SearchStats> => {
    const response = await apiClient.get<SearchStats>('/api/search/stats')
    return response.data
  },
}

