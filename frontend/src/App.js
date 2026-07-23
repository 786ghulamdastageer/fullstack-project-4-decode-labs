import React, { useState, useEffect, useCallback } from 'react';
import { AuthProvider, useAuth } from './AuthContext';
import api from './api';
import Navbar from './components/Navbar';
import Register from './components/Register';
import Login from './components/Login';
import VenueForm from './components/VenueForm';
import EventForm from './components/EventForm';
import EventList from './components/EventList';

function Dashboard() {
  const { user } = useAuth();
  const [events, setEvents] = useState([]);
  const [editingEvent, setEditingEvent] = useState(null);

  const loadEvents = useCallback(() => {
    api.get('/events').then((res) => setEvents(res.data));
  }, []);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  return (
    <div className="container">
      <Navbar />

      {!user && (
        <div className="auth-row">
          <Register />
          <Login />
        </div>
      )}

      <VenueForm onVenueAdded={loadEvents} />
      <EventForm
        onEventAdded={loadEvents}
        editingEvent={editingEvent}
        clearEdit={() => setEditingEvent(null)}
      />
      <EventList events={events} onChange={loadEvents} onEdit={setEditingEvent} />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Dashboard />
    </AuthProvider>
  );
}