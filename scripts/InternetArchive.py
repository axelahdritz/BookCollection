import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from scripts.OCR import run_OCR
from scripts.utilities import is_page_empty

class InternetArchiveBook:

  def __init__(self, url, start_page, end_page, is_borrow, last_page_full, page_num_diff):
    self.url = url
    options = webdriver.ChromeOptions()
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    self.driver = webdriver.Chrome(
      executable_path="/Users/axelahdritz/coding_projects/BookCollection/chromedriver",
      chrome_options=options)
    self.driver.get(self.url)
    self.username = "ahdritzaxel@gmail.com"
    self.password = "Garammasala2806!"
    self.start_page = start_page
    self.end_page = end_page
    self.is_borrow = is_borrow
    self.last_page_full = last_page_full
    self.page_num_diff = page_num_diff

  def expand_shadow_element(self, element):
    shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', element)
    return shadow_root

  def login(self):
    time.sleep(2)
    element = self.driver.find_element("xpath", 
      '//*[@id="topnav"]/ia-topnav/div[1]/primary-nav/nav/div[2]/login-button/div/span/a[2]')
    element.click()
    time.sleep(2)
    self.driver.find_element("name", "username").send_keys(self.username)
    # find password input field and insert password as well
    self.driver.find_element("name", "password").send_keys(self.password)
    # click login button
    self.driver.find_element("name", "submit-to-login").click()
    time.sleep(5)

  def borrow(self):
    open1 = self.driver.find_element(By.XPATH, '//*[@id="IABookReaderMessageWrapper"]/ia-book-actions')
    shadow_root1 = self.expand_shadow_element(open1)
    open2 = shadow_root1.find_element(By.CSS_SELECTOR, 'section > collapsible-action-group')
    shadow_root2 = self.expand_shadow_element(open2)
    borrow_button = shadow_root2.find_element(By.CSS_SELECTOR,
     'div > section.action-buttons.primary > button.ia-button.primary.initial')
    borrow_button.click()
    time.sleep(20)

  def ret(self):
    close1 = self.driver.find_element(By.XPATH, '//*[@id="IABookReaderMessageWrapper"]/ia-book-actions')
    shadow_root1 = self.expand_shadow_element(close1)
    close2 = shadow_root1.find_element(By.CSS_SELECTOR, 'section > collapsible-action-group')
    shadow_root2 = self.expand_shadow_element(close2)
    return_button = shadow_root2.find_element(By.CSS_SELECTOR, 
      'div > section.action-buttons.primary > button.ia-button.danger.initial')
    return_button.click()
  
  def config(self):
    # get next page button
    right_button_xpath = '//*[@id="BookReader"]/div[2]/div/nav/ul[2]/li[3]/button'
    right_button = self.driver.find_element(By.XPATH, right_button_xpath)

    # get previous page button
    left_button_xpath = '//*[@id="BookReader"]/div[2]/div/nav/ul[2]/li[2]/button'
    left_button = self.driver.find_element(By.XPATH, left_button_xpath)

    # get fullscreen
    fullscreen_xpath = '//*[@id="BookReader"]/div[2]/div/nav/ul[2]/li[11]/button'
    fullscreen_button = self.driver.find_element(By.XPATH, fullscreen_xpath)
    fullscreen_button.click()
    self.driver.maximize_window()
    time.sleep(2)

    # arrive at correct page
    page_view_xpath = '//*[@id="BookReader"]/div[2]/div/nav/ul[2]/li[4]/button'
    page_view_button = self.driver.find_element(By.XPATH, page_view_xpath)
    page_view_button.click()

    time.sleep(2)
    
    # get page numbers
    page_num_xpath = '//*[@id="BookReader"]/div[2]/div/nav/ul[2]/li[1]/p/span'
    page_numbers = self.driver.find_element(By.XPATH, page_num_xpath)
    page_num = int(re.sub('(\(|\))', '', page_numbers.text).split(' ')[0])

    if self.page_num_diff:
      previous_page = page_num - 1
      while page_num - 1 == previous_page:
        right_button.click()
        previous_page = page_num
        time.sleep(2)
        page_numbers = self.driver.find_element(By.XPATH, page_num_xpath)
        page_num = int(re.sub('(\(|\))', '', page_numbers.text).split(' ')[0])
    
    time.sleep(2)
    if page_num != self.start_page:
      while page_num != self.start_page:
        page_num += 1
        right_button.click()
        time.sleep(2)
      
    page_numbers = self.driver.find_element(By.XPATH, page_num_xpath)
    total_pages = int(re.sub('(\(|\))', '', page_numbers.text).split(' ')[-1])
    if total_pages == self.end_page:
      total_pages += 2
    
    # book view
    book_view_xpath = '//*[@id="BookReader"]/div[2]/div/nav/ul[2]/li[5]/button'
    book_view_button = self.driver.find_element(By.XPATH, book_view_xpath)
    book_view_button.click()
    time.sleep(1)

    # double check which page we are on
    first_flag = 0
    left_button.click()
    time.sleep(1)
    right_button.click()
    time.sleep(1)
    page_numbers = self.driver.find_element(By.XPATH, page_num_xpath)
    page_num_alt = int(re.sub('(\(|\))', '', page_numbers.text).split(' ')[0])
    if page_num_alt == page_num:
      first_flag = 1
    time.sleep(2)

    return right_button, left_button, page_num, total_pages, first_flag

  def extract_text(self):
    # login to instance and borrow the book
    self.login()
    if self.is_borrow == 1:
      self.borrow()

    right_button, left_button, page_num, total_pages, first_flag = self.config()

    # take screenshot
    full_text = []
    num_backtracks = 0
    page_num_xpath = '//*[@id="BookReader"]/div[2]/div/nav/ul[2]/li[1]/p/span'
    for i in range(page_num, total_pages, 2):
      # check to see if on start page or end page
      page_numbers = self.driver.find_element(By.XPATH, page_num_xpath)
      page_number = int(re.sub('(\(|\))', '', page_numbers.text).split(' ')[0])

      if page_number <= self.end_page:
        # take screenshot of the webpage
        file_name = '{num}.png'.format(num=i)
        self.driver.get_screenshot_as_file(file_name)
        right_button.click()
        if num_backtracks > 5:
          time.sleep(3)
        # extract text from the image and clean it of page numbers
        if self.borrow:
          text = run_OCR(file_name, 'eng', 80, 120, 3500, 1960)
        else:
          text = run_OCR(file_name, 'eng', 80, 30, 3500, 1960)
        os.remove(file_name)
        if i != page_num and page_number != self.end_page:
          page_empty1 = is_page_empty(text[0])
          page_empty2 = is_page_empty(text[1])
          if page_empty1 or page_empty2:
            num_backtracks += 1
            left_button.click()
            time.sleep(2)
            self.driver.get_screenshot_as_file(file_name)
            right_button.click()
            if self.borrow:
              text = run_OCR(file_name, 'eng', 80, 120, 3500, 1960)
            else:
              text = run_OCR(file_name, 'eng', 80, 30, 3500, 1960)
            os.remove(file_name)
        if i == page_num and first_flag == 0:
          full_text.append(text[1])
        elif i == page_num and first_flag == 1:
          full_text.extend(text)
        elif i != page_num and page_number != self.end_page:
          full_text.extend(text)
        elif self.last_page_full == 1:
          full_text.extend(text)
        else:
          full_text.append(text[0])
    
    # return the book
    if self.is_borrow == 1:
      self.ret()
    return full_text

  def quit(self):
    self.driver.quit()
  
  def main(self):
    full_text = self.extract_text()
    self.quit()
    return full_text