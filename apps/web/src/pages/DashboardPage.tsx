import { useQuery } from 'react-query'
import apiService from '../services/api'
import { Users, Calendar, LogIn, TrendingUp, User, FileText } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
  const { data: membershipStats, isLoading: membershipLoading } = useQuery(
    'membershipStats',
    () => apiService.getMembershipStats()
  )

  const { data: checkInStats, isLoading: checkInLoading } = useQuery(
    'checkInStats',
    () => apiService.getCheckInStats()
  )

  const { data: expiringMemberships, isLoading: expiringLoading } = useQuery(
    'expiringMemberships',
    () => apiService.getExpiringMemberships(30)
  )

  const { data: recentNotes, isLoading: notesLoading } = useQuery(
    'recentNotes',
    () => apiService.getRecentNotes(7, 20)
  )

  const stats = [
    {
      name: 'Active Memberships',
      value: membershipStats?.total_active || 0,
      icon: Users,
      change: '+12%',
      changeType: 'positive',
    },
    {
      name: 'Check-ins Today',
      value: checkInStats?.today || 0,
      icon: LogIn,
      change: '+4%',
      changeType: 'positive',
    },
    {
      name: 'Expiring Soon',
      value: membershipStats?.expiring_30_days || 0,
      icon: Calendar,
      change: '-2%',
      changeType: 'negative',
    },
    {
      name: 'Unique Visitors This Month',
      value: checkInStats?.unique_clients_month || 0,
      icon: TrendingUp,
      change: '+8%',
      changeType: 'positive',
    },
  ]

  if (membershipLoading || checkInLoading) {
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
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Overview of your gaming center operations
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div key={item.name} className="card">
            <div className="card-body">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <item.icon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {item.name}
                    </dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900 dark:text-white">
                        {item.value}
                      </div>
                      <div
                        className={`ml-2 flex items-baseline text-sm font-semibold ${
                          item.changeType === 'positive'
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}
                      >
                        {item.change}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Notes */}
      <div className="mt-8">
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Recent Notes (Past Week)
            </h3>
          </div>
          <div className="card-body">
            {notesLoading ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">Loading recent notes...</p>
            ) : recentNotes && recentNotes.length > 0 ? (
              <div className="space-y-4">
                {recentNotes.map((note: any) => (
                  <div key={note.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-900">
                    <div className="flex justify-between items-start mb-2">
                      <Link
                        to={`/clients/${note.client_id}`}
                        className="text-sm font-medium text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300"
                      >
                        {note.client_first_name} {note.client_last_name}
                      </Link>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(note.created_at).toLocaleDateString()} at {new Date(note.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                    <p className="text-sm text-gray-900 dark:text-white whitespace-pre-wrap mb-2">{note.note}</p>
                    <div className="flex items-center text-xs text-gray-600 dark:text-gray-400">
                      <User className="w-3 h-3 mr-1" />
                      <span>{note.user_username || note.user_email}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">No notes from the past week</p>
            )}
          </div>
        </div>
      </div>

      {/* Expiring Memberships Alert */}
      {membershipStats?.expiring_30_days > 0 && (
        <div className="mt-8">
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <Calendar className="h-5 w-5 text-yellow-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Memberships Expiring Soon
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>
                    {membershipStats.expiring_30_days} memberships are expiring within the next 30 days.
                    Consider reaching out to these members for renewal.
                  </p>
                </div>
                <div className="mt-4">
                  <div className="-mx-2 -my-1.5 flex">
                    <a
                      href="/memberships"
                      className="bg-yellow-50 px-2 py-1.5 rounded-md text-sm font-medium text-yellow-800 hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-yellow-50 focus:ring-yellow-600"
                    >
                      View expiring memberships
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}