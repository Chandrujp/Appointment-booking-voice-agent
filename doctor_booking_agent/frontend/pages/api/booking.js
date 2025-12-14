// This API route connects frontend to Flask backend
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { phone_number, doctor_name, specialty } = req.body;

  if (!phone_number) {
    return res.status(400).json({ error: 'Phone number is required' });
  }

  try {
    // Call Flask backend API
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
    
    // First, get the list of doctors to find the right doctor_id
    const doctorsResponse = await fetch(`${backendUrl}/api/doctors`);
    
    if (!doctorsResponse.ok) {
      throw new Error('Cannot connect to Flask backend. Make sure it is running on port 5000');
    }
    
    const doctorsData = await doctorsResponse.json();
    const doctors = doctorsData.data || doctorsData; // Handle both formats
    
    // Find doctor by name or specialty
    let doctor = doctors.find(d => d.name === doctor_name);
    if (!doctor && specialty) {
      doctor = doctors.find(d => d.specialty === specialty);
    }
    if (!doctor && doctors.length > 0) {
      doctor = doctors[0]; // Default to first doctor
    }
    
    if (!doctor) {
      return res.status(404).json({
        success: false,
        error: 'No doctors available'
      });
    }

    // Book appointment with the selected doctor
    const appointmentResponse = await fetch(`${backendUrl}/api/appointment/book`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        patient_phone: phone_number,
        doctor_id: doctor.id,
        patient_name: 'Patient',
        appointment_date: new Date().toISOString().split('T')[0]
      })
    });

    const data = await appointmentResponse.json();
    
    if (appointmentResponse.ok) {
      console.log(`📞 Call initiated for ${phone_number} with ${doctor.name}`);
      res.status(200).json({
        success: true,
        call_id: data.call_id,
        appointment_id: data.appointment_id,
        confirmation_number: data.confirmation_number,
        doctor: doctor.name,
        message: `Calling ${phone_number} to book appointment with ${doctor.name}`
      });
    } else {
      res.status(appointmentResponse.status).json({
        success: false,
        error: data.error || 'Failed to book appointment'
      });
    }
  } catch (error) {
    console.error('Backend connection error:', error);
    res.status(500).json({
      success: false,
      error: `Cannot connect to Flask backend: ${error.message}. Make sure it's running on port 5000.`
    });
  }
}
