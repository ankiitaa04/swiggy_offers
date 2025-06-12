import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def scrape_store(store_url):
    driver = setup_driver()
    offers = []

    try:
        driver.get(store_url)
        wait = WebDriverWait(driver, 10)

        offer_selectors = [
            'div[class*="styles_offersMain"]',
            'div[class*="styles_offerContainer"]',
            'div[class*="styles_offerCard"]',
        ]

        for selector in offer_selectors:
            try:
                offer_elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                for element in offer_elements:
                    offer_text = element.text.strip()
                    if offer_text and offer_text not in offers:
                        offers.append(offer_text)
                if offers:
                    break
            except:
                continue

    except Exception as e:
        st.warning(f"Error loading {store_url}: {e}")
    finally:
        driver.quit()

    return {"URL": store_url, "Offers": "\n".join(offers) if offers else "No offers found"}

STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-king-bandra-west-mumbai-17505",
    "https://www.swiggy.com/restaurants/subway-pali-hill-bandra-west-mumbai-23607",
    "https://www.swiggy.com/restaurants/faasos-wraps-and-rolls-bandra-west-mumbai-28141",
    "https://www.swiggy.com/restaurants/behrouz-biryani-bandra-west-mumbai-28142",
    "https://www.swiggy.com/restaurants/lunchbox-meals-and-thalis-bandra-west-mumbai-28144",
    "https://www.swiggy.com/restaurants/sweet-truth-cakes-and-desserts-bandra-west-mumbai-28143",
]

st.title("Swiggy Discount Offer Scraper")

if st.button("Scrape Offers"):
    st.info("Scraping in progress...")

    max_threads = 5
    results = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(scrape_store, url) for url in STORE_URLS]
        for future in futures:
            result = future.result()
            results.append(result)

    df = pd.DataFrame(results)
    st.success("Scraping complete!")
    st.dataframe(df, use_container_width=True)
