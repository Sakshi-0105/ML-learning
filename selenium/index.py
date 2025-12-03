import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time

# Auto-install correct ChromeDriver
chromedriver_autoinstaller.install()

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(), options=chrome_options)
wait = WebDriverWait(driver, 10)

# Step 1: Open site
driver.get("https://example-ecommerce.com")

# Step 2: Login
wait.until(EC.element_to_be_clickable((By.ID, "login-btn"))).click()
wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("testuser")
wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys("mypassword")
driver.find_element(By.ID, "submit-login").click()

# Step 3: Search keyword
search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
search_box.send_keys("laptop")
search_box.send_keys(Keys.RETURN)

# Step 4: Random product click
products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-item a")))
random.choice(products).click()

# Step 5: Add to cart
wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart"))).click()

# Step 6: Leave (simulate abandonment)
time.sleep(3)  # small wait so action completes
driver.quit()
 