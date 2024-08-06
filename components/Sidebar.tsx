import Link from 'next/link'
import { useRouter } from 'next/router'
import { FaHome, FaInstagram, FaChartBar } from 'react-icons/fa'

const Sidebar = () => {
  const router = useRouter()

  const isActive = (path: string) => router.pathname === path

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: FaHome },
    { path: '/instagram-scraper', label: 'Instagram Scraper', icon: FaInstagram },
    { path: '/view-data', label: 'View Data', icon: FaChartBar },
  ]

  return (
    <div className="bg-gray-900 text-white w-64 space-y-6 py-7 px-2 absolute inset-y-0 left-0 transform -translate-x-full md:relative md:translate-x-0 transition duration-200 ease-in-out">
      <div className="flex items-center justify-center mb-8">
        <span className="text-2xl font-semibold">Job Fraud Detector</span>
      </div>
      <nav>
        {menuItems.map((item) => (
          <Link key={item.path} href={item.path} className={`flex items-center space-x-2 py-2.5 px-4 rounded transition duration-200 ${
            isActive(item.path) ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'
          }`}>
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </div>
  )
}

export default Sidebar