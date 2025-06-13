import streamlit as st
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-santoshpur-kolkata-737986"
    # add more URLs as needed
]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_store_name_from_url(url):
    try:
        parts = url.split('/restaurants/')[1].split('-')
        name_parts = []
        for part in parts:
            if part.isdigit():
                break
            name_parts.append(part)
        return ' '.join(name_parts).title()
    except Exception:
        return "Unknown Store"

def scrape_single_store(driver, url):
    offers = []
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        try:
            accept_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
            )
            accept_btn.click()
        except Exception:
            pass
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(2)
        selectors = [
            "div[data-testid*='offer-card-container']",
            "div.sc-dExYaf.hQBmmU",
            "div[class*='offer']"
        ]
        offer_elements = []
        for sel in selectors:
            try:
                els = driver.find_elements(By.CSS_SELECTOR, sel)
                if els:
                    offer_elements = els
                    break
            except Exception:
                continue
        for el in offer_elements:
            text = el.text.strip()
            if not text:
                continue
            lines = text.split('\n')
            title = lines[0]
            desc = lines[1] if len(lines) > 1 else ""
            offers.append({
                "store_name": get_store_name_from_url(url),
                "store_url": url,
                "title": title,
                "description": desc
            })
    except Exception as e:
        st.error(f"❌ Error scraping {url}: {e}")
    return offers

def scrape_store_parallel(url):
    driver = setup_driver()
    try:
        return scrape_single_store(driver, url)
    finally:
        driver.quit()

def parallel_scrape_all_stores(urls, max_threads=5):
    total = len(urls)
    all_offers = []
    progress_bar = st.progress(0)
    status_text = st.empty()

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
            progress_bar.progress(idx / total)
            status_text.text(f"Scraped {idx} of {total} URLs")

    progress_bar.empty()
    status_text.empty()
    return all_offers

def update_google_sheet(offers):
    # Placeholder for Google Sheets updating logic
    st.info("Google Sheet update feature not implemented. Showing data below.")
    st.dataframe(offers)

st.set_page_config(page_title="Swiggy Discounts Scraper", page_icon="🍔", layout="wide")
st.title("🍔 Swiggy Discounts Scraper")

if st.button("Scrape Discounts"):
    total = len(STORE_URLS)
    st.write(f"Starting scraping 0 out of {total} URLs")
    with st.spinner("Scraping discounts from predefined stores..."):
        offers = parallel_scrape_all_stores(STORE_URLS, max_threads=5)

    if offers:
        update_google_sheet(offers)
        st.success(f"✅ {len(offers)} discounts scraped.")
    else:
        st.warning("No discounts found.")
else:
    st.write("Click the button above to start scraping discounts.")

