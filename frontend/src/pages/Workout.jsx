import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Plus, Check, Timer, Trash2, X, Dumbbell, ChevronDown, ChevronUp } from 'lucide-react';
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

const PHASES = [
  { id: 'warmup', label: 'Warm Up', color: 'text-warning' },
  { id: 'main', label: 'Main Workout', color: 'text-accent' },
  { id: 'cooldown', label: 'Cool Down', color: 'text-success' }
];

export default function Workout() {
  const { workoutId } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useUser();

  const [workout, setWorkout] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [showExerciseModal, setShowExerciseModal] = useState(false);
  const [selectedPhase, setSelectedPhase] = useState('main');
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredExercises, setFilteredExercises] = useState([]);
  const [restTimer, setRestTimer] = useState(0);
  const [isResting, setIsResting] = useState(false);
  const [workoutDuration, setWorkoutDuration] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showStartScreen, setShowStartScreen] = useState(false);
  const [collapsedPhases, setCollapsedPhases] = useState({});

  const timerRef = useRef(null);
  const durationRef = useRef(null);
  const startTimeRef = useRef(null);

  const weightUnit = currentUser?.weight_unit || 'kg';

  useEffect(() => {
    loadExercises();
    if (workoutId) {
      loadWorkout(workoutId);
    } else {
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
      const phaseExercises = workout.exercises.filter(e => e.phase === selectedPhase);
      const updatedWorkout = await addExerciseToWorkout(workout.id, {
        exercise_id: exercise.id,
        order: phaseExercises.length + 1,
        phase: selectedPhase,
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
        is_warmup: false,
        is_completed: false
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

  const handleToggleSetComplete = async (set) => {
    if (navigator.vibrate) navigator.vibrate(10);
    const newCompleted = !set.is_completed;
    try {
      await updateSet(set.id, { is_completed: newCompleted });
      const updatedWorkout = await getWorkout(workout.id);
      setWorkout(updatedWorkout);

      // Auto-start rest timer when completing a set
      if (newCompleted) {
        startRestTimer(90);
      }
    } catch (error) {
      console.error('Failed to toggle set completion:', error);
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

  const togglePhaseCollapse = (phaseId) => {
    setCollapsedPhases(prev => ({
      ...prev,
      [phaseId]: !prev[phaseId]
    }));
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getWorkoutProgress = () => {
    if (!workout) return { completed: 0, total: 0, percentage: 0 };
    const allSets = workout.exercises.flatMap(e => e.sets);
    const completed = allSets.filter(s => s.is_completed).length;
    const total = allSets.length;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    return { completed, total, percentage };
  };

  const getPhaseExercises = (phaseId) => {
    if (!workout) return [];
    return workout.exercises.filter(e => (e.phase || 'main') === phaseId);
  };

  if (loading) {
    return (
      <div className="p-5 flex items-center justify-center h-full">
        <p className="text-muted">Loading workout...</p>
      </div>
    );
  }

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

  const progress = getWorkoutProgress();

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 glass" style={{ borderRadius: '0 0 20px 20px', borderTop: 'none' }}>
        <div className="flex justify-between items-center mb-3">
          <div>
            <h3 className="font-semibold">Current Workout</h3>
            <div className="text-sm text-secondary">{formatTime(workoutDuration)}</div>
          </div>
          <button onClick={handleFinishWorkout} className="btn btn-primary">
            <Check size={18} />
            Finish
          </button>
        </div>

        {/* Progress Bar */}
        <div className="mt-2">
          <div className="flex justify-between text-xs text-muted mb-1">
            <span>Progress</span>
            <span>{progress.completed}/{progress.total} sets ({progress.percentage}%)</span>
          </div>
          <div className="w-full bg-white/10 rounded-full h-2">
            <div
              className="bg-accent h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress.percentage}%` }}
            />
          </div>
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

      {/* Exercises List by Phase */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-lg mx-auto space-y-4">
          {PHASES.map((phase) => {
            const phaseExercises = getPhaseExercises(phase.id);
            const isCollapsed = collapsedPhases[phase.id];
            const phaseSets = phaseExercises.flatMap(e => e.sets);
            const phaseCompleted = phaseSets.filter(s => s.is_completed).length;
            const phaseTotal = phaseSets.length;

            return (
              <div key={phase.id} className="glass-subtle">
                <button
                  onClick={() => togglePhaseCollapse(phase.id)}
                  className="w-full p-3 flex justify-between items-center"
                >
                  <div className="flex items-center gap-2">
                    <span className={`font-semibold ${phase.color}`}>{phase.label}</span>
                    {phaseTotal > 0 && (
                      <span className="text-xs text-muted">
                        ({phaseCompleted}/{phaseTotal})
                      </span>
                    )}
                  </div>
                  {isCollapsed ? <ChevronDown size={20} /> : <ChevronUp size={20} />}
                </button>

                {!isCollapsed && (
                  <div className="px-3 pb-3 space-y-3">
                    {phaseExercises.map((we) => (
                      <div key={we.id} className="bg-white/5 rounded-lg p-3">
                        <div className="flex justify-between items-center mb-3">
                          <h4 className="font-medium text-sm">{we.exercise.name}</h4>
                          <span className="text-xs text-muted px-2 py-1 rounded-full bg-white/10">
                            {we.exercise.category}
                          </span>
                        </div>

                        {/* Sets */}
                        <div className="space-y-2">
                          <div className="grid grid-cols-5 gap-2 text-xs text-muted font-medium">
                            <div>SET</div>
                            <div>{weightUnit.toUpperCase()}</div>
                            <div>REPS</div>
                            <div>DONE</div>
                            <div></div>
                          </div>

                          {we.sets.map((set) => (
                            <div key={set.id} className="grid grid-cols-5 gap-2 items-center">
                              <div className="text-sm font-medium">{set.set_number}</div>
                              <input
                                type="number"
                                value={set.weight || ''}
                                onChange={(e) =>
                                  handleUpdateSet(set.id, 'weight', parseFloat(e.target.value) || null)
                                }
                                placeholder={weightUnit}
                                className="text-sm py-1 px-2"
                                style={{ borderRadius: '6px' }}
                              />
                              <input
                                type="number"
                                value={set.reps || ''}
                                onChange={(e) =>
                                  handleUpdateSet(set.id, 'reps', parseInt(e.target.value) || null)
                                }
                                placeholder="reps"
                                className="text-sm py-1 px-2"
                                style={{ borderRadius: '6px' }}
                              />
                              <button
                                onClick={() => handleToggleSetComplete(set)}
                                className={`flex items-center justify-center w-8 h-8 rounded-full transition-all ${
                                  set.is_completed
                                    ? 'bg-success text-white'
                                    : 'bg-white/10 text-muted'
                                }`}
                              >
                                <Check size={16} />
                              </button>
                              <button
                                onClick={() => handleDeleteSet(set.id)}
                                className="btn btn-ghost btn-icon p-1"
                              >
                                <Trash2 size={14} className="text-danger" />
                              </button>
                            </div>
                          ))}

                          <div className="flex gap-2 mt-2">
                            <button
                              onClick={() => handleAddSet(we.id, we.sets[we.sets.length - 1])}
                              className="btn btn-secondary flex-1 text-xs py-1"
                            >
                              <Plus size={14} />
                              Add Set
                            </button>
                            <button
                              onClick={() => startRestTimer(90)}
                              className="btn btn-ghost text-xs py-1"
                            >
                              <Timer size={14} />
                              Rest
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}

                    <button
                      onClick={() => {
                        setSelectedPhase(phase.id);
                        setShowExerciseModal(true);
                      }}
                      className="w-full glass p-3 flex items-center justify-center gap-2 text-sm font-medium transition-all hover:bg-white/10"
                    >
                      <Plus size={16} />
                      Add {phase.label} Exercise
                    </button>
                  </div>
                )}
              </div>
            );
          })}
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
                <h3 className="font-semibold text-lg">
                  Add {PHASES.find(p => p.id === selectedPhase)?.label} Exercise
                </h3>
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
                    className="w-full glass-subtle p-3 text-left transition-all hover:bg-white/10"
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
