import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ScrapeButton from '../components/ScrapeButton';
import InstagramData from '../components/InstagramData';
import ScrapingProgress from '../components/ScrapingProgress';

export default function InstagramScraper() {
  const [isLoading, setIsLoading] = useState(false);
  const [scrapedData, setScrapedData] = useState(null);
  const [profile, setProfile] = useState('');
  const [progressData, setProgressData] = useState(null);

  const handleScrape = async () => {
    if (!profile) {
      alert('Please enter an Instagram profile name');
      return;
    }
    setIsLoading(true);
    setProgressData(null);
    try {
      const response = await fetch('/api/scrape-instagram', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ profile }),
      });
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        setProgressData(prevData => prevData ? prevData + chunk : chunk);
      }

      setScrapedData(progressData);
    } catch (error) {
      console.error('Error scraping data:', error);
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
      <div className="max-w-3xl mx-auto">
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
          className="bg-white shadow-xl rounded-lg overflow-hidden"
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
            <ScrapingProgress isLoading={isLoading} scrapedData={progressData} />
            {scrapedData && <InstagramData data={scrapedData} />}
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}