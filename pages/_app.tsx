import '../styles/globals.css'
import type { AppProps } from 'next/app'
import Sidebar from '../components/Sidebar'
import Head from 'next/head'
import DarkModeToggle from '../components/DarkModeToggle'

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>Fraud Job Detection Dashboard</title>
        <meta name="description" content="Dashboard for detecting fraudulent job postings" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className="flex h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-200">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <header className="bg-white dark:bg-gray-800 shadow-sm z-10 transition-colors duration-200">
            <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
              <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">Fraud Job Detection Dashboard</h1>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500 dark:text-gray-400">Welcome, User</span>
                <DarkModeToggle />
                <button className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded-md text-sm">Logout</button>
              </div>
            </div>
          </header>
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 dark:bg-gray-900 transition-colors duration-200">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <Component {...pageProps} />
            </div>
          </main>
        </div>
      </div>
    </>
  )
}

export default MyApp