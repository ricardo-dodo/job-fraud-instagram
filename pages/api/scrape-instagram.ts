import { NextApiRequest, NextApiResponse } from 'next';
import { exec } from 'child_process';
import path from 'path';
import clientPromise from '../../lib/mongodb';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      const { profile } = req.body;
      if (!profile) {
        return res.status(400).json({ error: 'Profile name is required' });
      }

      const scriptPath = path.join(process.cwd(), 'python-code', 'ig.py');
      console.log(`Executing Python script: ${scriptPath}`);

      const pythonProcess = exec(`python3 ${scriptPath} ${profile}`);

      pythonProcess.stdout.on('data', (data) => {
        console.log(`Python script output: ${data}`);
      });

      pythonProcess.stderr.on('data', (data) => {
        console.error(`Python script error: ${data}`);
      });

      pythonProcess.on('close', async (code) => {
        console.log(`Python script exited with code ${code}`);
        if (code === 0) {
          const client = await clientPromise;
          const db = client.db('instagram_scraper');
          const collection = db.collection('scraped_data');
          const data = await collection.find({ profile }).toArray();
          res.status(200).json({ message: 'Scraping completed', data });
        } else {
          res.status(500).json({ error: 'Scraping process failed' });
        }
      });
    } catch (error) {
      console.error('An error occurred:', error);
      res.status(500).json({ error: 'An error occurred while starting the scraping process' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}