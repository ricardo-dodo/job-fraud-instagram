import { useState, useEffect } from 'react';
import InstagramData from '../components/InstagramData';

export default function ViewAllData() {
  const [allData, setAllData] = useState<any[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAllData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/get-all-data');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setAllData(data);
      } catch (error) {
        console.error('Error fetching all data:', error);
        setError(`Failed to load data: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAllData();
  }, []);

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

  if (!allData || allData.length === 0) {
    return <div>No data available. Please scrape some profiles first.</div>;
  }

  return <InstagramData data={allData} />;
}