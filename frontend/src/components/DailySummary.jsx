import React from 'react';
import api from '../utils/api';
import '../styles/DailySummary.css';

export default function DailySummary({ summary, onMealDeleted }) {
  const handleDeleteMeal = async (mealId) => {
    if (window.confirm('Delete this meal?')) {
      try {
        await api.delete(`/api/meals/${mealId}`);
        onMealDeleted();
      } catch (error) {
        console.error('Error deleting meal:', error);
      }
    }
  };

  const getStatusColor = (status) => {
    if (status === 'Low') return '#ffc107';
    if (status === 'On Target') return '#4caf50';
    return '#f44336';
  };

  return (
    <div className="daily-summary-container">
      <h2>📊 Daily Summary</h2>

      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-label">Target</div>
          <div className="card-value">{summary.daily_target}</div>
          <div className="card-unit">kcal</div>
        </div>

        <div className="summary-card">
          <div className="card-label">Consumed</div>
          <div className="card-value">{summary.total_calories}</div>
          <div className="card-unit">kcal</div>
        </div>

        <div className="summary-card">
          <div className="card-label">Remaining</div>
          <div className="card-value">{summary.remaining}</div>
          <div className="card-unit">kcal</div>
        </div>
      </div>

      <div className="status-badge" style={{ borderColor: getStatusColor(summary.status) }}>
        <span className="status-label">Status:</span>
        <span className="status-value" style={{ color: getStatusColor(summary.status) }}>
          {summary.status}
        </span>
      </div>

      <div className="meals-list">
        <h3>Meals Today</h3>
        {summary.meals && summary.meals.length > 0 ? (
          <div className="meals">
            {summary.meals.map(meal => (
              <div key={meal.id} className="meal-item">
                <div className="meal-info">
                  <div className="meal-name">{meal.dish_name}</div>
                  <div className="meal-details">
                    {meal.grams}g • {meal.calories} kcal
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteMeal(meal.id)}
                  className="delete-btn"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-meals">No meals logged yet</p>
        )}
      </div>
    </div>
  );
}
