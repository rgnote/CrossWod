import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from './App'
import * as api from './utils/api'

vi.mock('./utils/api')

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    // Default mock for getUsers (used by ProfileSelect)
    api.getUsers.mockResolvedValue([])
  })

  it('should render loading state initially', () => {
    render(<App />)
    expect(screen.getByText('CrossWod')).toBeInTheDocument()
    // Either shows "Loading..." or "Loading profiles..." depending on state
    expect(
      screen.queryByText('Loading...') || screen.queryByText('Loading profiles...')
    ).toBeInTheDocument()
  })

  it('should redirect to profile select when no user', async () => {
    api.getUsers.mockResolvedValueOnce([])

    render(<App />)

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument()
    })

    // Should show profile selection screen
    expect(screen.getByText('Select your profile to continue')).toBeInTheDocument()
  })

  it('should load user from localStorage', async () => {
    localStorage.setItem('crosswod_user_id', '1')
    api.getUser.mockResolvedValueOnce({
      id: 1,
      name: 'Test User',
      has_profile_picture: false,
      created_at: new Date().toISOString(),
      last_active: new Date().toISOString()
    })

    // Mock dashboard data
    api.getWeeklySummary.mockResolvedValueOnce({
      total_workouts: 0,
      total_volume: 0,
      total_sets: 0,
      muscle_groups_worked: {},
      new_prs: 0
    })
    api.getStreakInfo.mockResolvedValueOnce({
      current_streak: 0,
      longest_streak: 0,
      total_workouts: 0
    })
    api.getWorkouts.mockResolvedValueOnce([])
    api.getTemplates.mockResolvedValueOnce([])

    render(<App />)

    await waitFor(() => {
      expect(api.getUser).toHaveBeenCalledWith(1)
    })
  })

  it('should handle user load failure gracefully', async () => {
    localStorage.setItem('crosswod_user_id', '999')
    api.getUser.mockRejectedValueOnce(new Error('User not found'))
    api.getUsers.mockResolvedValueOnce([])

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText('Select your profile to continue')).toBeInTheDocument()
    })
  })

  it('should clear invalid user from localStorage', async () => {
    localStorage.setItem('crosswod_user_id', 'invalid')
    api.getUser.mockRejectedValueOnce(new Error('Invalid user'))
    api.getUsers.mockResolvedValueOnce([])

    render(<App />)

    await waitFor(() => {
      expect(localStorage.removeItem).toHaveBeenCalledWith('crosswod_user_id')
    })
  })
})
