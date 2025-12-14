import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';

export default function DoctorDashboard() {
  const [doctors, setDoctors] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDoctors();
    fetchStats();
  }, []);

  const fetchDoctors = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const res = await fetch(`${backendUrl}/api/doctors`);
      const data = await res.json();
      
      if (data.status === 'success') {
        setDoctors(data.data);
      }
    } catch (error) {
      console.error('Error fetching doctors:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const res = await fetch(`${backendUrl}/api/stats/dashboard`);
      const data = await res.json();
      
      if (data.status === 'success') {
        setStats(data.data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchDoctorAppointments = async (doctorId) => {
    setLoading(true);
    setSelectedDoctor(doctorId);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const res = await fetch(`${backendUrl}/api/doctor/${doctorId}/appointments`);
      const data = await res.json();
      
      if (data.status === 'success') {
        setAppointments(data.data);
      }
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)' }}>
      <Head>
        <title>Doctor Overview | Hospital Management</title>
      </Head>

      <header style={{ background: 'white', borderBottom: '1px solid var(--border)', padding: '1rem 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--primary)' }}>
            👨‍⚕️ Doctor Overview
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <Link href="/admin" className="btn" style={{ color: 'var(--text-muted)', background: 'transparent' }}>
              Admin Panel
            </Link>
            <Link href="/doctor-login" className="btn" style={{ color: 'white', background: 'var(--primary)' }}>
              Login as Doctor
            </Link>
          </div>
        </div>
      </header>

      <main className="container animate-fade-in" style={{ padding: '2rem 1rem' }}>
        
        {stats && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
            <div className="card">
              <div style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--primary)' }}>{stats.total_patients}</div>
              <div style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Total Patients</div>
            </div>
            <div className="card">
              <div style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--primary)' }}>{stats.total_doctors}</div>
              <div style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Total Doctors</div>
            </div>
            <div className="card">
              <div style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--success)' }}>{stats.today_appointments}</div>
              <div style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Today's Appointments</div>
            </div>
            <div className="card">
              <div style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--warning)' }}>{stats.pending_appointments}</div>
              <div style={{ color: 'var(--text-muted)', fontWeight: '600' }}>Pending</div>
            </div>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '2rem', alignItems: 'start' }}>
          
          {/* Doctors List */}
          <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
            <div style={{ padding: '1rem', borderBottom: '1px solid var(--border)', background: '#f8fafc' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700' }}>Select Doctor</h3>
            </div>
            <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
              {doctors.map((doctor) => (
                <div
                  key={doctor.id}
                  onClick={() => fetchDoctorAppointments(doctor.id)}
                  style={{ 
                    padding: '1rem', 
                    borderBottom: '1px solid var(--border)', 
                    cursor: 'pointer',
                    background: selectedDoctor === doctor.id ? '#eff6ff' : 'white',
                    borderLeft: selectedDoctor === doctor.id ? '4px solid var(--primary)' : '4px solid transparent',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ fontWeight: '600', color: 'var(--text-main)' }}>{doctor.name}</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--primary)' }}>{doctor.specialty}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{doctor.clinic_name}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Appointments Section */}
          <div className="card" style={{ minHeight: '400px' }}>
            {selectedDoctor ? (
              <>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.5rem', fontWeight: '700' }}>Appointments</h2>
                  {loading && <span className="badge badge-warning">Loading...</span>}
                </div>

                {appointments.length > 0 ? (
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ textAlign: 'left', borderBottom: '2px solid var(--border)' }}>
                          <th style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Patient</th>
                          <th style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Date & Time</th>
                          <th style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Status</th>
                          <th style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Reason</th>
                        </tr>
                      </thead>
                      <tbody>
                        {appointments.map((apt) => (
                          <tr key={apt.id} style={{ borderBottom: '1px solid var(--border)' }}>
                            <td style={{ padding: '0.75rem' }}>
                              <div style={{ fontWeight: '500' }}>{apt.patient_name}</div>
                              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{apt.patient_phone}</div>
                            </td>
                            <td style={{ padding: '0.75rem' }}>
                              <div>{apt.appointment_date}</div>
                              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{apt.appointment_time}</div>
                            </td>
                            <td style={{ padding: '0.75rem' }}>
                              <span className={`badge ${
                                apt.status === 'confirmed' ? 'badge-success' : 
                                apt.status === 'cancelled' ? 'badge-danger' : 'badge-warning'
                              }`}>
                                {apt.status}
                              </span>
                            </td>
                            <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{apt.reason || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    {loading ? 'Fetching appointments...' : 'No appointments found for this doctor.'}
                  </div>
                )}
              </>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '300px', color: 'var(--text-muted)' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👈</div>
                <p>Select a doctor from the list to view their appointments.</p>
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}
