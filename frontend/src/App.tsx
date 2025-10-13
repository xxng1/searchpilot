import { useState } from 'react'
import SearchBar from './components/SearchBar'
import SearchResults from './components/SearchResults'
import SearchStats from './components/SearchStats'
import Header from './components/Header'
import { SearchParams } from './types'

function App() {
  const [searchParams, setSearchParams] = useState<SearchParams>({
    q: '',
    page: 1,
    size: 20,
  })

  const handleSearch = (params: SearchParams) => {
    setSearchParams(params)
  }

  const handleReset = () => {
    setSearchParams({
      q: '',
      page: 1,
      size: 20,
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <Header onLogoClick={handleReset} />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Search Bar */}
          <div className="mb-8">
            <SearchBar onSearch={handleSearch} />
          </div>

          {/* Search Stats - Always visible */}
          <div className="mb-6">
            <SearchStats />
          </div>

          {/* Search Results */}
          {searchParams.q && (
            <SearchResults searchParams={searchParams} onPageChange={(page) => {
              setSearchParams({ ...searchParams, page })
            }} />
          )}

          {/* Welcome Message */}
          {!searchParams.q && (
            <div className="text-center py-20">
              <div className="text-6xl mb-6">🔍</div>
              <h2 className="text-4xl font-bold text-white mb-4">
                SearchPilot에 오신 것을 환영합니다
              </h2>
              <p className="text-gray-400 text-lg">
                10만 건 이상의 데이터를 빠르고 정확하게 검색하세요
              </p>
            </div>
          )}
        </div>
      </main>

      <footer className="mt-20 py-8 border-t border-gray-800">
        <div className="container mx-auto px-4 text-center text-gray-500">
          <p>© 2024 SearchPilot. 고성능 검색 플랫폼</p>
        </div>
      </footer>
    </div>
  )
}

export default App

