const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Don't set Content-Type for FormData
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  // Handle empty responses
  const text = await response.text();
  return text ? JSON.parse(text) : {};
}

// Users
export const getUsers = () => request('/users/');
export const createUser = (name) => request('/users/', {
  method: 'POST',
  body: JSON.stringify({ name }),
});
export const getUser = (userId) => request(`/users/${userId}`);
export const updateUser = (userId, data) => request(`/users/${userId}`, {
  method: 'PUT',
  body: JSON.stringify(data),
});
export const deleteUser = (userId) => request(`/users/${userId}`, {
  method: 'DELETE',
});
export const uploadProfilePicture = (userId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return request(`/users/${userId}/profile-picture`, {
    method: 'POST',
    body: formData,
  });
};
export const getProfilePictureUrl = (userId) => `${API_BASE}/users/${userId}/profile-picture`;

// Exercises
export const getExercises = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return request(`/exercises/${query ? `?${query}` : ''}`);
};
export const getCategories = () => request('/exercises/categories');
export const getMuscleGroups = () => request('/exercises/muscle-groups');
export const createExercise = (userId, data) => request(`/exercises/?user_id=${userId}`, {
  method: 'POST',
  body: JSON.stringify(data),
});

// Workouts
export const getWorkouts = (userId, limit = 50, offset = 0) =>
  request(`/workouts/?user_id=${userId}&limit=${limit}&offset=${offset}`);
export const getWorkout = (workoutId) => request(`/workouts/${workoutId}`);
export const createWorkout = (userId, data) => request(`/workouts/?user_id=${userId}`, {
  method: 'POST',
  body: JSON.stringify(data),
});
export const updateWorkout = (workoutId, data) => request(`/workouts/${workoutId}`, {
  method: 'PUT',
  body: JSON.stringify(data),
});
export const deleteWorkout = (workoutId) => request(`/workouts/${workoutId}`, {
  method: 'DELETE',
});
export const addExerciseToWorkout = (workoutId, data) => request(`/workouts/${workoutId}/exercises`, {
  method: 'POST',
  body: JSON.stringify(data),
});
export const addSet = (workoutExerciseId, data) => request(`/workouts/exercises/${workoutExerciseId}/sets`, {
  method: 'POST',
  body: JSON.stringify(data),
});
export const updateSet = (setId, data) => request(`/workouts/sets/${setId}`, {
  method: 'PUT',
  body: JSON.stringify(data),
});
export const deleteSet = (setId) => request(`/workouts/sets/${setId}`, {
  method: 'DELETE',
});
export const getPersonalRecords = (userId, exerciseId = null) => {
  const params = exerciseId ? `?exercise_id=${exerciseId}` : '';
  return request(`/workouts/prs/${userId}${params}`);
};

// Body Metrics
export const getBodyMetrics = (userId, limit = 100) =>
  request(`/body-metrics/?user_id=${userId}&limit=${limit}`);
export const createBodyMetric = (userId, data) => request(`/body-metrics/?user_id=${userId}`, {
  method: 'POST',
  body: JSON.stringify(data),
});
export const deleteBodyMetric = (metricId) => request(`/body-metrics/${metricId}`, {
  method: 'DELETE',
});
export const getProgressPhotos = (userId, limit = 50) =>
  request(`/body-metrics/photos?user_id=${userId}&limit=${limit}`);
export const uploadProgressPhoto = (userId, file, category, photoDate, notes) => {
  const formData = new FormData();
  formData.append('file', file);
  const params = new URLSearchParams({
    user_id: userId,
    photo_date: photoDate,
    ...(category && { category }),
    ...(notes && { notes }),
  });
  return request(`/body-metrics/photos?${params}`, {
    method: 'POST',
    body: formData,
  });
};
export const getProgressPhotoUrl = (photoId) => `${API_BASE}/body-metrics/photos/${photoId}/image`;

// Templates
export const getTemplates = (userId) => request(`/templates/?user_id=${userId}`);
export const getTemplate = (templateId) => request(`/templates/${templateId}`);
export const createTemplate = (userId, data) => request(`/templates/?user_id=${userId}`, {
  method: 'POST',
  body: JSON.stringify(data),
});
export const updateTemplate = (templateId, data) => request(`/templates/${templateId}`, {
  method: 'PUT',
  body: JSON.stringify(data),
});
export const deleteTemplate = (templateId) => request(`/templates/${templateId}`, {
  method: 'DELETE',
});
export const startWorkoutFromTemplate = (templateId, userId) =>
  request(`/templates/${templateId}/start?user_id=${userId}`, {
    method: 'POST',
  });

// Analytics
export const getWeeklySummary = (userId, weekOffset = 0) =>
  request(`/analytics/weekly-summary?user_id=${userId}&week_offset=${weekOffset}`);
export const getExerciseProgress = (userId, exerciseId, metricType = 'weight', days = 90) =>
  request(`/analytics/exercise-progress?user_id=${userId}&exercise_id=${exerciseId}&metric_type=${metricType}&days=${days}`);
export const getBodyWeightProgress = (userId, days = 90) =>
  request(`/analytics/body-weight-progress?user_id=${userId}&days=${days}`);
export const getStreakInfo = (userId) => request(`/analytics/streak?user_id=${userId}`);
export const getMuscleGroupBalance = (userId, days = 30) =>
  request(`/analytics/muscle-group-balance?user_id=${userId}&days=${days}`);
export const getWorkoutFrequency = (userId, days = 30) =>
  request(`/analytics/workout-frequency?user_id=${userId}&days=${days}`);

// Health check
export const healthCheck = () => request('/health');
