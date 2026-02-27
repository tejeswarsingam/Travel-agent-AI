import os
import uuid
import threading
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Import your AI logic
from ai_engine import generate_itinerary_logic
import sqlite3

def init_db():
    conn = sqlite3.connect('travel_guide.db')
    cursor = conn.cursor()
    # Create table for itineraries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itineraries (
            id TEXT PRIMARY KEY,
            destination TEXT,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Call this when the app starts
init_db()

def save_to_sql(task_id, destination, itinerary_json):
    conn = sqlite3.connect('travel_guide.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO itineraries (id, destination, data) VALUES (?, ?, ?)",
        (task_id, destination, str(itinerary_json))
    )
    conn.commit()
    conn.close()
# Load .env file for API Keys
load_dotenv()

app = Flask(__name__)

# In-memory storage for task statuses and results
# In production, use Redis or a Database
tasks = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def handle_generate():
    """Starts the AI generation in a background thread"""
    data = request.json
    task_id = str(uuid.uuid4())
    
    # Initialize task state
    tasks[task_id] = {"status": "processing", "data": None}

    # Extract data from request
    destination = data.get('dest', 'Paris')
    interests = data.get('interests', [])
    days = data.get('days', 3)

    # Start background thread so the user doesn't wait for the AI to finish
    thread = threading.Thread(
        target=background_ai_task, 
        args=(task_id, destination, interests, days)
    )
    thread.start()

    return jsonify({"task_id": task_id})

@app.route('/api/results/<task_id>')
def get_results(task_id):
    """Called by the frontend every few seconds to check if the AI is done"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"status": "not_found"}), 404
    
    return jsonify(task)

def background_ai_task(tid, dest, interests, days):
    """The actual worker that calls Gemini"""
    try:
        itinerary = generate_itinerary_logic(dest, interests, days)
        tasks[tid] = {"status": "completed", "data": itinerary}
    except Exception as e:
        print(f"AI Error for task {tid}: {e}")
        tasks[tid] = {"status": "failed", "error": str(e)}

if __name__ == '__main__':
    # Using port 8080 to avoid the macOS AirPlay conflict on 5000
    app.run(debug=True, port=8080)