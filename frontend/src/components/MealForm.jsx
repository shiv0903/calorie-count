import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import '../styles/MealForm.css';

export default function MealForm({ onMealAdded }) {
  const [dishes, setDishes] = useState([]);
  const [selectedDish, setSelectedDish] = useState('');
  const [grams, setGrams] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Custom dish state
  const [showCustom, setShowCustom] = useState(false);
  const [customName, setCustomName] = useState('');
  const [customCalories, setCustomCalories] = useState('');
  const [savingCustom, setSavingCustom] = useState(false);

  useEffect(() => {
    fetchDishes();
  }, []);

  const fetchDishes = async () => {
    try {
      const response = await api.get('/api/dishes');
      setDishes(response.data);
    } catch (error) {
      console.error('Error fetching dishes:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/api/meals', {
        dish_id: parseInt(selectedDish),
        grams_confirmed: parseFloat(grams),
      });
      setSelectedDish('');
      setGrams('');
      onMealAdded();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add meal');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCustomDish = async () => {
    setError('');
    if (!customName.trim() || !customCalories) {
      setError('Enter a name and calories per 100g for the custom dish');
      return;
    }
    setSavingCustom(true);
    try {
      const response = await api.post(
        `/api/dishes?name=${encodeURIComponent(customName.trim())}&calories_per_100g=${parseFloat(customCalories)}`
      );
      const newDish = response.data;
      // Refresh the dropdown so the new dish appears
      await fetchDishes();
      // Auto-select the dish we just created
      setSelectedDish(String(newDish.id));
      // Reset and hide the custom form
      setCustomName('');
      setCustomCalories('');
      setShowCustom(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add custom dish');
    } finally {
      setSavingCustom(false);
    }
  };

  const selectedDishData = dishes.find(d => d.id === parseInt(selectedDish));
  const estimatedCalories = selectedDishData
    ? Math.round((selectedDishData.calories_per_100g / 100) * parseFloat(grams || 0))
    : 0;

  return (
    <div className="meal-form-container">
      <h2>Add Meal</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="dish">Dish</label>
          <select
            id="dish"
            value={selectedDish}
            onChange={(e) => setSelectedDish(e.target.value)}
            required
          >
            <option value="">Select a dish...</option>
            {dishes.map(dish => (
              <option key={dish.id} value={dish.id}>
                {dish.name} ({dish.calories_per_100g} cal/100g)
              </option>
            ))}
          </select>
        </div>

        {!showCustom && (
          <button
            type="button"
            className="link-btn"
            onClick={() => { setShowCustom(true); setError(''); }}
          >
            + Dish not listed? Add it
          </button>
        )}

        {showCustom && (
          <div className="custom-dish-box">
            <div className="form-group">
              <label htmlFor="customName">New dish name</label>
              <input
                type="text"
                id="customName"
                value={customName}
                onChange={(e) => setCustomName(e.target.value)}
                placeholder="e.g. Grilled Salmon"
              />
            </div>
            <div className="form-group">
              <label htmlFor="customCalories">Calories per 100g</label>
              <input
                type="number"
                id="customCalories"
                value={customCalories}
                onChange={(e) => setCustomCalories(e.target.value)}
                placeholder="e.g. 180"
                step="0.1"
              />
            </div>
            <div className="custom-dish-actions">
              <button
                type="button"
                className="submit-btn"
                onClick={handleAddCustomDish}
                disabled={savingCustom}
              >
                {savingCustom ? 'Saving...' : 'Save dish'}
              </button>
              <button
                type="button"
                className="cancel-btn"
                onClick={() => { setShowCustom(false); setError(''); }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="form-group">
          <label htmlFor="grams">Grams Confirmed</label>
          <input
            type="number"
            id="grams"
            value={grams}
            onChange={(e) => setGrams(e.target.value)}
            placeholder="100"
            step="0.1"
            required
          />
        </div>

        {estimatedCalories > 0 && (
          <div className="calorie-preview">
            Estimated: <strong>{estimatedCalories} cal</strong>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Adding...' : 'Add Meal'}
        </button>
      </form>
    </div>
  );
}
