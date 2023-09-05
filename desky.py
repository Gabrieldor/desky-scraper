from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from multiprocessing import Pool
import time

#Number to Multi-threading
POOL = 4

class Scraper():
    LOGIN = "YOUR_EMAIL"
    PASSWORD = "YOUR_PASSWORD"

    def __init__(self):
        """
        Initializes the browser and some other selenium objects, get the emails from emails.txt and logins to the site
        """
        self.get_emails()

    def start_drivers(self):
        self.driver = webdriver.Chrome()
        self.act = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 30)
        self.login()

    def login(self):
        """
        Logins to the site using the Static Values
        """
        self.driver.get("https://nlp.desky.support/company/login")
        self.driver.find_element(By.XPATH, "//input[@type='email']").send_keys(self.LOGIN)
        self.driver.find_element(By.XPATH, "//input[@type='password']").send_keys(self.PASSWORD)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(2)
        
    def get_emails(self):
        """
        Reads each line from emails.txt and makes a list with each email
        """
        with open("emails.txt", 'r') as f:
            self.emails = [x.strip() for x in f.readlines()]

    def save_txt(self):
        with open("emails.txt", 'w') as f:
            f.truncate(0)
            for e in self.emails:
                f.write(e + '\n')

    def main_loop(self):
        with Pool(POOL) as p:
            res = p.imap_unordered(self.create_ticket, self.emails.copy())
            for r in res:
                self.emails.remove(r)
                self.save_txt()
    

    def create_ticket(self, email):
        self.start_drivers()
        """
        Iterates over each email creating new tickets for each one of them
        """
        self.driver.get("https://nlp.desky.support/create-ticket")
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//label[@for='customSelection2']")))

        self.driver.find_element(By.XPATH, "//label[@for='customSelection2']").click()
        time.sleep(1)

        self.driver.find_element(By.XPATH, "//input[@name='user_email']").send_keys(email)
        time.sleep(1)

        product_search = self.driver.find_element(By.XPATH, "//span[@data-select2-id='5']")
        self.act.move_to_element(product_search).click().perform()
        time.sleep(1)

        product = self.driver.find_element(By.XPATH, "//li[@role='option']")
        self.act.move_to_element(product).click().perform()
        time.sleep(1)

        #It sends "Testing" to subject just so it can complete the create ticket process, since it is an obligatory term
        self.driver.find_element(By.XPATH, "//input[@name='subject']").send_keys("Testing")
        time.sleep(1)
        
        """
        Insert here the other parts that you want to handle
        """
        
        btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        self.act.move_to_element(btn).perform()
        btn.click()
        
        return email


if __name__ == '__main__':
    s = Scraper()
    s.main_loop()