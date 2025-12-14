"""
Dinodial Proxy API Client for Doctor Booking Agent
"""
import requests
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class DinodialClient:
    """Client for interacting with Dinodial Proxy API"""
    
    def __init__(self):
        self.base_url = os.getenv('DINODIAL_BASE_URL', 'https://api-dinodial-proxy.cyces.co')
        self.admin_token = os.getenv('ADMIN_TOKEN')
        self.token = os.getenv('TOKEN')
        # Auto-generate a token if not present but admin creds and phone are available
        if not self.token and self.admin_token:
            phone = os.getenv('PHONE_NUMBER')
            if phone:
                try:
                    gen = self.generate_token(phone)
                    # Expecting response like {status: 'success', data: {token: '...'}}
                    self.token = (gen.get('data') or {}).get('token') or self.token
                except Exception:
                    # Leave token as-is; upstream will surface error
                    pass
    
    def _get_headers(self, use_admin: bool = False) -> Dict[str, str]:
        """Get authorization headers"""
        token = self.admin_token if use_admin else self.token
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def generate_token(self, phone_number: str) -> Dict[str, Any]:
        """Generate a token for a phone number (admin only)"""
        endpoint = f'{self.base_url}/api/proxy/token/generate/'
        payload = {'phone_number': phone_number}
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=self._get_headers(use_admin=True)
        )
        return response.json()
    
    def initiate_call(self, prompt: str, evaluation_tool: Dict[str, Any], 
                     vad_engine: str = 'CAWL') -> Dict[str, Any]:
        """Initiate a call with the given prompt and evaluation tool"""
        endpoint = f'{self.base_url}/api/proxy/make-call/'
        payload = {
            'prompt': prompt,
            'evaluation_tool': evaluation_tool,
            'vad_engine': vad_engine
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=self._get_headers(use_admin=False)
        )
        result = response.json()
        
        # Check for token error and retry
        if response.status_code in [400, 401] and 'Token is not valid' in str(result):
            print("Token invalid, attempting to refresh...")
            phone = os.getenv('PHONE_NUMBER')
            if phone and self.admin_token:
                try:
                    print(f"Generating new token for {phone} using admin token...")
                    gen = self.generate_token(phone)
                    print(f"Generate token response: {gen}")
                    new_token = (gen.get('data') or {}).get('token')
                    if new_token:
                        print(f"New token obtained: {new_token[:10]}...")
                        self.token = new_token
                        # Retry the call
                        response = requests.post(
                            endpoint,
                            json=payload,
                            headers=self._get_headers(use_admin=False)
                        )
                        return response.json()
                    else:
                        print("Failed to extract token from generation response")
                except Exception as e:
                    print(f"Failed to refresh token: {e}")
        
        return result
    
    def get_call_list(self) -> Dict[str, Any]:
        """Get list of calls for the token"""
        endpoint = f'{self.base_url}/api/proxy/calls/list/'
        
        response = requests.get(
            endpoint,
            headers=self._get_headers(use_admin=False)
        )
        return response.json()
    
    def get_call_detail(self, call_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific call"""
        endpoint = f'{self.base_url}/api/proxy/call/detail/{call_id}/'
        
        response = requests.get(
            endpoint,
            headers=self._get_headers(use_admin=False)
        )
        return response.json()
    
    def get_call_recording(self, call_id: int) -> Dict[str, Any]:
        """Get recording URL for a call"""
        endpoint = f'{self.base_url}/api/proxy/call/recording/{call_id}/'
        
        response = requests.get(
            endpoint,
            headers=self._get_headers(use_admin=False)
        )
        return response.json()
