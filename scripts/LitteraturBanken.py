import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from scripts.OCR import run_OCR


class LitteraturBankenBook:

    def __init__(self, url, start_page, end_page, is_pdf):
        self.url = url
        options = webdriver.ChromeOptions()
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches",["enable-automation"])
        self.driver = webdriver.Chrome(
            executable_path="/Users/axelahdritz/coding_projects/BookCollection/chromedriver",
            chrome_options=options)
        self.driver.get(self.url)
        self.start_page = start_page - 1
        self.end_page = end_page - 1
        self.is_pdf = is_pdf
        time.sleep(3)
        page_num_xpath = '/html/body/div[3]/div/div/div[3]/form/a/span'
        page_num = self.driver.find_element(By.XPATH, page_num_xpath)
        self.page_numbers = int(page_num.text.split(' ')[-1])
        self.driver.maximize_window()

    def focus(self):
        time.sleep(5)
        focus_xpath = '/html/body/div[3]/div/div/div[5]/ul/li[3]/a'
        focus_button = self.driver.find_element(By.XPATH, focus_xpath)
        focus_button.click()
        time.sleep(5)

    def next_page(self):
        next_page_xpath = '/html/body/div[11]/a[3]'
        next_page_button = self.driver.find_element(By.XPATH, next_page_xpath)
        next_page_button.click()
    
    def extract_text(self):
        # loop through the rows
        full_text = []
        for i in range(self.page_numbers):
            if self.start_page <= i <= self.end_page:
                # take a screenshot of the webpage
                if self.is_pdf == 1:
                    self.driver.execute_script("document.body.style.zoom='75%'")
                    file_name = '{num}.png'.format(num=i)
                    self.driver.get_screenshot_as_file(file_name)
                    self.driver.execute_script("document.body.style.zoom='100%'")
                    self.next_page()
                    text = run_OCR(file_name, 'swe', 0, 0, 3250, 1880, is_white=True, is_pdf=self.is_pdf, litbank=True)
                else:
                    self.driver.execute_script("document.body.style.zoom='75%'")
                    file_name = '{num}.png'.format(num=i)
                    self.driver.get_screenshot_as_file(file_name)
                    self.driver.execute_script("document.body.style.zoom='100%'")
                    self.next_page()
                    text = run_OCR(file_name, 'swe', 0, 0, 3250, 1880, is_white=True, is_pdf=self.is_pdf, litbank=True)
                full_text.append(text)
                os.remove(file_name)
                print("Finshed file number {ii}!".format(ii=i))
                print("========================")
            else:
                time.sleep(1)
                self.next_page()
                time.sleep(2)
                continue
        return full_text

    def quit(self):
        self.driver.quit()

    def main(self):
        self.focus()
        full_text = self.extract_text()
        self.quit()
        return full_text