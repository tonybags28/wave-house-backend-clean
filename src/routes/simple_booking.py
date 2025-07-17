from flask import Blueprint, request, jsonify
import psycopg
import os
from datetime import datetime

simple_booking_bp = Blueprint('simple_booking', __name__)

@simple_booking_bp.route('/submit-booking', methods=['POST', 'OPTIONS'])
def submit_booking():
    """Simple booking submission that saves directly to database"""
    
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return jsonify({'error': 'Database not configured'}), 500
        
        # Connect to database using psycopg3
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                # Create table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS bookings (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        phone VARCHAR(20),
                        service_type VARCHAR(100),
                        date DATE,
                        start_time TIME,
                        end_time TIME,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert booking
                cur.execute("""
                    INSERT INTO bookings (name, email, phone, service_type, date, start_time, end_time, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data.get('name'),
                    data.get('email'),
                    data.get('phone'),
                    data.get('service_type'),
                    data.get('date'),
                    data.get('start_time'),
                    data.get('end_time'),
                    data.get('notes')
                ))
                
                conn.commit()
        
        return jsonify({'message': 'Booking submitted successfully'}), 200
        
    except Exception as e:
        print(f"Error submitting booking: {str(e)}")
        return jsonify({'error': 'Failed to submit booking'}), 500

