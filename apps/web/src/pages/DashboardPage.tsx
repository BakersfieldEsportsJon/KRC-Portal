import { useQuery } from 'react-query'
import apiService from '../services/api'
import { Users, Calendar, LogIn, TrendingUp } from 'lucide-react'

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

      {/* Recent Activity */}
      <div className="mt-8">
        {/* Membership Plans */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Membership Plans
            </h3>
          </div>
          <div className="card-body">
            {membershipStats?.plans && Object.keys(membershipStats.plans).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(membershipStats.plans).map(([plan, count]) => (
                  <div key={plan} className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {plan.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">{count} active</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">No active memberships</p>
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