import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from src.models.user import db
from src.models.booking import Booking, BlockedSlot
from src.models.client import Client
from src.routes.user import user_bp
from src.routes.booking import booking_bp
from src.routes.admin import admin_bp
from src.routes.payment import payment_bp
from src.routes.verification import verification_bp
from src.routes.simple_booking import simple_booking_bp
from src.routes.direct_admin import direct_admin_bp

# Import database initialization
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def initialize_database():
    """Initialize database tables for Wave House booking system"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("No DATABASE_URL found, skipping database initialization")
        return
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Database connection successful!")
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database initialization error: {e}")

# Create Flask app (API only, no static files)
app = Flask(__name__)

# Configure CORS for frontend connections
CORS(app, origins=["*"])

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wave_house.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'wave-house-secret-key-2024')

# Initialize database
db.init_app(app)

# Register API blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(booking_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(payment_bp, url_prefix='/api')
app.register_blueprint(verification_bp, url_prefix='/api')
app.register_blueprint(simple_booking_bp, url_prefix='/api')
app.register_blueprint(direct_admin_bp, url_prefix='/api')

# Health check endpoint
@app.route('/')
def health_check():
    return jsonify({
        'status': 'Wave House Backend API is running',
        'admin': '/api/admin',
        'booking': '/api/booking',
        'version': '1.0'
    })

# Admin dashboard route (direct access)
@app.route('/admin')
def admin_dashboard():
    from src.routes.admin import admin_bp
    # This will serve the admin login page
    return admin_bp.view_functions['admin_login']()

# Initialize database tables
with app.app_context():
    initialize_database()
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

