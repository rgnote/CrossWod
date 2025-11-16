import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Flame, Target, Trophy, Calendar } from 'lucide-react';
import { useUser } from '../context/UserContext';
import {
  getWeeklySummary,
  getStreakInfo,
  getWorkouts,
  getTemplates,
  startWorkoutFromTemplate
} from '../utils/api';

export default function Dashboard() {
  const { currentUser } = useUser();
  const navigate = useNavigate();
  const [weekSummary, setWeekSummary] = useState(null);
  const [streakInfo, setStreakInfo] = useState(null);
  const [recentWorkouts, setRecentWorkouts] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (currentUser) {
      loadDashboardData();
    }
  }, [currentUser]);

  const loadDashboardData = async () => {
    try {
      const [summary, streak, workouts, temps] = await Promise.all([
        getWeeklySummary(currentUser.id),
        getStreakInfo(currentUser.id),
        getWorkouts(currentUser.id, 5),
        getTemplates(currentUser.id)
      ]);
      setWeekSummary(summary);
      setStreakInfo(streak);
      setRecentWorkouts(workouts);
      setTemplates(temps);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartWorkout = () => {
    if (navigator.vibrate) navigator.vibrate(10);
    navigate('/workout');
  };

  const handleStartFromTemplate = async (templateId) => {
    if (navigator.vibrate) navigator.vibrate(10);
    try {
      const workout = await startWorkoutFromTemplate(templateId, currentUser.id);
      navigate(`/workout/${workout.id}`);
    } catch (error) {
      console.error('Failed to start workout from template:', error);
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0m';
    const mins = Math.floor(seconds / 60);
    if (mins < 60) return `${mins}m`;
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return `${hours}h ${remainingMins}m`;
  };

  if (loading) {
    return (
      <div className="p-5 flex items-center justify-center h-full">
        <p className="text-muted">Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="p-5 pb-2 overflow-y-auto h-full">
      <div className="max-w-lg mx-auto">
        {/* Header */}
        <div className="mb-6 slide-up">
          <h2 className="text-2xl font-bold">
            Hey, {currentUser?.name?.split(' ')[0]}!
          </h2>
          <p className="text-secondary">Ready to crush your workout?</p>
        </div>

        {/* Quick Start */}
        <button
          onClick={handleStartWorkout}
          className="w-full glass p-5 flex items-center justify-between mb-5 transition-all hover:scale-[1.02] active:scale-[0.98] slide-up"
        >
          <div>
            <div className="font-semibold text-lg">Start Workout</div>
            <div className="text-sm text-secondary">Begin a new session</div>
          </div>
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center"
            style={{ background: 'var(--accent)' }}
          >
            <Play size={24} fill="white" />
          </div>
        </button>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3 mb-5">
          <div className="glass-subtle p-4 slide-up" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center gap-2 mb-2">
              <Flame size={18} className="text-warning" />
              <span className="text-sm text-secondary">Streak</span>
            </div>
            <div className="text-2xl font-bold">{streakInfo?.current_streak || 0}</div>
            <div className="text-xs text-muted">days</div>
          </div>

          <div className="glass-subtle p-4 slide-up" style={{ animationDelay: '0.15s' }}>
            <div className="flex items-center gap-2 mb-2">
              <Calendar size={18} className="text-accent" />
              <span className="text-sm text-secondary">This Week</span>
            </div>
            <div className="text-2xl font-bold">{weekSummary?.total_workouts || 0}</div>
            <div className="text-xs text-muted">workouts</div>
          </div>

          <div className="glass-subtle p-4 slide-up" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center gap-2 mb-2">
              <Target size={18} className="text-success" />
              <span className="text-sm text-secondary">Volume</span>
            </div>
            <div className="text-2xl font-bold">
              {weekSummary?.total_volume ? Math.round(weekSummary.total_volume).toLocaleString() : 0}
            </div>
            <div className="text-xs text-muted">kg total</div>
          </div>

          <div className="glass-subtle p-4 slide-up" style={{ animationDelay: '0.25s' }}>
            <div className="flex items-center gap-2 mb-2">
              <Trophy size={18} className="text-warning" />
              <span className="text-sm text-secondary">Total</span>
            </div>
            <div className="text-2xl font-bold">{streakInfo?.total_workouts || 0}</div>
            <div className="text-xs text-muted">workouts</div>
          </div>
        </div>

        {/* Templates */}
        {templates.length > 0 && (
          <div className="mb-5 slide-up" style={{ animationDelay: '0.3s' }}>
            <h3 className="font-semibold mb-3">Quick Start Templates</h3>
            <div className="space-y-2">
              {templates.slice(0, 3).map((template) => (
                <button
                  key={template.id}
                  onClick={() => handleStartFromTemplate(template.id)}
                  className="w-full glass-subtle p-3 flex items-center justify-between transition-all hover:scale-[1.01] active:scale-[0.99]"
                >
                  <div className="text-left">
                    <div className="font-medium">{template.name}</div>
                    <div className="text-xs text-muted">
                      {template.exercises.length} exercises
                      {template.category && ` • ${template.category}`}
                    </div>
                  </div>
                  <Play size={18} className="text-accent" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Recent Workouts */}
        {recentWorkouts.length > 0 && (
          <div className="slide-up" style={{ animationDelay: '0.35s' }}>
            <h3 className="font-semibold mb-3">Recent Workouts</h3>
            <div className="space-y-2">
              {recentWorkouts.map((workout) => (
                <div key={workout.id} className="glass-subtle p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">
                        {workout.name || 'Workout'}
                      </div>
                      <div className="text-xs text-muted">
                        {new Date(workout.started_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm">
                        {workout.exercise_count} exercises
                      </div>
                      <div className="text-xs text-muted">
                        {formatDuration(workout.duration_seconds)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
