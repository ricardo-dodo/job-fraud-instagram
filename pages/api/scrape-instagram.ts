import { NextApiRequest, NextApiResponse } from 'next';
import fetch from 'node-fetch';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      const { profile } = req.body;
      if (!profile) {
        return res.status(400).json({ error: 'Profile name is required' });
      }

      const flaskUrl = 'http://localhost:5000/scrape'; // Update with your Flask server URL
      const response = await fetch(flaskUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ profile }),
      });

      if (!response.ok) {
        throw new Error(`Flask server responded with status ${response.status}`);
      }

      const result = await response.json();
      res.status(200).json(result);
    } catch (error) {
      console.error('An error occurred:', error);
      res.status(500).json({ error: 'An error occurred while starting the scraping process' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}