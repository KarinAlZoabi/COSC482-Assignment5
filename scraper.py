import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from datetime import datetime

# Setup WebDriver with dynamic user-agents
def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Rotate User-Agent to prevent detection
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def scrape_ebay_products():
    try:
        driver = setup_driver()
        driver.get("https://www.ebay.com/globaldeals/tech")

        print("scrolling down...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Wait for new results to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Stop scrolling if no more content is loaded
            last_height = new_height
  

        products = []
        product_elements = driver.find_elements(By.XPATH, '//div[@class="item"]')

        print("looping through products...")
        for product in product_elements:
            try: 
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except:
                timestamp = "N/A"
            try:
                title = product.find_element(By.XPATH, './/span[contains(@class,"ebayui-ellipsis-3") or contains(@class, "ebayui-ellipsis-2")]').text
            except:
                title = "N/A"
            try:
                price = product.find_element(By.XPATH, ".//div[@class='dne-itemtile-price']//span[@class='first']").text
            except:
                price = "N/A"
            try:
                original_price = product.find_element(By.XPATH, ".//div[@class='dne-itemtile-original-price']//span[@class='itemtile-price-strikethrough']").text
            except:
                original_price = "not available"
            try:
                shipping = product.find_element(By.CLASS_NAME, 'dne-itemtile-delivery').text
            except:
                shipping = "N/A"
            try:
                item_url = product.find_element(By.XPATH, ".//a[@itemprop='url']").get_attribute("href")
            except:
                item_url = "Not Found"
            
            
            products.append({"Timestamp": timestamp, "Title": title, "Price": price,"Original Price": original_price, "Shipping": shipping, "Item Url": item_url})
            
        driver.quit()
            
        return products

    except Exception as e:
        print("Error")
        return []
    
def save_to_csv(data):
    """Save scraped data to CSV."""
    file_name = "ebay_tech_deals.csv"
    try:
        # Read existing file if it exists
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        # Create an empty DataFrame if the file doesn't exist
        df = pd.DataFrame(columns=[
            "Timestamp", "Title", "Price", "Original Price",
            "Shipping", "Item Url"
        ])

    # Convert the list of dictionaries to a DataFrame
    new_data = pd.DataFrame(data)

    # Concatenate the new data with the existing DataFrame
    df = pd.concat([df, new_data], ignore_index=True)

    # Save back to CSV
    df.to_csv(file_name, index=False)

def main():

    print("starting to scrape...")
    ebay_products = scrape_ebay_products()
    # Save data
    if ebay_products:
        save_to_csv(ebay_products)
    else:
        print("No data saved.")

if __name__ == '__main__':
    main()