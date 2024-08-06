import { useState, useEffect } from 'react';
import DataGrid from 'react-data-grid';
import 'react-data-grid/lib/styles.css';

interface InstagramDataProps {
  data: any;
}

export default function InstagramData({ data }: InstagramDataProps) {
  const [csvData, setCsvData] = useState<any[]>([]);

  useEffect(() => {
    const fetchCsvData = async () => {
      try {
        const response = await fetch('/api/get-csv-data');
        const text = await response.text();
        const rows = text.split('\n').map(row => row.split(','));
        const headers = rows[0];
        const formattedData = rows.slice(1).map(row => {
          const obj: { [key: string]: string } = {};
          headers.forEach((header, index) => {
            obj[header] = row[index];
          });
          return obj;
        });
        setCsvData(formattedData);
      } catch (error) {
        console.error('Error fetching CSV data:', error);
      }
    };

    fetchCsvData();
  }, [data]);

  const columns = csvData.length > 0
    ? Object.keys(csvData[0]).map(key => ({
        key,
        name: key,
        resizable: true,
        sortable: true,
      }))
    : [];

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Scraped Data</h2>
      {csvData.length > 0 ? (
        <div className="h-[600px] w-full">
          <DataGrid
            columns={columns}
            rows={csvData}
            className="rdg-light"
          />
        </div>
      ) : (
        <p className="text-gray-500">No data available</p>
      )}
    </div>
  );
}