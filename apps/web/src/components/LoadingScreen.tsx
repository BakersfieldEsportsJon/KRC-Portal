export default function LoadingScreen() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center">
      <div className="text-center">
        {/* Logo placeholder - replace with your actual logo */}
        <div className="mx-auto mb-8">
          <img
            src="/logo-large.svg"
            alt="BEC Logo"
            className="h-32 w-auto mx-auto"
            onError={(e) => {
              // Fallback if logo doesn't exist yet
              e.currentTarget.style.display = 'none'
              const fallback = e.currentTarget.nextElementSibling
              if (fallback) fallback.classList.remove('hidden')
            }}
          />
          {/* Fallback text logo if image doesn't exist */}
          <div className="hidden">
            <div className="text-6xl font-bold text-primary-600">BEC</div>
            <div className="text-xl text-primary-500 mt-2">Gaming Center</div>
          </div>
        </div>

        {/* Animated spinner */}
        <div className="flex justify-center mb-6">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary-200 border-t-primary-600"></div>
        </div>

        {/* Loading text */}
        <p className="text-lg text-primary-700 font-medium">Loading...</p>
      </div>
    </div>
  )
}
