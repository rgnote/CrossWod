import { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Clock, Dumbbell, Weight } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { getWorkouts, getWorkoutFrequency } from '../utils/api';

export default function History() {
  const { currentUser } = useUser();
  const [workouts, setWorkouts] = useState([]);
  const [frequency, setFrequency] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState(new Date());

  useEffect(() => {
    if (currentUser) {
      loadHistory();
    }
  }, [currentUser]);

  const loadHistory = async () => {
    try {
      const [workoutData, freqData] = await Promise.all([
        getWorkouts(currentUser.id, 100),
        getWorkoutFrequency(currentUser.id, 90)
      ]);
      setWorkouts(workoutData);
      setFrequency(freqData.dates || {});
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    if (mins < 60) return `${mins}m`;
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return `${hours}h ${remainingMins}m`;
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();

    const days = [];
    for (let i = 0; i < startingDay; i++) {
      days.push(null);
    }
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(i);
    }
    return days;
  };

  const isWorkoutDay = (day) => {
    if (!day) return false;
    const dateStr = `${selectedMonth.getFullYear()}-${String(selectedMonth.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return frequency[dateStr] > 0;
  };

  const isToday = (day) => {
    if (!day) return false;
    const today = new Date();
    return (
      day === today.getDate() &&
      selectedMonth.getMonth() === today.getMonth() &&
      selectedMonth.getFullYear() === today.getFullYear()
    );
  };

  const prevMonth = () => {
    setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() + 1));
  };

  if (loading) {
    return (
      <div className="p-5 flex items-center justify-center h-full">
        <p className="text-muted">Loading history...</p>
      </div>
    );
  }

  return (
    <div className="p-5 overflow-y-auto h-full">
      <div className="max-w-lg mx-auto">
        <h2 className="text-2xl font-bold mb-5">Workout History</h2>

        {/* Calendar */}
        <div className="glass-subtle p-4 mb-5 slide-up">
          <div className="flex justify-between items-center mb-4">
            <button onClick={prevMonth} className="btn btn-ghost text-sm">
              ←
            </button>
            <h3 className="font-semibold">
              {selectedMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h3>
            <button onClick={nextMonth} className="btn btn-ghost text-sm">
              →
            </button>
          </div>

          <div className="grid grid-cols-7 gap-1 text-center">
            {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day, i) => (
              <div key={i} className="text-xs text-muted py-1">
                {day}
              </div>
            ))}
            {getDaysInMonth(selectedMonth).map((day, i) => (
              <div
                key={i}
                className={`py-2 text-sm rounded-lg ${
                  !day
                    ? ''
                    : isToday(day)
                    ? 'bg-accent text-white font-bold'
                    : isWorkoutDay(day)
                    ? 'bg-success/20 text-success font-medium'
                    : 'text-muted'
                }`}
              >
                {day}
              </div>
            ))}
          </div>
        </div>

        {/* Workout List */}
        <div className="space-y-3">
          {workouts.length === 0 ? (
            <div className="text-center py-10 text-muted">
              No workouts yet. Start your first workout!
            </div>
          ) : (
            workouts.map((workout, index) => (
              <div
                key={workout.id}
                className="glass-subtle p-4 slide-up"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-semibold">
                      {workout.name || 'Workout'}
                    </h4>
                    <div className="flex items-center gap-1 text-xs text-muted">
                      <CalendarIcon size={12} />
                      {new Date(workout.started_at).toLocaleDateString('en-US', {
                        weekday: 'short',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </div>
                  </div>
                  {workout.completed_at && (
                    <span className="text-xs px-2 py-1 rounded-full bg-success/20 text-success">
                      Completed
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="flex items-center gap-2">
                    <Dumbbell size={14} className="text-accent" />
                    <div>
                      <div className="text-sm font-medium">{workout.exercise_count}</div>
                      <div className="text-xs text-muted">exercises</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Weight size={14} className="text-warning" />
                    <div>
                      <div className="text-sm font-medium">{workout.total_sets}</div>
                      <div className="text-xs text-muted">sets</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock size={14} className="text-success" />
                    <div>
                      <div className="text-sm font-medium">
                        {formatDuration(workout.duration_seconds)}
                      </div>
                      <div className="text-xs text-muted">duration</div>
                    </div>
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t border-white/10">
                  <div className="text-xs text-muted">
                    Total Volume:{' '}
                    <span className="text-secondary font-medium">
                      {Math.round(workout.total_volume).toLocaleString()} kg
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
