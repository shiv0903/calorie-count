import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import MealForm from '../components/MealForm';
import DailySummary from '../components/DailySummary';
import '../styles/DailyLogPage.css';

export default function DailyLogPage({ profile, user, onLogout }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const today = new Date().toISOString().split('T')[0];
  const [date, setDate] = useState(today);

  useEffect(() => {
    fetchSummary();
  }, [date]);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/daily-summary?date=${date}`);
      setSummary(response.data);
    } catch (error) {
      console.error('Error fetching summary:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMealAdded = () => {
    fetchSummary();
  };

  const handleMealDeleted = () => {
    fetchSummary();
  };

  const handleDateChange = (e) => {
    const picked = e.target.value;
    // Don't allow future dates
    if (picked > today) {
      setDate(today);
    } else {
      setDate(picked);
    }
  };

  return (
    <div className="daily-log-container">
      <header className="daily-log-header">
        <div className="header-content">
          <h1>Calorie Count</h1>
          <button onClick={onLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>
      <div className="daily-log-content">
        <div className="date-selector">
          <input
            type="date"
            value={date}
            max={today}
            onChange={handleDateChange}
            className="date-input"
          />
        </div>
        <div className="log-grid">
          <div className="log-section">
            <MealForm onMealAdded={handleMealAdded} selectedDate={date} />
          </div>
          <div className="log-section">
            {loading ? (
              <div className="loader">Loading...</div>
            ) : summary ? (
              <DailySummary summary={summary} onMealDeleted={handleMealDeleted} />
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
