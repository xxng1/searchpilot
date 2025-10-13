import { useQuery } from '@tanstack/react-query'
import { searchAPI } from '../api/search'

const SearchStats = () => {
  const { data } = useQuery({
    queryKey: ['stats'],
    queryFn: () => searchAPI.getStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  if (!data) return null

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">📊 검색 통계</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <div className="text-sm text-gray-400 mb-1">전체 아이템</div>
          <div className="text-2xl font-bold text-white">
            {data.total_items.toLocaleString()}
          </div>
        </div>
        
        <div>
          <div className="text-sm text-gray-400 mb-1">총 검색 수</div>
          <div className="text-2xl font-bold text-white">
            {data.total_searches.toLocaleString()}
          </div>
        </div>
        
        <div>
          <div className="text-sm text-gray-400 mb-1">평균 응답 시간</div>
          <div className="text-2xl font-bold text-primary-400">
            {data.avg_response_time_ms.toFixed(1)}ms
          </div>
        </div>
      </div>

      {data.popular_queries.length > 0 && (
        <div className="mt-6">
          <div className="text-sm text-gray-400 mb-3">인기 검색어 TOP 5</div>
          <div className="space-y-2">
            {data.popular_queries.slice(0, 5).map((item, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <span className="text-gray-300">
                  {index + 1}. {item.query}
                </span>
                <span className="text-gray-500">
                  {item.count}회 · {item.avg_time_ms.toFixed(1)}ms
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SearchStats

