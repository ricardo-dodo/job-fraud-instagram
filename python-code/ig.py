import csv
import time
import os
import random
import logging
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import easyocr
import io
import numpy as np
import cv2
from openpyxl import Workbook
import sys

class InstagramScraper:
    def __init__(self, profile):
        load_dotenv()
        self.BASE_URL = "https://www.instagram.com"
        self.PROFILE = profile
        self.CSV_FILE = f"{profile}_instagram_posts.csv"
        self.USERNAME = os.getenv('INSTAGRAM_USERNAME')
        self.PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
        self.PROFILE_URL = f"{self.BASE_URL}/{self.PROFILE}/"
        self.setup_logging()
        self.reader = easyocr.Reader(['id','en'])  # Initialize EasyOCR with English and Indonesian

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(console_handler)

    async def login(self, page):
        await page.goto(f"{self.BASE_URL}/accounts/login/")
        await page.wait_for_selector('input[name="username"]')
        await page.fill('input[name="username"]', self.USERNAME)
        await page.fill('input[name="password"]', self.PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        logging.info("Login attempted")

        await page.goto(self.PROFILE_URL)
        await page.wait_for_load_state('networkidle')
        logging.info(f"Navigated to profile: {self.PROFILE_URL}")

    async def get_first_post(self, page):
        try:
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await page.wait_for_load_state('networkidle', timeout=5000)
            
            current_url = page.url
            logging.info(f"Current page URL: {current_url}")
            
            await page.wait_for_selector('body', timeout=10000)
            
            page_title = await page.title()
            logging.info(f"Page title: {page_title}")
            
            # Try multiple selectors
            selectors = [
                'div.x1lliihq.x1n2onr6.xh8yej3 a[href^="/p/"]',
                'article a[href^="/p/"]',
                'div[role="presentation"] a[href^="/p/"]'
            ]
            
            for selector in selectors:
                logging.info(f"Trying selector: {selector}")
                try:
                    first_post = await page.wait_for_selector(selector, timeout=10000)
                    if first_post:
                        logging.info("Found first post, clicking it")
                        await first_post.click()
                        await page.wait_for_selector('div[role="dialog"]', timeout=10000)
                        logging.info("Post preview loaded")
                        return True
                except Exception as e:
                    logging.warning(f"Selector {selector} failed: {str(e)}")
            
            logging.error("Could not find any posts using the selectors")
            
            page_content = await page.content()
            logging.debug(f"Page content: {page_content[:2000]}...")
            
            return False
        except Exception as e:
            logging.error(f"Error in get_first_post: {str(e)}")
            return False

    async def extract_post_data(self, page):
        try:
            await page.wait_for_selector('div[role="dialog"]', timeout=10000)
            logging.debug("Dialog selector found")

            post_url = await page.evaluate('''
                () => {
                    const linkElement = document.querySelector('div[role="dialog"] a[href^="/p/"]');
                    return linkElement ? linkElement.href : null;
                }
            ''')
            logging.debug(f"Post URL: {post_url}")

            post_content = await page.evaluate('''
                () => {
                    const contentElement = document.querySelector('div[role="dialog"] h1');
                    return contentElement ? contentElement.innerText : 'No content found';
                }
            ''')
            logging.debug(f"Post content: {post_content[:50]}...")  # Log first 50 characters

            ocr_text = ''
            try:
                logging.debug("Attempting to find image")
                img = await page.query_selector('div[role="dialog"] div._aagu img')
                if img:
                    logging.debug("Image found, attempting screenshot")
                    img_buffer = await img.screenshot()
                    logging.debug("Screenshot taken, converting to numpy array")
                    img_np = np.frombuffer(img_buffer, np.uint8)
                    img_np = cv2.imdecode(img_np, cv2.IMREAD_COLOR)  # Convert to OpenCV format
                    logging.debug("Performing OCR")
                    ocr_result = self.reader.readtext(img_np)
                    ocr_text = ' '.join([text for _, text, _ in ocr_result])
                    logging.info(f"OCR performed on image, result: {ocr_text[:50]}...")  # Log first 50 characters
                else:
                    logging.warning("No image found for post")
            except Exception as e:
                logging.error(f"Error during image processing or OCR: {str(e)}")
                ocr_text = "OCR processing failed"

            logging.debug("Extracting comments")
            comments = await page.evaluate('''
                () => {
                    const comments = Array.from(document.querySelectorAll('ul._a9ym > div[role="button"]'));
                    return comments.map(comment => {
                        const username = comment.querySelector('h3 a')?.innerText || 'Unknown';
                        const text = comment.querySelector('div._a9zs span')?.innerText || '';
                        return {username, text};
                    }).filter(comment => comment.text !== '' && comment.text !== 'No text');
                }
            ''')
            
            logging.info(f"Extracted {len(comments)} valid comments for post")

            return {
                'url': post_url,
                'content': post_content,
                'comments': comments,
                'ocr_text': ocr_text
            }
        except Exception as e:
            logging.error(f"Failed to extract data from post. Error: {str(e)}")
            return None

    async def extract_and_download_posts(self, page):
        if not await self.get_first_post(page):
            logging.error("No posts found or couldn't open preview. Ending extraction process.")
            return None
        
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(['Post URL', 'Post Content', 'OCR Text', 'Comment Username', 'Comment Text'])

        post_count = 0
        max_posts = 2  # Increase this number to scrape more posts

        while post_count < max_posts:
            logging.info(f"Processing post {post_count + 1}")
            
            post_data = await self.extract_post_data(page)
            if post_data:
                if post_data['comments']:
                    for comment in post_data['comments']:
                        sheet.append([
                            post_data['url'],
                            post_data['content'],
                            post_data['ocr_text'],
                            comment['username'],
                            comment['text']
                        ])
                else:
                    sheet.append([
                        post_data['url'],
                        post_data['content'],
                        post_data['ocr_text'],
                        '', ''  # Empty fields for comment data
                    ])
                logging.info(f"Processed post {post_count + 1} with {len(post_data['comments'])} comments")
            else:
                logging.error(f"Failed to process post {post_count + 1}")

            next_button = await page.query_selector('button svg[aria-label="Next"]')
            if next_button:
                await next_button.click()
                await page.wait_for_selector('div[role="dialog"]', state='visible', timeout=10000)
            else:
                logging.info("No more posts to process")
                break

            post_count += 1
            await asyncio.sleep(random.uniform(2, 4))

        logging.info(f"Finished processing {post_count} posts")
        
        excel_file = io.BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)
        
        return excel_file

    async def run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            try:
                logging.info("Starting login process")
                await self.login(page)
                logging.info("Login successful, starting data extraction")
                excel_file = await self.extract_and_download_posts(page)
                logging.info("Data extraction complete")
                return excel_file
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
                return None
            finally:
                await browser.close()

def scrape_profile(profile):
    scraper = InstagramScraper(profile)
    excel_file = asyncio.run(scraper.run())
    if excel_file:
        file_path = os.path.abspath(f"{profile}_instagram_posts.xlsx")
        with open(file_path, "wb") as f:
            f.write(excel_file.getvalue())
        print(f"Data saved to {file_path}")
        return file_path
    else:
        print("Failed to scrape data")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ig.py <instagram_profile>")
        sys.exit(1)
    
    profile = sys.argv[1]
    file_path = scrape_profile(profile)
    
    if file_path:
        print(f"Excel file created at: {file_path}")
    else:
        print("No data was scraped, no file created.")