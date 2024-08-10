import { useState } from 'react';
import { motion } from 'framer-motion';
import ScrapeButton from '../components/ScrapeButton';
import ScrapingProgress from '../components/ScrapingProgress';
import InstagramData from '../components/InstagramData';
import * as XLSX from 'xlsx';

export default function InstagramScraper() {
  const [isLoading, setIsLoading] = useState(false);
  const [profile, setProfile] = useState('');
  const [scrapedData, setScrapedData] = useState(null);

  const handleScrape = async () => {
    if (!profile) {
      alert('Please enter an Instagram profile name');
      return;
    }
    setIsLoading(true);
    setScrapedData(null);
    try {
      const response = await fetch('/api/scrape-instagram', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ profile }),
      });

      if (!response.ok) {
        throw new Error('Failed to start scraping');
      }

      const blob = await response.blob();
      const workbook = XLSX.read(await blob.arrayBuffer(), { type: 'array' });
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
      setScrapedData(data);
    } catch (error) {
      console.error('Error during scraping:', error);
      alert('An error occurred during scraping. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-3xl font-bold mb-8 text-center text-gray-800 dark:text-white"
      >
        Instagram Scraper
      </motion.h1>
      <div className="mb-8">
        <div className="mb-4">
          <label htmlFor="profile" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Instagram Profile Name
          </label>
          <input
            type="text"
            id="profile"
            value={profile}
            onChange={(e) => setProfile(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="Enter Instagram profile name"
          />
        </div>
        <ScrapeButton onClick={handleScrape} isLoading={isLoading} />
      </div>
      <ScrapingProgress isLoading={isLoading} />
      {scrapedData && <InstagramData data={scrapedData} />}
    </div>
  );
}