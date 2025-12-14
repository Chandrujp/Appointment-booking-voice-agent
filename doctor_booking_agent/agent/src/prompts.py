"""
Prompt templates for Doctor Booking Agent
"""
from typing import Dict, Any, Optional
import os
import json

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

def get_booking_prompt(phone_number: str, doctor_info: Optional[Dict[str, Any]] = None, roster: Optional[list] = None) -> str:
    """Generate prompt from XML template"""
    
    # Check if a specific doctor is requested (from UI click)
    # Only consider it a target if a name is provided and it's not a generic placeholder
    name = doctor_info.get('name') if doctor_info else None
    has_target = name and name not in ['the duty doctor', 'Dr.Sharma', 'Available Doctor']
    
    target_block = ""
    if has_target:
        target_block = (
            f"    <target_doctor>\n"
            f"      <name>{name}</name>\n"
            f"      <spec>{doctor_info.get('specialty')}</spec>\n"
            f"      <time>{doctor_info.get('time')}</time>\n"
            f"      <date>{doctor_info.get('date', 'tomorrow')}</date>\n"
            f"    </target_doctor>\n"
        )

    # Generate Roster XML
    roster_xml = ""
    if roster:
        roster_xml = "    <hospital_roster>\n"
        for doc in roster:
            # Ensure slots exist, default to 9am-5pm if missing
            slots = doc.get('slots') or doc.get('available_time') or '9am-5pm'
            roster_xml += f"      <doc><name>{doc['name']}</name><spec>{doc['specialty']}</spec><slots>{slots}</slots></doc>\n"
        roster_xml += "    </hospital_roster>\n"
    else:
        # Fallback to hardcoded roster if none provided
        roster_xml = (
            f"    <hospital_roster>\n"
            f"      <doc><name>Dr. Sharma</name><spec>General Medicine</spec><slots>10am-2pm</slots></doc>\n"
            f"      <doc><name>Dr. Anita</name><spec>Cardiology</spec><slots>4pm-6pm</slots></doc>\n"
            f"      <doc><name>Dr. Raj</name><spec>Dermatology</spec><slots>11am-1pm</slots></doc>\n"
            f"      <doc><name>Dr. Priya</name><spec>Orthopedics</spec><slots>2pm-5pm</slots></doc>\n"
            f"      <doc><name>Dr. Khan</name><spec>Pediatrics</spec><slots>9am-12pm</slots></doc>\n"
            f"    </hospital_roster>\n"
        )

    # Read template
    template_path = os.path.join(TEMPLATES_DIR, 'prompt.txt')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Fill template
        return template_content.format(
            phone_number=phone_number,
            target_block=target_block,
            roster_xml=roster_xml
        )
    except Exception as e:
        print(f"Error reading template: {e}")
        # Fallback to a minimal prompt if file read fails
        return f"<ai_master_prompt><critical_directive>System Error. Please try again.</critical_directive></ai_master_prompt>"

def get_reminder_prompt(patient_name: str, doctor_name: str, date: str, time: str) -> str:
    """Generate reminder prompt"""
    template_path = os.path.join(TEMPLATES_DIR, 'reminder_prompt.txt')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read().format(
                patient_name=patient_name,
                doctor_name=doctor_name,
                date=date,
                time=time
            )
    except Exception as e:
        return "System Error"

def get_evaluation_tool() -> Dict[str, Any]:
    """Load evaluation tool from JSON"""
    tool_path = os.path.join(TEMPLATES_DIR, 'evaluationTool.json')
    try:
        with open(tool_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading tool definition: {e}")
        return {}
