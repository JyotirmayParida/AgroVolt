/**
 * Extracts a user-friendly error message distinguishing network/connection failures,
 * backend HTTP error responses, and configuration issues.
 */
export function getErrorMessage(err, fallback = 'An unexpected error occurred.') {
  if (!err) return fallback

  // Axios network error or server unreachable
  if (err.code === 'ERR_NETWORK' || !err.response) {
    if (import.meta.env.DEV) {
      return 'Unable to reach backend API. Ensure the backend server is running locally (http://localhost:8000).'
    }
    return 'Unable to reach the backend service. The server may be offline, waking up, or temporarily unreachable. Please check backend status or try again.'
  }

  // Server responded with HTTP status code
  if (err.response) {
    const status = err.response.status
    const data = err.response.data

    if (data?.detail) {
      if (typeof data.detail === 'string') {
        return `Backend error (${status}): ${data.detail}`
      }
      if (Array.isArray(data.detail)) {
        return `Validation error (${status}): ${data.detail.map(d => d.msg || JSON.stringify(d)).join(', ')}`
      }
    }

    if (data?.message) {
      return `Server error (${status}): ${data.message}`
    }

    if (status === 404) {
      return 'API endpoint not found (404). Please verify the backend routing.'
    }
    if (status >= 500) {
      return `Backend server encountered an error (${status}). Please try again later.`
    }
    return `Request failed with status code ${status}.`
  }

  return err.message || fallback
}
