const Header = () => {
  return (
    <header className="bg-gray-900 border-b border-gray-800">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-3xl">🔍</div>
            <div>
              <h1 className="text-2xl font-bold text-white">SearchPilot</h1>
              <p className="text-sm text-gray-400">고성능 검색 플랫폼</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <a 
              href="/docs" 
              className="text-gray-400 hover:text-white transition-colors"
            >
              API 문서
            </a>
            <a 
              href="/metrics" 
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

