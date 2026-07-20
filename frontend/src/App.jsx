import React, { useState, useEffect } from 'react';
import './App.css';
import LoginPage from './pages/LoginPage';
import ProfileSetupPage from './pages/ProfileSetupPage';
import DailyLogPage from './pages/DailyLogPage';

export default function App() {
  const [page, setPage] = useState('login');
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      fetchProfile(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchProfile = async (token) => {
    try {
      const response = await fetch('/api/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUser({ token });
        setProfile(data);
        setPage('daily-log');
      } else {
        localStorage.removeItem('token');
        setPage('login');
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      setPage('login');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = (token) => {
    localStorage.setItem('token', token);
    setUser({ token });
    setPage('profile-setup');
  };

  const handleProfileSetup = (profileData) => {
    setProfile(profileData);
    setPage('daily-log');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setProfile(null);
    setPage('login');
  };

  if (loading) {
    return (
      <div className="container loading-container">
        <div className="loader"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="app">
      {page === 'login' && (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      )}
      
      {page === 'profile-setup' && (
        <ProfileSetupPage onProfileSetup={handleProfileSetup} />
      )}
      
      {page === 'daily-log' && profile && (
        <DailyLogPage 
          profile={profile} 
          user={user}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
}
