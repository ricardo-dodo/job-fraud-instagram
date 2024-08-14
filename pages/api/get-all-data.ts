import { NextApiRequest, NextApiResponse } from 'next';
import clientPromise from '../../lib/mongodb';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    try {
      const client = await clientPromise;
      const db = client.db('instagram_scraper');
      const collection = db.collection('scraped_data');
      
      const data = await collection.find({}).toArray();
      
      console.log(`Total data fetched: ${data.length}`);
      
      if (data.length === 0) {
        return res.status(404).json({ error: 'No data found in the database' });
      }
      
      res.status(200).json(data);
    } catch (error) {
      console.error('An error occurred:', error);
      res.status(500).json({ error: `An error occurred while fetching the data: ${error.message}` });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}