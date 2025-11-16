import { useState, useEffect } from 'react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { TrendingUp, Trophy, Scale } from 'lucide-react';
import { useUser } from '../context/UserContext';
import {
  getExercises,
  getExerciseProgress,
  getBodyWeightProgress,
  getMuscleGroupBalance,
  getPersonalRecords
} from '../utils/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function Progress() {
  const { currentUser } = useUser();
  const [exercises, setExercises] = useState([]);
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [exerciseProgress, setExerciseProgress] = useState(null);
  const [bodyWeightData, setBodyWeightData] = useState(null);
  const [muscleBalance, setMuscleBalance] = useState(null);
  const [personalRecords, setPersonalRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('exercises');

  useEffect(() => {
    if (currentUser) {
      loadInitialData();
    }
  }, [currentUser]);

  useEffect(() => {
    if (selectedExercise) {
      loadExerciseProgress(selectedExercise);
    }
  }, [selectedExercise]);

  const loadInitialData = async () => {
    try {
      const [exerciseData, bodyWeight, balance, prs] = await Promise.all([
        getExercises({ user_id: currentUser.id }),
        getBodyWeightProgress(currentUser.id, 90),
        getMuscleGroupBalance(currentUser.id, 30),
        getPersonalRecords(currentUser.id)
      ]);
      setExercises(exerciseData);
      setBodyWeightData(bodyWeight);
      setMuscleBalance(balance.muscle_groups);
      setPersonalRecords(prs);
      if (exerciseData.length > 0) {
        setSelectedExercise(exerciseData[0].id);
      }
    } catch (error) {
      console.error('Failed to load progress data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadExerciseProgress = async (exerciseId) => {
    try {
      const data = await getExerciseProgress(currentUser.id, exerciseId, 'weight', 90);
      setExerciseProgress(data);
    } catch (error) {
      console.error('Failed to load exercise progress:', error);
    }
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: 'rgba(255, 255, 255, 0.5)', maxTicksLimit: 6 }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: 'rgba(255, 255, 255, 0.5)' }
      }
    },
    elements: {
      line: { tension: 0.4 },
      point: { radius: 3, hoverRadius: 6 }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: 'rgba(255, 255, 255, 0.7)', padding: 10, font: { size: 11 } }
      }
    },
    cutout: '60%'
  };

  if (loading) {
    return (
      <div className="p-5 flex items-center justify-center h-full">
        <p className="text-muted">Loading progress...</p>
      </div>
    );
  }

  return (
    <div className="p-5 overflow-y-auto h-full">
      <div className="max-w-lg mx-auto">
        <h2 className="text-2xl font-bold mb-5">Progress</h2>

        {/* Tabs */}
        <div className="flex gap-2 mb-5">
          {[
            { id: 'exercises', label: 'Exercises' },
            { id: 'body', label: 'Body' },
            { id: 'prs', label: 'PRs' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-accent text-white'
                  : 'bg-white/5 text-muted'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Exercise Progress */}
        {activeTab === 'exercises' && (
          <div className="space-y-4 slide-up">
            <div className="glass-subtle p-4">
              <label className="text-sm text-secondary mb-2 block">Select Exercise</label>
              <select
                value={selectedExercise || ''}
                onChange={(e) => setSelectedExercise(parseInt(e.target.value))}
                className="w-full"
              >
                {exercises.map((ex) => (
                  <option key={ex.id} value={ex.id}>
                    {ex.name}
                  </option>
                ))}
              </select>
            </div>

            {exerciseProgress && exerciseProgress.dates.length > 0 ? (
              <div className="glass-subtle p-4">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp size={18} className="text-accent" />
                  <h3 className="font-semibold">Weight Progress</h3>
                </div>
                <div style={{ height: '200px' }}>
                  <Line
                    data={{
                      labels: exerciseProgress.dates.map((d) =>
                        new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                      ),
                      datasets: [
                        {
                          label: 'Weight (kg)',
                          data: exerciseProgress.values,
                          borderColor: '#0A84FF',
                          backgroundColor: 'rgba(10, 132, 255, 0.1)',
                          fill: true
                        }
                      ]
                    }}
                    options={chartOptions}
                  />
                </div>
              </div>
            ) : (
              <div className="glass-subtle p-4 text-center text-muted">
                No data available for this exercise yet.
              </div>
            )}

            {/* Muscle Group Balance */}
            {muscleBalance && Object.keys(muscleBalance).length > 0 && (
              <div className="glass-subtle p-4">
                <h3 className="font-semibold mb-3">Muscle Group Balance (30 days)</h3>
                <div style={{ height: '250px' }}>
                  <Doughnut
                    data={{
                      labels: Object.keys(muscleBalance).map(
                        (k) => k.charAt(0).toUpperCase() + k.slice(1).replace('_', ' ')
                      ),
                      datasets: [
                        {
                          data: Object.values(muscleBalance),
                          backgroundColor: [
                            '#FF6384',
                            '#36A2EB',
                            '#FFCE56',
                            '#4BC0C0',
                            '#9966FF',
                            '#FF9F40',
                            '#FF6384',
                            '#C9CBCF',
                            '#7C4DFF',
                            '#00E676'
                          ]
                        }
                      ]
                    }}
                    options={doughnutOptions}
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {/* Body Metrics */}
        {activeTab === 'body' && (
          <div className="space-y-4 slide-up">
            {bodyWeightData && bodyWeightData.dates.length > 0 ? (
              <div className="glass-subtle p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Scale size={18} className="text-success" />
                  <h3 className="font-semibold">Body Weight</h3>
                </div>
                <div style={{ height: '200px' }}>
                  <Line
                    data={{
                      labels: bodyWeightData.dates.map((d) =>
                        new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                      ),
                      datasets: [
                        {
                          label: 'Weight (kg)',
                          data: bodyWeightData.weights,
                          borderColor: '#30D158',
                          backgroundColor: 'rgba(48, 209, 88, 0.1)',
                          fill: true
                        }
                      ]
                    }}
                    options={chartOptions}
                  />
                </div>
              </div>
            ) : (
              <div className="glass-subtle p-4 text-center text-muted">
                No body weight data recorded yet.
              </div>
            )}
          </div>
        )}

        {/* Personal Records */}
        {activeTab === 'prs' && (
          <div className="space-y-3 slide-up">
            {personalRecords.length === 0 ? (
              <div className="glass-subtle p-4 text-center text-muted">
                No personal records yet. Keep training!
              </div>
            ) : (
              personalRecords.map((pr) => (
                <div key={pr.id} className="glass-subtle p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <Trophy size={16} className="text-warning" />
                        <h4 className="font-semibold">{pr.exercise_name}</h4>
                      </div>
                      <div className="text-xs text-muted mt-1">
                        {pr.record_type === 'max_weight' ? 'Max Weight' : 'Max Volume'}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-accent">
                        {pr.record_type === 'max_weight'
                          ? `${pr.value}kg`
                          : `${Math.round(pr.value)}kg`}
                      </div>
                      {pr.reps && (
                        <div className="text-xs text-muted">{pr.reps} reps</div>
                      )}
                    </div>
                  </div>
                  <div className="text-xs text-muted mt-2">
                    Achieved: {new Date(pr.achieved_at).toLocaleDateString()}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
