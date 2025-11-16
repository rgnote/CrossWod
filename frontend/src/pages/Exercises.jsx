import { useState, useEffect } from 'react';
import { Search, Plus, Filter, X } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { getExercises, getCategories, createExercise } from '../utils/api';

export default function Exercises() {
  const { currentUser } = useUser();
  const [exercises, setExercises] = useState([]);
  const [categories, setCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newExercise, setNewExercise] = useState({
    name: '',
    category: 'push',
    muscle_groups: [],
    equipment: '',
    description: ''
  });

  const muscleGroupOptions = [
    'chest', 'back', 'shoulders', 'biceps', 'triceps',
    'forearms', 'core', 'quadriceps', 'hamstrings',
    'glutes', 'calves', 'hip_flexors', 'full_body'
  ];

  useEffect(() => {
    loadData();
  }, [currentUser]);

  const loadData = async () => {
    try {
      const [exerciseData, categoryData] = await Promise.all([
        getExercises({ user_id: currentUser.id }),
        getCategories()
      ]);
      setExercises(exerciseData);
      setCategories(categoryData);
    } catch (error) {
      console.error('Failed to load exercises:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredExercises = exercises.filter((ex) => {
    const matchesSearch = ex.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ex.muscle_groups.some((mg) => mg.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = !selectedCategory || ex.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleCreateExercise = async (e) => {
    e.preventDefault();
    if (!newExercise.name.trim() || newExercise.muscle_groups.length === 0) return;

    try {
      const created = await createExercise(currentUser.id, newExercise);
      setExercises([...exercises, created]);
      setShowCreateModal(false);
      setNewExercise({
        name: '',
        category: 'push',
        muscle_groups: [],
        equipment: '',
        description: ''
      });
    } catch (error) {
      console.error('Failed to create exercise:', error);
    }
  };

  const toggleMuscleGroup = (mg) => {
    setNewExercise((prev) => ({
      ...prev,
      muscle_groups: prev.muscle_groups.includes(mg)
        ? prev.muscle_groups.filter((m) => m !== mg)
        : [...prev.muscle_groups, mg]
    }));
  };

  if (loading) {
    return (
      <div className="p-5 flex items-center justify-center h-full">
        <p className="text-muted">Loading exercises...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Exercises</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary text-sm"
          >
            <Plus size={16} />
            New
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-3">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search exercises..."
            className="pl-10"
          />
        </div>

        {/* Category Filter */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          <button
            onClick={() => setSelectedCategory('')}
            className={`px-3 py-1 rounded-full text-sm whitespace-nowrap transition-all ${
              !selectedCategory
                ? 'bg-accent text-white'
                : 'bg-white/10 text-muted'
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-full text-sm whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-accent text-white'
                  : 'bg-white/10 text-muted'
              }`}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Exercise List */}
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        <div className="max-w-lg mx-auto space-y-2">
          {filteredExercises.length === 0 ? (
            <div className="text-center py-10 text-muted">
              No exercises found.
            </div>
          ) : (
            filteredExercises.map((exercise, index) => (
              <div
                key={exercise.id}
                className="glass-subtle p-3 slide-up"
                style={{ animationDelay: `${Math.min(index * 0.02, 0.5)}s` }}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium">{exercise.name}</div>
                    <div className="text-xs text-muted mt-1">
                      {exercise.muscle_groups
                        .map((mg) => mg.charAt(0).toUpperCase() + mg.slice(1).replace('_', ' '))
                        .join(', ')}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-xs px-2 py-1 rounded-full bg-white/10">
                      {exercise.category}
                    </span>
                    {exercise.is_custom && (
                      <span className="text-xs text-accent">Custom</span>
                    )}
                  </div>
                </div>
                {exercise.equipment && (
                  <div className="text-xs text-secondary mt-2">
                    Equipment: {exercise.equipment}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Create Exercise Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-end" style={{ background: 'rgba(0, 0, 0, 0.6)' }}>
          <div
            className="w-full glass slide-up"
            style={{
              borderRadius: '24px 24px 0 0',
              maxHeight: '85vh',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <div className="p-4 border-b border-white/10">
              <div className="flex justify-between items-center">
                <h3 className="font-semibold text-lg">Create Exercise</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="btn btn-ghost btn-icon"
                >
                  <X size={20} />
                </button>
              </div>
            </div>

            <form onSubmit={handleCreateExercise} className="flex-1 overflow-y-auto p-4">
              <div className="space-y-4">
                <div>
                  <label>Name *</label>
                  <input
                    type="text"
                    value={newExercise.name}
                    onChange={(e) => setNewExercise({ ...newExercise, name: e.target.value })}
                    placeholder="Exercise name"
                    required
                  />
                </div>

                <div>
                  <label>Category *</label>
                  <select
                    value={newExercise.category}
                    onChange={(e) => setNewExercise({ ...newExercise, category: e.target.value })}
                  >
                    <option value="push">Push</option>
                    <option value="pull">Pull</option>
                    <option value="legs">Legs</option>
                    <option value="core">Core</option>
                    <option value="cardio">Cardio</option>
                    <option value="olympic">Olympic</option>
                  </select>
                </div>

                <div>
                  <label>Muscle Groups * (select at least one)</label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {muscleGroupOptions.map((mg) => (
                      <button
                        key={mg}
                        type="button"
                        onClick={() => toggleMuscleGroup(mg)}
                        className={`px-3 py-1 rounded-full text-sm transition-all ${
                          newExercise.muscle_groups.includes(mg)
                            ? 'bg-accent text-white'
                            : 'bg-white/10 text-muted'
                        }`}
                      >
                        {mg.charAt(0).toUpperCase() + mg.slice(1).replace('_', ' ')}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label>Equipment</label>
                  <input
                    type="text"
                    value={newExercise.equipment}
                    onChange={(e) => setNewExercise({ ...newExercise, equipment: e.target.value })}
                    placeholder="e.g., barbell, dumbbell, bodyweight"
                  />
                </div>

                <div>
                  <label>Description</label>
                  <textarea
                    value={newExercise.description}
                    onChange={(e) => setNewExercise({ ...newExercise, description: e.target.value })}
                    placeholder="Optional description..."
                    rows={3}
                  />
                </div>
              </div>

              <div className="mt-6">
                <button
                  type="submit"
                  className="btn btn-primary w-full"
                  disabled={!newExercise.name.trim() || newExercise.muscle_groups.length === 0}
                >
                  Create Exercise
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
