// This API route proxies booking requests to the Flask backend
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { phone_number, doctor_id, patient_name, appointment_date } = req.body;

  if (!phone_number) {
    return res.status(400).json({ error: 'Phone number required' });
  }

  try {
    // Call Flask backend API
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
    const response = await fetch(`${backendUrl}/api/appointment/book`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        phone_number,
        doctor_id,
        patient_name: patient_name || 'Patient',
        appointment_date: appointment_date || new Date().toISOString().split('T')[0]
      })
    });

    const data = await response.json();
    
    if (response.ok) {
      res.status(200).json({
        success: true,
        call_id: data.call_id,
        appointment_id: data.appointment_id,
        confirmation_number: data.confirmation_number
      });
    } else {
      res.status(response.status).json({
        success: false,
        error: data.error || 'Failed to book appointment'
      });
    }
  } catch (error) {
    console.error('Backend connection error:', error);
    res.status(500).json({
      success: false,
      error: 'Cannot connect to backend server. Make sure Flask API is running on port 5000.'
    });
  }
}
    
/*
    <booking_workflow>
        <step1>Greet the patient warmly</step1>
        <step2>Confirm doctor and specialty</step2>
        <step3>Ask for preferred date and time</step3>
        <step4>Note any special requirements</step4>
        <step5>Confirm appointment details</step5>
        <step6>Provide confirmation number</step6>
    </booking_workflow>
    
    <example_responses>
        <greeting>Good day. I'm your appointment booking assistant. I can help you schedule with ${doctorName}.</greeting>
        <availability>What date and time works best for you?</availability>
        <confirmation>Perfect. Your appointment is confirmed. Please arrive 10 minutes early.</confirmation>
    </example_responses>
</ai_master_prompt>`;

  const evaluation_tool = {
    name: "appointment_booking",
    behavior: "BLOCKING",
    parameters: {
      type: "OBJECT",
      required: ["appointment_confirmed", "patient_name", "appointment_date"],
      properties: {
        appointment_confirmed: {
          type: "BOOLEAN",
          description: "Whether the appointment was successfully booked"
        },
        patient_name: {
          type: "STRING",
          description: "Name of the patient"
        },
        appointment_date: {
          type: "STRING",
          description: "Scheduled appointment date and time"
        },
        doctor_name: {
          type: "STRING",
          description: "Name of the assigned doctor"
        },
        confirmation_number: {
          type: "STRING",
          description: "Appointment confirmation number"
        },
        special_notes: {
          type: "STRING",
          description: "Any special requirements or notes from the patient"
        }
      }
    },
    description: "Evaluate doctor appointment booking call outcome"
  };

  try {
    const response = await fetch('https://api-dinodial-proxy.cyces.co/api/proxy/make-call/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.DINODIAL_TOKEN}`
      },
      body: JSON.stringify({
        prompt,
        evaluation_tool,
        vad_engine: 'CAWL'
      })
    });

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
*/
