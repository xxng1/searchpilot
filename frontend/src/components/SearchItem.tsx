import { SearchItem as SearchItemType } from '../types'

interface SearchItemProps {
  item: SearchItemType
}

const SearchItem = ({ item }: SearchItemProps) => {
  return (
    <div className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors border border-gray-700 hover:border-gray-600">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Title with highlight */}
          <h3 className="text-xl font-semibold text-white mb-2">
            {item.highlight ? (
              <span dangerouslySetInnerHTML={{ __html: item.highlight }} />
            ) : (
              item.title
            )}
          </h3>

          {/* Description */}
          {item.description && (
            <p className="text-gray-400 mb-3 line-clamp-2">
              {item.description}
            </p>
          )}

          {/* Metadata */}
          <div className="flex items-center space-x-4 text-sm">
            {item.category && (
              <span className="px-2 py-1 bg-primary-900/30 text-primary-400 rounded">
                {item.category}
              </span>
            )}
            
            {item.tags && (
              <div className="flex items-center space-x-2">
                {item.tags.split(',').slice(0, 3).map((tag, index) => (
                  <span key={index} className="text-gray-500">
                    #{tag.trim()}
                  </span>
                ))}
              </div>
            )}

            <span className="text-gray-500">
              👍 {item.popularity}
            </span>
          </div>
        </div>

        {/* Price */}
        {item.price !== null && (
          <div className="ml-6 text-right">
            <div className="text-2xl font-bold text-primary-400">
              ₩{item.price.toLocaleString()}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SearchItem

