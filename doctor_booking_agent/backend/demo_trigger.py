import sys
import os
from datetime import datetime, timedelta

# Add agent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agent')))

from hospital_api import app, db, Appointment, FollowUpCall, Patient, Doctor
from scheduler import process_followups

def trigger_demo_followups():
    """
    Creates immediate follow-up tasks for the most recent appointment
    and triggers the scheduler to process them.
    """
    print("--- Setting up Demo Follow-ups ---")
    
    with app.app_context():
        # 1. Get the latest appointment
        latest_appt = Appointment.query.order_by(Appointment.id.desc()).first()
        
        if not latest_appt:
            print("Error: No appointments found in the database. Please book an appointment first.")
            return

        patient = db.session.get(Patient, latest_appt.patient_id)
        doctor = db.session.get(Doctor, latest_appt.doctor_id)
        
        print(f"Targeting Appointment ID: {latest_appt.id}")
        print(f"Patient: {patient.name} ({patient.phone})")
        print(f"Doctor: {doctor.name}")
        
        # 2. Create immediate follow-ups (scheduled for NOW)
        now = datetime.utcnow()
        
        # WhatsApp Reminder (Immediate)
        wa_followup = FollowUpCall(
            appointment_id=latest_appt.id,
            scheduled_time=now, # Due immediately
            type='whatsapp',
            status='pending'
        )
        
        # Voice Call Reminder (Immediate + 5 seconds delay to ensure order)
        call_followup = FollowUpCall(
            appointment_id=latest_appt.id,
            scheduled_time=now, # Due immediately
            type='call',
            status='pending'
        )
        
        db.session.add(wa_followup)
        db.session.add(call_followup)
        db.session.commit()
        
        print("Created pending WhatsApp and Call tasks scheduled for NOW.")
        
        # 3. Trigger the processor
        print("\n--- Triggering Scheduler ---")
        process_followups()
        print("\n--- Demo Complete ---")

if __name__ == "__main__":
    trigger_demo_followups()
