import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { Eye, EyeOff, CheckCircle, XCircle, Lock } from 'lucide-react'
import apiService from '../services/api'

interface ChangePasswordForm {
  current_password: string
  new_password: string
  confirm_password: string
}

export default function ChangePasswordPage() {
  const navigate = useNavigate()
  const [showCurrent, setShowCurrent] = useState(false)
  const [showNew, setShowNew] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm<ChangePasswordForm>()

  const newPassword = watch('new_password', '')

  // Password strength indicator
  const getPasswordStrength = (pwd: string) => {
    if (pwd.length < 12) return { strength: 'weak', color: 'text-red-600', message: 'Too short (min 12 chars)' }

    const checks = {
      length: pwd.length >= 12,
      upper: /[A-Z]/.test(pwd),
      lower: /[a-z]/.test(pwd),
      number: /[0-9]/.test(pwd),
      special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(pwd)
    }

    const score = Object.values(checks).filter(Boolean).length

    if (score === 5) return { strength: 'strong', color: 'text-green-600', message: 'Strong password' }
    if (score >= 4) return { strength: 'good', color: 'text-blue-600', message: 'Good password' }
    if (score >= 3) return { strength: 'fair', color: 'text-yellow-600', message: 'Fair password' }
    return { strength: 'weak', color: 'text-red-600', message: 'Weak password' }
  }

  const passwordStrength = getPasswordStrength(newPassword)

  const onSubmit = async (data: ChangePasswordForm) => {
    if (data.new_password !== data.confirm_password) {
      toast.error('Passwords do not match')
      return
    }

    setIsSubmitting(true)

    try {
      await apiService.changePassword({
        current_password: data.current_password,
        new_password: data.new_password
      })

      toast.success('Password changed successfully!')
      setTimeout(() => navigate('/dashboard'), 1500)
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to change password'
      toast.error(message)
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100 dark:bg-primary-900">
            <Lock className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Change Your Password
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            You must change your temporary password before continuing
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="rounded-md shadow-sm space-y-4">
            {/* Current Password Field */}
            <div>
              <label htmlFor="current_password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Current (Temporary) Password
              </label>
              <div className="relative">
                <input
                  {...register('current_password', {
                    required: 'Current password is required'
                  })}
                  id="current_password"
                  type={showCurrent ? 'text' : 'password'}
                  className="input pr-10"
                  placeholder="Enter your temporary password"
                />
                <button
                  type="button"
                  onClick={() => setShowCurrent(!showCurrent)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showCurrent ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.current_password && (
                <p className="mt-1 text-sm text-red-600">{errors.current_password.message}</p>
              )}
            </div>

            {/* New Password Field */}
            <div>
              <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                New Password
              </label>
              <div className="relative">
                <input
                  {...register('new_password', {
                    required: 'New password is required',
                    minLength: { value: 12, message: 'Password must be at least 12 characters' },
                    pattern: {
                      value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?])/,
                      message: 'Password must contain uppercase, lowercase, number, and special character'
                    }
                  })}
                  id="new_password"
                  type={showNew ? 'text' : 'password'}
                  className="input pr-10"
                  placeholder="Enter new password"
                />
                <button
                  type="button"
                  onClick={() => setShowNew(!showNew)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showNew ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.new_password && (
                <p className="mt-1 text-sm text-red-600">{errors.new_password.message}</p>
              )}
              {newPassword && (
                <p className={`mt-1 text-sm ${passwordStrength.color}`}>
                  {passwordStrength.message}
                </p>
              )}
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirm New Password
              </label>
              <div className="relative">
                <input
                  {...register('confirm_password', {
                    required: 'Please confirm your password',
                    validate: (value) => value === newPassword || 'Passwords do not match'
                  })}
                  id="confirm_password"
                  type={showConfirm ? 'text' : 'password'}
                  className="input pr-10"
                  placeholder="Confirm new password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showConfirm ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.confirm_password && (
                <p className="mt-1 text-sm text-red-600">{errors.confirm_password.message}</p>
              )}
            </div>
          </div>

          {/* Password Requirements */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-4">
            <h3 className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-2">
              Password Requirements:
            </h3>
            <ul className="space-y-1 text-sm text-blue-800 dark:text-blue-400">
              <li className="flex items-start">
                {newPassword.length >= 12 ? (
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                )}
                At least 12 characters
              </li>
              <li className="flex items-start">
                {/[A-Z]/.test(newPassword) ? (
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                )}
                At least one uppercase letter
              </li>
              <li className="flex items-start">
                {/[a-z]/.test(newPassword) ? (
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                )}
                At least one lowercase letter
              </li>
              <li className="flex items-start">
                {/[0-9]/.test(newPassword) ? (
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                )}
                At least one number
              </li>
              <li className="flex items-start">
                {/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(newPassword) ? (
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                )}
                At least one special character
              </li>
            </ul>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Changing Password...' : 'Change Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
