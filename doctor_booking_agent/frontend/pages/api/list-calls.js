export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const response = await fetch('https://api-dinodial-proxy.cyces.co/api/proxy/calls/list/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${process.env.DINODIAL_TOKEN}`
      }
    });

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
