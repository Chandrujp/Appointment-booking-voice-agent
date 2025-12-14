"""
Doctor Appointment Booking Voice AI Agent
Direct Dinodial Proxy Integration - No External Dependencies
"""
from typing import Dict, Any, Optional
from src.dinodial_client import DinodialClient
from src.prompts import get_booking_prompt, get_evaluation_tool, get_reminder_prompt

class DoctorBookingAgent:
    """Voice AI agent for doctor appointment booking"""
    
    def __init__(self):
        self.client = DinodialClient()
    
    def create_reminder_call(self, phone_number: str, patient_name: str, doctor_name: str, date: str, time: str) -> Dict[str, Any]:
        """Initiate a reminder call"""
        prompt = get_reminder_prompt(patient_name, doctor_name, date, time)
        # Use a simple evaluation tool or None for reminders
        # For now, we reuse the tool but maybe we don't need to extract much
        return self.client.initiate_call(
            prompt=prompt,
            evaluation_tool=get_evaluation_tool(), # Reuse for now
            vad_engine='CAWL'
        )

    def create_booking_call(self, phone_number: str, doctor_info: Dict[str, Any] = None, roster: list = None) -> Dict[str, Any]:
        """
        Initiate a voice call for doctor appointment booking
        
        Args:
            phone_number: Patient phone number
            doctor_info: Optional doctor information to include in context
            roster: Optional list of available doctors
        
        Returns:
            Response from Dinodial API
        """
        # Get the appointment booking prompt
        prompt = get_booking_prompt(phone_number, doctor_info, roster)
        
        # Get evaluation tool configuration
        evaluation_tool = get_evaluation_tool()
        
        # Initiate the call
        response = self.client.initiate_call(
            prompt=prompt,
            evaluation_tool=evaluation_tool,
            vad_engine='CAWL'
        )
        
        return response
    
    def get_booking_status(self, call_id: int) -> Dict[str, Any]:
        """Get the status and details of a booking call"""
        return self.client.get_call_detail(call_id)
    
    def get_call_recording(self, call_id: int) -> Dict[str, Any]:
        """Get the recording of a booking call"""
        return self.client.get_call_recording(call_id)
    
    def list_calls(self) -> Dict[str, Any]:
        """List all booking calls"""
        return self.client.get_call_list()
