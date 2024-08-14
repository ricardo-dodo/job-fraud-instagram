import { useState, useEffect } from 'react';
import InstagramData from './InstagramData';

interface ViewScrapedDataProps {
  profile: string;
}

export default function ViewScrapedData({ profile }: ViewScrapedDataProps) {
  const [scrapedData, setScrapedData] = useState<any[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!profile) return;
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/get-scraped-data?profile=${profile}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Fetched data:', data);
        setScrapedData(data);
      } catch (error) {
        console.error('Error fetching scraped data:', error);
        setError(`Failed to load data: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [profile]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return (
      <div className="text-red-500">
        <p>{error}</p>
        <p>Please try again or check the server logs for more information.</p>
      </div>
    );
  }

  if (!scrapedData || scrapedData.length === 0) {
    return <div>No data available for profile: {profile}. Please scrape this profile first.</div>;
  }

  return <InstagramData data={scrapedData} />;
}