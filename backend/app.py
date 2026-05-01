from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import redis, json, os
import requests
try:
    import firebase_admin
    from firebase_admin import messaging, credentials
    FIREBASE_AVAILABLE = True
except Exception:
    FIREBASE_AVAILABLE = False
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL)
CHANNEL = "telemetry_updates"

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_status(level: int) -> str:
    # Consider a bin FULL only when above 90% to match user's requirement
    if level <= 30:
        return "EMPTY"
    elif level <= 90:
        return "HALF"
    return "FULL"


def haversine_km(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def init_db():
    con = db_conn()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bins(
        bin_id TEXT PRIMARY KEY,
        level INTEGER,
        lat REAL,
        lon REAL,
        status TEXT,
        last_updated TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trucks(
        truck_id TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT,
        lat REAL,
        lon REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT,
        email TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS driver_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        truck_id TEXT,
        name TEXT,
        phone TEXT,
        device_token TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        name TEXT,
        phone TEXT,
        email TEXT,
        device_token TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications(
        notif_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bin_id TEXT,
        truck_id TEXT,
        message TEXT,
        status TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS waste_collections(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bin_id TEXT,
        truck_id TEXT,
        level_at_collection INTEGER,
        collected_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact TEXT,
        type TEXT,
        message TEXT,
        created_at TEXT
    )
    """)


        # BIN HISTORY TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bin_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bin_id TEXT,
        level INTEGER,
        timestamp TEXT
    )
    """)
    

    
    # COLLECTION HISTORY
    #cur.execute("""
    #CREATE TABLE IF NOT EXISTS collection_history(
       ### id INTEGER PRIMARY KEY AUTOINCREMENT,
       # bin_id TEXT,
      #  truck_id TEXT,
       # timestamp TEXT
    #)
    #""")
    # create default admin if none exists (for testing)
    cur.execute("SELECT COUNT(*) as c FROM admin")
    row = cur.fetchone()
    if row and row[0] == 0:
        # create default admin with hashed password for demo
        cur.execute("INSERT INTO admin(username, password) VALUES(?, ?)", ("admin", generate_password_hash("admin")))

    # ensure existing admin passwords are hashed (migration step)
    cur.execute("SELECT username, password FROM admin")
    all_admins = cur.fetchall()
    for a in all_admins:
        uname = a['username']
        pwd = a['password']
        if pwd and not (pwd.startswith('pbkdf2:') or pwd.startswith('argon2:')):
            hashed = generate_password_hash(pwd)
            cur.execute("UPDATE admin SET password=? WHERE username=?", (hashed, uname))

    # For demo convenience ensure the 'admin' user has known password 'admin' (hashed).
    try:
        cur.execute("UPDATE admin SET password=? WHERE username=?", (generate_password_hash('admin'), 'admin'))
    except Exception:
        pass
    # create sample trucks for demo if none exist
    cur.execute("SELECT COUNT(*) as c FROM trucks")
    trow = cur.fetchone()
    if trow and trow[0] == 0:
        sample_trucks = [
            ("TRUCK_1", "Ravi", "9876543210", 10.8520, 76.2720),
            ("TRUCK_2", "Suresh", "9876501234", 10.8605, 76.2790),
            ("TRUCK_3", "Asha", "9876512345", 10.8450, 76.2650)
        ]
        cur.executemany("INSERT INTO trucks(truck_id, name, phone, lat, lon) VALUES(?,?,?,?,?)", sample_trucks)

    con.commit()
    con.close()

init_db()


def send_fcm_message(topic=None, token=None, title=None, body=None, data_payload=None):
    """Send an FCM message to a topic or token. Uses firebase-admin if available, otherwise
    falls back to legacy HTTP API using env var `FCM_SERVER_KEY` if set.
    """
    # Build notification payload
    msg_payload = {
        'notification': {
            'title': title or 'Notification',
            'body': body or ''
        }
    }
    if data_payload:
        msg_payload['data'] = {k: str(v) for k, v in (data_payload.items() if isinstance(data_payload, dict) else [])}

    # firebase-admin path
    if FIREBASE_AVAILABLE:
        try:
            if not firebase_admin._apps:
                # initialize app with default credentials if available
                try:
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred)
                except Exception:
                    try:
                        firebase_admin.initialize_app()
                    except Exception:
                        pass
            if topic:
                message = messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    topic=topic,
                    data=data_payload or None
                )
                return messaging.send(message)
            elif token:
                message = messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    token=token,
                    data=data_payload or None
                )
                return messaging.send(message)
        except Exception:
            # fallthrough to HTTP legacy if available
            pass

    # Legacy HTTP fallback
    server_key = os.environ.get('FCM_SERVER_KEY')
    if server_key:
        headers = {
            'Authorization': 'key=' + server_key,
            'Content-Type': 'application/json'
        }
        payload = {}
        if token:
            payload['to'] = token
        elif topic:
            payload['to'] = '/topics/' + topic
        payload['notification'] = {'title': title or '', 'body': body or ''}
        if data_payload:
            payload['data'] = {k: str(v) for k, v in data_payload.items()}
        try:
            resp = requests.post('https://fcm.googleapis.com/fcm/send', headers=headers, json=payload, timeout=5)
            return resp.text
        except Exception:
            return None
    # if nothing possible, just return None
    return None


