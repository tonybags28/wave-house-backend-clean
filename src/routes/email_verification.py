from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.client import Client
from src.models.booking import Booking
from src.utils.email_sender import send_email
import os

email_verification_bp = Blueprint('email_verification', __name__)

@email_verification_bp.route('/api/verification/send-email', methods=['POST'])
def send_verification_email():
    """Send verification email to client"""
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        
        if not email or not name:
            return jsonify({'error': 'Email and name are required'}), 400
        
        # Find client
        client = Client.query.filter_by(email=email).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Send verification email
        verification_subject = "Wave House - ID Verification Required"
        verification_body = f"""
Hello {name},

Thank you for booking with Wave House! 

As a first-time client, we require ID verification for studio security. This is a one-time process that takes just a few minutes.

VERIFICATION INSTRUCTIONS:
1. Reply to this email with a clear photo of your government-issued ID (driver's license, passport, or state ID)
2. Include a selfie of yourself holding your ID next to your face
3. We'll review and approve your verification within 24 hours

Once verified, you won't need to complete this process again for future bookings.

Questions? Reply to this email or call us.

Best regards,
Wave House Team
letswork@wavehousela.com
"""
        
        if send_email(email, verification_subject, verification_body):
            return jsonify({
                'success': True,
                'message': 'Verification email sent successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to send verification email'}), 500
            
    except Exception as e:
        print(f"Verification email error: {e}")
        return jsonify({'error': 'Failed to send verification email'}), 500

@email_verification_bp.route('/api/verification/mark-verified', methods=['POST'])
def mark_client_verified():
    """Mark a client as verified (admin use)"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Find and update client
        client = Client.query.filter_by(email=email).first()
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        client.is_verified = True
        client.verification_status = 'verified'
        db.session.commit()
        
        # Update all pending bookings for this client
        pending_bookings = Booking.query.filter_by(
            email=email, 
            status='pending_verification'
        ).all()
        
        for booking in pending_bookings:
            booking.status = 'pending_confirmation'
        
        db.session.commit()
        
        # Send confirmation email to client
        confirmation_subject = "Wave House - Verification Complete"
        confirmation_body = f"""
Hello {client.name},

Great news! Your ID verification has been approved.

Your booking requests are now being processed and we'll contact you within 24 hours to confirm your sessions.

Thank you for choosing Wave House!

Best regards,
Wave House Team
letswork@wavehousela.com
"""
        
        send_email(email, confirmation_subject, confirmation_body)
        
        return jsonify({
            'success': True,
            'message': 'Client marked as verified',
            'updated_bookings': len(pending_bookings)
        }), 200
        
    except Exception as e:
        print(f"Mark verified error: {e}")
        return jsonify({'error': 'Failed to mark client as verified'}), 500

@email_verification_bp.route('/api/verification/status/<email>', methods=['GET'])
def get_verification_status(email):
    """Get verification status for a client"""
    try:
        client = Client.query.filter_by(email=email).first()
        
        if not client:
            return jsonify({
                'exists': False,
                'is_verified': False,
                'verification_status': 'new_client'
            }), 200
        
        return jsonify({
            'exists': True,
            'is_verified': client.is_verified,
            'verification_status': client.verification_status,
            'total_bookings': client.total_bookings
        }), 200
        
    except Exception as e:
        print(f"Verification status error: {e}")
        return jsonify({'error': 'Failed to get verification status'}), 500

