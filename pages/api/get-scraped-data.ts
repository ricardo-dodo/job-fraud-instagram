import { NextApiRequest, NextApiResponse } from 'next';
import clientPromise from '../../lib/mongodb';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    try {
      const { profile } = req.query;
      if (!profile) {
        return res.status(400).json({ error: 'Profile name is required' });
      }

      console.log(`Attempting to fetch data for profile: ${profile}`);

      const client = await clientPromise;
      const db = client.db('instagram_scraper');
      const collection = db.collection('scraped_data');
      
      const data = await collection.find({ profile: profile }).toArray();
      
      console.log(`Data fetched for profile ${profile}:`, data);
      
      if (data.length === 0) {
        return res.status(404).json({ error: `No data found for profile: ${profile}` });
      }
      
      res.status(200).json(data);
    } catch (error) {
      console.error('An error occurred:', error);
      res.status(500).json({ error: `An error occurred while fetching the scraped data: ${error.message}` });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}