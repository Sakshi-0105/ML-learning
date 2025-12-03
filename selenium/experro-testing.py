from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random
import time

driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 20)


# ---- OPEN SITE ----
driver.get("https://experro-bnp-2.mybigcommerce.com/")

# ---- LOGIN ----
wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/login.php']"))).click()
wait.until(EC.presence_of_element_located((By.ID, "login_email"))).send_keys("sakshi.sharma@rapidops.com")
driver.find_element(By.ID, "login_pass").send_keys("Tiger@18")
driver.find_element(By.XPATH, "//input[@value='Sign in']").click()

# ---- SEARCH ----
time.sleep(5)
search_box = wait.until(EC.presence_of_element_located((By.ID, "search_query")))
search_box.send_keys("zhou")
time.sleep(5)
search_box.submit()

def get_products():
    return wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.product")))

products = get_products()
top_10 = products[:5]  # keep 5 products only for testing

for i in range(len(top_10)):
    products = get_products()
    product = products[i]

    link = product.find_element(By.CSS_SELECTOR, "article.card a")

    # remove cookie banner if blocking
    driver.execute_script("""
        let banner = document.querySelector('.eapp-cookie-consent-widget-container');
        if(banner){ banner.remove(); }
    """)

    driver.execute_script("arguments[0].click();", link)
    product_name = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.productView-title"))
    ).text
    print("👉 Selected:", product_name)

    try:
        wait.until(EC.presence_of_element_located((By.ID, "form-action-addToCart")))
    except TimeoutException:
        print("❌ Product page not loaded")
        driver.back()
        continue

    # ---- CHECK VARIANTS ----
    variant_options = driver.find_elements(By.CSS_SELECTOR, "div.form-field[data-product-attribute]")
    if variant_options:
        print("⚡ Variants found, selecting one...")
        radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        if radios:
            chosen = random.choice(radios)
            driver.execute_script("arguments[0].click();", chosen)
            print(f"✅ Selected variant: {chosen.get_attribute('value')}")
        else:
            print("❌ No radio button found for variants")
    else:
        print("✅ No variant selection required")

    # ✅ Wait for mini-cart confirmation
    try:

    # ---- ADD TO CART ----
        add_btn = wait.until(EC.element_to_be_clickable((By.ID, "form-action-addToCart")))
        driver.execute_script("arguments[0].click();", add_btn)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".previewCart")))
        print("🛒 Cart popup appeared for:", product_name)
    except TimeoutException:
        print("⚠️ No popup, but item should be in cart")

    # ✅ Instead of going back, search again to refresh list
    driver.get("https://experro-bnp-2.mybigcommerce.com/search-results/?search_query=zhou&page=1&sort_by=relevance")
    time.sleep(5)

# ---- FINAL CART CHECK ----
driver.get("https://experro-bnp-2.mybigcommerce.com/cart.php")
print("✅ Opened Cart Page")

time.sleep(20)
driver.quit()
