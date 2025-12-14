"""
Complete Hospital Booking Management System API
Patient Portal + Doctor Dashboard + Admin Panel
"""
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_compress import Compress
from models import db, Doctor, Patient, Appointment, CallLog, DoctorAvailability, FollowUpCall
import sys
import os
# Add agent directory to path to allow importing src.agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agent')))
from src.agent import DoctorBookingAgent
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
import os
import secrets

app = Flask(__name__)
CORS(app)
Compress(app)  # Enable gzip compression for faster response times

# Database configuration with performance optimizations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital_booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['JSON_SORT_KEYS'] = False  # Faster JSON serialization

db.init_app(app)

# Initialize agent
agent = DoctorBookingAgent()

# SMS Confirmation Helper
def send_sms_confirmation(phone, appointment_data):
    """Send SMS confirmation (mock implementation - integrate with Twilio/SMS service)"""
    message = f"""Appointment Confirmed!

Patient: {appointment_data['patient_name']}
Doctor: {appointment_data['doctor_name']} ({appointment_data['specialty']})
Date: {appointment_data['date']}
Time: {appointment_data['time']}
Confirmation: {appointment_data['confirmation']}

Arrive 10 min early. Call to reschedule.
- Hospital Booking System"""
    
    # TODO: Integrate with SMS gateway (Twilio, Nexmo, etc.)
    print(f"[SMS] Sending to {phone}:")
    print(message)
    return True

# WhatsApp Confirmation Helper
def send_whatsapp_confirmation(phone, appointment_data):
    """Send WhatsApp confirmation via Twilio"""
    
    # Twilio Credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    message_body = f"""*Appointment Confirmed!* ✅

👤 *Patient:* {appointment_data['patient_name']}
👨‍⚕️ *Doctor:* {appointment_data['doctor_name']} ({appointment_data['specialty']})
📅 *Date:* {appointment_data['date']}
⏰ *Time:* {appointment_data['time']}
🔖 *ID:* {appointment_data['confirmation']}

Please arrive 10 min early.
Reply to this message to reschedule."""

    print(f"\n[WhatsApp] Sending to {phone}...")
    
    try:
        client = Client(account_sid, auth_token)
        
        # FOR TESTING: Override recipient to verified number
        # Ensure phone number has country code (defaulting to +91 if missing for India)
        # to_number = phone if phone.startswith('+') else f"+91{phone}"
        to_number = "+919970208412" # Hardcoded for testing
        
        message = client.messages.create(
            from_='whatsapp:+14155238886',  # Twilio Sandbox Number
            body=message_body,
            to=f'whatsapp:{to_number}'
        )
        print(f"[WhatsApp] Sent successfully to {to_number}! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[WhatsApp] Failed to send: {str(e)}")
        return False

def send_whatsapp_reminder(phone, appointment_data):
    """Send WhatsApp reminder via Twilio"""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    message_body = f"""*Appointment Reminder* 🔔

Hi {appointment_data['patient_name']},
This is a reminder for your appointment with *{appointment_data['doctor_name']}* ({appointment_data['specialty']}).

📅 *Date:* {appointment_data['date']}
⏰ *Time:* {appointment_data['time']}

Please reply if you need to reschedule.
"""
    print(f"\n[WhatsApp Reminder] Sending to {phone}...")
    try:
        client = Client(account_sid, auth_token)
        to_number = "+919970208412" # Hardcoded for testing
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=message_body,
            to=f'whatsapp:{to_number}'
        )
        print(f"[WhatsApp] Sent successfully! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[WhatsApp] Failed to send: {str(e)}")
        return False

# Create tables
with app.app_context():
    db.create_all()
    print("[OK] Database initialized")

# ==================== PATIENT ENDPOINTS ====================

@app.route('/api/patient/register', methods=['POST'])
def register_patient():
    """Register a new patient"""
    try:
        data = request.json
        
        # Check if patient exists
        existing = Patient.query.filter_by(phone=data['phone']).first()
        if existing:
            return jsonify({
                'status': 'success',
                'data': {'id': existing.id, 'message': 'Patient already registered'}
            }), 200
        
        patient = Patient(
            name=data['name'],
            phone=data['phone'],
            email=data.get('email'),
            age=data.get('age'),
            gender=data.get('gender'),
            address=data.get('address'),
            medical_history=data.get('medical_history')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {'id': patient.id, 'message': 'Patient registered successfully'}
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'data': {'message': str(e)}}), 500

@app.route('/api/patient/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient details"""
    patient = Patient.query.get_or_404(patient_id)
    return jsonify({
        'status': 'success',
        'data': {
            'id': patient.id,
            'name': patient.name,
            'phone': patient.phone,
            'email': patient.email,
            'age': patient.age,
            'gender': patient.gender,
            'address': patient.address,
            'medical_history': patient.medical_history
        }
    })

