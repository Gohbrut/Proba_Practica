import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from db_manager import db, Product


# The urls for web scraping
LOGIN_URL = "https://www.web-scraping.dev/login"
PRODUCTS_URL = "https://www.web-scraping.dev/products?category=consumables"


# The credentials for logging in to the website
USERNAME = "user123"
PASSWORD = "password"


def create_driver():
    """Creates and returns a Selenium Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    return driver

def login(driver):
    """Logs in to the website using the provided credentials."""
    driver.get(LOGIN_URL)

    time.sleep(2)

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)

    login_button = driver.find_element(By.TAG_NAME, "button")
    login_button.click()

    time.sleep(3)

def scrape_products(app):
    """Scrapes product data from the website and saves it to the database."""

    driver = create_driver()

    try:
        login(driver)

        driver.get(PRODUCTS_URL)

        wait = WebDriverWait(driver, 10)

        wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".row.product")
            )
        )

        products = driver.find_elements(
            By.CSS_SELECTOR,
            ".row.product"
        )

        print(f"Found {len(products)} products")

        with app.app_context():

            for product in products:

                try:

                    name = product.find_element(
                        By.CSS_SELECTOR,
                        "h3 a"
                    ).text

                    description = product.find_element(
                        By.CSS_SELECTOR,
                        ".short-description"
                    ).text

                    price = product.find_element(
                        By.CSS_SELECTOR,
                        ".price"
                    ).text

                    image_url = product.find_element(
                        By.TAG_NAME,
                        "img"
                    ).get_attribute("src")

                    existing_product = Product.query.filter_by(
                        name=name
                    ).first()

                    if existing_product:

                        existing_product.price = price
                        existing_product.description = description
                        existing_product.image_url = image_url

                    else:

                        new_product = Product(
                            name=name,
                            price=price,
                            description=description,
                            image_url=image_url
                        )

                        db.session.add(new_product)

                    db.session.commit()

                    print(f"Saved: {name}")

                except Exception as e:
                    print("Error product:", e)

    finally:
        driver.quit()
