import React, { useState, useEffect } from 'react';
import api from '../api';
import { useAuth } from '../AuthContext';

export default function EventForm({ onEventAdded, editingEvent, clearEdit }) {
  const { user } = useAuth();
  const [form, setForm] = useState({ title: '', description: '', event_date: '', venue_id: '' });
  const [venues, setVenues] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/venues').then((res) => setVenues(res.data));
  }, []);

  useEffect(() => {
    if (editingEvent) {
      setForm({
        title: editingEvent.title,
        description: editingEvent.description || '',
        event_date: editingEvent.event_date,
        venue_id: editingEvent.venue_id || ''
      });
    }
  }, [editingEvent]);

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
      const payload = { ...form, venue_id: form.venue_id || null };

      if (editingEvent) {
        await api.put(`/events/${editingEvent.event_id}`, payload);
        clearEdit();
      } else {
        await api.post('/events', payload);
      }

      setForm({ title: '', description: '', event_date: '', venue_id: '' });
      onEventAdded();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save event');
    }
  };

  const handleCancel = () => {
    setForm({ title: '', description: '', event_date: '', venue_id: '' });
    clearEdit();
  };

  return (
    <div className="card">
      <h2>{editingEvent ? 'Edit Event' : 'Create Event'}</h2>
      <form onSubmit={handleSubmit}>
        <input name="title" placeholder="Event Title" value={form.title} onChange={handleChange} required />
        <input name="description" placeholder="Description" value={form.description} onChange={handleChange} />
        <input name="event_date" type="date" value={form.event_date} onChange={handleChange} required />
        <select name="venue_id" value={form.venue_id} onChange={handleChange}>
          <option value="">Select Venue</option>
          {venues.map((v) => (
            <option key={v.venue_id} value={v.venue_id}>{v.name}</option>
          ))}
        </select>
        <button type="submit">{editingEvent ? 'Update Event' : 'Create Event'}</button>
        {editingEvent && <button type="button" onClick={handleCancel}>Cancel</button>}
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  );
}