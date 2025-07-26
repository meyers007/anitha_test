from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime, date
import sqlite3
import os
import requests
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Weather API configuration (you can get a free API key from OpenWeatherMap)
WEATHER_API_KEY = 'demo'  # Replace with your actual API key
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Database setup
def init_db():
    conn = sqlite3.connect('exercise_tracker.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Updated exercises table with user_id and hiking places
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT NOT NULL,
            exercise_type TEXT NOT NULL,
            duration INTEGER NOT NULL,
            calories INTEGER,
            notes TEXT,
            hiking_place TEXT,
            weather_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Authentication helpers
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_id():
    return session.get('user_id')

def get_weather_info(city='San Francisco'):
    """Get weather information for the day"""
    try:
        if WEATHER_API_KEY == 'demo':
            # Return demo weather data
            return {
                'temperature': 72,
                'description': 'Sunny',
                'icon': '01d'
            }
        
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'imperial'
        }
        response = requests.get(WEATHER_API_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'temperature': int(data['main']['temp']),
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon']
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    
    # Fallback weather data
    return {
        'temperature': 70,
        'description': 'Pleasant',
        'icon': '01d'
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        conn = sqlite3.connect('exercise_tracker.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Create new user
        password_hash = hash_password(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                      (username, password_hash))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        conn = sqlite3.connect('exercise_tracker.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[1] == hash_password(password):
            session['user_id'] = user[0]
            session['username'] = username
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/current_user')
def current_user():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session['username'],
            'user_id': session['user_id']
        })
    return jsonify({'logged_in': False})

@app.route('/add_exercise', methods=['POST'])
def add_exercise():
    try:
        data = request.get_json()
        user_id = get_current_user_id()  # Optional - can be None for guest users
        
        # Get weather info for the day
        weather_info = get_weather_info()
        weather_str = f"{weather_info['temperature']}°F, {weather_info['description']}"
        
        conn = sqlite3.connect('exercise_tracker.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO exercises (user_id, date, exercise_type, duration, calories, notes, hiking_place, weather_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['date'],
            data['exercise_type'],
            data['duration'],
            data.get('calories', 0),
            data.get('notes', ''),
            data.get('hiking_place', ''),
            weather_str
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Exercise added successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/get_exercises')
def get_exercises():
    try:
        user_id = get_current_user_id()
        conn = sqlite3.connect('exercise_tracker.db')
        cursor = conn.cursor()
        
        # Filter by user if logged in, otherwise show all exercises
        if user_id:
            cursor.execute('''
                SELECT date, exercise_type, duration, calories, notes, hiking_place, weather_info, created_at
                FROM exercises
                WHERE user_id = ? OR user_id IS NULL
                ORDER BY date DESC, created_at DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT date, exercise_type, duration, calories, notes, hiking_place, weather_info, created_at
                FROM exercises
                WHERE user_id IS NULL
                ORDER BY date DESC, created_at DESC
            ''')
        
        exercises = []
        for row in cursor.fetchall():
            exercises.append({
                'date': row[0],
                'exercise_type': row[1],
                'duration': row[2],
                'calories': row[3],
                'notes': row[4],
                'hiking_place': row[5],
                'weather_info': row[6],
                'created_at': row[7]
            })
        
        conn.close()
        return jsonify(exercises)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_stats')
def get_stats():
    try:
        user_id = get_current_user_id()
        conn = sqlite3.connect('exercise_tracker.db')
        cursor = conn.cursor()
        
        # Filter by user if logged in
        user_filter = 'WHERE (user_id = ? OR user_id IS NULL)' if user_id else 'WHERE user_id IS NULL'
        user_params = (user_id,) if user_id else ()
        
        # Get total exercises this week
        cursor.execute(f'''
            SELECT COUNT(*), SUM(duration), SUM(calories)
            FROM exercises
            {user_filter} AND date >= date('now', '-7 days')
        ''', user_params)
        week_stats = cursor.fetchone()
        
        # Get total exercises this month
        cursor.execute(f'''
            SELECT COUNT(*), SUM(duration), SUM(calories)
            FROM exercises
            {user_filter} AND date >= date('now', 'start of month')
        ''', user_params)
        month_stats = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'week': {
                'count': week_stats[0] or 0,
                'duration': week_stats[1] or 0,
                'calories': week_stats[2] or 0
            },
            'month': {
                'count': month_stats[0] or 0,
                'duration': month_stats[1] or 0,
                'calories': month_stats[2] or 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_reports')
def get_reports():
    try:
        user_id = get_current_user_id()
        conn = sqlite3.connect('exercise_tracker.db')
        cursor = conn.cursor()
        
        # Filter by user if logged in
        user_filter = 'WHERE (user_id = ? OR user_id IS NULL)' if user_id else 'WHERE user_id IS NULL'
        user_params = (user_id,) if user_id else ()
        
        # Get daily workout data for the last 30 days
        cursor.execute(f'''
            SELECT date, SUM(duration) as total_duration, SUM(calories) as total_calories, COUNT(*) as workout_count
            FROM exercises
            {user_filter} AND date >= date('now', '-30 days')
            GROUP BY date
            ORDER BY date
        ''', user_params)
        
        daily_data = []
        for row in cursor.fetchall():
            daily_data.append({
                'date': row[0],
                'duration': row[1] or 0,
                'calories': row[2] or 0,
                'count': row[3] or 0
            })
        
        # Get exercise type breakdown
        cursor.execute(f'''
            SELECT exercise_type, COUNT(*) as count, SUM(duration) as total_duration, SUM(calories) as total_calories
            FROM exercises
            {user_filter} AND date >= date('now', '-30 days')
            GROUP BY exercise_type
            ORDER BY count DESC
        ''', user_params)
        
        exercise_breakdown = []
        for row in cursor.fetchall():
            exercise_breakdown.append({
                'type': row[0],
                'count': row[1],
                'duration': row[2] or 0,
                'calories': row[3] or 0
            })
        
        conn.close()
        
        return jsonify({
            'daily_data': daily_data,
            'exercise_breakdown': exercise_breakdown
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_weather')
def get_weather():
    weather = get_weather_info()
    return jsonify(weather)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
