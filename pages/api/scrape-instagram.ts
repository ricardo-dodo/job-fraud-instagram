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
      console.log(`Executing Python script: ${scriptPath}`);

      const pythonProcess = exec(`python3 ${scriptPath} ${profile}`);

      let output = '';
      let errorOutput = '';

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
        console.log(`Python script output: ${data.toString()}`);
      });

      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
        console.error(`Python script error: ${data.toString()}`);
      });

      // Set a timeout for the Python process (e.g., 5 minutes)
      const timeout = setTimeout(() => {
        pythonProcess.kill();
        console.error('Python script execution timed out');
        res.status(504).json({ error: 'Scraping process timed out' });
      }, 300000); // 5 minutes

      pythonProcess.on('close', async (code) => {
        clearTimeout(timeout);
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
      res.status(500).json({ error: 'An error occurred while scraping', details: error.message });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}