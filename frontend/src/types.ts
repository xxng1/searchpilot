export interface SearchItem {
  id: number
  title: string
  description: string | null
  category: string | null
  tags: string | null
  price: number | null
  popularity: number
  created_at: string
  updated_at: string
  highlight: string | null
}

export interface SearchResponse {
  query: string
  total: number
  page: number
  size: number
  total_pages: number
  items: SearchItem[]
  response_time_ms: number
  facets: {
    categories: Record<string, number>
  } | null
}

export interface SearchParams {
  q: string
  category?: string
  min_price?: number
  max_price?: number
  sort?: string
  order?: string
  page: number
  size: number
}

export interface AutocompleteResponse {
  suggestions: string[]
  response_time_ms: number
}

export interface SearchStats {
  total_items: number
  total_searches: number
  avg_response_time_ms: number
  popular_queries: Array<{
    query: string
    count: number
    avg_time_ms: number
  }>
}

export interface SuggestionResponse {
  popular: string[]
  recent: string[]
}

