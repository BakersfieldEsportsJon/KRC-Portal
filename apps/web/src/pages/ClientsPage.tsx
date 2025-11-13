import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Link, useSearchParams } from 'react-router-dom'
import apiService from '../services/api'
import { Plus, Search, X, Upload, Edit, Filter, LogIn } from 'lucide-react'
import { ClientForm } from '../types'
import toast from 'react-hot-toast'
import { useAuth } from '../hooks/useAuth'

export default function ClientsPage() {
  const { isAdmin } = useAuth()
  const [searchParams] = useSearchParams()
  const [searchQuery, setSearchQuery] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [statusFilter, setStatusFilter] = useState<string>('all')

  // Read filter from URL query parameter on mount
  useEffect(() => {
    const filterParam = searchParams.get('filter')
    if (filterParam && ['active', 'expiring', 'expired', 'none'].includes(filterParam)) {
      setStatusFilter(filterParam)
    }
  }, [searchParams])
  const [formData, setFormData] = useState<ClientForm>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    parent_guardian_name: '',
    pos_number: '',
    service_coordinator: '',
    pos_start_date: '',
    pos_end_date: ''
  })
  const [showImportModal, setShowImportModal] = useState(false)
  const [importFile, setImportFile] = useState<File | null>(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingClient, setEditingClient] = useState<any>(null)
  const [editFormData, setEditFormData] = useState<ClientForm>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    parent_guardian_name: '',
    pos_number: '',
    service_coordinator: '',
    pos_start_date: '',
    pos_end_date: '',
    notes: '',
    language: ''
  })

  const queryClient = useQueryClient()

  const { data: clients, isLoading } = useQuery(
    ['clients', searchQuery],
    () => apiService.getClients({ query: searchQuery, limit: 50 }),
    { keepPreviousData: true }
  )

  const createMutation = useMutation(
    (data: ClientForm) => apiService.createClient(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('clients')
        setShowAddModal(false)
        setFormData({
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          date_of_birth: '',
          parent_guardian_name: '',
          pos_number: '',
          service_coordinator: '',
          pos_start_date: '',
          pos_end_date: '',
          notes: '',
          language: ''
        })
        toast.success('Client added successfully')
      },
      onError: () => {
        toast.error('Failed to add client')
      }
    }
  )

  const importMutation = useMutation(
    (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return apiService.api.post('/clients/import', formData)
    },
    {
      onSuccess: (response) => {
        const { created_count, errors } = response.data

        queryClient.invalidateQueries('clients')
        setShowImportModal(false)
        setImportFile(null)

        if (created_count > 0) {
          toast.success(`Successfully imported ${created_count} client${created_count === 1 ? '' : 's'}`)
        }

        if (errors && errors.length > 0) {
          // Show errors in a more visible way
          const errorMessage = `Import completed with errors:\n${errors.join('\n')}`
          toast.error(errorMessage, { duration: 10000 })
        }

        if (created_count === 0 && (!errors || errors.length === 0)) {
          toast.error('No clients were imported from the CSV file')
        }
      },
      onError: () => {
        toast.error('Failed to import clients')
      }
    }
  )

  const updateMutation = useMutation(
    ({ clientId, data }: { clientId: string; data: Partial<ClientForm> }) =>
      apiService.updateClient(clientId, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('clients')
        setShowEditModal(false)
        setEditingClient(null)
        setEditFormData({
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          date_of_birth: '',
          parent_guardian_name: '',
          pos_number: '',
          service_coordinator: '',
          pos_start_date: '',
          pos_end_date: '',
          notes: '',
          language: ''
        })
        toast.success('Client updated successfully')
      },
      onError: () => {
        toast.error('Failed to update client')
      }
    }
  )

  const checkInMutation = useMutation(
    (clientId: string) => apiService.createCheckIn({
      client_id: clientId,
      method: 'staff',
      station: 'Front Desk'
    }),
    {
      onSuccess: (data: any) => {
        queryClient.invalidateQueries('clients')

        // Show membership warning if present
        if (data.membership_warning) {
          const warning = data.membership_warning.toLowerCase()
          if (warning.includes('expired')) {
            toast.error(
              `✓ Checked in - MEMBERSHIP EXPIRED\n${data.membership_warning}\nClient may play today. Please remind them to contact their service coordinator to renew.`,
              { duration: 8000 }
            )
          } else if (warning.includes('expiring')) {
            toast(
              `✓ Checked in - Membership Expiring Soon\n${data.membership_warning}\nPlease remind client to contact their service coordinator for renewal.`,
              {
                duration: 6000,
                icon: '⚠️'
              }
            )
          } else {
            toast.success('Check-in successful!')
          }
        } else {
          toast.success('Check-in successful!')
        }
      },
      onError: () => {
        toast.error('Failed to check in')
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingClient) {
      updateMutation.mutate({ clientId: editingClient.id, data: editFormData })
    }
  }

  const getStatusColor = (status?: string | null) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'expiring':
        return 'bg-yellow-100 text-yellow-800'
      case 'expired':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status?: string | null) => {
    switch (status) {
      case 'active':
        return 'Active'
      case 'expiring':
        return 'Expiring Soon'
      case 'expired':
        return 'Expired'
      default:
        return 'No Membership'
    }
  }

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
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Clients</h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Manage your gaming center members and their information
          </p>
        </div>
        {isAdmin() && (
          <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none flex gap-3">
            <button onClick={() => setShowImportModal(true)} className="btn-secondary">
              <Upload className="w-4 h-4 mr-2" />
              Import CSV
            </button>
            <button onClick={() => setShowAddModal(true)} className="btn-primary">
              <Plus className="w-4 h-4 mr-2" />
              Add Client
            </button>
          </div>
        )}
      </div>

      {/* Search and Filter */}
      <div className="mt-6 flex gap-4">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search clients..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10 w-full"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-5 w-5 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input min-w-[150px]"
          >
            <option value="all">All Clients</option>
            <option value="active">Active</option>
            <option value="expiring">Expiring Soon</option>
            <option value="expired">Expired</option>
            <option value="none">No Membership</option>
          </select>
        </div>
      </div>

      {/* Client List */}
      <div className="mt-8 card">
        <div className="overflow-hidden">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Expiration Date
                </th>
                <th className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="table-body">
              {clients?.filter((client) => {
                if (statusFilter === 'all') return true
                if (statusFilter === 'none') return !client.membership_status
                return client.membership_status === statusFilter
              }).map((client) => {
                // Calculate days until expiry for color coding
                const daysUntilExpiry = client.membership_end_date
                  ? Math.ceil((new Date(client.membership_end_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
                  : null;

                return (
                  <tr key={client.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {client.first_name} {client.last_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      <div>{client.email || 'N/A'}</div>
                      <div className="text-xs text-gray-400 dark:text-gray-500">{client.phone || ''}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(client.membership_status)}`}>
                        {getStatusText(client.membership_status)}
                      </span>
                      {client.membership_plan && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{client.membership_plan}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {client.membership_end_date ? (
                        <div>
                          <div className={`font-medium ${
                            daysUntilExpiry !== null && daysUntilExpiry < 0 ? 'text-red-600' :
                            daysUntilExpiry !== null && daysUntilExpiry <= 30 ? 'text-yellow-600' :
                            'text-gray-900 dark:text-white'
                          }`}>
                            {new Date(client.membership_end_date).toLocaleDateString()}
                          </div>
                          {daysUntilExpiry !== null && (
                            <div className={`text-xs ${
                              daysUntilExpiry < 0 ? 'text-red-600' :
                              daysUntilExpiry <= 30 ? 'text-yellow-600' :
                              'text-gray-500 dark:text-gray-400'
                            }`}>
                              {daysUntilExpiry < 0 ? `Expired ${Math.abs(daysUntilExpiry)} days ago` :
                               daysUntilExpiry === 0 ? 'Expires today' :
                               daysUntilExpiry === 1 ? 'Expires tomorrow' :
                               `${daysUntilExpiry} days left`}
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-400 dark:text-gray-500">N/A</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => checkInMutation.mutate(client.id)}
                          disabled={checkInMutation.isLoading}
                          className={`inline-flex items-center px-3 py-1.5 rounded-md font-medium text-white transition-colors ${
                            client.membership_status === 'expired'
                              ? 'bg-red-600 hover:bg-red-700'
                              : client.membership_status === 'expiring'
                              ? 'bg-yellow-500 hover:bg-yellow-600'
                              : 'bg-green-600 hover:bg-green-700'
                          } disabled:opacity-50`}
                          title="Check in client"
                        >
                          <LogIn className="w-3.5 h-3.5" />
                        </button>
                        {isAdmin() && (
                          <button
                            onClick={() => {
                              setEditingClient(client)
                              setEditFormData({
                                first_name: client.first_name,
                                last_name: client.last_name,
                                email: client.email || '',
                                phone: client.phone || '',
                                date_of_birth: client.date_of_birth || '',
                                parent_guardian_name: client.parent_guardian_name || '',
                                pos_number: client.pos_number || '',
                                service_coordinator: client.service_coordinator || '',
                                pos_start_date: client.pos_start_date || '',
                                pos_end_date: client.pos_end_date || '',
                                notes: client.notes || '',
                                language: client.language || ''
                              })
                              setShowEditModal(true)
                            }}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <Edit className="w-4 h-4 inline" />
                          </button>
                        )}
                        <Link
                          to={`/clients/${client.id}`}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          View
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Client Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-2xl max-h-[90vh] flex flex-col">
            <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Add New Client</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="flex flex-col flex-1 overflow-hidden">
              <div className="overflow-y-auto p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    First Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Parent/Guardian Name
                  </label>
                  <input
                    type="text"
                    value={formData.parent_guardian_name}
                    onChange={(e) => setFormData({ ...formData, parent_guardian_name: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    UCI Number
                  </label>
                  <input
                    type="text"
                    value={formData.pos_number}
                    onChange={(e) => setFormData({ ...formData, pos_number: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Service Coordinator
                  </label>
                  <input
                    type="text"
                    value={formData.service_coordinator}
                    onChange={(e) => setFormData({ ...formData, service_coordinator: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    POS Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.pos_start_date}
                    onChange={(e) => setFormData({ ...formData, pos_start_date: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    POS End Date
                  </label>
                  <input
                    type="date"
                    value={formData.pos_end_date}
                    onChange={(e) => setFormData({ ...formData, pos_end_date: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Language
                  </label>
                  <input
                    type="text"
                    value={formData.language}
                    onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Notes
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    className="input mt-1"
                    rows={3}
                  />
                </div>
                </div>
              </div>

              <div className="border-t border-gray-200 dark:border-gray-700 p-6 flex justify-end space-x-3 bg-gray-50 dark:bg-gray-900">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isLoading}
                  className="btn-primary"
                >
                  {createMutation.isLoading ? 'Adding...' : 'Add Client'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Import Clients from CSV</h2>
              <button
                onClick={() => {
                  setShowImportModal(false)
                  setImportFile(null)
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Select CSV File
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-semibold
                    file:bg-primary-50 file:text-primary-700
                    hover:file:bg-primary-100"
                />
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => {
                    window.location.href = `${apiService.api.defaults.baseURL}/clients/import/template`
                  }}
                  className="text-sm text-primary-600 hover:text-primary-900 underline"
                >
                  Download Template
                </button>
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowImportModal(false)
                    setImportFile(null)
                  }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => {
                    if (importFile) {
                      importMutation.mutate(importFile)
                    }
                  }}
                  disabled={!importFile || importMutation.isLoading}
                  className="btn-primary"
                >
                  {importMutation.isLoading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Client Modal */}
      {showEditModal && editingClient && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-2xl max-h-[90vh] flex flex-col">
            <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Edit Client</h2>
              <button
                onClick={() => {
                  setShowEditModal(false)
                  setEditingClient(null)
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="flex flex-col flex-1 overflow-hidden">
              <div className="overflow-y-auto p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    First Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={editFormData.first_name}
                    onChange={(e) => setEditFormData({ ...editFormData, first_name: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={editFormData.last_name}
                    onChange={(e) => setEditFormData({ ...editFormData, last_name: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Email
                  </label>
                  <input
                    type="email"
                    value={editFormData.email}
                    onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={editFormData.phone}
                    onChange={(e) => setEditFormData({ ...editFormData, phone: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    value={editFormData.date_of_birth}
                    onChange={(e) => setEditFormData({ ...editFormData, date_of_birth: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Parent/Guardian Name
                  </label>
                  <input
                    type="text"
                    value={editFormData.parent_guardian_name}
                    onChange={(e) => setEditFormData({ ...editFormData, parent_guardian_name: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    UCI Number
                  </label>
                  <input
                    type="text"
                    value={editFormData.pos_number}
                    onChange={(e) => setEditFormData({ ...editFormData, pos_number: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Service Coordinator
                  </label>
                  <input
                    type="text"
                    value={editFormData.service_coordinator}
                    onChange={(e) => setEditFormData({ ...editFormData, service_coordinator: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    POS Start Date
                  </label>
                  <input
                    type="date"
                    value={editFormData.pos_start_date}
                    onChange={(e) => setEditFormData({ ...editFormData, pos_start_date: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    POS End Date
                  </label>
                  <input
                    type="date"
                    value={editFormData.pos_end_date}
                    onChange={(e) => setEditFormData({ ...editFormData, pos_end_date: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Language
                  </label>
                  <input
                    type="text"
                    value={editFormData.language}
                    onChange={(e) => setEditFormData({ ...editFormData, language: e.target.value })}
                    className="input mt-1"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Notes
                  </label>
                  <textarea
                    value={editFormData.notes}
                    onChange={(e) => setEditFormData({ ...editFormData, notes: e.target.value })}
                    className="input mt-1"
                    rows={3}
                  />
                </div>
                </div>
              </div>

              <div className="border-t border-gray-200 dark:border-gray-700 p-6 flex justify-end space-x-3 bg-gray-50 dark:bg-gray-900">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false)
                    setEditingClient(null)
                  }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateMutation.isLoading}
                  className="btn-primary"
                >
                  {updateMutation.isLoading ? 'Updating...' : 'Update Client'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}