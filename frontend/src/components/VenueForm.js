import React, { useState } from 'react';
import api from '../api';
import { useAuth } from '../AuthContext';

export default function VenueForm({ onVenueAdded }) {
  const { user } = useAuth();
  const [form, setForm] = useState({ name: '', address: '', capacity: '' });
  const [error, setError] = useState('');

  if (!user || (user.role !== 'organizer' && user.role !== 'admin')) {
    return null;
  }

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/venues', { ...form, capacity: parseInt(form.capacity) });
      setForm({ name: '', address: '', capacity: '' });
      onVenueAdded();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add venue');
    }
  };

  return (
    <div className="card">
      <h2>Add Venue</h2>
      <form onSubmit={handleSubmit}>
        <input name="name" placeholder="Venue Name" value={form.name} onChange={handleChange} required />
        <input name="address" placeholder="Address" value={form.address} onChange={handleChange} required />
        <input name="capacity" type="number" placeholder="Capacity" value={form.capacity} onChange={handleChange} required />
        <button type="submit">Add Venue</button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
