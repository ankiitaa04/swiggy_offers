import streamlit as st
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ========= CONFIG =========

STORE_URLS = [
   "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
   "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-stational-club-durga-mandir-purnea-purnea-698848",
   # ... add the rest of your predefined URLs ...
]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)

def get_store_name_from_url(url):
    try:
        parts = url.split('/restaurants/')[1].split('-')
        name_parts = []
        for part in parts:
            if part.isdigit():
                break
            name_parts.append(part)
        return ' '.join(name_parts).title()
    except:
        return "Unknown Store"

def scrape_single_store(driver, url):
    offers = []
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    try:
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
        ).click()
    except:
        pass

    driver.execute_script("window.scrollTo(0, 1000);")
    time.sleep(3)

    selectors = [
        "div[data-testid*='offer-card-container']",
        "div.sc-dExYaf.hQBmmU",
        "div[class*='offer']"
    ]

    for sel in selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            if els:
                for el in els:
                    text = el.text.strip()
                    if not text:
                        continue
                    lines = text.split('\n')
                    offers.append({
                        "store_name": get_store_name_from_url(url),
                        "store_url": url,
                        "title": lines[0],
                        "description": lines[1] if len(lines) > 1 else ""
                    })
                break
        except:
            continue
    return offers

def scrape_store_parallel(url):
    driver = setup_driver()
    try:
        return scrape_single_store(driver, url)
    finally:
        driver.quit()

def parallel_scrape_all_stores(urls, max_threads=5):
    total = len(urls)
    status_text = st.empty()
    all_offers = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(scrape_store_parallel, url): url for url in urls}
        for idx, future in enumerate(as_completed(future_to_url), start=1):
            url = future_to_url[future]
            try:
                offers = future.result()
                if offers:
                    all_offers.extend(offers)
            except Exception as e:
                st.error(f"❌ Error scraping {url}: {e}")
            status_text.text(f"Scraped {idx} out of {total} URLs")

    return all_offers

# ========== STREAMLIT APP ==========

st.title("🍔 Swiggy Discounts Scraper (Predefined URLs)")

if st.button("Scrape Discounts"):
    total = len(STORE_URLS)
    st.write(f"Starting scraping 0 out of {total} URLs")
    with st.spinner("Scraping discounts from predefined stores..."):
        offers = parallel_scrape_all_stores(STORE_URLS, max_threads=5)

    if offers:
        st.success(f"✅ {len(offers)} discounts scraped.")
        st.dataframe(offers)
    else:
        st.warning("❌ No discounts found.")
