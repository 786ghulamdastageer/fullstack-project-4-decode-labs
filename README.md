# Event Management System

A full-stack web application for managing events, venues, and participant registrations, built as part of the DecodeLabs Full Stack Development Internship i.e., Project 4: Frontend & Backend Integration (Authentication & Authorization).

##  Scenario

The Event Management System (EMS) is designed to streamline the organization and management of events. It serves as a central platform for event organizers, participants, and venue providers to interact, transact, and coordinate all aspects related to events.

Organizers can register, create venues, and publish events. Participants can register for an account and sign up for events they are interested in attending. Access to sensitive operations — such as creating, editing, or deleting events — is restricted through secure authentication and role-based authorization, ensuring only the right users can perform the right actions.

## Tools & Technologies

**Backend**
- **Python** — core backend language
- **Flask** — REST API framework
- **Flask-CORS** — enables secure cross-origin requests from the React frontend
- **SQLite3** — relational database (built into Python, no separate installation required)
- **PyJWT** — JSON Web Token generation and verification
- **Werkzeug Security** — password hashing (salted, one-way hash)
- **Waitress** — production-ready WSGI server

**Frontend**
- **React** — component-based UI library (functional components + Hooks)
- **React Context API** — global authentication state management
- **Axios** — HTTP client for REST API integration, with a request interceptor that automatically attaches the JWT token

##  Architecture

- **Backend**: Flask REST API (SQLite, JWT authentication, RBAC middleware)
- **Frontend**: React (functional components, hooks, Context API for auth state, Axios for API calls)
- Frontend and backend run as **two separate servers** and communicate over HTTP (CORS enabled), reflecting a real-world decoupled client-server architecture.

## Database Design

| Table | Description |
|---|---|
| `user` | Stores registered users with hashed passwords and a role (`admin`, `organizer`, `participant`) |
| `venue` | Stores venue details (name, address, capacity) |
| `event` | Stores event details, linked to an organizer and a venue |
| `registration` | Junction table linking participants to the events they register for (Many-to-Many) |

**Relationships**
- One-to-Many: Organizer (`user`) → Events
- One-to-Many: Venue → Events
- Many-to-Many: Participants ↔ Events (via `registration`)

**Constraints enforced at the schema level**
- `UNIQUE` — prevents duplicate user emails
- `NOT NULL` — required fields cannot be empty
- `CHECK` — restricts `role` to valid values and `capacity` to positive numbers
- `PRIMARY KEY` / `FOREIGN KEY` — maintains referential integrity across all related tables

## Authentication & Authorization

- **Registration & Login** — users sign up with a name, unique email, password, and role
- **Password Hashing** — passwords are never stored in plain text; hashed and salted using Werkzeug Security before being saved
- **Token-Based Authentication** — on successful login/registration, a signed JWT (containing user ID, role, and expiry) is issued
- **Protected Routes** — a `@token_required` middleware decorator verifies the JWT on every protected request; missing or invalid tokens are rejected with `401 Unauthorized`
- **Role-Based Access Control (RBAC)** — a `@role_required(...)` decorator restricts specific actions to specific roles (e.g. only `organizer`/`admin` can create events and venues; only `participant` can register for events); unauthorized roles are rejected with `403 Forbidden`
- **Ownership Checks** — event updates and deletions are restricted to the event's original organizer or an admin
- Password hashes are **never** included in any API response

