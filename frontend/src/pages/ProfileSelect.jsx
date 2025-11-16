import { useState, useEffect } from 'react';
import { Plus, User as UserIcon, Camera } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { getUsers, createUser, uploadProfilePicture, getProfilePictureUrl } from '../utils/api';

export default function ProfileSelect() {
  const { selectUser } = useUser();
  const [users, setUsers] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (!newName.trim()) return;

    setCreating(true);
    try {
      const user = await createUser(newName.trim());
      setUsers([...users, user]);
      setNewName('');
      setShowCreate(false);
      selectUser(user.id);
    } catch (error) {
      console.error('Failed to create user:', error);
    } finally {
      setCreating(false);
    }
  };

  const handleSelectUser = (userId) => {
    // Haptic feedback
    if (navigator.vibrate) {
      navigator.vibrate(10);
    }
    selectUser(userId);
  };

  return (
    <div className="min-h-full flex flex-col p-6 safe-top safe-bottom fade-in">
      <div className="flex-1 flex flex-col justify-center max-w-md mx-auto w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">CrossWod</h1>
          <p className="text-secondary">Select your profile to continue</p>
        </div>

        {loading ? (
          <div className="text-center text-muted">Loading profiles...</div>
        ) : (
          <div className="space-y-3">
            {users.map((user) => (
              <button
                key={user.id}
                onClick={() => handleSelectUser(user.id)}
                className="w-full glass p-4 flex items-center gap-4 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                <div
                  className="w-14 h-14 rounded-full flex items-center justify-center overflow-hidden"
                  style={{ background: 'rgba(255, 255, 255, 0.1)' }}
                >
                  {user.has_profile_picture ? (
                    <img
                      src={getProfilePictureUrl(user.id)}
                      alt={user.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <UserIcon size={28} className="text-muted" />
                  )}
                </div>
                <div className="flex-1 text-left">
                  <div className="font-semibold text-lg">{user.name}</div>
                  <div className="text-sm text-muted">
                    Last active: {new Date(user.last_active).toLocaleDateString()}
                  </div>
                </div>
              </button>
            ))}

            {!showCreate ? (
              <button
                onClick={() => setShowCreate(true)}
                className="w-full glass-subtle p-4 flex items-center justify-center gap-3 text-accent font-medium transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                <Plus size={24} />
                <span>Create New Profile</span>
              </button>
            ) : (
              <form onSubmit={handleCreateUser} className="glass p-4 slide-up">
                <div className="mb-4">
                  <label htmlFor="name">Profile Name</label>
                  <input
                    id="name"
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="Enter your name"
                    autoFocus
                    disabled={creating}
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreate(false);
                      setNewName('');
                    }}
                    className="btn btn-secondary flex-1"
                    disabled={creating}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary flex-1"
                    disabled={!newName.trim() || creating}
                  >
                    {creating ? 'Creating...' : 'Create'}
                  </button>
                </div>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
