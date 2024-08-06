import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    try {
      const csvPath = path.join(process.cwd(), 'instagram_posts.csv');
      const csvData = fs.readFileSync(csvPath, 'utf-8');
      res.status(200).send(csvData);
    } catch (error) {
      res.status(500).json({ error: 'Failed to read CSV file' });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}