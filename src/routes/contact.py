from flask import Blueprint, request, jsonify
from src.utils.email_sender import send_email
import os

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ('name', 'email', 'message')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        name = data['name']
        email = data['email']
        message = data['message']
        
        # Send email notification to Wave House
        admin_email = os.environ.get('ADMIN_EMAIL', 'letswork@wavehousela.com')
        
        subject = f"New Contact Form Submission from {name}"
        body = f"""
New contact form submission from Wave House website:

Name: {name}
Email: {email}

Message:
{message}

---
This message was sent from the Wave House contact form.
"""
        
        # Send email to admin
        if send_email(admin_email, subject, body):
            return jsonify({
                'success': True,
                'message': 'Contact form submitted successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send email notification'
            }), 500
            
    except Exception as e:
        print(f"Contact form error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

