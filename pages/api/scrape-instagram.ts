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

      res.writeHead(200, {
        'Content-Type': 'text/plain',
        'Transfer-Encoding': 'chunked',
      });

      const scriptPath = path.join(process.cwd(), 'python-code', 'ig.py');
      const csvPath = path.join(process.cwd(), `${profile}_instagram_posts.csv`);

      const pythonProcess = exec(`python3 ${scriptPath} ${profile}`);

      pythonProcess.stdout.on('data', (data) => {
        res.write(data);
      });

      pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
      });

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          const csvContent = fs.readFileSync(csvPath, 'utf-8');
          res.write(csvContent);
        } else {
          res.write('Error occurred during scraping');
        }
        res.end();
      });
    } catch (error) {
      res.status(500).json({ error: 'An error occurred while scraping' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}