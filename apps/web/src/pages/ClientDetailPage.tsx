import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import apiService from '../services/api'
import { Mail, Phone, Calendar, Tag, User, Briefcase, FileText, Languages, LogIn, X, Edit2, AlertTriangle, Clock } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../hooks/useAuth'
import { useState } from 'react'

export default function ClientDetailPage() {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()
  const { isAdmin } = useAuth()
  const [showNotesModal, setShowNotesModal] = useState(false)
  const [notesText, setNotesText] = useState('')

  const { data: client, isLoading } = useQuery(
    ['client', id],
    () => apiService.getClient(id!),
    { enabled: !!id }
  )

  const { data: membership } = useQuery(
    ['clientMembership', id],
    () => apiService.getClientMembership(id!),
    { enabled: !!id }
  )

  const { data: checkIns } = useQuery(
    ['clientCheckIns', id],
    () => apiService.getClientCheckIns(id!, { limit: 10 }),
    { enabled: !!id }
  )

  const checkInMutation = useMutation(
    () => apiService.createCheckIn({
      client_id: id!,
      method: 'staff',
      station: 'Front Desk'
    }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['clientCheckIns', id])
        toast.success('Check-in successful!')
      },
      onError: () => {
        toast.error('Failed to check in')
      }
    }
  )

  const handleCheckIn = () => {
    checkInMutation.mutate()
  }

  // Calculate membership status details
  const getMembershipStatusInfo = () => {
    if (!membership) return null

    const now = new Date()
    const endsOn = new Date(membership.ends_on)
    const daysUntilExpiry = Math.ceil((endsOn.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

    if (membership.status === 'expired' || daysUntilExpiry < 0) {
      return {
        status: 'expired',
        label: 'Expired',
        color: 'bg-red-100 text-red-800 border-red-200',
        message: 'Membership has expired',
        daysUntilExpiry
      }
    } else if (daysUntilExpiry <= 14) {
      return {
        status: 'expiring',
        label: 'Expiring Soon',
        color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        message: `Expires in ${daysUntilExpiry} day${daysUntilExpiry !== 1 ? 's' : ''}`,
        daysUntilExpiry
      }
    } else {
      return {
        status: 'active',
        label: 'Active',
        color: 'bg-green-100 text-green-800 border-green-200',
        message: `Expires ${endsOn.toLocaleDateString()}`,
        daysUntilExpiry
      }
    }
  }

  // Calculate days since last check-in
  const getDaysSinceLastCheckIn = () => {
    if (!checkIns || checkIns.length === 0) return null

    const lastCheckIn = new Date(checkIns[0].happened_at)
    const now = new Date()
    const daysSince = Math.floor((now.getTime() - lastCheckIn.getTime()) / (1000 * 60 * 60 * 24))

    return daysSince
  }

  const membershipInfo = getMembershipStatusInfo()
  const daysSinceLastCheckIn = getDaysSinceLastCheckIn()

  const updateNotesMutation = useMutation(
    (notes: string) => apiService.updateClient(id!, { notes }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['client', id])
        setShowNotesModal(false)
        setNotesText('')
        toast.success('Notes updated successfully!')
      },
      onError: () => {
        toast.error('Failed to update notes')
      }
    }
  )

  const handleNotesSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateNotesMutation.mutate(notesText)
  }

  const openNotesModal = () => {
    setNotesText(client?.notes || '')
    setShowNotesModal(true)
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!client) {
    return <div className="text-center text-gray-500">Client not found</div>
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">
          {client.first_name} {client.last_name}
        </h1>
        <p className="mt-2 text-sm text-gray-700">Client details and activity</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Client Info */}
        <div className="lg:col-span-2 space-y-8">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Information</h3>
            </div>
            <div className="card-body">
              <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Email</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <Mail className="w-4 h-4 mr-2 text-gray-400" />
                    {client.email || 'Not provided'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Phone</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <Phone className="w-4 h-4 mr-2 text-gray-400" />
                    {client.phone || 'Not provided'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Date of Birth</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                    {client.date_of_birth ? new Date(client.date_of_birth).toLocaleDateString() : 'Not provided'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Member Since</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(client.created_at).toLocaleDateString()}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Parent/Guardian Name</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <User className="w-4 h-4 mr-2 text-gray-400" />
                    {client.parent_guardian_name || 'Not provided'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">UCI Number</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <FileText className="w-4 h-4 mr-2 text-gray-400" />
                    {client.pos_number || 'Not provided'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Service Coordinator</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <Briefcase className="w-4 h-4 mr-2 text-gray-400" />
                    {client.service_coordinator || 'Not provided'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">POS Start Date</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                    {client.pos_start_date ? new Date(client.pos_start_date).toLocaleDateString() : 'Not provided'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">POS End Date</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                    {client.pos_end_date ? new Date(client.pos_end_date).toLocaleDateString() : 'Not provided'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Language</dt>
                  <dd className="mt-1 text-sm text-gray-900 flex items-center">
                    <Languages className="w-4 h-4 mr-2 text-gray-400" />
                    {client.language || 'Not provided'}
                  </dd>
                </div>
                {client.notes && (
                  <div className="sm:col-span-2">
                    <dt className="text-sm font-medium text-gray-500">Notes</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {client.notes}
                    </dd>
                  </div>
                )}
              </dl>

              {/* Tags */}
              {client.tags && client.tags.length > 0 && (
                <div className="mt-6">
                  <dt className="text-sm font-medium text-gray-500 mb-2">Tags</dt>
                  <div className="flex flex-wrap gap-2">
                    {client.tags.map((tag) => (
                      <span
                        key={tag.id}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                      >
                        <Tag className="w-3 h-3 mr-1" />
                        {tag.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Recent Check-ins */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Recent Check-ins</h3>
            </div>
            <div className="card-body">
              {checkIns && checkIns.length > 0 ? (
                <div className="space-y-3">
                  {checkIns.map((checkIn) => (
                    <div key={checkIn.id} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {checkIn.station || 'General'}
                        </div>
                        <div className="text-xs text-gray-500">
                          {checkIn.method === 'kiosk' ? 'Self Check-in' : 'Staff Assisted'}
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">
                        {new Date(checkIn.happened_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No recent check-ins</p>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
          {/* Alert Banners */}
          {daysSinceLastCheckIn !== null && daysSinceLastCheckIn >= 30 && (
            <div className="card border-2 border-orange-200 bg-orange-50">
              <div className="card-body">
                <div className="flex items-start">
                  <AlertTriangle className="w-5 h-5 text-orange-600 mr-3 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-semibold text-orange-900">Inactive Client</h4>
                    <p className="text-sm text-orange-800 mt-1">
                      Last seen {daysSinceLastCheckIn} days ago. Consider reaching out to this client.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Last Check-in */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Last Check-in</h3>
            </div>
            <div className="card-body">
              {checkIns && checkIns.length > 0 ? (
                <div>
                  <div className="flex items-center text-sm text-gray-600 mb-2">
                    <Clock className="w-4 h-4 mr-2" />
                    {new Date(checkIns[0].happened_at).toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-500">
                    {checkIns[0].station || 'General'} • {checkIns[0].method === 'kiosk' ? 'Self Check-in' : 'Staff Assisted'}
                  </div>
                  {daysSinceLastCheckIn !== null && (
                    <div className={`mt-2 text-xs font-medium ${
                      daysSinceLastCheckIn >= 30 ? 'text-orange-600' :
                      daysSinceLastCheckIn >= 14 ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {daysSinceLastCheckIn === 0 ? 'Today' :
                       daysSinceLastCheckIn === 1 ? 'Yesterday' :
                       `${daysSinceLastCheckIn} days ago`}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No check-ins yet</p>
              )}
            </div>
          </div>

          {/* Membership */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Membership</h3>
            </div>
            <div className="card-body">
              {membership && membershipInfo ? (
                <div>
                  <div className={`inline-flex px-3 py-1.5 text-sm font-semibold rounded-lg border-2 mb-3 ${membershipInfo.color}`}>
                    {membershipInfo.label}
                  </div>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium">Plan:</span> {membership.plan_code}
                    </div>
                    <div>
                      <span className="font-medium">Starts:</span> {new Date(membership.starts_on).toLocaleDateString()}
                    </div>
                    <div>
                      <span className="font-medium">Ends:</span> {new Date(membership.ends_on).toLocaleDateString()}
                    </div>
                    <div className={`pt-2 text-xs font-medium ${
                      membershipInfo.status === 'expired' ? 'text-red-700' :
                      membershipInfo.status === 'expiring' ? 'text-yellow-700' :
                      'text-green-700'
                    }`}>
                      {membershipInfo.message}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-500">No active membership</p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="card">
            <div className="card-body">
              <div className="space-y-3">
                {isAdmin() && (
                  <>
                    <button className="btn-primary w-full">Edit Client</button>
                    <button className="btn-secondary w-full">Add Membership</button>
                  </>
                )}

                {/* Enhanced Check-in Button with Status */}
                <div className="space-y-2">
                  <button
                    onClick={handleCheckIn}
                    disabled={checkInMutation.isLoading}
                    className={`w-full flex items-center justify-center font-semibold py-2.5 px-4 rounded-lg transition-colors ${
                      membershipInfo?.status === 'expired'
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : membershipInfo?.status === 'expiring'
                        ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
                        : 'bg-green-600 hover:bg-green-700 text-white'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    <LogIn className="w-4 h-4 mr-2" />
                    {checkInMutation.isLoading ? 'Checking In...' : 'Check In Client'}
                  </button>

                  {/* Status message below button */}
                  {membershipInfo && (
                    <div className={`text-xs text-center font-medium ${
                      membershipInfo.status === 'expired' ? 'text-red-700' :
                      membershipInfo.status === 'expiring' ? 'text-yellow-700' :
                      'text-green-700'
                    }`}>
                      {membershipInfo.status === 'expired' && '⚠️ Membership Expired'}
                      {membershipInfo.status === 'expiring' && `⚠️ Expiring in ${membershipInfo.daysUntilExpiry} days`}
                      {membershipInfo.status === 'active' && '✓ Active Membership'}
                    </div>
                  )}
                </div>

                <button
                  onClick={openNotesModal}
                  className="btn-secondary w-full flex items-center justify-center"
                >
                  <Edit2 className="w-4 h-4 mr-2" />
                  Edit Notes
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Notes Modal */}
      {showNotesModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Edit Notes</h2>
              <button
                onClick={() => setShowNotesModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleNotesSubmit}>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes for {client?.first_name} {client?.last_name}
                </label>
                <textarea
                  value={notesText}
                  onChange={(e) => setNotesText(e.target.value)}
                  className="input w-full"
                  rows={6}
                  placeholder="Add notes about this client..."
                />
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowNotesModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateNotesMutation.isLoading}
                  className="btn-primary"
                >
                  {updateNotesMutation.isLoading ? 'Saving...' : 'Save Notes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}