@app.route("/api/bin/update", methods=["POST"])
@app.route("/update", methods=["POST"])  # backward compatible
def update_bin():
    data = request.get_json() or {}
    bin_id = data.get("bin_id")
    try:
        level = int(data.get("level", 0))
    except Exception:
        level = 0
    try:
        lat = float(data.get("latitude", data.get("lat", 0)))
        lon = float(data.get("longitude", data.get("lon", 0)))
    except Exception:
        lat = 0.0
        lon = 0.0

    status = get_status(level)

    con = db_conn()
    cur = con.cursor()

    # upsert bin
    cur.execute("""
    INSERT OR REPLACE INTO bins(bin_id, level, lat, lon, status, last_updated)
    VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (bin_id, level, lat, lon, status))

    # create notification when bin becomes FULL and there is no active notification
    if status == "FULL":
        cur.execute("SELECT notif_id FROM notifications WHERE bin_id=? AND status IN ('SENT','ACK')", (bin_id,))
        existing = cur.fetchone()
        if not existing:
            # find nearest truck
            trucks = cur.execute("SELECT truck_id, lat, lon FROM trucks").fetchall()
            nearest = None
            nearest_dist = None
            for t in trucks:
                dist = haversine_km(lat, lon, t['lat'], t['lon'])
                if nearest is None or dist < nearest_dist:
                    nearest = t['truck_id']
                    nearest_dist = dist

            message = f"Bin {bin_id} is FULL ({level}%). Please collect."
            cur.execute("INSERT INTO notifications(bin_id, truck_id, message, status, created_at, updated_at) VALUES(?,?,?,?,datetime('now'),datetime('now'))",
                        (bin_id, nearest, message, 'SENT'))

    con.commit()
    con.close()
    return jsonify({"message": "Updated", "status": status})


@app.route("/api/bins", methods=["GET"])
@app.route("/bins", methods=["GET"])  # backward compatible
def get_bins():
    con = db_conn()
    cur = con.cursor()
    rows = cur.execute("SELECT bin_id, level, lat, lon, status, last_updated FROM bins").fetchall()
    con.close()
    bins = [dict(row) for row in rows]
    return jsonify(bins)


@app.route("/api/collect/<bin_id>", methods=["POST", "GET"])
@app.route("/collect/<bin_id>", methods=["POST", "GET"])  # backward compatible
def collect(bin_id):
    con = db_conn()
    cur = con.cursor()
    cur.execute("UPDATE bins SET level=0, status='COLLECTED', last_updated=datetime('now') WHERE bin_id=?", (bin_id,))
    con.commit()
    con.close()
    return jsonify({"message": "Waste Collected", "bin_id": bin_id})


@app.route("/api/trucks", methods=["GET", "POST"])
def trucks():
    con = db_conn()
    cur = con.cursor()
    if request.method == 'POST':
        data = request.get_json() or {}
        cur.execute("INSERT OR REPLACE INTO trucks(truck_id, name, phone, lat, lon) VALUES(?,?,?,?,?)",
                    (data.get('truck_id'), data.get('name'), data.get('phone'), data.get('lat', 0), data.get('lon', 0)))
        con.commit()
    rows = cur.execute("SELECT truck_id, name, phone, lat, lon FROM trucks").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/history", methods=["GET"])
def get_history():
    # returns waste collection history; params: bin_id (optional), months (optional, default 3)
    bin_id = request.args.get('bin_id')
    months = int(request.args.get('months', 3))
    con = db_conn()
    cur = con.cursor()
    if bin_id:
        rows = cur.execute("SELECT id, bin_id, truck_id, level_at_collection, collected_at FROM waste_collections WHERE bin_id=? AND collected_at>=datetime('now', ? ) ORDER BY collected_at DESC", (bin_id, f'-{months} months')).fetchall()
    else:
        rows = cur.execute("SELECT id, bin_id, truck_id, level_at_collection, collected_at FROM waste_collections WHERE collected_at>=datetime('now', ? ) ORDER BY collected_at DESC", (f'-{months} months',)).fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/complaints', methods=['POST','GET'])
def complaints():
    con = db_conn()
    cur = con.cursor()
    if request.method == 'POST':
        data = request.get_json() or {}
        contact = data.get('contact')
        ctype = data.get('type')
        message = data.get('message')
        cur.execute("INSERT INTO complaints(contact, type, message, created_at) VALUES(?,?,?,datetime('now'))", (contact, ctype, message))
        con.commit()
        con.close()
        return jsonify({'success': True})
    else:
        ctype = request.args.get('type')
        if ctype:
            rows = cur.execute("SELECT id, contact, type, message, created_at FROM complaints WHERE type=? ORDER BY created_at DESC", (ctype,)).fetchall()
        else:
            rows = cur.execute("SELECT id, contact, type, message, created_at FROM complaints ORDER BY created_at DESC").fetchall()
        con.close()
        return jsonify([dict(r) for r in rows])


@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    con = db_conn()
    cur = con.cursor()
    # if query param all=true then include collected notifications
    include_all = request.args.get('all', 'false').lower() == 'true'
    truck_id = request.args.get('truck_id')
    if include_all:
        if truck_id:
            rows = cur.execute("SELECT notif_id, bin_id, truck_id, message, status, created_at, updated_at FROM notifications WHERE truck_id=? ORDER BY created_at DESC", (truck_id,)).fetchall()
        else:
            rows = cur.execute("SELECT notif_id, bin_id, truck_id, message, status, created_at, updated_at FROM notifications ORDER BY created_at DESC").fetchall()
    else:
        if truck_id:
            # For trucks, only return notifications acknowledged by admin (ACK) so driver sees tasks after admin acknowledgement
            rows = cur.execute("SELECT notif_id, bin_id, truck_id, message, status, created_at, updated_at FROM notifications WHERE status='ACK' AND truck_id=? ORDER BY created_at DESC", (truck_id,)).fetchall()
        else:
            rows = cur.execute("SELECT notif_id, bin_id, truck_id, message, status, created_at, updated_at FROM notifications WHERE status!='COLLECTED' ORDER BY created_at DESC").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/notifications/respond", methods=["POST"])
def respond_notification():
    data = request.get_json() or {}
    notif_id = data.get('notif_id')
    action = data.get('action')  # 'ACK', 'COLLECTED'
    truck_id = data.get('truck_id')
    con = db_conn()
    cur = con.cursor()
    if action == 'ACK':
        # If admin acknowledges without specifying a truck, assign the nearest truck to the bin
        if not truck_id:
            cur.execute("SELECT bin_id FROM notifications WHERE notif_id=?", (notif_id,))
            r = cur.fetchone()
            if r:
                bin_id = r['bin_id']
                # lookup bin location
                cur.execute("SELECT lat, lon FROM bins WHERE bin_id=?", (bin_id,))
                brow = cur.fetchone()
                if brow:
                    lat = brow['lat']
                    lon = brow['lon']
                    # find nearest truck
                    trucks = cur.execute("SELECT truck_id, lat, lon FROM trucks").fetchall()
                    nearest = None
                    nearest_dist = None
                    for t in trucks:
                        try:
                            dist = haversine_km(lat, lon, t['lat'], t['lon'])
                        except Exception:
                            dist = None
                        if dist is not None and (nearest is None or dist < nearest_dist):
                            nearest = t['truck_id']
                            nearest_dist = dist
                    truck_id = nearest
        cur.execute("UPDATE notifications SET status='ACK', truck_id=?, updated_at=datetime('now') WHERE notif_id=?", (truck_id, notif_id))
    elif action == 'COLLECTED':
        # mark notification collected and update bin
        cur.execute("SELECT bin_id, truck_id FROM notifications WHERE notif_id=?", (notif_id,))
        row = cur.fetchone()
        if row:
            bin_id = row['bin_id']
            notif_truck = row['truck_id']
            # fetch current level before resetting
            cur.execute("SELECT level FROM bins WHERE bin_id=?", (bin_id,))
            brow = cur.fetchone()
            level_at = brow['level'] if brow else None
            # insert into history
            cur.execute("INSERT INTO waste_collections(bin_id, truck_id, level_at_collection, collected_at) VALUES(?,?,?,datetime('now'))",
                        (bin_id, notif_truck or truck_id, level_at))
            cur.execute("UPDATE bins SET level=0, status='COLLECTED', last_updated=datetime('now') WHERE bin_id=?", (bin_id,))
            # create admin notification about collection
            admin_msg = f"Bin {bin_id} was collected by {notif_truck or truck_id} (level {level_at})."
            cur.execute("INSERT INTO notifications(bin_id, truck_id, message, status, created_at, updated_at) VALUES(?,?,?,?,datetime('now'),datetime('now'))",
                        (bin_id, 'ADMIN', admin_msg, 'SENT'))
        cur.execute("UPDATE notifications SET status='COLLECTED', updated_at=datetime('now') WHERE notif_id=?", (notif_id,))
    con.commit()
    con.close()
    return jsonify({"success": True})


@app.route('/api/collect_by_truck', methods=['POST'])
def collect_by_truck():
    data = request.get_json() or {}
    bin_id = data.get('bin_id')
    truck_id = data.get('truck_id')
    con = db_conn()
    cur = con.cursor()
    # fetch current level
    cur.execute("SELECT level FROM bins WHERE bin_id=?", (bin_id,))
    brow = cur.fetchone()
    level_at = brow['level'] if brow else None
    # insert history
    cur.execute("INSERT INTO waste_collections(bin_id, truck_id, level_at_collection, collected_at) VALUES(?,?,?,datetime('now'))",
                (bin_id, truck_id, level_at))
    # update bin
    cur.execute("UPDATE bins SET level=0, status='COLLECTED', last_updated=datetime('now') WHERE bin_id=?", (bin_id,))
    # notify admin
    admin_msg = f"Bin {bin_id} was collected by {truck_id} (level {level_at})."
    cur.execute("INSERT INTO notifications(bin_id, truck_id, message, status, created_at, updated_at) VALUES(?,?,?,?,datetime('now'),datetime('now'))",
                (bin_id, 'ADMIN', admin_msg, 'SENT'))
    con.commit()
    con.close()
    return jsonify({"success": True})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    role = data.get('role', 'admin')
    con = db_conn()
    cur = con.cursor()
    if role == 'admin':
        username = data.get('username')
        password = data.get('password')
        cur.execute("SELECT username, password FROM admin WHERE username=?", (username,))
        user = cur.fetchone()
        if user:
            stored = user['password'] or ''
            # first try hashed check
            try:
                if stored and check_password_hash(stored, password):
                    con.close()
                    return jsonify({"success": True, "role": "admin", "username": username})
            except Exception:
                # check_password_hash may raise if stored not a valid hash; fallthrough
                pass
            # fallback: if stored appears to be plaintext and matches, upgrade to hashed
            if stored == password:
                try:
                    newh = generate_password_hash(password)
                    cur.execute("UPDATE admin SET password=? WHERE username=?", (newh, username))
                    con.commit()
                except Exception:
                    pass
                con.close()
                return jsonify({"success": True, "role": "admin", "username": username})
        con.close()
        return jsonify({"success": False}), 401
    elif role == 'truck':
        # truck login uses truck_id and phone for demo. If truck not found, create a pending request
        truck_id = data.get('truck_id')
        phone = data.get('phone')
        device_token = data.get('device_token')
        cur.execute("SELECT truck_id, name, phone FROM trucks WHERE truck_id=? AND phone=?", (truck_id, phone))
        t = cur.fetchone()
        if t:
            con.close()
            return jsonify({"success": True, "role": "truck", "truck_id": t['truck_id'], "name": t['name']})
        # not found -> create a driver request if not already pending
        cur.execute("SELECT id FROM driver_requests WHERE truck_id=? AND status='PENDING'", (truck_id,))
        existing = cur.fetchone()
        if not existing:
            cur.execute("INSERT INTO driver_requests(truck_id, name, phone, device_token, status, created_at) VALUES(?,?,?,?,?,datetime('now'))",
                        (truck_id, data.get('name'), phone, device_token, 'PENDING'))
            req_id = cur.lastrowid
            # record an admin notification
            msg = f"New truck driver login request: {truck_id} ({data.get('name')})"
            cur.execute("INSERT INTO notifications(bin_id, truck_id, message, status, created_at, updated_at) VALUES(?,?,?,?,datetime('now'),datetime('now'))",
                        (None, 'ADMIN', msg, 'PENDING'))
            con.commit()
            # send FCM to admin topic (requires FCM_SERVER_KEY or firebase-admin)
            try:
                send_fcm_message(topic='admin', title='New Driver Request', body=msg, data_payload={'type':'driver_request','truck_id':truck_id,'request_id':req_id})
            except Exception:
                pass
        con.close()
        return jsonify({"success": False, "reason": "registration_requested"}), 202
    elif role == 'user':
        # user login: check `users` table; if not found create a pending user request
        user_id = data.get('user_id')
        phone = data.get('phone')
        email = data.get('email')
        device_token = data.get('device_token')
        # try lookup by user_id or phone or email
        if user_id:
            cur.execute("SELECT user_id, name, phone, email FROM users WHERE user_id=?", (user_id,))
        elif phone:
            cur.execute("SELECT user_id, name, phone, email FROM users WHERE phone=?", (phone,))
        elif email:
            cur.execute("SELECT user_id, name, phone, email FROM users WHERE email=?", (email,))
        else:
            cur.execute("SELECT user_id, name, phone, email FROM users WHERE phone=?", (phone,))
        u = cur.fetchone()
        if u:
            con.close()
            return jsonify({"success": True, "role": "user", "user_id": u['user_id'], "name": u['name']})
        # create pending request
        cur.execute("SELECT id FROM user_requests WHERE (user_id=? OR phone=? OR email=?) AND status='PENDING'", (user_id, phone, email))
        existing = cur.fetchone()
        if not existing:
            cur.execute("INSERT INTO user_requests(user_id, name, phone, email, device_token, status, created_at) VALUES(?,?,?,?,?,? ,datetime('now'))",
                        (user_id, data.get('name'), phone, email, device_token, 'PENDING'))
            req_id = cur.lastrowid
            msg = f"New user registration request: {data.get('name') or phone}"
            cur.execute("INSERT INTO notifications(bin_id, truck_id, message, status, created_at, updated_at) VALUES(?,?,?,?,datetime('now'),datetime('now'))",
                        (None, 'ADMIN', msg, 'PENDING'))
            con.commit()
            try:
                send_fcm_message(topic='admin', title='New User Request', body=msg, data_payload={'type':'user_request','request_id':req_id})
            except Exception:
                pass
        con.close()
        return jsonify({"success": False, "reason": "registration_requested"}), 202
    else:
        con.close()
        return jsonify({"success": False}), 400


@app.route('/api/register/driver', methods=['POST'])
def register_driver():
    data = request.get_json() or {}
    truck_id = data.get('truck_id')
    name = data.get('name')
    phone = data.get('phone')
    device_token = data.get('device_token')
    con = db_conn()
    cur = con.cursor()
    cur.execute("INSERT INTO driver_requests(truck_id, name, phone, device_token, status, created_at) VALUES(?,?,?,?,?,datetime('now'))",
                (truck_id, name, phone, device_token, 'PENDING'))
    req_id = cur.lastrowid
    cur.execute("INSERT INTO notifications(bin_id, truck_id, message, status, created_at, updated_at) VALUES(?,?,?,?,datetime('now'),datetime('now'))",
                (None, 'ADMIN', f"New driver registration: {truck_id} ({name})", 'PENDING'))
    con.commit()
    try:
        send_fcm_message(topic='admin', title='New Driver Registration', body=f"{name} ({truck_id}) requested registration", data_payload={'type':'driver_request','request_id':req_id})
    except Exception:
        pass
    con.close()
    return jsonify({'success': True, 'request_id': req_id})


@app.route('/api/register/user', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    device_token = data.get('device_token')
    con = db_conn()
    cur = con.cursor()
    cur.execute("INSERT INTO user_requests(user_id, name, phone, email, device_token, status, created_at) VALUES(?,?,?,?,?,? ,datetime('now'))",
                (user_id, name, phone, email, device_token, 'PENDING'))
    req_id = cur.lastrowid
    cur.execute("INSERT INTO notifications(bin_id, truck_id, message, status, created_at, updated_at) VALUES(?,?,?,?,datetime('now'),datetime('now'))",
                (None, 'ADMIN', f"New user registration: {name} ({phone})", 'PENDING'))
    con.commit()
    try:
        send_fcm_message(topic='admin', title='New User Registration', body=f"{name} requested registration", data_payload={'type':'user_request','request_id':req_id})
    except Exception:
        pass
    con.close()
    return jsonify({'success': True, 'request_id': req_id})


@app.route('/api/registrations/drivers', methods=['GET'])
def list_driver_requests():
    con = db_conn()
    cur = con.cursor()
    rows = cur.execute("SELECT id, truck_id, name, phone, device_token, status, created_at FROM driver_requests ORDER BY created_at DESC").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/registrations/users', methods=['GET'])
def list_user_requests():
    con = db_conn()
    cur = con.cursor()
    rows = cur.execute("SELECT id, user_id, name, phone, email, device_token, status, created_at FROM user_requests ORDER BY created_at DESC").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/registrations/driver/approve', methods=['POST'])
def approve_driver():
    data = request.get_json() or {}
    req_id = data.get('request_id')
    action = data.get('action', 'approve')
    con = db_conn()
    cur = con.cursor()
    cur.execute("SELECT id, truck_id, name, phone, device_token, status FROM driver_requests WHERE id=?", (req_id,))
    r = cur.fetchone()
    if not r:
        con.close()
        return jsonify({'success': False, 'error': 'not_found'}), 404
    if action == 'approve':
        cur.execute("INSERT OR REPLACE INTO trucks(truck_id, name, phone, lat, lon) VALUES(?,?,?,0,0)", (r['truck_id'], r['name'], r['phone']))
        cur.execute("UPDATE driver_requests SET status='APPROVED' WHERE id=?", (req_id,))
        con.commit()
        # notify driver device if token present
        if r['device_token']:
            try:
                send_fcm_message(token=r['device_token'], title='Registration Approved', body='Your driver registration has been approved.')
            except Exception:
                pass
        con.close()
        return jsonify({'success': True})
    else:
        cur.execute("UPDATE driver_requests SET status='REJECTED' WHERE id=?", (req_id,))
        con.commit()
        con.close()
        return jsonify({'success': True})


@app.route('/api/registrations/user/approve', methods=['POST'])
def approve_user():
    data = request.get_json() or {}
    req_id = data.get('request_id')
    action = data.get('action', 'approve')
    con = db_conn()
    cur = con.cursor()
    cur.execute("SELECT id, user_id, name, phone, email, device_token, status FROM user_requests WHERE id=?", (req_id,))
    r = cur.fetchone()
    if not r:
        con.close()
        return jsonify({'success': False, 'error': 'not_found'}), 404
    if action == 'approve':
        uid = r['user_id'] or f"USER_{r['phone']}"
        cur.execute("INSERT OR REPLACE INTO users(user_id, name, phone, email, created_at) VALUES(?,?,?,?,datetime('now'))", (uid, r['name'], r['phone'], r['email']))
        cur.execute("UPDATE user_requests SET status='APPROVED' WHERE id=?", (req_id,))
        con.commit()
        if r['device_token']:
            try:
                send_fcm_message(token=r['device_token'], title='Registration Approved', body='Your user registration has been approved.')
            except Exception:
                pass
        con.close()
        return jsonify({'success': True})
    else:
        cur.execute("UPDATE user_requests SET status='REJECTED' WHERE id=?", (req_id,))
        con.commit()
        con.close()
        return jsonify({'success': True})


def handle_collect(bin_id, payload):
    # validate & persist payload to DB (existing logic)
    # ...
    # publish to redis for realtime delivery
    r.publish(CHANNEL, json.dumps({
      "type": "bin_update",
      "bin_id": bin_id,
      "level": payload.get("level"),
      "status": payload.get("status"),
      "lat": payload.get("lat"),
      "lon": payload.get("lon"),
      "ts": payload.get("timestamp")
    }))
# -------------------------------------------------------------
# GET ALL APPROVED DRIVERS (For Admin Dashboard)
# -------------------------------------------------------------
@app.route("/api/drivers", methods=["GET"])
def get_drivers():
    """
    Returns all approved drivers stored in trucks table.
    Used by Admin Dashboard Driver Details widget.
    """

    con = db_conn()
    cur = con.cursor()

    rows = cur.execute("""
        SELECT
            truck_id,
            name,
            phone,
            lat,
            lon
        FROM trucks
        ORDER BY name
    """).fetchall()

    con.close()

    drivers = []

    for r in rows:
        drivers.append({
            "truck_id": r["truck_id"],
            "name": r["name"],
            "phone": r["phone"],
            "lat": r["lat"],
            "lon": r["lon"]
        })

    return jsonify(drivers)


@app.route("/api/bins/full", methods=["GET"])
def get_full_bins():

    con = db_conn()
    cur = con.cursor()

    rows = cur.execute("""
    SELECT * FROM bins
    WHERE status='FULL'
    """).fetchall()

    con.close()

    return jsonify([dict(r) for r in rows])
@app.route("/api/bins/nearest", methods=["GET"])
def nearest_bin():

    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))

    con = db_conn()
    cur = con.cursor()

    rows = cur.execute("SELECT * FROM bins").fetchall()

    nearest = None
    nearest_distance = None

    for r in rows:
        dist = haversine_km(lat, lon, r["lat"], r["lon"])

        if nearest is None or dist < nearest_distance:
            nearest = r
            nearest_distance = dist

    con.close()

    if nearest:
        return jsonify(dict(nearest))
    else:
        return jsonify({"message": "No bins found"})
@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():

    con = db_conn()
    cur = con.cursor()

    total = cur.execute("SELECT COUNT(*) FROM bins").fetchone()[0]
    full = cur.execute("SELECT COUNT(*) FROM bins WHERE status='FULL'").fetchone()[0]
    half = cur.execute("SELECT COUNT(*) FROM bins WHERE status='HALF'").fetchone()[0]
    empty = cur.execute("SELECT COUNT(*) FROM bins WHERE status='EMPTY'").fetchone()[0]

    con.close()

    return jsonify({
        "total_bins":total,
        "full_bins":full,
        "half_bins":half,
        "empty_bins":empty
    })



@app.route("/api/complaints", methods=["POST"])
def add_complaint():

    data = request.json

    conn = db_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO complaints(type,message,contact,created_at) VALUES(?,?,?,datetime('now'))",
        (
            data.get("type"),
            data.get("message"),
            data.get("contact")
        )
    )

    conn.commit()
    conn.close()

    return jsonify({"message":"submitted"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)