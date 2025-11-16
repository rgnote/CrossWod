import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Plus, Check, Timer, Trash2, Save, X, Dumbbell } from 'lucide-react';
import { useUser } from '../context/UserContext';
import {
  createWorkout,
  getWorkout,
  updateWorkout,
  addExerciseToWorkout,
  addSet,
  updateSet,
  deleteSet,
  getExercises
} from '../utils/api';

export default function Workout() {
  const { workoutId } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useUser();

  const [workout, setWorkout] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [showExerciseModal, setShowExerciseModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredExercises, setFilteredExercises] = useState([]);
  const [restTimer, setRestTimer] = useState(0);
  const [isResting, setIsResting] = useState(false);
  const [workoutDuration, setWorkoutDuration] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showStartScreen, setShowStartScreen] = useState(false);

  const timerRef = useRef(null);
  const durationRef = useRef(null);
  const startTimeRef = useRef(null);

  useEffect(() => {
    loadExercises();
    if (workoutId) {
      loadWorkout(workoutId);
    } else {
      // Show start screen instead of auto-creating workout
      setShowStartScreen(true);
      setLoading(false);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (durationRef.current) clearInterval(durationRef.current);
    };
  }, [workoutId]);

  const loadExercises = async () => {
    try {
      const data = await getExercises({ user_id: currentUser.id });
      setExercises(data);
      setFilteredExercises(data);
    } catch (error) {
      console.error('Failed to load exercises:', error);
    }
  };

  const loadWorkout = async (id) => {
    try {
      const data = await getWorkout(id);
      setWorkout(data);
      startTimeRef.current = new Date(data.started_at);
      startDurationTimer();
    } catch (error) {
      console.error('Failed to load workout:', error);
    } finally {
      setLoading(false);
    }
  };

  const startNewWorkout = async () => {
    setLoading(true);
    try {
      const newWorkout = await createWorkout(currentUser.id, {
        started_at: new Date().toISOString(),
        exercises: []
      });
      setWorkout(newWorkout);
      startTimeRef.current = new Date();
      startDurationTimer();
      setShowStartScreen(false);
      navigate(`/workout/${newWorkout.id}`, { replace: true });
    } catch (error) {
      console.error('Failed to create workout:', error);
    } finally {
      setLoading(false);
    }
  };

  const startDurationTimer = () => {
    durationRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTimeRef.current.getTime()) / 1000);
      setWorkoutDuration(elapsed);
    }, 1000);
  };

  const startRestTimer = (seconds = 90) => {
    if (navigator.vibrate) navigator.vibrate(10);
    setRestTimer(seconds);
    setIsResting(true);

    if (timerRef.current) clearInterval(timerRef.current);

    timerRef.current = setInterval(() => {
      setRestTimer((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          setIsResting(false);
          if (navigator.vibrate) navigator.vibrate([100, 50, 100]);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const stopRestTimer = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setIsResting(false);
    setRestTimer(0);
  };

  const handleSearchExercise = (query) => {
    setSearchQuery(query);
    const filtered = exercises.filter((ex) =>
      ex.name.toLowerCase().includes(query.toLowerCase()) ||
      ex.category.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredExercises(filtered);
  };

  const handleAddExercise = async (exercise) => {
    if (navigator.vibrate) navigator.vibrate(10);
    try {
      const updatedWorkout = await addExerciseToWorkout(workout.id, {
        exercise_id: exercise.id,
        order: workout.exercises.length + 1,
        sets: []
      });
      setWorkout(updatedWorkout);
      setShowExerciseModal(false);
      setSearchQuery('');
      setFilteredExercises(exercises);
    } catch (error) {
      console.error('Failed to add exercise:', error);
    }
  };

  const handleAddSet = async (workoutExerciseId, lastSet = null) => {
    if (navigator.vibrate) navigator.vibrate(10);
    const we = workout.exercises.find((e) => e.id === workoutExerciseId);
    const setNumber = we.sets.length + 1;

    try {
      await addSet(workoutExerciseId, {
        set_number: setNumber,
        reps: lastSet?.reps || null,
        weight: lastSet?.weight || null,
        is_warmup: false
      });
      const updatedWorkout = await getWorkout(workout.id);
      setWorkout(updatedWorkout);
    } catch (error) {
      console.error('Failed to add set:', error);
    }
  };

  const handleUpdateSet = async (setId, field, value) => {
    try {
      await updateSet(setId, { [field]: value });
      const updatedWorkout = await getWorkout(workout.id);
      setWorkout(updatedWorkout);
    } catch (error) {
      console.error('Failed to update set:', error);
    }
  };

  const handleDeleteSet = async (setId) => {
    if (navigator.vibrate) navigator.vibrate(10);
    try {
      await deleteSet(setId);
      const updatedWorkout = await getWorkout(workout.id);
      setWorkout(updatedWorkout);
    } catch (error) {
      console.error('Failed to delete set:', error);
    }
  };

  const handleFinishWorkout = async () => {
    if (navigator.vibrate) navigator.vibrate([50, 50, 50]);
    try {
      await updateWorkout(workout.id, {
        completed_at: new Date().toISOString(),
        duration_seconds: workoutDuration
      });
      if (durationRef.current) clearInterval(durationRef.current);
      navigate('/history');
    } catch (error) {
      console.error('Failed to finish workout:', error);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="p-5 flex items-center justify-center h-full">
        <p className="text-muted">Loading workout...</p>
      </div>
    );
  }

  // Show start workout screen
  if (showStartScreen) {
    return (
      <div className="p-5 flex flex-col items-center justify-center h-full">
        <div className="text-center max-w-sm">
          <div className="glass-subtle p-8 mb-6">
            <Dumbbell size={64} className="mx-auto mb-4 text-accent" />
            <h2 className="text-2xl font-bold mb-2">Ready to Train?</h2>
            <p className="text-muted mb-6">
              Start a new workout session to track your exercises, sets, and progress.
            </p>
            <button
              onClick={startNewWorkout}
              className="btn btn-primary w-full py-3 text-lg"
            >
              <Plus size={24} />
              Start Workout
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 glass" style={{ borderRadius: '0 0 20px 20px', borderTop: 'none' }}>
        <div className="flex justify-between items-center">
          <div>
            <h3 className="font-semibold">Current Workout</h3>
            <div className="text-sm text-secondary">{formatTime(workoutDuration)}</div>
          </div>
          <button onClick={handleFinishWorkout} className="btn btn-primary">
            <Check size={18} />
            Finish
          </button>
        </div>
      </div>

      {/* Rest Timer Overlay */}
      {isResting && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center"
          style={{ background: 'rgba(0, 0, 0, 0.8)' }}
          onClick={stopRestTimer}
        >
          <div className="text-center">
            <Timer size={48} className="mx-auto mb-4 text-accent" />
            <div className="text-6xl font-bold mb-2">{formatTime(restTimer)}</div>
            <p className="text-secondary">Tap to skip</p>
          </div>
        </div>
      )}

      {/* Exercises List */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-lg mx-auto space-y-4">
          {workout?.exercises.map((we) => (
            <div key={we.id} className="glass-subtle p-4">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold">{we.exercise.name}</h4>
                <span className="text-xs text-muted px-2 py-1 rounded-full bg-white/10">
                  {we.exercise.category}
                </span>
              </div>

              {/* Sets */}
              <div className="space-y-2">
                <div className="grid grid-cols-4 gap-2 text-xs text-muted font-medium">
                  <div>SET</div>
                  <div>WEIGHT</div>
                  <div>REPS</div>
                  <div></div>
                </div>

                {we.sets.map((set) => (
                  <div key={set.id} className="grid grid-cols-4 gap-2 items-center">
                    <div className="text-sm font-medium">{set.set_number}</div>
                    <input
                      type="number"
                      value={set.weight || ''}
                      onChange={(e) =>
                        handleUpdateSet(set.id, 'weight', parseFloat(e.target.value) || null)
                      }
                      placeholder="kg"
                      className="text-sm py-2 px-2"
                      style={{ borderRadius: '8px' }}
                    />
                    <input
                      type="number"
                      value={set.reps || ''}
                      onChange={(e) =>
                        handleUpdateSet(set.id, 'reps', parseInt(e.target.value) || null)
                      }
                      placeholder="reps"
                      className="text-sm py-2 px-2"
                      style={{ borderRadius: '8px' }}
                    />
                    <button
                      onClick={() => handleDeleteSet(set.id)}
                      className="btn btn-ghost btn-icon p-2"
                    >
                      <Trash2 size={14} className="text-danger" />
                    </button>
                  </div>
                ))}

                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => handleAddSet(we.id, we.sets[we.sets.length - 1])}
                    className="btn btn-secondary flex-1 text-sm py-2"
                  >
                    <Plus size={16} />
                    Add Set
                  </button>
                  <button
                    onClick={() => startRestTimer(90)}
                    className="btn btn-ghost text-sm py-2"
                  >
                    <Timer size={16} />
                    Rest
                  </button>
                </div>
              </div>
            </div>
          ))}

          <button
            onClick={() => setShowExerciseModal(true)}
            className="w-full glass p-4 flex items-center justify-center gap-2 text-accent font-medium transition-all hover:scale-[1.01] active:scale-[0.99]"
          >
            <Plus size={20} />
            Add Exercise
          </button>
        </div>
      </div>

      {/* Exercise Selection Modal */}
      {showExerciseModal && (
        <div className="fixed inset-0 z-50 flex items-end" style={{ background: 'rgba(0, 0, 0, 0.6)' }}>
          <div
            className="w-full glass slide-up"
            style={{
              borderRadius: '24px 24px 0 0',
              maxHeight: '80vh',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <div className="p-4 border-b border-white/10">
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-semibold text-lg">Add Exercise</h3>
                <button
                  onClick={() => setShowExerciseModal(false)}
                  className="btn btn-ghost btn-icon"
                >
                  <X size={20} />
                </button>
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearchExercise(e.target.value)}
                placeholder="Search exercises..."
                autoFocus
              />
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              <div className="space-y-2">
                {filteredExercises.map((exercise) => (
                  <button
                    key={exercise.id}
                    onClick={() => handleAddExercise(exercise)}
                    className="w-full glass-subtle p-3 text-left transition-all hover:scale-[1.01] active:scale-[0.99]"
                  >
                    <div className="font-medium">{exercise.name}</div>
                    <div className="text-xs text-muted">
                      {exercise.category} • {exercise.muscle_groups.join(', ')}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
