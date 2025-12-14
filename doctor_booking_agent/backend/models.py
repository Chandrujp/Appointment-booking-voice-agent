"""
Database Models for Hospital Booking Management System
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Doctor(db.Model):
    """Doctor model"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))  # For doctor login
    clinic_name = db.Column(db.String(200))
    available_days = db.Column(db.String(200))  # JSON string
    available_time = db.Column(db.String(100))
    consultation_fee = db.Column(db.Float, default=0.0)
    is_available = db.Column(db.Boolean, default=True)  # Current availability status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    availability_slots = db.relationship('DoctorAvailability', backref='doctor', lazy=True)

class Patient(db.Model):
    """Patient model"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Appointment(db.Model):
    """Appointment model"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(20), nullable=False)
    
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled, no_show
    
    # Call details
    call_id = db.Column(db.String(100))
    call_status = db.Column(db.String(50))
    call_recording_url = db.Column(db.String(500))
    
    # Booking details
    reason = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    special_notes = db.Column(db.Text)
    confirmation_number = db.Column(db.String(50), unique=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CallLog(db.Model):
    """Call log model for tracking all voice calls"""
    __tablename__ = 'call_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    call_id = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(20), nullable=False)
    
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    
    status = db.Column(db.String(50))  # not_started, in_progress, completed, failed
    duration = db.Column(db.Integer)  # in seconds
    
    # Call metadata
    prompt_used = db.Column(db.Text)
    evaluation_result = db.Column(db.JSON)
    recording_url = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class DoctorAvailability(db.Model):
    """Doctor availability slots"""
    __tablename__ = 'doctor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)  # e.g., "10:00 AM"
    is_booked = db.Column(db.Boolean, default=False)
    max_patients = db.Column(db.Integer, default=1)  # Patients per slot
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FollowUpCall(db.Model):
    """Model to schedule follow-up calls"""
    __tablename__ = 'follow_up_calls'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(20), default='call') # call, whatsapp
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
