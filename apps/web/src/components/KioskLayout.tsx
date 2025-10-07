import { ReactNode } from 'react'

interface KioskLayoutProps {
  children: ReactNode
}

export default function KioskLayout({ children }: KioskLayoutProps) {
  return (
    <div className="min-h-screen bg-primary-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-center h-16 items-center">
            <h1 className="text-2xl font-bold text-primary-900">
              Bakersfield eSports Center
            </h1>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-4 text-center text-sm text-gray-600">
            Need help? Please ask a staff member.
          </div>
        </div>
      </footer>
    </div>
  )
}