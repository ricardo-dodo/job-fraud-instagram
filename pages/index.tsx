import Link from 'next/link';
import { FaInstagram, FaChartBar, FaExclamationTriangle } from 'react-icons/fa';
import { motion } from 'framer-motion';

const DashboardCard = ({ href, title, description, icon: Icon, color }) => (
  <Link href={href}>
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={`bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 hover:shadow-xl ${color}`}
    >
      <Icon className="w-12 h-12 mb-4" />
      <h2 className="text-xl font-semibold mb-2 dark:text-white">{title}</h2>
      <p className="text-gray-600 dark:text-gray-300">{description}</p>
    </motion.div>
  </Link>
);

export default function Home() {
  return (
    <div className="container mx-auto p-8">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-4xl font-bold mb-8 text-center text-gray-800 dark:text-white"
      >
        Job Fraud Detection Dashboard
      </motion.h1>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
      >
        <DashboardCard
          href="/instagram-scraper"
          title="Instagram Scraper"
          description="Scrape job postings from Instagram"
          icon={FaInstagram}
          color="text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900"
        />
        <DashboardCard
          href="/view-data"
          title="View Data"
          description="Analyze scraped job postings"
          icon={FaChartBar}
          color="text-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900"
        />
        <DashboardCard
          href="/fraud-detection"
          title="Fraud Detection"
          description="Detect potentially fraudulent job postings"
          icon={FaExclamationTriangle}
          color="text-red-500 hover:bg-red-50 dark:hover:bg-red-900"
        />
      </motion.div>
    </div>
  );
}