@app.route('/api/patient/phone/<phone>', methods=['GET'])
def get_patient_by_phone(phone):
    """Get patient by phone number"""
    patient = Patient.query.filter_by(phone=phone).first()
    if not patient:
        return jsonify({'status': 'error', 'data': {'message': 'Patient not found'}}), 404
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': patient.id,
            'name': patient.name,
            'phone': patient.phone,
            'email': patient.email
        }
    })

# ==================== DOCTOR ENDPOINTS ====================

@app.route('/api/doctor/register', methods=['POST'])
def register_doctor():
    """Register a new doctor"""
    try:
        data = request.json
        
        doctor = Doctor(
            name=data['name'],
            specialty=data['specialty'],
            phone=data.get('phone'),
            email=data.get('email'),
            clinic_name=data.get('clinic_name'),
            available_days=data.get('available_days', 'Mon-Fri'),
            available_time=data.get('available_time', '9 AM - 5 PM'),
            consultation_fee=data.get('consultation_fee', 500)
        )
        
        db.session.add(doctor)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {'id': doctor.id, 'message': 'Doctor registered successfully'}
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'data': {'message': str(e)}}), 500

@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    """Get all doctors"""
    specialty = request.args.get('specialty')
    
    query = Doctor.query
    if specialty:
        query = query.filter_by(specialty=specialty)
    
    doctors = query.all()
    
    return jsonify({
        'status': 'success',
        'data': [{
            'id': d.id,
            'name': d.name,
            'specialty': d.specialty,
            'clinic_name': d.clinic_name,
            'available_time': d.available_time,
            'consultation_fee': d.consultation_fee
        } for d in doctors]
    })

