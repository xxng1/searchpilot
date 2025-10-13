import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { searchAPI } from '../api/search'
import { SearchParams } from '../types'

interface SearchBarProps {
  onSearch: (params: SearchParams) => void
}

const SearchBar = ({ onSearch }: SearchBarProps) => {
  const [query, setQuery] = useState('')
  const [showAutocomplete, setShowAutocomplete] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)
  const autocompleteRef = useRef<HTMLDivElement>(null)

  // Autocomplete query
  const { data: autocompleteData } = useQuery({
    queryKey: ['autocomplete', query],
    queryFn: () => searchAPI.autocomplete(query),
    enabled: query.length >= 2,
  })

  // Suggestions query
  const { data: suggestionsData } = useQuery({
    queryKey: ['suggestions'],
    queryFn: () => searchAPI.getSuggestions(),
  })

  // Handle click outside autocomplete
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (autocompleteRef.current && !autocompleteRef.current.contains(event.target as Node)) {
        setShowAutocomplete(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch({
        q: query.trim(),
        category: selectedCategory || undefined,
        page: 1,
        size: 20,
      })
      setShowAutocomplete(false)
    }
  }

  const handleQueryChange = (value: string) => {
    setQuery(value)
    setShowAutocomplete(value.length >= 2)
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion)
    setShowAutocomplete(false)
    onSearch({
      q: suggestion,
      category: selectedCategory || undefined,
      page: 1,
      size: 20,
    })
  }

  return (
    <div className="relative" ref={autocompleteRef}>
      <form onSubmit={handleSubmit}>
        <div className="bg-white rounded-lg shadow-2xl overflow-hidden">
          {/* Main search input */}
          <div className="flex items-center p-4">
            <input
              type="text"
              value={query}
              onChange={(e) => handleQueryChange(e.target.value)}
              placeholder="검색어를 입력하세요..."
              className="flex-1 text-lg outline-none text-gray-800"
              autoFocus
            />
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              ⚙️ 필터
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              검색
            </button>
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="border-t border-gray-200 p-4 bg-gray-50">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    카테고리
                  </label>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">전체</option>
                    <option value="전자제품">전자제품</option>
                    <option value="의류">의류</option>
                    <option value="도서">도서</option>
                    <option value="식품">식품</option>
                    <option value="가구">가구</option>
                    <option value="스포츠">스포츠</option>
                    <option value="완구">완구</option>
                    <option value="화장품">화장품</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </form>

      {/* Autocomplete dropdown */}
      {showAutocomplete && autocompleteData && autocompleteData.suggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-2 bg-white rounded-lg shadow-xl border border-gray-200 overflow-hidden">
          <div className="p-2">
            <div className="text-xs text-gray-500 px-3 py-2">자동완성</div>
            {autocompleteData.suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full text-left px-3 py-2 hover:bg-gray-100 rounded transition-colors text-gray-800"
              >
                🔍 {suggestion}
              </button>
            ))}
            <div className="text-xs text-gray-400 px-3 py-2 text-right">
              {autocompleteData.response_time_ms.toFixed(1)}ms
            </div>
          </div>
        </div>
      )}

      {/* Suggestions (popular & recent) */}
      {!query && suggestionsData && (
        <div className="mt-4 flex flex-wrap gap-4">
          {suggestionsData.popular.length > 0 && (
            <div>
              <div className="text-sm text-gray-400 mb-2">🔥 인기 검색어</div>
              <div className="flex flex-wrap gap-2">
                {suggestionsData.popular.map((term, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(term)}
                    className="px-3 py-1 bg-gray-800 text-white rounded-full text-sm hover:bg-gray-700 transition-colors"
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default SearchBar

