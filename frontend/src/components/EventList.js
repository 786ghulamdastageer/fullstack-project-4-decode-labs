import React from 'react';
import api from '../api';
import { useAuth } from '../AuthContext';

export default function EventList({ events, onChange, onEdit }) {
  const { user } = useAuth();

  const handleRegister = async (eventId) => {
    if (!user) {
      alert('Please login first');
      return;
    }
    try {
      const res = await api.post(`/events/${eventId}/register`);
      alert(res.data.message);
    } catch (err) {
      alert(err.response?.data?.error || 'Registration failed');
    }
  };

  const handleDelete = async (eventId) => {
    if (!user) {
      alert('Please login first');
      return;
    }
    if (!window.confirm('Delete this event?')) return;
    try {
      await api.delete(`/events/${eventId}`);
      onChange();
    } catch (err) {
      alert(err.response?.data?.error || 'Delete failed');
    }
  };

  return (
    <div className="card">
      <h2>Events</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th><th>Title</th><th>Date</th><th>Organizer</th><th>Venue</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {events.map((ev) => (
            <tr key={ev.event_id}>
              <td>{ev.event_id}</td>
              <td>{ev.title}</td>
              <td>{ev.event_date}</td>
              <td>{ev.organizer_name || '-'}</td>
              <td>{ev.venue_name || '-'}</td>
              <td>
                {user?.role === 'participant' && (
                  <button className="register-btn" onClick={() => handleRegister(ev.event_id)}>Register</button>
                )}
                {user && (user.role === 'admin' || Number(user.userId) === ev.organizer_id) && (
                  <>
                    <button className="edit-btn" onClick={() => onEdit(ev)}>Edit</button>
                    <button className="delete-btn" onClick={() => handleDelete(ev.event_id)}>Delete</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}