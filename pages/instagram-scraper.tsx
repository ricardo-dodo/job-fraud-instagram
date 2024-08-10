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

      if (response.ok) {
        const arrayBuffer = await response.arrayBuffer();
        const workbook = XLSX.read(new Uint8Array(arrayBuffer), { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });
        setScrapedData(data);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to scrape data');
      }
    } catch (error) {
      console.error('Error scraping data:', error);
      alert('An error occurred while scraping data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen bg-gradient-to-br from-purple-100 to-indigo-200 py-12 px-4 sm:px-6 lg:px-8"
    >
      <div className="max-w-6xl mx-auto">
        <motion.h1
          initial={{ y: -20 }}
          animate={{ y: 0 }}
          className="text-4xl font-extrabold text-gray-900 text-center mb-8"
        >
          Instagram Scraper
        </motion.h1>
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white shadow-xl rounded-lg overflow-hidden mb-8"
        >
          <div className="p-6">
            <div className="flex items-center space-x-4 mb-6">
              <input
                type="text"
                value={profile}
                onChange={(e) => setProfile(e.target.value)}
                placeholder="Enter Instagram profile name"
                className="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <ScrapeButton onClick={handleScrape} isLoading={isLoading} />
            </div>
            <ScrapingProgress isLoading={isLoading} />
          </div>
        </motion.div>
        {scrapedData && <InstagramData data={scrapedData} />}
      </div>
    </motion.div>
  );
}