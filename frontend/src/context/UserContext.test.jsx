import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { UserProvider, useUser } from './UserContext'
import * as api from '../utils/api'

vi.mock('../utils/api')

// Test component to access context
function TestComponent() {
  const { currentUser, loading, selectUser, logout, updateCurrentUser } = useUser()

  return (
    <div>
      <div data-testid="loading">{loading.toString()}</div>
      <div data-testid="user">{currentUser ? currentUser.name : 'none'}</div>
      <button onClick={() => selectUser(1)}>Select User</button>
      <button onClick={logout}>Logout</button>
      <button onClick={() => updateCurrentUser({ name: 'Updated' })}>Update</button>
    </div>
  )
}

describe('UserContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('UserProvider', () => {
    it('should load without saved user', async () => {
      render(
        <UserProvider>
          <TestComponent />
        </UserProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false')
      })

      expect(screen.getByTestId('user')).toHaveTextContent('none')
    })

    it('should load saved user from localStorage', async () => {
      localStorage.setItem('crosswod_user_id', '1')
      api.getUser.mockResolvedValueOnce({ id: 1, name: 'Saved User' })

      render(
        <UserProvider>
          <TestComponent />
        </UserProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('Saved User')
      })

      expect(api.getUser).toHaveBeenCalledWith(1)
    })

    it('should handle failed user load', async () => {
      localStorage.setItem('crosswod_user_id', '999')
      api.getUser.mockRejectedValueOnce(new Error('Not found'))

      render(
        <UserProvider>
          <TestComponent />
        </UserProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false')
      })

      expect(screen.getByTestId('user')).toHaveTextContent('none')
      expect(localStorage.getItem('crosswod_user_id')).toBeNull()
    })
  })

  describe('selectUser', () => {
    it('should select user and save to localStorage', async () => {
      api.getUser.mockResolvedValueOnce({ id: 1, name: 'Selected User' })

      render(
        <UserProvider>
          <TestComponent />
        </UserProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false')
      })

      await act(async () => {
        await userEvent.click(screen.getByText('Select User'))
      })

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('Selected User')
      })

      expect(localStorage.setItem).toHaveBeenCalledWith('crosswod_user_id', '1')
    })

    it('should handle selection error', async () => {
      api.getUser.mockRejectedValueOnce(new Error('Failed'))

      render(
        <UserProvider>
          <TestComponent />
        </UserProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false')
      })

      await act(async () => {
        await userEvent.click(screen.getByText('Select User'))
      })

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('none')
      })
    })
  })

  describe('logout', () => {
    it('should clear user and localStorage', async () => {
      localStorage.setItem('crosswod_user_id', '1')
      api.getUser.mockResolvedValueOnce({ id: 1, name: 'Test User' })

      render(
        <UserProvider>
          <TestComponent />
        </UserProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('Test User')
      })

      await act(async () => {
        await userEvent.click(screen.getByText('Logout'))
      })

      expect(screen.getByTestId('user')).toHaveTextContent('none')
      expect(localStorage.removeItem).toHaveBeenCalledWith('crosswod_user_id')
    })
  })

  describe('updateCurrentUser', () => {
    it('should update user data', async () => {
      localStorage.setItem('crosswod_user_id', '1')
      api.getUser.mockResolvedValueOnce({ id: 1, name: 'Original' })

      render(
        <UserProvider>
          <TestComponent />
        </UserProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('Original')
      })

      await act(async () => {
        await userEvent.click(screen.getByText('Update'))
      })

      expect(screen.getByTestId('user')).toHaveTextContent('Updated')
    })
  })

  describe('useUser hook', () => {
    it('should throw error when used outside provider', () => {
      const consoleError = console.error
      console.error = vi.fn()

      expect(() => {
        render(<TestComponent />)
      }).toThrow('useUser must be used within a UserProvider')

      console.error = consoleError
    })
  })
})
