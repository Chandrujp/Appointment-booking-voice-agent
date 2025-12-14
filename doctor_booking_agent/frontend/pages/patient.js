import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function PatientDashboard() {
  const [appointments, setAppointments] = useState([]);
  const [patientInfo, setPatientInfo] = useState(null);
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchPatientInfo = async (e) => {
    e.preventDefault();
    if (!phone) return;
    
    setLoading(true);
    setError('');
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const res = await fetch(`${apiBase}/api/patient/phone/${phone}`);
      const data = await res.json();
      
      if (data.status === 'success') {
        setPatientInfo(data.data);
        // Assuming the API returns appointments in the patient object or we need to fetch them separately
        // For now, let's assume we just show patient info. 
        // If there's an endpoint for patient appointments, we should call it.
        // Based on previous context, there isn't a direct "get my appointments" endpoint used here yet, 
        // but let's check if the patient object has them or if we need to add that.
        // The previous code didn't fetch appointments, just patient info.
      } else {
        setError('Patient not found');
        setPatientInfo(null);
      }
    } catch (error) {
      console.error('Error fetching patient:', error);
      setError('Failed to fetch patient info');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)' }}>
      <Head>
        <title>Patient Dashboard | HealthCare AI</title>
      </Head>

      <header style={{ background: 'white', borderBottom: '1px solid var(--border)', padding: '1rem 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--primary)' }}>
            🏥 Patient Portal
          </div>
          <Link href="/" className="btn" style={{ color: 'var(--text-muted)', background: '#f1f5f9' }}>
            Back to Booking
          </Link>
        </div>
      </header>

      <main className="container animate-fade-in" style={{ padding: '2rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        
        <div className="card" style={{ width: '100%', maxWidth: '500px', marginBottom: '2rem' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Check Your Records</h2>
          
          <form onSubmit={fetchPatientInfo}>
            <div className="input-group">
              <label className="input-label">Phone Number</label>
              <input
                type="tel"
                placeholder="Enter your phone number"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="input-field"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
              {loading ? 'Searching...' : 'View My Info'}
            </button>
          </form>
          
          {error && (
            <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#fee2e2', color: '#991b1b', borderRadius: '8px', textAlign: 'center' }}>
              {error}
            </div>
          )}
        </div>

        {patientInfo && (
          <div className="card animate-fade-in" style={{ width: '100%', maxWidth: '800px', borderTop: '4px solid var(--success)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
              <div>
                <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{patientInfo.name}</h2>
                <div style={{ color: 'var(--text-muted)' }}>Patient ID: {patientInfo.id}</div>
              </div>
              <div className="badge badge-success">Active</div>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
              <div>
                <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Phone</label>
                <div style={{ fontSize: '1.1rem', fontWeight: '500' }}>{patientInfo.phone}</div>
              </div>
              <div>
                <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Email</label>
                <div style={{ fontSize: '1.1rem', fontWeight: '500' }}>{patientInfo.email || 'Not provided'}</div>
              </div>
              <div>
                <label style={{ display: 'block', color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.25rem' }}>Registered On</label>
                <div style={{ fontSize: '1.1rem', fontWeight: '500' }}>{new Date().toLocaleDateString()}</div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
