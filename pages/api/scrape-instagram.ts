import { NextApiRequest, NextApiResponse } from 'next';
import { exec } from 'child_process';
import path from 'path';
import fs from 'fs/promises';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      const { profile } = req.body;
      if (!profile) {
        return res.status(400).json({ error: 'Profile name is required' });
      }

      const scriptPath = path.join(process.cwd(), 'python-code', 'ig.py');

      const pythonProcess = exec(`python3 ${scriptPath} ${profile}`);

      let output = '';
      let errorOutput = '';

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
        console.log(data.toString()); // This will log to the server console
      });

      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
        console.error(data.toString()); // This will log errors to the server console
      });

      pythonProcess.on('close', async (code) => {
        if (code === 0) {
          const excelPath = path.join(process.cwd(), `${profile}_instagram_posts.xlsx`);
          console.log(`Attempting to read file from: ${excelPath}`);
          
          try {
            const data = await fs.readFile(excelPath);
            res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
            res.setHeader('Content-Disposition', `attachment; filename=${profile}_instagram_posts.xlsx`);
            res.send(data);

            // Delete the file after sending
            await fs.unlink(excelPath);
          } catch (err) {
            console.error('Error reading or deleting file:', err);
            res.status(500).json({ error: 'Error reading or deleting file', details: err.message });
          }
        } else {
          console.error('Python script error:', errorOutput);
          res.status(500).json({ error: 'Error occurred during scraping', details: errorOutput });
        }
      });
    } catch (error) {
      console.error('An error occurred:', error);
      res.status(500).json({ error: 'An error occurred while scraping' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}