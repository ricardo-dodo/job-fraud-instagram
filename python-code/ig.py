import csv
import time
import os
import random
import logging
import asyncio
from playwright.async_api import async_playwright, TimeoutError
from dotenv import load_dotenv

class InstagramScraper:
    def __init__(self):
        load_dotenv()
        self.BASE_URL = "https://www.instagram.com"
        self.PROFILE = "loker_it"
        self.CSV_FILE = "instagram_posts.csv"
        self.IMAGE_DIR = "instagram_images"
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler('instagram_scraper.log')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)

    async def check_for_login_prompt(self, page):
        try:
            login_prompt = await page.wait_for_selector('text="Log in to Instagram"', timeout=5000)
            if login_prompt:
                logging.warning("Login prompt detected. Please log in manually.")
                input("Press Enter after you've logged in...")
                await page.reload()
                await page.wait_for_load_state('networkidle')
                return True
        except TimeoutError:
            pass  # No login prompt found, which is fine
        return False

    async def get_posts(self, page):
        await page.goto(f"{self.BASE_URL}/{self.PROFILE}/")
        await page.wait_for_load_state('networkidle')
        
        while True:
            # Scroll to bottom
            previous_height = await page.evaluate('document.body.scrollHeight')
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)  # Wait for 2 seconds after scrolling
            
            # Check for login prompt
            login_detected = await self.check_for_login_prompt(page)
            if login_detected:
                continue  # Start the loop again to retry scrolling
            
            # Check for "Show more posts" button
            show_more_button = await page.query_selector('text="Show more posts from loker_it"')
            if show_more_button:
                await show_more_button.click()
                await page.wait_for_load_state('networkidle')
                continue  # Start the loop again to scroll further
            
            # Check if we've reached the end
            new_height = await page.evaluate('document.body.scrollHeight')
            if new_height == previous_height:
                # If no new content loaded after scrolling, we've reached the end
                break

        posts = await page.evaluate('''
            () => {
                const links = Array.from(document.querySelectorAll('article a'));
                return links.map(link => link.href).filter(href => href.includes('/p/'));
            }
        ''')
        logging.info(f"Found {len(posts)} posts")
        return posts

    async def extract_post_data(self, page, url):
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        
        try:
            # Wait for the content to load
            await page.wait_for_selector('article', timeout=10000)

            # Extract post content
            post_content = await page.evaluate('''
                () => {
                    const contentElement = document.querySelector('div[class*="_a9zs"]');
                    return contentElement ? contentElement.innerText : 'No content found';
                }
            ''')

            # Extract likes (this might not be visible for all posts)
            likes = "N/A"
            try:
                likes_element = await page.wait_for_selector('section span', timeout=5000)
                likes = await likes_element.inner_text()
            except TimeoutError:
                logging.warning(f"Likes not found for post: {url}")

            # Scroll to load more comments
            for _ in range(3):  # Adjust this number to scroll more or less
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(1000)  # Wait for 1 second after each scroll

            # Extract comments using the alternative method, filtering out "No text" comments
            comments = await page.evaluate('''
                () => {
                    const comments = Array.from(document.querySelectorAll('ul > div > li'));
                    return comments.map(comment => {
                        const username = comment.querySelector('a')?.innerText || 'Unknown';
                        const text = comment.querySelector('div > div > div > span')?.innerText || '';
                        return {username, text};
                    }).filter(comment => comment.text !== '' && comment.text !== 'No text');
                }
            ''')
            
            logging.info(f"Extracted {len(comments)} valid comments for post: {url}")

            # Take screenshot of the post image
            img = await page.query_selector('article img')
            if img:
                filename = f"{self.IMAGE_DIR}/img_{int(time.time())}.jpg"
                await img.screenshot(path=filename)
                logging.info(f"Image saved: {filename}")
            else:
                filename = "N/A"
                logging.error(f"No image found for post: {url}")

            return {
                'url': url,
                'content': post_content,
                'likes': likes,
                'comments': comments,
                'filename': filename
            }
        except Exception as e:
            logging.error(f"Failed to extract data from post: {url}. Error: {str(e)}")
            return None

    async def extract_and_download_posts(self, page):
        posts = await self.get_posts(page)
        
        if not posts:
            logging.error("No posts retrieved")
            return
        
        os.makedirs(self.IMAGE_DIR, exist_ok=True)
        
        with open(self.CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Post URL', 'Post Content', 'Likes', 'Image Filename', 'Comment Username', 'Comment Text'])

            for post_url in posts[:10]:  # Limit to first 10 posts for testing
                logging.info(f"Processing post: {post_url}")
                post_data = await self.extract_post_data(page, post_url)
                if post_data:
                    valid_comments = [c for c in post_data['comments'] if c['text'] != 'No text']
                    if valid_comments:
                        # Write each valid comment with post data
                        for comment in valid_comments:
                            writer.writerow([
                                post_data['url'],
                                post_data['content'],
                                post_data['likes'],
                                post_data['filename'],
                                comment['username'],
                                comment['text']
                            ])
                        logging.info(f"Processed post {post_url} with {len(valid_comments)} valid comments")
                    else:
                        # If there are no valid comments, still write the post data with empty comment fields
                        writer.writerow([
                            post_data['url'],
                            post_data['content'],
                            post_data['likes'],
                            post_data['filename'],
                            '',  # Empty username for posts without valid comments
                            ''   # Empty comment text for posts without valid comments
                        ])
                        logging.info(f"Processed post {post_url} with no valid comments")
                else:
                    logging.error(f"Failed to process post: {post_url}")
                await asyncio.sleep(random.uniform(1, 3))

    async def run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Set to False for debugging
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            try:
                await self.extract_and_download_posts(page)
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
            finally:
                await browser.close()

if __name__ == "__main__":
    scraper = InstagramScraper()
    asyncio.run(scraper.run())