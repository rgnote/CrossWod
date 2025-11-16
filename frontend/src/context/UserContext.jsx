import { createContext, useContext, useState, useEffect } from 'react';
import { getUser } from '../utils/api';

const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load saved user from localStorage
    const savedUserId = localStorage.getItem('crosswod_user_id');
    if (savedUserId) {
      loadUser(parseInt(savedUserId));
    } else {
      setLoading(false);
    }
  }, []);

  const loadUser = async (userId) => {
    try {
      const user = await getUser(userId);
      setCurrentUser(user);
      localStorage.setItem('crosswod_user_id', userId.toString());
    } catch (error) {
      console.error('Failed to load user:', error);
      localStorage.removeItem('crosswod_user_id');
    } finally {
      setLoading(false);
    }
  };

  const selectUser = async (userId) => {
    setLoading(true);
    await loadUser(userId);
  };

  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('crosswod_user_id');
  };

  const updateCurrentUser = (userData) => {
    setCurrentUser(prev => ({ ...prev, ...userData }));
  };

  return (
    <UserContext.Provider value={{
      currentUser,
      loading,
      selectUser,
      logout,
      updateCurrentUser
    }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}
