import time
from datetime import datetime
import sys
import os

# Add agent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agent')))

from hospital_api import app, db, FollowUpCall, Appointment, Patient, Doctor, send_whatsapp_reminder, agent
from sqlalchemy import text

def ensure_schema():
    """Ensure the type column exists in the database"""
    with app.app_context():
        try:
            # Try to query the column to see if it exists
            db.session.execute(text("SELECT type FROM follow_up_calls LIMIT 1"))
            print("Schema check: 'type' column exists.")
        except Exception:
            print("Schema check: 'type' column missing. Adding it...")
            try:
                # Add the column
                db.session.execute(text("ALTER TABLE follow_up_calls ADD COLUMN type VARCHAR(20) DEFAULT 'call'"))
                db.session.commit()
                print("Schema updated successfully.")
            except Exception as e:
                print(f"Error updating schema: {e}")

def process_followups():
    """Check for pending follow-ups and execute them"""
    with app.app_context():
        now = datetime.utcnow()
        # Find pending calls that are due
        pending = FollowUpCall.query.filter(
            FollowUpCall.status == 'pending',
            FollowUpCall.scheduled_time <= now
        ).all()
        
        if pending:
            print(f"[{now}] Found {len(pending)} pending follow-ups.")
        
        for call in pending:
            try:
                appt = db.session.get(Appointment, call.appointment_id)
                if not appt:
                    print(f"Appointment {call.appointment_id} not found. Marking failed.")
                    call.status = 'failed'
                    db.session.commit()
                    continue
                
                patient = db.session.get(Patient, appt.patient_id)
                doctor = db.session.get(Doctor, appt.doctor_id)
                
                data = {
                    'patient_name': patient.name,
                    'doctor_name': doctor.name,
                    'specialty': doctor.specialty,
                    'date': str(appt.appointment_date),
                    'time': appt.appointment_time
                }
                
                # Determine action based on type
                call_type = getattr(call, 'type', 'call') # Default to call if attribute missing
                
                if call_type == 'whatsapp':
                    print(f"Processing WhatsApp Reminder for {patient.name}...")
                    success = send_whatsapp_reminder(patient.phone, data)
                    if success:
                        call.status = 'completed'
                    else:
                        call.status = 'failed'
                    
                elif call_type == 'call':
                    print(f"Processing Voice Call Reminder for {patient.name}...")
                    # Use the new create_reminder_call method
                    response = agent.create_reminder_call(
                        phone_number=patient.phone,
                        patient_name=patient.name,
                        doctor_name=doctor.name,
                        date=str(appt.appointment_date),
                        time=appt.appointment_time
                    )
                    print(f"Call initiated: {response}")
                    
                    # Check for rate limit error
                    if isinstance(response, dict) and 'error' in response and 'Rate limit' in response['error']:
                        print("Rate limit hit. Will retry later.")
                        # Do not mark as completed, so it gets picked up again
                        # But we should probably back off for this loop
                        time.sleep(65) # Wait a bit more than a minute
                    else:
                        call.status = 'completed'
                
                else:
                    print(f"Unknown follow-up type: {call_type}")
                    call.status = 'failed'
                    
                db.session.commit()
                
            except Exception as e:
                print(f"Error processing follow-up {call.id}: {e}")
                call.status = 'failed'
                db.session.commit()

if __name__ == "__main__":
    print("Starting Follow-up Scheduler...")
    ensure_schema()
    print("Scheduler running. Press Ctrl+C to stop.")
    while True:
        try:
            process_followups()
        except Exception as e:
            print(f"Scheduler loop error: {e}")
        
        # Sleep for 60 seconds
        time.sleep(60)
