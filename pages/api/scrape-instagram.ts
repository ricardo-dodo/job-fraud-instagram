import { NextApiRequest, NextApiResponse } from 'next';
import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      const { profile } = req.body;
      if (!profile) {
        return res.status(400).json({ error: 'Profile name is required' });
      }

      const scriptPath = path.join(process.cwd(), 'python-code', 'ig.py');
      exec(`python3 ${scriptPath} ${profile}`, async (error, stdout, stderr) => {
        if (error) {
          console.error(`Error: ${error.message}`);
          return res.status(500).json({ error: 'Failed to run the script' });
        }
        if (stderr) {
          console.error(`stderr: ${stderr}`);
          return res.status(500).json({ error: 'Script encountered an error' });
        }
        
        const csvFilePath = path.join(process.cwd(), `${profile}_instagram_posts.csv`);
        if (fs.existsSync(csvFilePath)) {
          const csvContent = await fs.promises.readFile(csvFilePath, 'utf-8');
          res.status(200).json({ message: 'Scraping completed successfully', csvContent });
        } else {
          res.status(404).json({ error: 'CSV file not found' });
        }
      });
    } catch (error) {
      res.status(500).json({ error: 'An error occurred while scraping' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}