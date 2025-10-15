import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { KioskCheckInForm } from '../types'
import apiService from '../services/api'
import toast from 'react-hot-toast'
import { CheckCircle, AlertCircle, Phone, CreditCard } from 'lucide-react'

export default function KioskPage() {
  const [loading, setLoading] = useState(false)
  const [clientInfo, setClientInfo] = useState<any>(null)
  const [step, setStep] = useState<'lookup' | 'confirm' | 'success'>('lookup')

  const {
    register,
    handleSubmit,
    reset,
    getValues,
  } = useForm<KioskCheckInForm>()

  const onLookup = async (data: KioskCheckInForm) => {
    if (!data.phone && !data.code) {
      toast.error('Please enter your phone number or member code')
      return
    }

    setLoading(true)
    try {
      const client = await apiService.lookupClient(data.phone, data.code)
      if (client) {
        setClientInfo(client)
        setStep('confirm')
      } else {
        toast.error('Client not found. Please check your information or ask staff for help.')
      }
    } catch (error) {
      toast.error('Error looking up client. Please try again or ask staff for help.')
    } finally {
      setLoading(false)
    }
  }

  const onCheckIn = async () => {
    setLoading(true)
    try {
      const formData = getValues()
      await apiService.kioskCheckIn({
        phone: formData.phone,
        code: formData.code,
        station: formData.station || 'Kiosk',
      })
      setStep('success')
      toast.success('Check-in successful!')
    } catch (error) {
      toast.error('Check-in failed. Please try again or ask staff for help.')
    } finally {
      setLoading(false)
    }
  }

  const startOver = () => {
    setStep('lookup')
    setClientInfo(null)
    reset()
  }

  if (step === 'success') {
    return (
      <div className="text-center">
        <div className="mx-auto w-32 h-32 bg-green-100 rounded-full flex items-center justify-center mb-8">
          <CheckCircle className="w-16 h-16 text-green-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Welcome, {clientInfo?.full_name}!
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          You've been successfully checked in. Enjoy your time at BEC!
        </p>
        {clientInfo?.membership_status === 'expired' && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-8">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-yellow-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Membership Expired
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>Your membership has expired. Please see staff to renew.</p>
                </div>
              </div>
            </div>
          </div>
        )}
        <button
          onClick={startOver}
          className="btn-primary text-lg px-8 py-3"
        >
          Check In Another Member
        </button>
      </div>
    )
  }

  if (step === 'confirm') {
    return (
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Confirm Your Information
        </h1>
        <div className="card max-w-md mx-auto">
          <div className="card-body">
            <h2 className="text-xl font-semibold mb-4">{clientInfo.full_name}</h2>
            {clientInfo.email && (
              <p className="text-gray-600 mb-2">{clientInfo.email}</p>
            )}
            {clientInfo.phone && (
              <p className="text-gray-600 mb-4">{clientInfo.phone}</p>
            )}
            {clientInfo.membership_status && (
              <div className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full mb-4 ${
                clientInfo.membership_status === 'active'
                  ? 'bg-green-100 text-green-800'
                  : clientInfo.membership_status === 'expired'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {clientInfo.membership_status.charAt(0).toUpperCase() +
                 clientInfo.membership_status.slice(1)} Membership
              </div>
            )}
            {clientInfo.membership_expires && (
              <p className="text-sm text-gray-500 mb-6">
                Expires: {new Date(clientInfo.membership_expires).toLocaleDateString()}
              </p>
            )}
            <div className="space-y-3">
              <button
                onClick={onCheckIn}
                disabled={loading}
                className="btn-primary w-full text-lg py-3"
              >
                {loading ? 'Checking In...' : 'Check In'}
              </button>
              <button
                onClick={startOver}
                className="btn-secondary w-full"
              >
                Not You? Start Over
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="text-center">
      <img
        src="/logo-large.svg"
        alt="BEC Logo"
        className="h-32 w-auto mx-auto mb-8"
        onError={(e) => {
          // Hide image if it doesn't exist
          e.currentTarget.style.display = 'none'
        }}
      />
      <h1 className="text-4xl font-bold text-gray-900 mb-8">
        Welcome to BEC!
      </h1>
      <p className="text-xl text-gray-600 mb-12">
        Please enter your information to check in
      </p>

      <form onSubmit={handleSubmit(onLookup)} className="max-w-md mx-auto space-y-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Phone className="inline w-4 h-4 mr-2" />
              Phone Number
            </label>
            <input
              {...register('phone')}
              type="tel"
              placeholder="(555) 123-4567"
              className="input text-lg py-3"
            />
          </div>

          <div className="text-center text-gray-500">
            <span>OR</span>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <CreditCard className="inline w-4 h-4 mr-2" />
              Member Code
            </label>
            <input
              {...register('code')}
              type="text"
              placeholder="Enter your member code"
              className="input text-lg py-3"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Station (Optional)
            </label>
            <input
              {...register('station')}
              type="text"
              placeholder="Gaming station number"
              className="input"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full text-lg py-3"
        >
          {loading ? 'Looking Up...' : 'Find My Account'}
        </button>
      </form>

      <div className="mt-12 bg-blue-50 border border-blue-200 rounded-md p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-2">
          Need Help?
        </h3>
        <p className="text-blue-700">
          If you're having trouble checking in, please ask a staff member for assistance.
        </p>
      </div>
    </div>
  )
}