@app.route('/api/doctor/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    """Get doctor details"""
    doctor = Doctor.query.get_or_404(doctor_id)
    return jsonify({
        'status': 'success',
        'data': {
            'id': doctor.id,
            'name': doctor.name,
            'specialty': doctor.specialty,
            'phone': doctor.phone,
            'email': doctor.email,
            'clinic_name': doctor.clinic_name,
            'available_days': doctor.available_days,
            'available_time': doctor.available_time,
            'consultation_fee': doctor.consultation_fee
        }
    })

@app.route('/api/doctor/<int:doctor_id>/appointments', methods=['GET'])
def get_doctor_appointments(doctor_id):
    """Get all appointments for a doctor - optimized with eager loading"""
    from sqlalchemy.orm import joinedload
    
    appointments = (Appointment.query
                   .options(joinedload(Appointment.patient))
                   .filter_by(doctor_id=doctor_id)
                   .order_by(Appointment.appointment_date.desc())
                   .all())
    
    return jsonify({
        'status': 'success',
        'data': [{
            'id': a.id,
            'patient_name': a.patient.name,
            'patient_phone': a.patient.phone,
            'appointment_date': a.appointment_date.isoformat(),
            'appointment_time': a.appointment_time,
            'status': a.status,
            'reason': a.reason,
            'symptoms': a.symptoms,
            'confirmation_number': a.confirmation_number
        } for a in appointments]
    })

# ==================== APPOINTMENT ENDPOINTS ====================

@app.route('/api/booking/initiate', methods=['POST'])
def initiate_booking_call():
    """Initiate a booking call from the frontend"""
    try:
        data = request.json
        phone = data.get('phone_number')
        doctor_info = data.get('doctor_info')
        
        if not phone:
            return jsonify({'status': 'error', 'message': 'Phone number required'}), 400

        # Fetch active doctors for the roster
        active_doctors = Doctor.query.filter_by(is_available=True).all()
        roster = []
        for doc in active_doctors:
            roster.append({
                'name': doc.name,
                'specialty': doc.specialty,
                'slots': doc.available_time or '9am-5pm'
            })

        response = agent.create_booking_call(phone, doctor_info, roster)
        return jsonify(response)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/appointment/book', methods=['POST'])
def book_appointment():
    """Book an appointment with voice call"""
    try:
        data = request.json
        phone = data.get('patient_phone') or data.get('phone_number')
        
        if not phone:
            return jsonify({'error': 'Phone number required'}), 400
        
        # Get or create patient
        patient = Patient.query.filter_by(phone=phone).first()
        if not patient:
            patient = Patient(
                name=data.get('patient_name', 'Unknown'),
                phone=phone
            )
            db.session.add(patient)
            db.session.flush()
        
        # Get doctor (optional - if not provided, pick first available)
        doctor_id = data.get('doctor_id')
        if doctor_id:
            doctor = db.session.get(Doctor, doctor_id)
        else:
            doctor = Doctor.query.first()
            
        if not doctor:
            # Create dummy doctor if none exists
            doctor = Doctor(name="Dr. Sharma", specialty="General Medicine", phone="0000000000")
            db.session.add(doctor)
            db.session.flush()
        
        # Create appointment
        confirmation_num = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Parse date and time (with defaults)
        appointment_date = data.get('appointment_date') or data.get('date') or datetime.now().strftime('%Y-%m-%d')
        appointment_time = data.get('appointment_time') or data.get('time') or '10:00 AM'
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=datetime.strptime(appointment_date, '%Y-%m-%d').date(),
            appointment_time=appointment_time,
            reason=data.get('reason'),
            symptoms=data.get('symptoms'),
            special_notes=data.get('special_notes'),
            confirmation_number=confirmation_num,
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Initiate voice call
        doctor_info = {
            'name': doctor.name,
            'specialty': doctor.specialty,
            'clinic': doctor.clinic_name,
            'date': appointment_date,
            'time': appointment_time
        }
        
        # Fetch active doctors for the roster
        active_doctors = Doctor.query.filter_by(is_available=True).all()
        roster = []
        for doc in active_doctors:
            roster.append({
                'name': doc.name,
                'specialty': doc.specialty,
                'slots': doc.available_time or '9am-5pm'
            })

        call_response = agent.create_booking_call(phone, doctor_info, roster)
        
        # Log the call
        if call_response.get('status') == 'success':
            call_log = CallLog(
                call_id=str(call_response['data'].get('id')),
                phone_number=phone,
                appointment_id=appointment.id,
                status='in_progress'
            )
            db.session.add(call_log)
            
            appointment.call_id = str(call_response['data'].get('id'))
            appointment.call_status = 'initiated'
            
            db.session.commit()
            
            # Send SMS confirmation (simulated - implement with Twilio/SMS gateway)
            send_sms_confirmation(patient.phone, {
                'patient_name': patient.name,
                'doctor_name': doctor.name,
                'specialty': doctor.specialty,
                'date': appointment_date,
                'time': appointment_time,
                'confirmation': confirmation_num
            })
        
        return jsonify({
            'appointment_id': appointment.id,
            'confirmation_number': confirmation_num,
            'call_id': call_response['data'].get('id') if call_response.get('status') == 'success' else None,
            'call_status': call_response.get('status'),
            'message': 'Appointment booked and call initiated'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error booking appointment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointment/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    """Get appointment details"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': appointment.id,
            'patient': {
                'id': appointment.patient.id,
                'name': appointment.patient.name,
                'phone': appointment.patient.phone
            },
            'doctor': {
                'id': appointment.doctor.id,
                'name': appointment.doctor.name,
                'specialty': appointment.doctor.specialty,
                'clinic': appointment.doctor.clinic_name
            },
            'appointment_date': appointment.appointment_date.isoformat(),
            'appointment_time': appointment.appointment_time,
            'status': appointment.status,
            'reason': appointment.reason,
            'symptoms': appointment.symptoms,
            'special_notes': appointment.special_notes,
            'confirmation_number': appointment.confirmation_number,
            'call_id': appointment.call_id,
            'call_status': appointment.call_status,
            'call_recording_url': appointment.call_recording_url
        }
    })

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """Get all appointments with filters"""
    status = request.args.get('status')
    date_str = request.args.get('date')
    
    query = Appointment.query
    
    if status:
        query = query.filter_by(status=status)
    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        query = query.filter_by(appointment_date=target_date)
    
    appointments = query.order_by(Appointment.appointment_date.desc()).all()
    
    return jsonify({
        'status': 'success',
        'data': [{
            'id': a.id,
            'patient_name': a.patient.name,
            'doctor_name': a.doctor.name,
            'date': a.appointment_date.isoformat(),
            'time': a.appointment_time,
            'status': a.status,
            'confirmation_number': a.confirmation_number
        } for a in appointments]
    })

@app.route('/api/appointment/<int:appointment_id>/cancel', methods=['POST'])
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'cancelled'
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'data': {'message': 'Appointment cancelled successfully'}
    })

# ==================== CALL MANAGEMENT ====================

@app.route('/api/calls', methods=['GET'])
def get_calls():
    """Get all call logs"""
    calls = CallLog.query.order_by(CallLog.created_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'data': [{
            'id': c.id,
            'call_id': c.call_id,
            'phone_number': c.phone_number,
            'status': c.status,
            'duration': c.duration,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in calls]
    })

# ==================== DASHBOARD STATS ====================

@app.route('/api/stats/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_appointments = Appointment.query.count()
    
    today = date.today()
    today_appointments = Appointment.query.filter_by(appointment_date=today).count()
    
    pending_appointments = Appointment.query.filter_by(status='scheduled').count()
    completed_appointments = Appointment.query.filter_by(status='completed').count()
    
    return jsonify({
        'status': 'success',
        'data': {
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_appointments': total_appointments,
            'today_appointments': today_appointments,
            'pending_appointments': pending_appointments,
            'completed_appointments': completed_appointments
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'service': 'Hospital Management System'}), 200

# ==================== DOCTOR AUTHENTICATION ====================

@app.route('/api/doctor/login', methods=['POST'])
def doctor_login():
    """Doctor login"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        doctor = Doctor.query.filter_by(email=email).first()
        
        if not doctor or not doctor.password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if check_password_hash(doctor.password, password):
            session['doctor_id'] = doctor.id
            return jsonify({
                'success': True,
                'doctor': {
                    'id': doctor.id,
                    'name': doctor.name,
                    'email': doctor.email,
                    'specialty': doctor.specialty,
                    'clinic_name': doctor.clinic_name
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/doctor/set-password', methods=['POST'])
def set_doctor_password():
    """Set doctor password (for initial setup)"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        doctor = Doctor.query.filter_by(email=email).first()
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        doctor.password = generate_password_hash(password)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Password set successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== DOCTOR AVAILABILITY MANAGEMENT ====================

@app.route('/api/doctor/<int:doctor_id>/availability', methods=['GET'])
def get_doctor_availability(doctor_id):
    """Get doctor's availability slots"""
    try:
        start_date = request.args.get('start_date', date.today().isoformat())
        end_date = request.args.get('end_date', (date.today() + timedelta(days=7)).isoformat())
        
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        slots = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date >= start,
            DoctorAvailability.date <= end
        ).all()
        
        return jsonify({
            'success': True,
            'slots': [{
                'id': slot.id,
                'date': slot.date.isoformat(),
                'time_slot': slot.time_slot,
                'is_booked': slot.is_booked,
                'max_patients': slot.max_patients
            } for slot in slots]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/doctor/<int:doctor_id>/availability', methods=['POST'])
def add_doctor_availability(doctor_id):
    """Add availability slots for doctor"""
    try:
        data = request.json
        date_str = data.get('date')
        time_slots = data.get('time_slots', [])  # List of time slots
        
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        added_slots = []
        for time_slot in time_slots:
            # Check if slot already exists
            existing = DoctorAvailability.query.filter_by(
                doctor_id=doctor_id,
                date=appointment_date,
                time_slot=time_slot
            ).first()
            
            if not existing:
                slot = DoctorAvailability(
                    doctor_id=doctor_id,
                    date=appointment_date,
                    time_slot=time_slot,
                    max_patients=data.get('max_patients', 1)
                )
                db.session.add(slot)
                added_slots.append(time_slot)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Added {len(added_slots)} availability slots',
            'slots_added': added_slots
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/doctor/<int:doctor_id>/availability/<int:slot_id>', methods=['DELETE'])
def delete_availability_slot(doctor_id, slot_id):
    """Delete an availability slot"""
    try:
        slot = DoctorAvailability.query.filter_by(id=slot_id, doctor_id=doctor_id).first()
        if not slot:
            return jsonify({'error': 'Slot not found'}), 404
        
        if slot.is_booked:
            return jsonify({'error': 'Cannot delete booked slot'}), 400
        
        db.session.delete(slot)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Slot deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/doctor/<int:doctor_id>/toggle-availability', methods=['POST'])
def toggle_doctor_availability(doctor_id):
    """Toggle doctor's overall availability status"""
    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        doctor.is_available = not doctor.is_available
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_available': doctor.is_available,
            'message': f'Doctor is now {"available" if doctor.is_available else "unavailable"}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== GET AVAILABLE DOCTORS FOR BOOKING ====================

@app.route('/api/doctors/available', methods=['GET'])
def get_available_doctors():
    """Get currently available doctors with their next available slots"""
    try:
        specialty = request.args.get('specialty')
        date_str = request.args.get('date', date.today().isoformat())
        
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        query = Doctor.query.filter_by(is_available=True)
        if specialty:
            query = query.filter_by(specialty=specialty)
        
        doctors = query.all()
        
        result = []
        for doctor in doctors:
            # Get available slots for this doctor
            available_slots = DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor.id,
                DoctorAvailability.date >= query_date,
                DoctorAvailability.is_booked == False
            ).order_by(DoctorAvailability.date, DoctorAvailability.time_slot).limit(5).all()
            
            result.append({
                'id': doctor.id,
                'name': doctor.name,
                'specialty': doctor.specialty,
                'clinic_name': doctor.clinic_name,
                'consultation_fee': doctor.consultation_fee,
                'available_slots': [{
                    'date': slot.date.isoformat(),
                    'time': slot.time_slot
                } for slot in available_slots]
            })
        
        return jsonify({
            'success': True,
            'doctors': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== CALL RESULT SYNC ====================

@app.route('/api/call/sync/<call_id>', methods=['POST'])
def sync_call_results(call_id):
    """Sync call evaluation results with database"""
    try:
        # Get call details from Dinodial
        call_detail = agent.get_booking_status(int(call_id))
        
        if call_detail.get('status') != 'success':
            return jsonify({'error': 'Failed to fetch call details'}), 400
        
        call_data = call_detail['data']
        
        # Extract evaluation result from nested structure if necessary
        evaluation_result = call_data.get('evaluation_result', {})
        if not evaluation_result and 'call_details' in call_data:
            # Try to find it in callOutcomesData
            evaluation_result = call_data['call_details'].get('callOutcomesData', {})
            
        phone_number = call_data.get('phone_number', 'Unknown')
        
        # 1. Find or Create Patient
        patient = Patient.query.filter_by(phone=phone_number).first()
        if not patient:
            # Try to get name from evaluation, else use "Unknown"
            patient_name = evaluation_result.get('name', 'New Patient')
            patient = Patient(name=patient_name, phone=phone_number)
            db.session.add(patient)
            db.session.flush() # Get ID
            
        # Update patient name if we have a better one now
        if evaluation_result.get('name') and evaluation_result['name'] != 'Unknown':
            patient.name = evaluation_result['name']

        # 2. Find or Create CallLog
        call_log = CallLog.query.filter_by(call_id=str(call_id)).first()
        if not call_log:
            call_log = CallLog(
                call_id=str(call_id),
                phone_number=phone_number,
                status=call_data.get('status', 'completed'),
                duration=call_data.get('duration', 0),
                recording_url=call_data.get('recording_url'),
                evaluation_result=evaluation_result
            )
            db.session.add(call_log)
        else:
            call_log.status = call_data.get('status', 'completed')
            call_log.duration = call_data.get('duration')
            call_log.evaluation_result = evaluation_result
            if call_data.get('recording_url'):
                call_log.recording_url = call_data.get('recording_url')

        # 3. Find or Create Appointment
        # If call_log already had an appointment, use it. Otherwise create new.
        appointment = None
        if call_log.appointment_id:
            appointment = db.session.get(Appointment, call_log.appointment_id)
        
        if not appointment:
            # Default doctor (first available or specific one)
            doctor = Doctor.query.first()
            if not doctor:
                # Create a dummy doctor if none exists
                doctor = Doctor(name="Dr. Sharma", specialty="General Medicine", phone="0000000000")
                db.session.add(doctor)
                db.session.flush()
            
            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_date=date.today() + timedelta(days=1), # Default tomorrow
                appointment_time="10:00 AM", # Default time
                call_id=str(call_id),
                status='pending'
            )
            db.session.add(appointment)
            db.session.flush()
            call_log.appointment_id = appointment.id

        # 4. Update Appointment from Evaluation
        if evaluation_result.get('symptoms'):
            appointment.symptoms = evaluation_result['symptoms']
        
        if evaluation_result.get('specialty'):
            specialty = evaluation_result['specialty']
            # Try to find a doctor with matching specialty
            matching_doctor = Doctor.query.filter(Doctor.specialty.ilike(f"%{specialty}%")).first()
            if matching_doctor:
                appointment.doctor_id = matching_doctor.id
        
        if evaluation_result.get('time'):
            appointment.appointment_time = evaluation_result['time']
            
        if evaluation_result.get('booked') == True:
            appointment.status = 'confirmed'
            appointment.call_status = 'completed'
            
            # Generate confirmation number if not exists
            if not appointment.confirmation_number:
                appointment.confirmation_number = f"APT-{appointment.id}-{secrets.token_hex(4).upper()}"

            # Send SMS Confirmation
            appointment_data = {
                'patient_name': patient.name,
                'doctor_name': appointment.doctor.name,
                'specialty': appointment.doctor.specialty,
                'date': str(appointment.appointment_date),
                'time': appointment.appointment_time,
                'confirmation': appointment.confirmation_number
            }
            send_sms_confirmation(patient.phone, appointment_data)
            send_whatsapp_confirmation(patient.phone, appointment_data)
            
            # Schedule Follow-up Calls (1 hour and 2 hours later)
            now = datetime.utcnow()
            follow_up_1 = FollowUpCall(
                appointment_id=appointment.id,
                scheduled_time=now + timedelta(hours=1),
                type='whatsapp',
                status='pending'
            )
            follow_up_2 = FollowUpCall(
                appointment_id=appointment.id,
                scheduled_time=now + timedelta(hours=2),
                type='call',
                status='pending'
            )
            db.session.add(follow_up_1)
            db.session.add(follow_up_2)

        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Call results synced successfully',
            'data': {
                'patient_name': patient.name,
                'doctor': appointment.doctor.name,
                'specialty': appointment.doctor.specialty,
                'symptoms': appointment.symptoms,
                'status': appointment.status
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/call-completed', methods=['POST'])
def call_completed_webhook():
    """Webhook endpoint for Dinodial to notify when call is completed"""
    try:
        data = request.json
        call_id = data.get('call_id')
        
        if not call_id:
            return jsonify({'error': 'call_id required'}), 400
        
        # Sync the results
        return sync_call_results(str(call_id))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

