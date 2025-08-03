import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNotificationStore } from '../../stores/notificationStore';
import { UserIcon, EnvelopeIcon, CalendarIcon } from '@heroicons/react/24/outline';

interface ProfileSettingsProps {
  className?: string;
}

const ProfileSettings: React.FC<ProfileSettingsProps> = ({ className = '' }) => {
  const { user } = useAuth();
  const addNotification = useNotificationStore((state) => state.addNotification);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
  });

  const handleSave = async () => {
    try {
      // TODO: Implement profile update API call
      addNotification({
        type: 'success',
        title: 'Profile Updated',
        message: 'Your profile information has been updated successfully.',
      });
      setIsEditing(false);
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: 'Failed to update profile information. Please try again.',
      });
    }
  };

  const handleCancel = () => {
    setFormData({
      name: user?.name || '',
      email: user?.email || '',
    });
    setIsEditing(false);
  };

  if (!user) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
        <p className="text-gray-500 dark:text-gray-400">No user information available.</p>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Profile Information
        </h3>
        {!isEditing ? (
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Edit Profile
          </button>
        ) : (
          <div className="flex space-x-2">
            <button
              onClick={handleSave}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-500 dark:hover:text-gray-400"
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      <div className="space-y-6">
        {/* Profile Picture Placeholder */}
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
            <UserIcon className="w-8 h-8 text-gray-400 dark:text-gray-500" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
              Profile Picture
            </h4>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Profile pictures are managed through your Reddit account
            </p>
          </div>
        </div>

        {/* Name Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            <UserIcon className="w-4 h-4 inline mr-2" />
            Display Name
          </label>
          {isEditing ? (
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="Enter your display name"
            />
          ) : (
            <p className="text-gray-900 dark:text-white">{user.name}</p>
          )}
        </div>

        {/* Email Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            <EnvelopeIcon className="w-4 h-4 inline mr-2" />
            Email Address
          </label>
          {isEditing ? (
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="Enter your email address"
            />
          ) : (
            <p className="text-gray-900 dark:text-white">{user.email}</p>
          )}
        </div>

        {/* OAuth Provider */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            OAuth Provider
          </label>
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              {user.oauth_provider.toUpperCase()}
            </span>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Connected
            </span>
          </div>
        </div>

        {/* Account Created */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            <CalendarIcon className="w-4 h-4 inline mr-2" />
            Account Created
          </label>
          <p className="text-gray-900 dark:text-white">
            {new Date(user.created_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProfileSettings;