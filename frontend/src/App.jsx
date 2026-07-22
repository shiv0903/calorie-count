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
  const [diag, setDiag] = useState('');

  useEffect(() => {
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
      setDiag(`Auto-login profile check: HTTP ${response.status}`);
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
      setDiag(`Auto-login profile check ERROR: ${error.message}`);
      setPage('login');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = async (token) => {
    localStorage.setItem('token', token);
    setUser({ token });
    try {
      const response = await fetch('/api/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const bodyText = await response.text();
      setDiag(`Login profile check: HTTP ${response.status} | body: ${bodyText.substring(0, 200)}`);
      if (response.ok) {
        const data = JSON.parse(bodyText);
        setProfile(data);
        setPage('daily-log');
      } else {
        setPage('profile-setup');
      }
    } catch (error) {
      setDiag(`Login profile check ERROR: ${error.message}`);
      setPage('profile-setup');
    }
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
      {diag && (
        <div style={{ background: '#fff3cd', color: '#664d03', padding: '10px', fontSize: '13px', fontFamily: 'monospace', borderBottom: '1px solid #ddd', wordBreak: 'break-all' }}>
          DIAGNOSTIC: {diag}
        </div>
      )}
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
