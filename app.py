from flask import Flask, render_template, request, jsonify, g
import sqlite3
from datetime import datetime
import os
import shutil

app = Flask(__name__)

# Update the DATABASE path to be absolute
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'office_tracker.db')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# Create backup directory if it doesn't exist
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def backup_db():
    """Create a backup of the database"""
    if os.path.exists(DATABASE):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(BACKUP_DIR, f'office_tracker_backup_{timestamp}.db')
        shutil.copy2(DATABASE, backup_file)
        
        # Keep only the last 5 backups
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')])
        while len(backups) > 5:
            os.remove(os.path.join(BACKUP_DIR, backups.pop(0)))

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.before_request
def before_request():
    """Ensure database exists before each request"""
    init_db()

@app.teardown_appcontext
def close_db(error):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database and create tables if they don't exist"""
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events', methods=['GET'])
def get_events():
    db = get_db()
    cursor = db.execute('SELECT * FROM events')
    events = cursor.fetchall()
    formatted_events = []
    
    # Create a mapping for event types to titles
    type_to_title = {
        'WFH': 'Work From Home',
        'WFO': 'Work From Office',
        'AL': 'Annual Leave',
        'SL': 'Sick Leave',
        'HOL': 'Holiday',
        'OTHER': 'Other'
    }
    
    for event in events:
        formatted_events.append({
            'id': event['id'],
            'title': type_to_title.get(event['type'], event['type']),  # Display friendly name
            'start': event['date'],
            'classNames': [event['type']],  # Add the type as a class for styling
            'type': event['type']  # Keep the original type
        })
    
    return jsonify(formatted_events)

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.get_json()
    db = get_db()
    db.execute(
        'INSERT INTO events (date, type) VALUES (?, ?)',
        [data['date'], data['type']]
    )
    db.commit()
    backup_db()  # Create backup after modification
    return jsonify({'status': 'success'})

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    db = get_db()
    db.execute('DELETE FROM events WHERE id = ?', [event_id])
    db.commit()
    backup_db()  # Create backup after modification
    return jsonify({'status': 'success'})

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json()
    db = get_db()
    db.execute(
        'UPDATE events SET date = ?, type = ? WHERE id = ?',
        [data['date'], data['type'], event_id]
    )
    db.commit()
    backup_db()  # Create backup after modification
    return jsonify({'status': 'success'})

@app.route('/api/backup/restore/<filename>', methods=['POST'])
def restore_backup(filename):
    try:
        backup_file = os.path.join(BACKUP_DIR, filename)
        if os.path.exists(backup_file):
            # Close any existing database connections
            db = g.pop('db', None)
            if db is not None:
                db.close()
            
            # Backup current database before restore
            backup_db()
            
            # Restore from backup
            shutil.copy2(backup_file, DATABASE)
            return jsonify({'status': 'success', 'message': 'Backup restored successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Backup file not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/backups', methods=['GET'])
def list_backups():
    backups = []
    for f in os.listdir(BACKUP_DIR):
        if f.endswith('.db'):
            backup_path = os.path.join(BACKUP_DIR, f)
            backup_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
            backups.append({
                'filename': f,
                'timestamp': backup_time.strftime('%Y-%m-%d %H:%M:%S'),
                'size': os.path.getsize(backup_path)
            })
    return jsonify(sorted(backups, key=lambda x: x['timestamp'], reverse=True))

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 