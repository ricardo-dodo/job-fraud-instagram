import csv
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

class InstagramScraper:
    def __init__(self):
        load_dotenv()
        self.USERNAME = os.getenv("INSTAGRAM_USERNAME")
        self.PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
        self.BASE_URL = "https://www.instagram.com"
        self.PROFILE = "loker_it"
        self.CSV_FILE = "instagram_posts.csv"
        self.SCROLL_PAUSE_TIME = 2
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 3)

    def login(self):
        self.driver.get(f"{self.BASE_URL}/accounts/login/")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(self.USERNAME)
        self.driver.find_element(By.NAME, "password").send_keys(self.PASSWORD + Keys.RETURN)
        time.sleep(5)  # Wait for login to complete

    def navigate_to_profile(self):
        self.driver.get(f"{self.BASE_URL}/{self.PROFILE}/")

    @staticmethod
    def download_image(url, filename):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"Image downloaded: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download image: {e}")

    def get_posts(self):
        return self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article div img")))

    @staticmethod
    def combine_images_vertically(images_list):
        imgs = [Image.open(BytesIO(requests.get(url).content)) for url in images_list]
        max_width = max(i.width for i in imgs)
        total_height = sum(i.height for i in imgs)
        combined_image = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for img in imgs:
            combined_image.paste(img, (0, y_offset))
            y_offset += img.height
        return combined_image

    def scroll_to_end(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                try:
                    load_more_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Load More']")))
                    load_more_button.click()
                    time.sleep(self.SCROLL_PAUSE_TIME)
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                except TimeoutException:
                    print("Reached the end of the page or there is no 'Load More' button.")
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(self.SCROLL_PAUSE_TIME)
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        print("Confirmed the end of the page after scrolling back to the top.")
                        break
                    else:
                        last_height = new_height
            else:
                last_height = new_height

    def extract_and_download_posts(self):
        self.navigate_to_profile()
        time.sleep(2)

        post_counter = 0
        with open("posts.csv", mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            if file.tell() == 0:
                writer.writerow(['Image URL', 'Timestamp', 'Filename'])
            posts = self.get_posts()
            if posts:
                first_post = posts[0]
                self.driver.execute_script("arguments[0].scrollIntoView();", first_post)
                self.wait.until(EC.element_to_be_clickable(first_post))
                self.driver.execute_script("arguments[0].click();", first_post)
                time.sleep(2)

            while True:
                image_urls = []
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog'] img")))
                    
                    image_element = self.driver.find_element(By.CSS_SELECTOR, "div[role='dialog'] img")
                    image_url = image_element.get_attribute('src')
                    image_urls.append(image_url)

                    timestamp_element = self.driver.find_element(By.CSS_SELECTOR, "div[role='dialog'] time")
                    timestamp = timestamp_element.get_attribute('datetime')
                    year = timestamp.split('-')[0]
                    if year < '2022':
                        print(f"Encountered a post from {year}, which is before 2022. Ending the process.")
                        break                
                    if '2022' not in timestamp:
                        next_button = self.driver.find_element(By.XPATH, "//div[contains(@class,'_aaqg _aaqh')]//button[@type='button']")
                        next_button.click()
                        time.sleep(1)
                        continue

                    while True:
                        try:
                            next_image_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Next']")
                            next_image_button.click()
                            time.sleep(1)
                            image_element = self.driver.find_element(By.CSS_SELECTOR, "div[role='dialog'] img")
                            image_url = image_element.get_attribute('src')
                            if image_url not in image_urls:
                                image_urls.append(image_url)
                        except NoSuchElementException:
                            break

                    filename_prefix = timestamp.split('T')[0] + "_post_" + self.PROFILE + str(post_counter) 
                    if len(image_urls) > 1:
                        combined_image = self.combine_images_vertically(image_urls)
                        combined_filename = f"{filename_prefix}_combined.jpg"
                        combined_image_path = f"downloaded_images/{combined_filename}"
                        combined_image.save(combined_image_path)
                        writer.writerow(['; '.join(image_urls), timestamp, combined_filename])
                    else:
                        single_filename = f"{filename_prefix}_image.jpg"
                        single_image_path = f"downloaded_images/{single_filename}"
                        self.download_image(image_urls[0], single_image_path)
                        writer.writerow([image_urls[0], timestamp, single_filename])

                    post_counter += 1

                    next_post_button = self.driver.find_element(By.XPATH, "//div[contains(@class,'_aaqg _aaqh')]//button[@type='button']")
                    next_post_button.click()
                    time.sleep(1)

                    if post_counter % 20 == 0:
                        print(f"Processed {post_counter} posts. Taking a short break.")

                except Exception as e:
                    print(f"An error occurred at post {post_counter}: {e}. Moving to the next post.")
                    try:
                        next_post_button = self.driver.find_element(By.XPATH, "//div[contains(@class,'_aaqg _aaqh')]//button[@type='button']")
                        next_post_button.click()
                        time.sleep(1)
                    except Exception as next_post_exception:
                        print(f"Failed to navigate to the next post: {next_post_exception}. Exiting...")
                        break

                try:
                    self.driver.find_element(By.XPATH, "//div[contains(@class,'_aaqg _aaqh')]//button[@type='button']")
                except NoSuchElementException:
                    print("Reached the end of the posts or no next button found. Ending the process.")
                    break

        print("Finished extracting posts.")

    def run(self):
        self.login()
        self.extract_and_download_posts()
        self.driver.quit()

