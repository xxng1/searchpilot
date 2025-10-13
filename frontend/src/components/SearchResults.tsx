import { useQuery } from '@tanstack/react-query'
import { searchAPI } from '../api/search'
import { SearchParams } from '../types'
import SearchItem from './SearchItem'
import Pagination from './Pagination'

interface SearchResultsProps {
  searchParams: SearchParams
  onPageChange: (page: number) => void
}

const SearchResults = ({ searchParams, onPageChange }: SearchResultsProps) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['search', searchParams],
    queryFn: () => searchAPI.search(searchParams),
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-800 rounded-lg p-6 text-center">
        <div className="text-4xl mb-4">❌</div>
        <h3 className="text-xl font-semibold text-red-400 mb-2">검색 오류</h3>
        <p className="text-gray-400">검색 중 오류가 발생했습니다. 다시 시도해주세요.</p>
      </div>
    )
  }

  if (!data || data.total === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-12 text-center">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-2xl font-semibold text-white mb-2">검색 결과 없음</h3>
        <p className="text-gray-400">
          '{searchParams.q}'에 대한 검색 결과가 없습니다.
        </p>
      </div>
    )
  }

  return (
    <div>
      {/* Results header */}
      <div className="flex items-center justify-between mb-6">
        <div className="text-gray-300">
          총 <span className="font-semibold text-white">{data.total.toLocaleString()}</span>개의 결과
          <span className="ml-4 text-sm text-gray-500">
            ({data.response_time_ms.toFixed(1)}ms)
          </span>
        </div>
        
        {/* Sorting options */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-400">정렬:</span>
          <select className="bg-gray-800 text-white px-3 py-1 rounded border border-gray-700 text-sm">
            <option>관련도</option>
            <option>최신순</option>
            <option>인기순</option>
            <option>가격순</option>
          </select>
        </div>
      </div>

      {/* Facets */}
      {data.facets && data.facets.categories && Object.keys(data.facets.categories).length > 0 && (
        <div className="mb-6 bg-gray-800 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-3">카테고리별 결과</div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(data.facets.categories).map(([category, count]) => (
              <div
                key={category}
                className="px-3 py-1 bg-gray-700 text-gray-300 rounded text-sm"
              >
                {category} ({count})
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Results list */}
      <div className="space-y-4">
        {data.items.map((item) => (
          <SearchItem key={item.id} item={item} />
        ))}
      </div>

      {/* Pagination */}
      {data.total_pages > 1 && (
        <div className="mt-8">
          <Pagination
            currentPage={data.page}
            totalPages={data.total_pages}
            onPageChange={onPageChange}
          />
        </div>
      )}
    </div>
  )
}

export default SearchResults

