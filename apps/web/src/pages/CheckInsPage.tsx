import { useQuery } from 'react-query'
import apiService from '../services/api'
import { Calendar, User } from 'lucide-react'

export default function CheckInsPage() {
  const { data: checkIns, isLoading } = useQuery(
    'checkIns',
    () => apiService.getCheckIns({ limit: 100 })
  )

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Check-ins</h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            View recent client check-ins at your gaming center
          </p>
        </div>
      </div>

      {/* Check-ins List */}
      <div className="mt-8 card">
        <div className="overflow-hidden">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Client
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Method
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Station
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Notes
                </th>
              </tr>
            </thead>
            <tbody className="table-body">
              {checkIns?.map((checkIn) => (
                <tr key={checkIn.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    <div className="flex items-center">
                      <User className="w-4 h-4 mr-2 text-gray-400 dark:text-gray-500" />
                      {checkIn.client_first_name} {checkIn.client_last_name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-2 text-gray-400 dark:text-gray-500" />
                      <div>
                        <div>{new Date(checkIn.happened_at).toLocaleDateString()}</div>
                        <div className="text-xs text-gray-400 dark:text-gray-500">
                          {new Date(checkIn.happened_at).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        checkIn.method === 'kiosk'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-purple-100 text-purple-800'
                      }`}
                    >
                      {checkIn.method === 'kiosk' ? 'Kiosk' : 'Staff'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {checkIn.station || 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                    {checkIn.notes || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {(!checkIns || checkIns.length === 0) && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">No check-ins recorded yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
