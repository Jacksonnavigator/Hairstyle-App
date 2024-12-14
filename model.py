import sqlite3
import bcrypt

# Create database connection
def get_db_connection():
    conn = sqlite3.connect('hairstylist_app.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db_connection()
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    user_type TEXT -- 'hairstylist' or 'client'
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS hairstylists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    styles TEXT,
    salon_price REAL,
    home_price REAL,
    availability TEXT,
    location TEXT,
    style_image BLOB,
    rating REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    stylist_id INTEGER,
    date TEXT,
    time TEXT,
    service_type TEXT,
    price REAL,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (client_id) REFERENCES users (id),
    FOREIGN KEY (stylist_id) REFERENCES hairstylists (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stylist_id INTEGER,
    client_id INTEGER,
    rating INTEGER,
    comment TEXT,
    FOREIGN KEY (stylist_id) REFERENCES hairstylists (id),
    FOREIGN KEY (client_id) REFERENCES users (id)
)
''')

conn.commit()

# User Authentication
def register_user(username, password, user_type):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        return {"success": False, "message": "Username already exists."}

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)',
                       (username, hashed_password, user_type))
        conn.commit()
        return {"success": True, "message": "User registered successfully."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Database error: {e}"}

def login_user(username, password):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    return None

# Add/Edit Hairstylist Profile
def add_or_edit_hairstylist(user_id, name, styles, salon_price, home_price, availability, location, image_bytes):
    cursor.execute('''
        INSERT OR REPLACE INTO hairstylists (user_id, name, styles, salon_price, home_price, availability, location, style_image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, name, styles, salon_price, home_price, availability, location, image_bytes))
    conn.commit()

# Fetch Hairstylists
def fetch_hairstylists(location=None):
    query = 'SELECT * FROM hairstylists'
    params = []
    if location:
        query += " WHERE location LIKE ?"
        params.append(f"%{location}%")
    cursor.execute(query, params)
    return cursor.fetchall()

def fetch_stylist_by_id(stylist_id):
    cursor.execute('SELECT * FROM hairstylists WHERE id = ?', (stylist_id,))
    return cursor.fetchone()

# Booking
def add_booking(client_id, stylist_id, date, time, service_type, price):
    cursor.execute('''
        INSERT INTO bookings (client_id, stylist_id, date, time, service_type, price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (client_id, stylist_id, date, time, service_type, price, 'pending'))
    conn.commit()
