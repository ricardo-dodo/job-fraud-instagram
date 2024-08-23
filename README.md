# Fraud Detection in Job Postings

This project aims to detect fraudulent job postings using machine learning techniques. It includes several steps from data collection to model training and evaluation, with a web-based dashboard for interaction.

## Project Description

The project consists of two main parts:

1. A Python backend for scraping Instagram posts, performing OCR, and processing data.
2. A Next.js frontend for user interaction and data visualization.

Key features include:
- Instagram scraping using Playwright
- OCR processing with EasyOCR
- Data storage in MongoDB
- Web dashboard for initiating scrapes and viewing results
- Dark mode support

## Prerequisites

- Node.js (v14 or later)
- Python (v3.7 or later)
- MongoDB

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install Node.js dependencies:
   ```
   npm install
   ```

3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   MONGODB_URI=your_mongodb_connection_string
   ```

## Running the Application

1. Start the development server:
   ```
   npm run dev
   ```

   This command will concurrently start the Next.js frontend and the Flask backend.

2. Open your browser and navigate to `http://localhost:3000` to access the dashboard.

## Building for Production

1. Build the Next.js application:
   ```
   npm run build
   ```

2. Start the production server:
   ```
   npm start
   ```

## Project Structure

- `/pages`: Next.js pages
- `/components`: React components
- `/styles`: CSS styles
- `/lib`: Utility functions
- `/python-code`: Python backend code
- `/public`: Static assets

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).