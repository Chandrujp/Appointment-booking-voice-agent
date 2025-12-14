import React, { useState, useEffect } from 'react';
import Head from 'next/head';

export default function DoctorDashboard() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [doctor, setDoctor] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  // Check login status on mount
  useEffect(() => {
    const savedDoctor = localStorage.getItem('doctor');
    if (savedDoctor) {
      const doctorData = JSON.parse(savedDoctor);
      setDoctor(doctorData);
      setIsLoggedIn(true);
      fetchAppointments(doctorData.id);
    }
  }, []);

  // Auto-refresh appointments every 5 seconds
  useEffect(() => {
    if (isLoggedIn && doctor) {
      const interval = setInterval(() => {
        fetchAppointments(doctor.id);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [isLoggedIn, doctor]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/doctor/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setDoctor(data.doctor);
        setIsLoggedIn(true);
        localStorage.setItem('doctor', JSON.stringify(data.doctor));
        fetchAppointments(data.doctor.id);
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Connection error');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('doctor');
    setIsLoggedIn(false);
    setDoctor(null);
  };

  const fetchAppointments = async (doctorId) => {
    try {
      const response = await fetch(`${API_URL}/api/doctor/${doctorId}/appointments`);
      const data = await response.json();
      if (data.status === 'success') {
        setAppointments(data.data);
      }
    } catch (err) {
      console.error('Failed to fetch appointments', err);
    }
  };

  if (!isLoggedIn) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--background)' }}>
        <Head><title>Doctor Login</title></Head>
        <div className="card animate-fade-in" style={{ width: '100%', maxWidth: '400px', borderTop: '4px solid var(--primary)' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '0.5rem', fontWeight: '700' }}>Doctor Portal</h2>
          <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '2rem' }}>Sign in to manage appointments</p>
          
          {error && <div className="animate-fade-in" style={{ background: '#fee2e2', color: '#991b1b', padding: '0.75rem', borderRadius: '8px', marginBottom: '1.5rem', textAlign: 'center', fontSize: '0.9rem' }}>{error}</div>}
          
          <form onSubmit={handleLogin}>
            <div className="input-group">
              <label className="input-label">Email Address</label>
              <input type="email" className="input-field" value={email} onChange={e => setEmail(e.target.value)} placeholder="doctor@hospital.com" required />
            </div>
            <div className="input-group">
              <label className="input-label">Password</label>
              <input type="password" className="input-field" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }} disabled={loading}>
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)' }}>
      <Head><title>Doctor Dashboard | {doctor?.name}</title></Head>
      
      {/* Navbar */}
      <nav style={{ background: 'rgba(255, 255, 255, 0.8)', backdropFilter: 'blur(10px)', borderBottom: '1px solid var(--border)', padding: '1rem 0', position: 'sticky', top: 0, zIndex: 10 }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontWeight: '800', fontSize: '1.25rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>👨‍⚕️</span> {doctor?.name}
          </div>
          <button onClick={handleLogout} className="btn" style={{ color: 'var(--danger)', background: '#fee2e2', fontSize: '0.9rem', padding: '0.5rem 1rem' }}>
            Sign Out
          </button>
        </div>
      </nav>

      <main className="container animate-fade-in" style={{ padding: '2rem 1rem' }}>
        {/* Stats Row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="card" style={{ borderLeft: '4px solid var(--primary)' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Appointments</div>
            <div style={{ fontSize: '2.5rem', fontWeight: '800', marginTop: '0.5rem' }}>{appointments.length}</div>
          </div>
          <div className="card" style={{ borderLeft: '4px solid var(--success)' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Confirmed</div>
            <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--success)', marginTop: '0.5rem' }}>
              {appointments.filter(a => a.status === 'confirmed').length}
            </div>
          </div>
          <div className="card" style={{ borderLeft: '4px solid var(--warning)' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Pending Action</div>
            <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--warning)', marginTop: '0.5rem' }}>
              {appointments.filter(a => a.status === 'pending' || a.status === 'scheduled').length}
            </div>
          </div>
        </div>

        {/* Appointments Table */}
        <div className="card" style={{ overflowX: 'auto', padding: '0' }}>
          <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '700' }}>Recent Appointments</h3>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '800px' }}>
            <thead>
              <tr style={{ background: '#f8fafc', textAlign: 'left' }}>
                <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: '600', fontSize: '0.85rem', textTransform: 'uppercase' }}>Patient</th>
                <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: '600', fontSize: '0.85rem', textTransform: 'uppercase' }}>Date & Time</th>
                <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: '600', fontSize: '0.85rem', textTransform: 'uppercase' }}>Symptoms</th>
                <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: '600', fontSize: '0.85rem', textTransform: 'uppercase' }}>Status</th>
                <th style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontWeight: '600', fontSize: '0.85rem', textTransform: 'uppercase' }}>Ref ID</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map((apt) => (
                <tr key={apt.id} style={{ borderBottom: '1px solid var(--border)', transition: 'background 0.1s' }} className="hover:bg-gray-50">
                  <td style={{ padding: '1rem 1.5rem' }}>
                    <div style={{ fontWeight: '600', color: 'var(--text-main)' }}>{apt.patient_name}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{apt.patient_phone}</div>
                  </td>
                  <td style={{ padding: '1rem 1.5rem' }}>
                    <div style={{ fontWeight: '500' }}>{apt.appointment_date}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{apt.appointment_time}</div>
                  </td>
                  <td style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)' }}>{apt.symptoms || '-'}</td>
                  <td style={{ padding: '1rem 1.5rem' }}>
                    <span className={`badge ${
                      apt.status === 'confirmed' ? 'badge-success' : 
                      apt.status === 'cancelled' ? 'badge-danger' : 'badge-warning'
                    }`}>
                      {apt.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: '1rem 1.5rem', fontFamily: 'monospace', fontSize: '0.9rem', color: 'var(--text-muted)' }}>{apt.confirmation_number || '-'}</td>
                </tr>
              ))}
              {appointments.length === 0 && (
                <tr>
                  <td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No appointments found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
