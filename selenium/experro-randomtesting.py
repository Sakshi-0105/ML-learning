from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random
import time

# ---------- USERS LIST ----------
users = [
    ("oliver@gmail.com", "Test@12345"),
    # ("james@gmail.com", "Test@12345"),
    # ("charlotte@gmail.com", "Tester@12345"),
    # ("henry@gmail.com", "Tester@12345"),
    # ("emily@gmail.com", "Tester@12345"),
    # ("william@gmail.com", "Tester@12345"),
    # ("sophie@gmail.com", "Tester@12345"),
    # ("george@gmail.com", "Tester@12345"),
    # ("grace@gmail.com", "Tester@12345"),
    # ("daniel@gmail.com", "Tester@12345"),
    # ("lily@gmail.com", "Tester@12345"),
    # ("thomas@gmail.com", "Tester@12345"),
    # ("ava@gmail.com", "Tester@12345"),
    # ("benjamin@gmail.com", "Tester@12345"),
    # ("mia@gmail.com", "Tester@12345"),
    # ("jack@gmail.com", "Tester@12345"),
    # ("ella@gmail.com", "Tester@12345"),
    # ("samuel@gmail.com", "Tester@12345"),
    # ("olivia@gmail.com", "Tester@12345"),
    # ("smith@gmail.com", "Test@123456789"),
]

# ---------- DRIVER SETUP ----------
driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 10)


def login_user(email, password):
    try:
        driver.get("https://experro-bnp-2.mybigcommerce.com/")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/login.php']"))).click()
        wait.until(EC.presence_of_element_located((By.ID, "login_email"))).clear()
        driver.find_element(By.ID, "login_email").send_keys(email)
        driver.find_element(By.ID, "login_pass").clear()
        driver.find_element(By.ID, "login_pass").send_keys(password)
        driver.find_element(By.XPATH, "//input[@value='Sign in']").click()

        # check if login failed (look for error message)
        time.sleep(3)
        if "login.php" in driver.current_url:
            print(f"❌ Login failed for {email}")
            return False
        print(f"✅ Login success: {email}")
        return True
    except Exception as e:
        print(f"⚠️ Login error for {email}: {e}")
        return False


def logout_user():
    try:
        # look for logout link
        driver.get("https://experro-bnp-2.mybigcommerce.com/login.php?action=logout")
        driver.delete_all_cookies()
        time.sleep(2)
        print("🔒 Logged out successfully")
    except TimeoutException:
        print("⚠️ Logout button not found, maybe already logged out")


def get_products_links():
    try:
        product_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.product article.card"))
        )
        hrefs = []
        for card in product_cards:
            try:
                link = card.find_element(By.CSS_SELECTOR, "a")
                hrefs.append(link.get_attribute("href"))
            except:
                continue
        return list(dict.fromkeys(hrefs))  # remove duplicates
    except TimeoutException:
        print("⚠️ No products found.")
        return []


def select_product_options():
    try:
        option_groups = driver.find_elements(By.CSS_SELECTOR, ".productView-options .form-field")
        for group in option_groups:
            radios = group.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            if radios:
                choice = random.choice(radios)
                driver.execute_script("arguments[0].click();", choice)
                time.sleep(1)
        print("✅ Selected product options (if any)")
    except Exception:
        print("ℹ️ No selectable options found.")


def add_random_products(search_query="zhou", visit_products=5, add_to_cart_count=2):
    try:
        # Search
        time.sleep(2)
        search_box = wait.until(EC.presence_of_element_located((By.ID, "search_query")))
        search_box.clear()
        search_box.send_keys(search_query)
        time.sleep(1)
        search_box.submit()

        # Get product links
        products = get_products_links()
        if not products:
            return

        random.shuffle(products)
        selected_products = products[: min(visit_products, len(products))]

        # Randomly pick which ones to add to cart
        add_to_cart_products = set(random.sample(selected_products, min(add_to_cart_count, len(selected_products))))

        for link in selected_products:
            try:
                driver.get(link)
                driver.execute_script("""
                    let banner = document.querySelector('.eapp-cookie-consent-widget-container');
                    if(banner){ banner.remove(); }
                """)
                product_name = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.productView-title"))
                ).text
                print(f"👉 Visited product: {product_name}")

                select_product_options()

                # Decide if this product should be added to cart
                if link in add_to_cart_products:
                    try:
                        add_btn = wait.until(
                            EC.presence_of_element_located((By.ID, "form-action-addToCart"))
                        )
                        if add_btn.is_enabled():
                            driver.execute_script("arguments[0].click();", add_btn)
                            print(f"🛒 Added to cart: {product_name}")
                            time.sleep(2)
                        else:
                            print(f"⚠️ Add to Cart disabled for {product_name}")
                    except TimeoutException:
                        print(f"⚠️ No Add to Cart button for {product_name}")
                else:
                    print(f"ℹ️ Only visited, not added to cart: {product_name}")

            except Exception as e:
                print(f"⚠️ Error handling product: {e}")
                continue

    except Exception as e:
        print(f"⚠️ Search failed: {e}")

# ---------- MAIN LOOP ----------
for email, password in users:
    if login_user(email, password):
        add_random_products("zhou", 5)

        # Go to cart (optional check)
        driver.get("https://experro-bnp-2.mybigcommerce.com/cart.php")
        driver.get("https://experro-bnp-2.mybigcommerce.com/account.php?action=edit_shipping_address&address_id=2&from=account.php%3Faction%3Daddress_book")
        from selenium.webdriver.support.ui import Select

        # locate the dropdown
        country_dropdown = wait.until(EC.presence_of_element_located((By.ID, "FormField_11_select")))

        # create Select object
        select = Select(country_dropdown)

        # select by visible text
        select.select_by_visible_text("United Kingdom")
        save_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.button.button--primary")))
        driver.execute_script("arguments[0].click();", save_btn)
        print("✅ Address submitted successfully")
        time.sleep(1)
        driver.get("https://experro-bnp-2.mybigcommerce.com/checkout.php")

        country_dropdown = wait.until(EC.presence_of_element_located((By.ID, "countryCodeInput")))
        # create Select object
        select = Select(country_dropdown)
        
        select.select_by_visible_text("United States")
        
        state_dropdown = wait.until(EC.presence_of_element_located((By.ID, "provinceCodeInput")))

        # create Select object
        select = Select(state_dropdown)

        # select by visible text
        select.select_by_visible_text("Alabama")
        save_btn = wait.until(EC.element_to_be_clickable((By.ID, "checkout-shipping-continue")))
        driver.execute_script("arguments[0].click();", save_btn)
        time.sleep(10)
        cod_radio = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "radio-cod"))
     )
        driver.execute_script("arguments[0].click();", cod_radio)
        print("✅ Selected Cash on Delivery")

    # Wait for "Place Order" button and click it
        place_order_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "checkout-payment-continue"))
    )
        driver.execute_script("arguments[0].click();", place_order_btn)
        print("✅ Order placed successfully (clicked Place Order)")

        print(f"✅ Cart page opened for {email}")
        time.sleep(20)
        logout_user() 

print("🎯 All users processed.")
driver.quit()
