interface HeaderProps {
  onLogoClick?: () => void
}

const Header = ({ onLogoClick }: HeaderProps) => {
  return (
    <header className="bg-gray-900 border-b border-gray-800">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <button 
            onClick={onLogoClick}
            className="flex items-center space-x-3 hover:opacity-80 transition-opacity cursor-pointer"
          >
            <div className="text-3xl">🔍</div>
            <div className="text-left">
              <h1 className="text-2xl font-bold text-white">SearchPilot</h1>
              <p className="text-sm text-gray-400">고성능 검색 플랫폼</p>
            </div>
          </button>
          <div className="flex items-center space-x-4">
            <a 
              href="http://localhost:8000/docs" 
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
            >
              API 문서
            </a>
            <a 
              href="http://localhost:9090" 
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
            >
              모니터링
            </a>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header

