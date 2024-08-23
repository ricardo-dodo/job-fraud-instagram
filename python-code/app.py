from flask import Flask, request, jsonify
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
from pymongo import MongoClient
import sys

app = Flask(__name__)

# Set up logging once at the module level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger(__name__)
logger.addHandler(console_handler)

class InstagramScraper:
    def __init__(self, profile):
        load_dotenv()
        self.BASE_URL = "https://www.instagram.com"
        self.PROFILE = profile
        self.USERNAME = os.getenv('INSTAGRAM_USERNAME')
        self.PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
        self.PROFILE_URL = f"{self.BASE_URL}/{self.PROFILE}/"
        self.reader = easyocr.Reader(['id','en'])  # Initialize EasyOCR with English and Indonesian

    async def login(self, page):
        await page.goto(f"{self.BASE_URL}/accounts/login/")
        await page.wait_for_selector('input[name="username"]')
        await page.fill('input[name="username"]', self.USERNAME)
        await page.fill('input[name="password"]', self.PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        logger.info("Login attempted")

        await page.goto(self.PROFILE_URL)
        await page.wait_for_load_state('networkidle')
        logger.info(f"Navigated to profile: {self.PROFILE_URL}")

    async def get_first_post(self, page):
        try:
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await page.wait_for_load_state('networkidle', timeout=5000)
            
            current_url = page.url
            logger.info(f"Current page URL: {current_url}")
            
            await page.wait_for_selector('body', timeout=10000)
            
            page_title = await page.title()
            logger.info(f"Page title: {page_title}")
            
            # Try multiple selectors
            selectors = [
                'div.x1lliihq.x1n2onr6.xh8yej3 a[href^="/p/"]',
                'article a[href^="/p/"]',
                'div[role="presentation"] a[href^="/p/"]'
            ]
            
            for selector in selectors:
                logger.info(f"Trying selector: {selector}")
                try:
                    first_post = await page.wait_for_selector(selector, timeout=10000)
                    if first_post:
                        logger.info("Found first post, clicking it")
                        await first_post.click()
                        await page.wait_for_selector('div[role="dialog"]', timeout=10000)
                        logger.info("Post preview loaded")
                        return True
                except Exception as e:
                    logger.warning(f"Selector {selector} failed: {str(e)}")
            
            logger.error("Could not find any posts using the selectors")
            
            page_content = await page.content()
            logger.debug(f"Page content: {page_content[:2000]}...")
            
            return False
        except Exception as e:
            logger.error(f"Error in get_first_post: {str(e)}")
            return False

    async def extract_post_data(self, page):
        try:
            await page.wait_for_selector('div[role="dialog"]', timeout=10000)
            logger.debug("Dialog selector found")

            post_url = await page.evaluate('''
                () => {
                    const linkElement = document.querySelector('div[role="dialog"] a[href^="/p/"]');
                    return linkElement ? linkElement.href : null;
                }
            ''')
            logger.debug(f"Post URL: {post_url}")

            post_content = await page.evaluate('''
                () => {
                    const contentElement = document.querySelector('div[role="dialog"] h1');
                    return contentElement ? contentElement.innerText : 'No content found';
                }
            ''')
            logger.debug(f"Post content: {post_content[:50]}...")  # Log first 50 characters

            ocr_text = ''
            try:
                logger.debug("Attempting to find image")
                img = await page.query_selector('div[role="dialog"] div._aagu img')
                if img:
                    logger.debug("Image found, attempting screenshot")
                    img_buffer = await img.screenshot()
                    logger.debug("Screenshot taken, converting to numpy array")
                    img_np = np.frombuffer(img_buffer, np.uint8)
                    img_np = cv2.imdecode(img_np, cv2.IMREAD_COLOR)  # Convert to OpenCV format
                    logger.debug("Performing OCR")
                    ocr_result = self.reader.readtext(img_np)
                    ocr_text = ' '.join([text for _, text, _ in ocr_result])
                    logger.info(f"OCR performed on image, result: {ocr_text[:50]}...")  # Log first 50 characters
                else:
                    logger.warning("No image found for post")
            except Exception as e:
                logger.error(f"Error during image processing or OCR: {str(e)}")
                ocr_text = "OCR processing failed"

            logger.debug("Extracting comments")
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
            
            logger.info(f"Extracted {len(comments)} valid comments for post")

            return {
                'url': post_url,
                'content': post_content,
                'comments': comments,
                'ocr_text': ocr_text
            }
        except Exception as e:
            logger.error(f"Failed to extract data from post. Error: {str(e)}")
            return None

    async def extract_and_download_posts(self, page):
        if not await self.get_first_post(page):
            logger.error("No posts found or couldn't open preview. Ending extraction process.")
            return None
        
        posts_data = []
        post_count = 0
        max_posts = 2  # Increase this number to scrape more posts

        while post_count < max_posts:
            logger.info(f"Processing post {post_count + 1}")
            
            post_data = await self.extract_post_data(page)
            if post_data:
                posts_data.append(post_data)
                logger.info(f"Processed post {post_count + 1} with {len(post_data['comments'])} comments")
            else:
                logger.error(f"Failed to process post {post_count + 1}")

            next_button = await page.query_selector('button svg[aria-label="Next"]')
            if next_button:
                await next_button.click()
                await page.wait_for_selector('div[role="dialog"]', state='visible', timeout=10000)
            else:
                logger.info("No more posts to process")
                break

            post_count += 1
            await asyncio.sleep(random.uniform(2, 4))

        logger.info(f"Finished processing {post_count} posts")
        
        return posts_data

    async def run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            try:
                logger.info("Starting login process")
                await self.login(page)
                logger.info("Login successful, starting data extraction")
                data = await self.extract_and_download_posts(page)
                logger.info("Data extraction complete")
                return data
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                return None
            finally:
                await browser.close()

@app.route('/scrape', methods=['POST'])
def scrape_profile():
    profile = request.json.get('profile')
    if not profile:
        return jsonify({"error": "Profile is required"}), 400

    try:
        scraper = InstagramScraper(profile)
        data = asyncio.run(scraper.run())
        if data:
            client = MongoClient(os.getenv('MONGODB_URI'))
            db = client['instagram_scraper']
            collection = db['scraped_data']
            
            # Add profile name to each document
            for item in data:
                item['profile'] = profile
            
            result = collection.insert_many(data)
            return jsonify({"message": f"Inserted {len(result.inserted_ids)} documents into MongoDB for profile: {profile}"}), 200
        else:
            return jsonify({"error": f"No data was scraped for profile: {profile}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred during scraping: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)