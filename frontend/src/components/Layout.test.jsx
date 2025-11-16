import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import Layout from './Layout'

describe('Layout Component', () => {
  const renderWithRouter = (initialRoute = '/') => {
    return render(
      <MemoryRouter initialEntries={[initialRoute]}>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<div>Home Content</div>} />
            <Route path="workout" element={<div>Workout Content</div>} />
            <Route path="history" element={<div>History Content</div>} />
            <Route path="progress" element={<div>Progress Content</div>} />
            <Route path="settings" element={<div>Settings Content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    )
  }

  it('should render navigation bar', () => {
    renderWithRouter()
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Workout')).toBeInTheDocument()
    expect(screen.getByText('History')).toBeInTheDocument()
    expect(screen.getByText('Progress')).toBeInTheDocument()
    expect(screen.getByText('Profile')).toBeInTheDocument()
  })

  it('should render outlet content', () => {
    renderWithRouter()
    expect(screen.getByText('Home Content')).toBeInTheDocument()
  })

  it('should highlight active route', () => {
    renderWithRouter('/workout')
    const workoutLink = screen.getByText('Workout')
    expect(workoutLink).toHaveClass('text-accent')
  })

  it('should render workout content on /workout route', () => {
    renderWithRouter('/workout')
    expect(screen.getByText('Workout Content')).toBeInTheDocument()
  })

  it('should render history content on /history route', () => {
    renderWithRouter('/history')
    expect(screen.getByText('History Content')).toBeInTheDocument()
  })

  it('should render progress content on /progress route', () => {
    renderWithRouter('/progress')
    expect(screen.getByText('Progress Content')).toBeInTheDocument()
  })

  it('should render settings content on /settings route', () => {
    renderWithRouter('/settings')
    expect(screen.getByText('Settings Content')).toBeInTheDocument()
  })

  it('should have correct structure', () => {
    const { container } = renderWithRouter()
    const main = container.querySelector('main')
    const nav = container.querySelector('nav')

    expect(main).toBeInTheDocument()
    expect(nav).toBeInTheDocument()
    expect(nav).toHaveClass('glass')
  })

  it('should have safe area padding classes', () => {
    const { container } = renderWithRouter()
    const main = container.querySelector('main')
    const nav = container.querySelector('nav')

    expect(main).toHaveClass('safe-top')
    expect(nav).toHaveClass('safe-bottom')
  })
})
