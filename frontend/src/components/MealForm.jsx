import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import '../styles/MealForm.css';

export default function MealForm({ onMealAdded }) {
  const [dishes, setDishes] = useState([]);
  const [selectedDish, setSelectedDish] = useState('');
  const [grams, setGrams] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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

  const selectedDishData = dishes.find(d => d.id === parseInt(selectedDish));
  const estimatedCalories = selectedDishData
    ? Math.round((selectedDishData.calories_per_100g / 100) * parseFloat(grams || 0))
    : 0;

  return (
    <div className="meal-form-container">
      <h2>➕ Add Meal</h2>
      
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