## API Endpoints

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/register` | Public | Register a new user |
| POST | `/api/login` | Public | Authenticate and receive a JWT |
| GET | `/api/me` | Authenticated | Get current logged-in user info |
| GET | `/api/venues` | Public | List all venues |
| POST | `/api/venues` | organizer, admin | Create a new venue |
| GET | `/api/events` | Public | List all events |
| POST | `/api/events` | organizer, admin | Create a new event |
| PUT | `/api/events/:id` | owner or admin | Update an event |
| DELETE | `/api/events/:id` | owner or admin | Delete an event |
| POST | `/api/events/:id/register` | participant | Register for an event |
| GET | `/api/events/:id/participants` | organizer, admin | View participants of an event |

##  How It Works, Frontend & Backend Integration

1. The Flask backend initializes the SQLite database on startup and exposes a set of RESTful JSON endpoints.
2. The React frontend runs independently on its own development server and communicates with the backend exclusively through HTTP requests via `axios` (see `src/api.js`).
3. An Axios **request interceptor** automatically attaches the JWT token (stored in `localStorage`) to the `Authorization` header of every outgoing request, so protected endpoints can be called without manually re-adding the token each time.
4. `AuthContext.js` uses React's Context API to manage login state globally, making the current user's identity and role available throughout the component tree without prop-drilling.
5. The UI conditionally renders elements based on role: the "Add Venue" and "Create Event" forms only appear for `organizer`/`admin` accounts, and the "Register" button on events only appears for `participant` accounts — mirroring the backend's `@role_required` checks.
6. When a form is submitted, React sends the corresponding `POST`/`PUT`/`DELETE` request to the Flask API. The backend validates the request, checks the JWT and role, executes the parameterized SQL query, and returns a JSON response.
7. On success, the frontend refreshes its state and re-renders the updated data; on failure (e.g. `401`/`403`/`400`), the error message returned by the backend is displayed to the user.
8. This request/response cycle — from UI event, to API call, to database operation, to UI update — demonstrates the complete frontend-to-backend integration required for this project.

##  Testing the API (Thunder Client / Postman)

All endpoints can be tested directly against the backend, independent of the React frontend, using any REST client such as Thunder Client in VS Code:

1. **Register** a user via `POST /api/register` and copy the returned `token`.
2. For any protected endpoint, add a header:
   Authorization: Bearer <token>
3. Test the full CRUD flow: create a venue → create an event (`venue_id` from step above) → register a participant for the event → update the event → view participants → delete the event.

This confirms the backend operates correctly as a standalone REST API, independent of any frontend client — the same principle React itself relies on for integration.

##  How to Run

### 1. Clone the repository

git clone https://github.com/786ghulamdastageer/fullstack-project-4-decode-labs.git
cd fullstack-project-4-decode-labs

### 2. Run the Backend

cd backend
pip install -r requirements.txt
python app.py

Runs on `http://127.0.0.1:5000`

### 3. Run the Frontend
Open a new terminal:
cd frontend
npm install
npm start

Runs on `http://localhost:3000` and opens automatically in your browser.

> Both servers must be running simultaneously i.e., the React frontend depends on the Flask backend for all data operations.

##  Project Structure

```
fullstack-project-4-decode-labs/
├── backend/
│   ├── app.py            # Flask REST API routes
│   ├── auth.py            # Password hashing, JWT, auth/role decorators
│   ├── database.py        # Database connection and schema setup
│   ├── requirements.txt
│   └── ems.db              # SQLite database file (auto-generated)
└── frontend/
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── index.js
        ├── App.js
        ├── App.css
        ├── api.js          # Axios instance with JWT interceptor
        ├── AuthContext.js  # Global auth state (React Context API)
        └── components/
            ├── Navbar.js
            ├── Register.js
            ├── Login.js
            ├── VenueForm.js
            ├── EventForm.js
            └── EventList.js
```

## Project Highlights

- Full authentication flow: registration, login, hashed & salted passwords, JWT issuance
- Middleware-based route protection (`@token_required`) and role-based access control (`@role_required`)
- Ownership-based authorization for event editing/deletion
- Complete CRUD functionality for Events, Venues, and Registrations
- One-to-Many and Many-to-Many relationships enforced via Primary/Foreign Keys
- Schema-level data integrity constraints (UNIQUE, NOT NULL, CHECK)
- SQL Injection protection via parameterized queries
- Decoupled React frontend consuming a RESTful Flask API over HTTP
- Role-aware UI that dynamically adapts to the logged-in user's permissions

