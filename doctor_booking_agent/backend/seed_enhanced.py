"""
Enhanced seed script with passwords and availability slots
"""
from hospital_api import app, db
from models import Doctor, Patient, DoctorAvailability
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

with app.app_context():
    # Clear existing data
    DoctorAvailability.query.delete()
    Doctor.query.delete()
    Patient.query.delete()
    db.session.commit()
    
    print("🗑️  Cleared existing data")
    
    # Create doctors with passwords
    doctors_data = [
        {
            'name': 'Dr. Raj Kumar',
            'specialty': 'General Medicine',
            'phone': '+919876543210',
            'email': 'rajkumar@hospital.com',
            'password': 'password123',
            'clinic_name': 'City General Hospital',
            'available_days': 'Monday,Tuesday,Wednesday,Thursday,Friday',
            'available_time': '9:00 AM - 5:00 PM',
            'consultation_fee': 500.0,
            'is_available': True
        },
        {
            'name': 'Dr. Priya Sharma',
            'specialty': 'Pediatrics',
            'phone': '+919876543211',
            'email': 'priya@hospital.com',
            'password': 'password123',
            'clinic_name': 'Children Health Center',
            'available_days': 'Monday,Wednesday,Friday',
            'available_time': '10:00 AM - 4:00 PM',
            'consultation_fee': 600.0,
            'is_available': True
        },
        {
            'name': 'Dr. Arun Nair',
            'specialty': 'Cardiology',
            'phone': '+919876543212',
            'email': 'arun@hospital.com',
            'password': 'password123',
            'clinic_name': 'Heart Care Clinic',
            'available_days': 'Tuesday,Thursday,Saturday',
            'available_time': '9:00 AM - 3:00 PM',
            'consultation_fee': 1000.0,
            'is_available': True
        },
        {
            'name': 'Dr. Sujit Reddy',
            'specialty': 'Dermatology',
            'phone': '+919876543213',
            'email': 'sujit@hospital.com',
            'password': 'password123',
            'clinic_name': 'Skin & Hair Clinic',
            'available_days': 'Monday,Tuesday,Thursday,Friday',
            'available_time': '11:00 AM - 6:00 PM',
            'consultation_fee': 700.0,
            'is_available': True
        },
        {
            'name': 'Dr. Meera Patel',
            'specialty': 'Orthopedics',
            'phone': '+919876543214',
            'email': 'meera@hospital.com',
            'password': 'password123',
            'clinic_name': 'Bone & Joint Care',
            'available_days': 'Wednesday,Thursday,Friday,Saturday',
            'available_time': '10:00 AM - 5:00 PM',
            'consultation_fee': 800.0,
            'is_available': True
        }
    ]
    
    created_doctors = []
    for doc_data in doctors_data:
        doctor = Doctor(
            name=doc_data['name'],
            specialty=doc_data['specialty'],
            phone=doc_data['phone'],
            email=doc_data['email'],
            password=generate_password_hash(doc_data['password']),
            clinic_name=doc_data['clinic_name'],
            available_days=doc_data['available_days'],
            available_time=doc_data['available_time'],
            consultation_fee=doc_data['consultation_fee'],
            is_available=doc_data['is_available']
        )
        db.session.add(doctor)
        created_doctors.append(doctor)
    
    db.session.commit()
    print(f"✅ Created {len(created_doctors)} doctors with login credentials")
    
    # Create availability slots for next 7 days
    today = date.today()
    time_slots = ['9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM']
    
    slot_count = 0
    for doctor in created_doctors:
        for day_offset in range(7):  # Next 7 days
            slot_date = today + timedelta(days=day_offset)
            for time_slot in time_slots:
                availability = DoctorAvailability(
                    doctor_id=doctor.id,
                    date=slot_date,
                    time_slot=time_slot,
                    is_booked=False,
                    max_patients=1
                )
                db.session.add(availability)
                slot_count += 1
    
    db.session.commit()
    print(f"✅ Created {slot_count} availability slots for next 7 days")
    
    # Create sample patients
    patients_data = [
        {
            'name': 'Rahul Verma',
            'phone': '+918098444187',
            'email': 'rahul@example.com',
            'age': 35,
            'gender': 'Male',
            'address': '123, MG Road, Bangalore'
        },
        {
            'name': 'Anjali Mehta',
            'phone': '+919988776655',
            'email': 'anjali@example.com',
            'age': 28,
            'gender': 'Female',
            'address': '45, Park Street, Mumbai'
        },
        {
            'name': 'Vikram Singh',
            'phone': '+919876543210',
            'email': 'vikram@example.com',
            'age': 42,
            'gender': 'Male',
            'address': '78, Khan Market, Delhi'
        }
    ]
    
    for patient_data in patients_data:
        patient = Patient(**patient_data)
        db.session.add(patient)
    
    db.session.commit()
    print(f"✅ Created {len(patients_data)} sample patients")
    
    print("\n" + "="*60)
    print("🎉 Database seeded successfully!")
    print("="*60)
    print("\n📋 Doctor Login Credentials:")
    print("-" * 60)
    for doctor in created_doctors:
        print(f"  Email: {doctor.email}")
        print(f"  Password: password123")
        print(f"  Name: {doctor.name} ({doctor.specialty})")
        print("-" * 60)
    print("\n🔗 Access the system:")
    print("  • Patient Booking: http://localhost:3000")
    print("  • Doctor Login: http://localhost:3000/doctor-login")
    print("  • Admin Panel: http://localhost:3000/admin")
    print("\n")
