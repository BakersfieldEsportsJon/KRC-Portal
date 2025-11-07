import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { Eye, EyeOff, CheckCircle, XCircle, Lock } from 'lucide-react'
import apiService from '../services/api'

interface PasswordSetupForm {
  password: string
  password_confirm: string
}

interface TokenValidation {
  valid: boolean
  token_type: string
  user_email: string
  expires_at: string
}

export default function PasswordSetupPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [tokenValidation, setTokenValidation] = useState<TokenValidation | null>(null)
  const [isValidating, setIsValidating] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm<PasswordSetupForm>()

  const password = watch('password', '')

  // Password strength indicator
  const getPasswordStrength = (pwd: string) => {
    if (pwd.length < 8) return { strength: 'weak', color: 'text-red-600', message: 'Too short (min 8 chars)' }

    const checks = {
      length: pwd.length >= 8,
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

  const passwordStrength = getPasswordStrength(password)

  // Validate token on mount
  useEffect(() => {
    if (!token) {
      toast.error('No setup token provided')
      navigate('/login')
      return
    }

    const validateToken = async () => {
      try {
        const response = await apiService.api.get(`/password/validate-token/${token}`)
        setTokenValidation(response.data)
        setIsValidating(false)
      } catch (error: any) {
        const message = error.response?.data?.detail || 'Invalid or expired token'
        toast.error(message)
        setTimeout(() => navigate('/login'), 3000)
      }
    }

    validateToken()
  }, [token, navigate])

  const onSubmit = async (data: PasswordSetupForm) => {
    if (data.password !== data.password_confirm) {
      toast.error('Passwords do not match')
      return
    }

    setIsSubmitting(true)

    try {
      await apiService.api.post('/password/setup', {
        token,
        password: data.password,
        password_confirm: data.password_confirm
      })

      toast.success('Password set up successfully! Redirecting to login...')
      setTimeout(() => navigate('/login'), 2000)
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to set up password'
      toast.error(message)
      setIsSubmitting(false)
    }
  }

  if (isValidating) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Validating token...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100 dark:bg-primary-900">
            <Lock className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            {tokenValidation?.token_type === 'reset' ? 'Reset Your Password' : 'Set Up Your Password'}
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {tokenValidation?.user_email}
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="rounded-md shadow-sm space-y-4">
            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                New Password
              </label>
              <div className="relative">
                <input
                  {...register('password', {
                    required: 'Password is required',
                    minLength: { value: 8, message: 'Password must be at least 8 characters' },
                    pattern: {
                      value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;:,.<>?])/,
                      message: 'Password must contain uppercase, lowercase, number, and special character'
                    }
                  })}
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  className="input pr-10"
                  placeholder="Enter new password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
              {password && (
                <p className={`mt-1 text-sm ${passwordStrength.color}`}>
                  {passwordStrength.message}
                </p>
              )}
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <input
                  {...register('password_confirm', {
                    required: 'Please confirm your password',
                    validate: (value) => value === password || 'Passwords do not match'
                  })}
                  id="password_confirm"
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
              {errors.password_confirm && (
                <p className="mt-1 text-sm text-red-600">{errors.password_confirm.message}</p>
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
                {password.length >= 8 ? (
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                )}
                At least 8 characters
              </li>
              <li className="flex items-start">
                {/[A-Z]/.test(password) ? (
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                )}
                At least one uppercase letter
              </li>
              <li className="flex items-start">
                {/[a-z]/.test(password) ? (
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                )}
                At least one lowercase letter
              </li>
              <li className="flex items-start">
                {/[0-9]/.test(password) ? (
                  <CheckCircle className="h-4 w-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="h-4 w-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
                )}
                At least one number
              </li>
              <li className="flex items-start">
                {/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password) ? (
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
              {isSubmitting ? 'Setting up password...' : 'Set Password'}
            </button>
          </div>
        </form>

        <p className="text-center text-sm text-gray-600 dark:text-gray-400">
          Already have an account?{' '}
          <a href="/login" className="font-medium text-primary-600 hover:text-primary-500">
            Sign in
          </a>
        </p>
      </div>
    </div>
  )
}
