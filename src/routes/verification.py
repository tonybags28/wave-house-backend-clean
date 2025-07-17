from flask import Blueprint, request, jsonify
from datetime import datetime
import os

# Import models
from src.models.user import db
from src.models.client import Client
from src.models.booking import Booking

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/api/verification/check-client', methods=['POST'])
def check_client_verification_status():
    """Check if a client exists and their verification status"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if client exists
        client = Client.query.filter_by(email=email).first()
        
        if not client:
            return jsonify({
                'client_exists': False,
                'is_verified': False,
                'needs_verification': True,
                'verification_status': 'new_client'
            })
        
        return jsonify({
            'client_exists': True,
            'is_verified': client.is_verified,
            'needs_verification': client.needs_verification(),
            'verification_status': client.verification_status,
            'total_bookings': client.total_bookings,
            'is_first_time': client.is_first_time_client()
        })
        
    except Exception as e:
        print(f"Error checking client verification: {str(e)}")
        return jsonify({'error': 'Failed to check client status'}), 500

@verification_bp.route('/api/verification/create-session', methods=['POST'])
def create_verification_session():
    """Create a simplified verification session"""
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        
        if not email or not name:
            return jsonify({'error': 'Email and name are required'}), 400
        
        print(f"🔐 Creating verification session for {email}")
        
        # Create or get client record
        client = Client.query.filter_by(email=email).first()
        if not client:
            client = Client(
                email=email,
                name=name,
                verification_status='pending'
            )
            db.session.add(client)
            db.session.commit()
            print(f"✅ Created new client record for {email}")
        
        # For now, return a mock verification session
        # This will allow the frontend flow to work while we fix Stripe integration
        return jsonify({
            'session_id': f'vs_mock_{client.id}',
            'verification_session_id': f'vs_mock_{client.id}',
            'url': 'javascript:void(0)',  # No-op URL that won't open a new window
            'status': 'created',
            'mock': True  # Indicates this is a mock session
        })
        
    except Exception as e:
        print(f"❌ Verification session error: {str(e)}")
        return jsonify({'error': f'Verification error: {str(e)}'}), 500

@verification_bp.route('/api/verification/complete-mock', methods=['POST'])
def complete_mock_verification():
    """Complete mock verification for testing"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Find and update client
        client = Client.query.filter_by(email=email).first()
        if client:
            client.verification_status = 'verified'
            client.is_verified = True
            db.session.commit()
            print(f"✅ Mock verification completed for {email}")
        
        return jsonify({
            'status': 'verified',
            'message': 'Mock verification completed successfully'
        })
        
    except Exception as e:
        print(f"❌ Mock verification error: {str(e)}")
        return jsonify({'error': f'Mock verification error: {str(e)}'}), 500

