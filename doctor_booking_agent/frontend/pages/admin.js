import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function Admin() {
  const [stats, setStats] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchStats();
    fetchAppointments();
    fetchDoctors();
  }, []);

  const fetchStats = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const res = await fetch(`${backendUrl}/api/stats/dashboard`);
      const data = await res.json();
      if (data.status === 'success') {
        setStats(data.data);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const fetchAppointments = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const res = await fetch(`${backendUrl}/api/appointments`);
      const data = await res.json();
      if (data.status === 'success') {
        setAppointments(data.data);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const fetchDoctors = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const res = await fetch(`${backendUrl}/api/doctors`);
      const data = await res.json();
      if (data.status === 'success') {
        setDoctors(data.data);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)' }}>
      <Head>
        <title>Admin Dashboard - Hospital Management</title>
      </Head>

      <header style={{ background: 'white', borderBottom: '1px solid var(--border)', padding: '1rem 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--primary)' }}>
            🏥 Admin Panel
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link href="/" style={{ color: 'var(--text-muted)', fontWeight: '500' }}>Patient Booking</Link>
            <Link href="/doctor-login" style={{ color: 'var(--text-muted)', fontWeight: '500' }}>Doctor Portal</Link>
          </div>
        </div>
      </header>

      <main className="container animate-fade-in" style={{ padding: '2rem 1rem' }}>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
          <button
            className="btn"
            style={{ 
              background: activeTab === 'overview' ? 'var(--primary)' : 'transparent',
              color: activeTab === 'overview' ? 'white' : 'var(--text-muted)'
            }}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className="btn"
            style={{ 
              background: activeTab === 'appointments' ? 'var(--primary)' : 'transparent',
              color: activeTab === 'appointments' ? 'white' : 'var(--text-muted)'
            }}
            onClick={() => setActiveTab('appointments')}
          >
            Appointments
          </button>
          <button
            className="btn"
            style={{ 
              background: activeTab === 'doctors' ? 'var(--primary)' : 'transparent',
              color: activeTab === 'doctors' ? 'white' : 'var(--text-muted)'
            }}
            onClick={() => setActiveTab('doctors')}
          >
            Doctors
          </button>
        </div>

        {activeTab === 'overview' && stats && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
            <div className="card">
              <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--primary)' }}>{stats.total_patients}</div>
              <div style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Total Patients</div>
            </div>
            <div className="card">
              <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--primary)' }}>{stats.total_doctors}</div>
              <div style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Total Doctors</div>
            </div>
            <div className="card">
              <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--primary)' }}>{stats.total_appointments}</div>
              <div style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Total Appointments</div>
            </div>
            <div className="card">
              <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--success)' }}>{stats.today_appointments}</div>
              <div style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Today's Appointments</div>
            </div>
            <div className="card">
              <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--warning)' }}>{stats.pending_appointments}</div>
              <div style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Pending</div>
            </div>
            <div className="card">
              <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--success)' }}>{stats.completed_appointments}</div>
              <div style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Completed</div>
            </div>
          </div>
        )}

        {activeTab === 'appointments' && (
          <div className="card" style={{ overflowX: 'auto', padding: '0' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '800px' }}>
              <thead>
                <tr style={{ background: '#f8fafc', textAlign: 'left' }}>
                  <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '600' }}>ID</th>
                  <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '600' }}>Patient</th>
                  <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '600' }}>Doctor</th>
                  <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '600' }}>Date & Time</th>
                  <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '600' }}>Status</th>
                  <th style={{ padding: '1rem', color: 'var(--text-muted)', fontWeight: '600' }}>Ref ID</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map((apt) => (
                  <tr key={apt.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '1rem' }}>{apt.id}</td>
                    <td style={{ padding: '1rem', fontWeight: '500' }}>{apt.patient_name}</td>
                    <td style={{ padding: '1rem' }}>{apt.doctor_name}</td>
                    <td style={{ padding: '1rem' }}>{apt.date} {apt.time}</td>
                    <td style={{ padding: '1rem' }}>
                      <span className={`badge ${
                        apt.status === 'confirmed' ? 'badge-success' : 
                        apt.status === 'cancelled' ? 'badge-danger' : 'badge-warning'
                      }`}>
                        {apt.status}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', fontFamily: 'monospace' }}>{apt.confirmation_number}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'doctors' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {doctors.map((doc) => (
              <div key={doc.id} className="card">
                <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>{doc.name}</h3>
                <div style={{ color: 'var(--primary)', fontWeight: '600', marginBottom: '0.5rem' }}>{doc.specialty}</div>
                <div style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}>{doc.clinic_name}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
                  <span style={{ fontWeight: '500' }}>{doc.available_time}</span>
                  <span style={{ fontWeight: '700' }}>₹{doc.consultation_fee}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
