import { describe, it, expect, vi, beforeEach } from 'vitest'
import * as api from './api'

describe('API Utilities', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  describe('getUsers', () => {
    it('should fetch users successfully', async () => {
      const mockUsers = [
        { id: 1, name: 'User 1' },
        { id: 2, name: 'User 2' }
      ]
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockUsers))
      })

      const result = await api.getUsers()
      expect(result).toEqual(mockUsers)
      expect(global.fetch).toHaveBeenCalledWith('/api/users/', expect.any(Object))
    })

    it('should handle fetch error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Server error' })
      })

      await expect(api.getUsers()).rejects.toThrow('Server error')
    })
  })

  describe('createUser', () => {
    it('should create user successfully', async () => {
      const mockUser = { id: 1, name: 'New User' }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockUser))
      })

      const result = await api.createUser('New User')
      expect(result).toEqual(mockUser)
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/users/',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ name: 'New User' })
        })
      )
    })

    it('should handle creation error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: () => Promise.resolve({ detail: 'Validation error' })
      })

      await expect(api.createUser('')).rejects.toThrow('Validation error')
    })
  })

  describe('getUser', () => {
    it('should fetch single user', async () => {
      const mockUser = { id: 1, name: 'Test User' }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockUser))
      })

      const result = await api.getUser(1)
      expect(result).toEqual(mockUser)
    })

    it('should handle user not found', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ detail: 'User not found' })
      })

      await expect(api.getUser(999)).rejects.toThrow('User not found')
    })
  })

  describe('getExercises', () => {
    it('should fetch exercises with no params', async () => {
      const mockExercises = [{ id: 1, name: 'Bench Press' }]
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockExercises))
      })

      const result = await api.getExercises()
      expect(result).toEqual(mockExercises)
      expect(global.fetch).toHaveBeenCalledWith('/api/exercises/', expect.any(Object))
    })

    it('should fetch exercises with filters', async () => {
      const mockExercises = [{ id: 1, name: 'Bench Press', category: 'push' }]
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockExercises))
      })

      await api.getExercises({ category: 'push', search: 'bench' })
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('category=push'),
        expect.any(Object)
      )
    })
  })

  describe('getWorkouts', () => {
    it('should fetch workouts for user', async () => {
      const mockWorkouts = [{ id: 1, name: 'Workout 1' }]
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockWorkouts))
      })

      const result = await api.getWorkouts(1, 50, 0)
      expect(result).toEqual(mockWorkouts)
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workouts/?user_id=1&limit=50&offset=0',
        expect.any(Object)
      )
    })
  })

  describe('createWorkout', () => {
    it('should create workout successfully', async () => {
      const mockWorkout = { id: 1, name: 'New Workout' }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockWorkout))
      })

      const workoutData = {
        name: 'New Workout',
        started_at: new Date().toISOString(),
        exercises: []
      }

      const result = await api.createWorkout(1, workoutData)
      expect(result).toEqual(mockWorkout)
    })
  })

  describe('updateWorkout', () => {
    it('should update workout successfully', async () => {
      const mockWorkout = { id: 1, name: 'Updated' }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockWorkout))
      })

      const result = await api.updateWorkout(1, { name: 'Updated' })
      expect(result).toEqual(mockWorkout)
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workouts/1',
        expect.objectContaining({ method: 'PUT' })
      )
    })
  })

  describe('deleteWorkout', () => {
    it('should delete workout successfully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify({ message: 'Deleted' }))
      })

      const result = await api.deleteWorkout(1)
      expect(result).toEqual({ message: 'Deleted' })
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workouts/1',
        expect.objectContaining({ method: 'DELETE' })
      )
    })
  })

  describe('getPersonalRecords', () => {
    it('should fetch PRs for user', async () => {
      const mockPRs = [{ id: 1, value: 100 }]
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockPRs))
      })

      const result = await api.getPersonalRecords(1)
      expect(result).toEqual(mockPRs)
    })

    it('should fetch PRs for specific exercise', async () => {
      const mockPRs = [{ id: 1, exercise_id: 5 }]
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockPRs))
      })

      const result = await api.getPersonalRecords(1, 5)
      expect(result).toEqual(mockPRs)
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workouts/prs/1?exercise_id=5',
        expect.any(Object)
      )
    })
  })

  describe('getWeeklySummary', () => {
    it('should fetch weekly summary', async () => {
      const mockSummary = { total_workouts: 5, total_volume: 10000 }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockSummary))
      })

      const result = await api.getWeeklySummary(1, 0)
      expect(result).toEqual(mockSummary)
    })
  })

  describe('getStreakInfo', () => {
    it('should fetch streak info', async () => {
      const mockStreak = { current_streak: 7, longest_streak: 30 }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockStreak))
      })

      const result = await api.getStreakInfo(1)
      expect(result).toEqual(mockStreak)
    })
  })

  describe('healthCheck', () => {
    it('should check API health', async () => {
      const mockHealth = { status: 'healthy', version: '1.0.0' }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockHealth))
      })

      const result = await api.healthCheck()
      expect(result).toEqual(mockHealth)
    })
  })

  describe('getProfilePictureUrl', () => {
    it('should return correct URL', () => {
      const url = api.getProfilePictureUrl(123)
      expect(url).toBe('/api/users/123/profile-picture')
    })
  })

  describe('getProgressPhotoUrl', () => {
    it('should return correct URL', () => {
      const url = api.getProgressPhotoUrl(456)
      expect(url).toBe('/api/body-metrics/photos/456/image')
    })
  })

  describe('Error handling', () => {
    it('should handle network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(api.getUsers()).rejects.toThrow('Network error')
    })

    it('should handle empty responses', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve('')
      })

      const result = await api.getUsers()
      expect(result).toEqual({})
    })

    it('should handle malformed JSON', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve('not json')
      })

      await expect(api.getUsers()).rejects.toThrow()
    })
  })
})
