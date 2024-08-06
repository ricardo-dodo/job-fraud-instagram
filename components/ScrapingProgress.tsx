import { useState, useEffect } from 'react';

interface ScrapingProgressProps {
  isLoading: boolean;
  scrapedData: string | null;
}

export default function ScrapingProgress({ isLoading, scrapedData }: ScrapingProgressProps) {
  const [parsedData, setParsedData] = useState<string[][]>([]);

  useEffect(() => {
    if (scrapedData) {
      const rows = scrapedData.split('\n').map(row => row.split('|'));
      setParsedData(rows);
    }
  }, [scrapedData]);

  if (!isLoading && !scrapedData) return null;

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Scraping Progress</h2>
      {isLoading && <p className="text-gray-600">Scraping in progress...</p>}
      {parsedData.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {parsedData[0].map((header, index) => (
                  <th key={index} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {parsedData.slice(1).map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}