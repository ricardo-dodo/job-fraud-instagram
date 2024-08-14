import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ScrapeButton from '../components/ScrapeButton';
import ScrapingProgress from '../components/ScrapingProgress';
import ViewScrapedData from '../components/ViewScrapedData';

export default function InstagramScraper() {
  const [isLoading, setIsLoading] = useState(false);
  const [profile, setProfile] = useState('');
  const [scrapedData, setScrapedData] = useState(null);
  const [isScrapingInProgress, setIsScrapingInProgress] = useState(false);
  const [activeTab, setActiveTab] = useState('scrape');

  const handleScrape = async () => {
    if (!profile) {
      alert('Please enter an Instagram profile name');
      return;
    }
    setIsLoading(true);
    setScrapedData(null);
    setIsScrapingInProgress(true);
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

      const result = await response.json();
      if (result.message === 'Scraping started') {
        alert('Scraping process has started. Please wait for it to complete.');
        checkScrapingStatus();
      } else if (result.data) {
        setScrapedData(result.data);
      }
    } catch (error) {
      console.error('Error during scraping:', error);
      alert('An error occurred during scraping. Please try again.');
    } finally {
      setIsLoading(false);
      setIsScrapingInProgress(false);
    }
  };

  const checkScrapingStatus = async () => {
    let attempts = 0;
    const maxAttempts = 12; // 1 minute total (5 seconds * 12)

    while (attempts < maxAttempts) {
      try {
        console.log(`Checking scraping status for profile: ${profile}`);
        const response = await fetch(`/api/get-scraped-data?profile=${profile}`);
        if (response.ok) {
          const data = await response.json();
          console.log('Received data:', data);
          if (data && data.length > 0) {
            setScrapedData(data);
            return;
          } else {
            console.log('No data received yet');
          }
        } else {
          console.error('Error response:', response.status, await response.text());
        }
      } catch (error) {
        console.error('Error checking scraping status:', error);
      }
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds before next attempt
    }
    console.log('Max attempts reached, no data found');
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
      <div className="mb-4">
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          <button
            className={`py-2 px-4 ${activeTab === 'scrape' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setActiveTab('scrape')}
          >
            Scrape
          </button>
          <button
            className={`py-2 px-4 ${activeTab === 'view' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setActiveTab('view')}
          >
            View Data
          </button>
        </div>
      </div>
      {activeTab === 'scrape' ? (
        <>
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
        </>
      ) : (
        <ViewScrapedData profile={profile} />
      )}
    </div>
  );
}