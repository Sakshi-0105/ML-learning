from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random

# Setup Chrome driver
driver = webdriver.Chrome()  # Make sure ChromeDriver is installed
driver.maximize_window()

# Open the dummy site
driver.get("http://localhost:8501")  # Streamlit default port
time.sleep(2)

# ---- LOGIN ----
driver.find_element(By.XPATH, "//input[@placeholder='Enter email']").send_keys("user@example.com")
driver.find_element(By.XPATH, "//input[@placeholder='Enter password']").send_keys("password123")
time.sleep(2)

driver.find_element(By.XPATH, "//button/div/p[contains(text(),'Login')]").click()

time.sleep(10)

# ---- SEARCH ----
search_box = driver.find_element(By.XPATH, "//input[@placeholder='Type product name...']")
search_box.send_keys("laptop")
search_button = driver.find_element(By.XPATH, "//button[contains(text(),'Search')]")
search_button.click()
time.sleep(2)

# ---- PICK RANDOM PRODUCT ----
products = driver.find_elements(By.XPATH, "//button[contains(text(),'Laptop')]")
random.choice(products).click()
time.sleep(2)

# ---- ADD TO CART ----
driver.find_element(By.XPATH, "//button[contains(text(),'Add to Cart')]").click()
time.sleep(2)

# ---- EXIT ----
driver.quit()
