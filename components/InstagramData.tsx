import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface InstagramDataProps {
  data: any[][];
}

const TextWithShowMore = ({ text, maxLength = 100 }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  if (text.length <= maxLength) return <p>{text}</p>;
  
  return (
    <div>
      <p>{isExpanded ? text : `${text.slice(0, maxLength)}...`}</p>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="text-blue-500 hover:text-blue-700 font-semibold mt-2"
      >
        {isExpanded ? 'Show Less' : 'Show More'}
      </button>
    </div>
  );
};

const ViewPostButton = ({ url }: { url: string }) => (
  <a
    href={url}
    target="_blank"
    rel="noopener noreferrer"
    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
  >
    View Post
    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
  </a>
);

export default function InstagramData({ data }: InstagramDataProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [processedData, setProcessedData] = useState([]);
  const itemsPerPage = 5;

  useEffect(() => {
    if (data && data.length > 1) {
      const headers = data[0];
      const rows = data.slice(1);
      const combinedRows = [];
      const seenPosts = new Set();

      rows.forEach((row) => {
        const rowData = {};
        headers.forEach((header, index) => {
          rowData[header] = row[index] || '';
        });

        const postKey = `${rowData['Post URL']}-${rowData['Post Content']}-${rowData['OCR Text']}`;
        if (!seenPosts.has(postKey)) {
          seenPosts.add(postKey);
          combinedRows.push({
            ...rowData,
            comments: [{
              username: rowData['Comment Username'],
              text: rowData['Comment Text']
            }]
          });
        } else {
          const existingRow = combinedRows.find(r => 
            r['Post URL'] === rowData['Post URL'] &&
            r['Post Content'] === rowData['Post Content'] &&
            r['OCR Text'] === rowData['OCR Text']
          );
          if (existingRow) {
            existingRow.comments.push({
              username: rowData['Comment Username'],
              text: rowData['Comment Text']
            });
          }
        }
      });

      setProcessedData(combinedRows);
    }
  }, [data]);

  const pageCount = Math.ceil(processedData.length / itemsPerPage);
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = processedData.slice(indexOfFirstItem, indexOfLastItem);

  const renderTableHeader = () => (
    <tr>
      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post URL</th>
      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Post Content</th>
      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">OCR Text</th>
      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Comments</th>
    </tr>
  );

  const renderTableRows = () => {
    return currentItems.map((row, rowIndex) => (
      <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
        <td className="px-6 py-4 text-sm text-gray-900">
          <ViewPostButton url={row['Post URL']} />
        </td>
        <td className="px-6 py-4 text-sm text-gray-900">
          <TextWithShowMore text={row['Post Content']} maxLength={100} />
        </td>
        <td className="px-6 py-4 text-sm text-gray-900">
          <TextWithShowMore text={row['OCR Text']} maxLength={100} />
        </td>
        <td className="px-6 py-4 text-sm text-gray-900">
          {row.comments.map((comment, index) => (
            <div key={index} className="mb-2">
              <strong>{comment.username}:</strong> {comment.text}
            </div>
          ))}
        </td>
      </tr>
    ));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white shadow-xl rounded-lg overflow-hidden"
    >
      <h2 className="text-2xl font-semibold text-gray-800 p-6">Scraped Data</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            {renderTableHeader()}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {renderTableRows()}
          </tbody>
        </table>
      </div>
      <div className="flex justify-between items-center p-4">
        <button
          onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
          disabled={currentPage === 1}
          className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-l disabled:opacity-50"
        >
          Previous
        </button>
        <span className="text-gray-700">
          Page {currentPage} of {pageCount}
        </span>
        <button
          onClick={() => setCurrentPage(prev => Math.min(prev + 1, pageCount))}
          disabled={currentPage === pageCount}
          className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-r disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </motion.div>
  );
}