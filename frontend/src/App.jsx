import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { UserProvider, useUser } from './context/UserContext';
import ProfileSelect from './pages/ProfileSelect';
import Dashboard from './pages/Dashboard';
import Workout from './pages/Workout';
import History from './pages/History';
import Progress from './pages/Progress';
import Exercises from './pages/Exercises';
import Settings from './pages/Settings';
import Layout from './components/Layout';

function ProtectedRoute({ children }) {
  const { currentUser, loading } = useUser();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="loader"></div>
          <p className="text-muted mt-3">Loading...</p>
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return <Navigate to="/profile" replace />;
  }

  return children;
}

function AppRoutes() {
  const { currentUser, loading } = useUser();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-2xl font-bold mb-2">CrossWod</div>
          <p className="text-muted">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      <Route
        path="/profile"
        element={
          currentUser ? <Navigate to="/" replace /> : <ProfileSelect />
        }
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="workout" element={<Workout />} />
        <Route path="workout/:workoutId" element={<Workout />} />
        <Route path="history" element={<History />} />
        <Route path="progress" element={<Progress />} />
        <Route path="exercises" element={<Exercises />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <UserProvider>
        <AppRoutes />
      </UserProvider>
    </BrowserRouter>
  );
}
