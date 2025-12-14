import React, { useState } from 'react';
import Head from 'next/head';

export default function Home() {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [doctorName, setDoctorName] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [loading, setLoading] = useState(false);
  const [callId, setCallId] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${backendUrl}/api/booking/initiate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: phoneNumber,
          doctor_info: {
            name: doctorName,
            specialty: specialty
          }
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        setCallId(data.data.id);
        setPhoneNumber('');
        setDoctorName('');
        setSpecialty('');
      } else {
        setError(data.data?.message || 'Failed to initiate call');
      }
    } catch (err) {
      setError('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Head>
        <title>HealthCare | Book Appointment</title>
      </Head>

      {/* Header */}
      <header style={{ background: 'rgba(255, 255, 255, 0.8)', backdropFilter: 'blur(10px)', borderBottom: '1px solid var(--border)', padding: '1rem 0', position: 'sticky', top: 0, zIndex: 10 }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span></span> HealthCare AI
          </div>
          <a href="/doctor-login" className="btn" style={{ color: 'var(--text-main)', background: 'white', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}>
            Doctor Login
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="container" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem' }}>
        <div className="card animate-fade-in" style={{ width: '100%', maxWidth: '480px', borderTop: '4px solid var(--primary)' }}>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem', textAlign: 'center', fontWeight: '700' }}>Book an Appointment</h1>
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: '2rem', fontSize: '0.95rem' }}>
            Enter your details and our AI Voice Agent will call you instantly to confirm your booking.
          </p>

          {error && (
            <div className="animate-fade-in" style={{ background: '#fee2e2', color: '#991b1b', padding: '1rem', borderRadius: '10px', marginBottom: '1.5rem', border: '1px solid #fecaca' }}>
              ⚠️ {error}
            </div>
          )}

          {callId && (
            <div className="animate-fade-in" style={{ background: '#dcfce7', color: '#166534', padding: '1rem', borderRadius: '10px', marginBottom: '1.5rem', border: '1px solid #bbf7d0' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>✅ Call Initiated!</div>
              <div style={{ fontSize: '0.9rem' }}>Please pick up the call from our AI agent to complete your booking.</div>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label className="input-label">Phone Number</label>
              <input
                type="tel"
                className="input-field"
                placeholder="+91 98765 43210"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label">Preferred Doctor (Optional)</label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g. Dr. Sharma"
                value={doctorName}
                onChange={(e) => setDoctorName(e.target.value)}
              />
            </div>

            <div className="input-group">
              <label className="input-label">Specialty (Optional)</label>
              <select 
                className="input-field"
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
                style={{ cursor: 'pointer' }}
              >
                <option value="">Any Specialty</option>
                <option value="General Medicine">General Medicine</option>
                <option value="Cardiology">Cardiology</option>
                <option value="Dermatology">Dermatology</option>
                <option value="Orthopedics">Orthopedics</option>
                <option value="Pediatrics">Pediatrics</option>
              </select>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              style={{ width: '100%', marginTop: '1rem', padding: '1rem' }}
              disabled={loading}
            >
              {loading ? 'Connecting...' : '📞 Call Me to Book'}
            </button>
          </form>
        </div>
      </main>

      {/* Footer */}
      <footer style={{ background: 'white', borderTop: '1px solid var(--border)', padding: '2rem 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
        <div className="container">
          &copy; 2025 HealthCare AI Booking System. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
