import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class JobstreetScraper:
    def __init__(self):
        self.service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.companies = set()

    def navigate_to_page(self):
        self.driver.get("https://www.jobstreet.co.id/en/companies/browse-reviews/")

    def scrape_data(self):
        company_elements = self.driver.find_elements(By.XPATH, "//a[@data-automation='CompanySearchResult']/span[@class='bmf23VXrbKovb5Hw_dat']")
        rating_elements = self.driver.find_elements(By.XPATH, "//div[@data-automation='CompanyDetails']//span[@class='bmf23VXrbKovb5Hw_dat']")

        for company, rating in zip(company_elements, rating_elements):
            company_info = (company.text, rating.text)
            if company_info not in self.companies:
                self.companies.add(company_info)
                print(company_info)

    def autoscroll_to_show_more_button(self):
        try:
            show_more_button = self.driver.find_element(By.XPATH, "//span[normalize-space()='Show more companies']")
            self.driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
            return show_more_button
        except NoSuchElementException:
            return None

    def click_show_more(self):
        while (show_more_button := self.autoscroll_to_show_more_button()) is not None:
            show_more_button.click()
            time.sleep(2)  # Wait for new content to load

    def save_to_csv(self, filename='company_ratings.csv'):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Company Name', 'Rating'])  # Header
            for company_info in self.companies:
                writer.writerow(company_info)

    def run(self):
        self.navigate_to_page()
        self.scrape_data()
        self.click_show_more()
        self.save_to_csv()
        self.driver.quit()
