import { useState, useRef } from 'react';
import { Camera, LogOut, User as UserIcon, Scale, Plus } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { uploadProfilePicture, getProfilePictureUrl, createBodyMetric } from '../utils/api';

export default function Settings() {
  const { currentUser, logout, updateCurrentUser } = useUser();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [showAddWeight, setShowAddWeight] = useState(false);
  const [newWeight, setNewWeight] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleProfilePictureChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await uploadProfilePicture(currentUser.id, file);
      updateCurrentUser({ has_profile_picture: true });
      if (navigator.vibrate) navigator.vibrate(10);
    } catch (error) {
      console.error('Failed to upload profile picture:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleAddWeight = async (e) => {
    e.preventDefault();
    if (!newWeight) return;

    try {
      await createBodyMetric(currentUser.id, {
        date: new Date().toISOString().split('T')[0],
        weight: parseFloat(newWeight)
      });
      setShowAddWeight(false);
      setNewWeight('');
      if (navigator.vibrate) navigator.vibrate(10);
    } catch (error) {
      console.error('Failed to add body weight:', error);
    }
  };

  const handleLogout = () => {
    if (navigator.vibrate) navigator.vibrate(10);
    logout();
  };

  return (
    <div className="p-5 overflow-y-auto h-full">
      <div className="max-w-lg mx-auto">
        <h2 className="text-2xl font-bold mb-5">Profile</h2>

        {/* Profile Card */}
        <div className="glass p-6 mb-5 text-center slide-up">
          <div className="relative inline-block mb-4">
            <div
              className="w-24 h-24 rounded-full flex items-center justify-center overflow-hidden mx-auto"
              style={{ background: 'rgba(255, 255, 255, 0.1)' }}
            >
              {currentUser?.has_profile_picture ? (
                <img
                  src={`${getProfilePictureUrl(currentUser.id)}?t=${Date.now()}`}
                  alt={currentUser.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <UserIcon size={40} className="text-muted" />
              )}
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-accent flex items-center justify-center"
              disabled={uploading}
            >
              <Camera size={16} />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleProfilePictureChange}
              className="hidden"
            />
          </div>

          <h3 className="text-xl font-semibold">{currentUser?.name}</h3>
          <p className="text-sm text-muted">
            Member since {new Date(currentUser?.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Quick Actions */}
        <div className="space-y-3 mb-5">
          <button
            onClick={() => setShowAddWeight(true)}
            className="w-full glass-subtle p-4 flex items-center gap-3 transition-all hover:scale-[1.01] active:scale-[0.99]"
          >
            <div className="w-10 h-10 rounded-full bg-success/20 flex items-center justify-center">
              <Scale size={20} className="text-success" />
            </div>
            <div className="text-left">
              <div className="font-medium">Log Body Weight</div>
              <div className="text-xs text-muted">Track your weight progress</div>
            </div>
          </button>
        </div>

        {/* App Info */}
        <div className="glass-subtle p-4 mb-5">
          <h4 className="font-semibold mb-3">About CrossWod</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted">Version</span>
              <span>1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted">Data Storage</span>
              <span>Local SQLite</span>
            </div>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={() => setShowLogoutConfirm(true)}
          className="w-full btn btn-secondary text-danger"
        >
          <LogOut size={18} />
          Switch Profile
        </button>

        {/* Logout Confirmation */}
        {showLogoutConfirm && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            style={{ background: 'rgba(0, 0, 0, 0.6)' }}
          >
            <div className="glass p-5 max-w-sm w-full slide-up">
              <h3 className="font-semibold text-lg mb-2">Switch Profile?</h3>
              <p className="text-sm text-secondary mb-4">
                You'll be taken back to the profile selection screen.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowLogoutConfirm(false)}
                  className="btn btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button onClick={handleLogout} className="btn btn-primary flex-1">
                  Switch
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Add Weight Modal */}
        {showAddWeight && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            style={{ background: 'rgba(0, 0, 0, 0.6)' }}
          >
            <div className="glass p-5 max-w-sm w-full slide-up">
              <h3 className="font-semibold text-lg mb-4">Log Body Weight</h3>
              <form onSubmit={handleAddWeight}>
                <div className="mb-4">
                  <label>Weight (kg)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={newWeight}
                    onChange={(e) => setNewWeight(e.target.value)}
                    placeholder="e.g., 75.5"
                    autoFocus
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setShowAddWeight(false)}
                    className="btn btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary flex-1"
                    disabled={!newWeight}
                  >
                    Save
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
