import React from 'react';
import { useAuth } from '../AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <h1>Event Management System</h1>
      {user ? (
        <div>
          <span>Logged in as {user.name} ({user.role})</span>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <span>Not logged in</span>
      )}
    </nav>
  );
}
