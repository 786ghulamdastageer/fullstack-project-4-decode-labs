from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_connection, init_db
from auth import hash_password, verify_password, generate_token, token_required, role_required

app = Flask(__name__)
CORS(app)
init_db()

# ---------- AUTH ----------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'participant')

    if role not in ('organizer', 'participant'):
        role = 'participant'

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400

    conn = get_connection()
    try:
        password_hash = hash_password(password)
        cur = conn.execute(
            "INSERT INTO user (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, role)
        )
        conn.commit()
        user_id = cur.lastrowid
        token = generate_token(user_id, role)
        return jsonify({"token": token, "user_id": user_id, "name": name, "role": role}), 201
    except Exception:
        return jsonify({"error": "Email already registered"}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_connection()
    user = conn.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not user or not verify_password(password, user['password_hash']):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(user['user_id'], user['role'])
    return jsonify({
        "token": token,
        "user_id": user['user_id'],
        "name": user['name'],
        "role": user['role']
    }), 200

@app.route('/api/me', methods=['GET'])
@token_required
def get_me():
    return jsonify(request.current_user), 200

# ---------- VENUES ----------
@app.route('/api/venues', methods=['POST'])
@token_required
@role_required('admin', 'organizer')
def create_venue():
    data = request.get_json()
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO venue (name, address, capacity) VALUES (?, ?, ?)",
            (data.get('name'), data.get('address'), data.get('capacity'))
        )
        conn.commit()
        return jsonify({"venue_id": cur.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/api/venues', methods=['GET'])
def get_venues():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM venue").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

# ---------- EVENTS (CRUD) ----------
@app.route('/api/events', methods=['POST'])
@token_required
@role_required('admin', 'organizer')
def create_event():
    data = request.get_json()
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO event (title, description, event_date, organizer_id, venue_id) VALUES (?, ?, ?, ?, ?)",
            (data.get('title'), data.get('description'), data.get('event_date'),
             request.current_user['user_id'], data.get('venue_id'))
        )
        conn.commit()
        return jsonify({"event_id": cur.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_connection()
    rows = conn.execute("""
        SELECT e.*, u.name AS organizer_name, v.name AS venue_name
        FROM event e
        LEFT JOIN user u ON e.organizer_id = u.user_id
        LEFT JOIN venue v ON e.venue_id = v.venue_id
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

@app.route('/api/events/<int:event_id>', methods=['PUT'])
@token_required
def update_event(event_id):
    conn = get_connection()
    event = conn.execute("SELECT * FROM event WHERE event_id = ?", (event_id,)).fetchone()

    if not event:
        conn.close()
        return jsonify({"error": "Event not found"}), 404

    if request.current_user['role'] != 'admin' and event['organizer_id'] != request.current_user['user_id']:
        conn.close()
        return jsonify({"error": "Forbidden: not your event"}), 403

    data = request.get_json()
    try:
        conn.execute(
            "UPDATE event SET title=?, description=?, event_date=?, venue_id=? WHERE event_id=?",
            (data.get('title'), data.get('description'), data.get('event_date'),
             data.get('venue_id'), event_id)
        )
        conn.commit()
        return jsonify({"message": "Event updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@token_required
def delete_event(event_id):
    conn = get_connection()
    event = conn.execute("SELECT * FROM event WHERE event_id = ?", (event_id,)).fetchone()

    if not event:
        conn.close()
        return jsonify({"error": "Event not found"}), 404

    if request.current_user['role'] != 'admin' and event['organizer_id'] != request.current_user['user_id']:
        conn.close()
        return jsonify({"error": "Forbidden: not your event"}), 403

    conn.execute("DELETE FROM registration WHERE event_id = ?", (event_id,))
    conn.execute("DELETE FROM event WHERE event_id = ?", (event_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Event deleted"}), 200

# ---------- REGISTRATIONS ----------
@app.route('/api/events/<int:event_id>/register', methods=['POST'])
@token_required
@role_required('participant')
def register_for_event(event_id):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO registration (event_id, participant_id) VALUES (?, ?)",
            (event_id, request.current_user['user_id'])
        )
        conn.commit()
        return jsonify({"message": "Registered successfully"}), 201
    except Exception:
        return jsonify({"error": "Already registered or invalid event"}), 400
    finally:
        conn.close()

@app.route('/api/events/<int:event_id>/participants', methods=['GET'])
@token_required
@role_required('admin', 'organizer')
def get_participants(event_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.user_id, u.name, u.email
        FROM registration r
        JOIN user u ON r.participant_id = u.user_id
        WHERE r.event_id = ?
    """, (event_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    from waitress import serve
    serve(app, host='127.0.0.1', port=5000)
