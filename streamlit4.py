import streamlit as st
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========= CONFIG =========
SERVICE_ACCOUNT_FILE = r"C:\Users\Ankita Singh\Desktop\swiggy_discounts\Dewansh_Crafty (1).json"
SPREADSHEET_KEY = "1rbS3QOzT7MPQHHh33v4pv_-84RQxOkehhmOPCtnGf3E"
WORKSHEET_NAME = "swiggy"

# Predefined list of Swiggy restaurant URLs
STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-stational-club-durga-mandir-purnea-purnea-698848",
    "https://www.swiggy.com/restaurants/burger-singh-gaya-city-gaya-701361",
    "https://www.swiggy.com/restaurants/burger-singh-kankarbagh-patna-745653",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-boring-road-srikrishnapuri-patna-905166",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-muz-muzaffarpur-city-muzaffarpur-875110",
    "https://www.swiggy.com/city/patna/burger-singh-big-punjabi-burgers-danapur-khagaul-road-khajpura-rest905153",
    "https://www.swiggy.com/city/bihta/burger-singh-big-punjabi-burgers-awas-vikas-colony-sikandra-dilawarpur-bihta-rest1019848",
    "https://www.swiggy.com/restaurants/burger-singh-samta-colony-raipur-725988",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-telipara-bilaspur-724177",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-nehru-nagar-bhilai-815960",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-outer-circle-connaught-place-delhi-8628",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sector-4-dwarka-delhi-14711",
    "https://www.swiggy.com/city/delhi/burger-singh-big-punjabi-burgers-epicuria-food-and-entertainment-hub-metro-station-nehru-place-rest984070",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-kingsway-camp-gtb-nagar-delhi-59630",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-kalkaji-greater-kailash-2-delhi-62721",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-vasant-arcade-vasant-kunj-delhi-69121",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-krishna-nagar-laxmi-nagar-delhi-152953",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-vardhman-janak-market-a2b-block-asalatpur-janakpuri-delhi-167974",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sector-7-rohini-delhi-168043",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-karol-bagh-delhi-189058",
    "https://www.swiggy.com/city/delhi/burger-singh-big-punjabi-burgers-kotwali-pratap-nagar-rest958130",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-nfc-delhi-342562",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-mayur-vihar-delhi-426746",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-laxmi-nagar-delhi-815837",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-dilshad-gardens-delhi-561780",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-south-campus-delhi-591025",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-chattarpur-delhi-645645",
    "https://www.swiggy.com/city/delhi/burger-singh-big-punjabi-burgers-mehrauli-gurgaon-road-chattarpur-dmrc-rest1016715",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sda-market-malviya-nagar-delhi-9906",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-najafgarh-delhi-821080",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-rajouri-garden-delhi-343544",
    "https://www.swiggy.com/city/delhi/burger-singh-big-punjabi-burgers-badarpur-dmrc-metro-station-rest958097",
    "https://www.swiggy.com/menu/1013456?source=sharing",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-madhapar-rajkot-565577",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-jawahar-ground-bhavnagar-637082",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-756037",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-bapunagar-ahmedabad-653936",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-mahadev-nagar-anand-786758",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-uttarsanda-road-nadiad-city-nadiad-791914?source=sharing",
    "https://www.swiggy.com/city/bharuch/burger-singh-big-punjabi-burgers-tavara-road-the-maple-square-rest957884",
    "https://www.swiggy.com/city/surat/burger-singh-big-punjabi-burgers-nh-08-sidhrawali-171-square-street-surat-rest1051053",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sushant-lok-1-dlf-phase-4-gurgaon-6244",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-palam-vihar-gurgaon-48784",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-golf-course-road-jalvayu-towers-gurgaon-6242",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-old-gurgaon-zone-6-gurgaon-357951",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-captain-nagar-panipat-428408",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sohna-road-gurgaon-392965",
    "https://www.swiggy.com/restaurants/burger-singh-big-pPunjabi-burgers-sohna-road-gurgaon-392965",
    "https://www.swiggy.com/city/gurgaon	burger-singh-big-punjabi-burgers-sector-28-dlf-mega-mall-rest958152",
    "https://www.swiggy.com/restaurants	burger-singh-big-punjabi-burgers-sonipat-city-sonipat-532253",
    "https://www.swiggy.com/restaurants	burger-singh-big-punjabi-burgers-rohtak-city-rohtak-552338",
    "https://www.swiggy.com/restaurants	burger-singh-big-pPunjabi-burgers-sector-13-karnal-592314?sld=false",
    "https://www.swiggy.com/restaurants	burger-singh-big-punjabi-burgers-zirakpur-chandigarh-597155",
    "https://www.swiggy.com/restaurants	burger-singh-big-punjabi-burgers-sector-79-faridabad-588858",
    # ... and so on
]
# ==========================

def setup_driver_uc():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return uc.Chrome(options=options)

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

def scrape_single_store_uc(driver, url):
    offers = []
    try:
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

        offer_elements = []
        for sel in selectors:
            try:
                els = driver.find_elements(By.CSS_SELECTOR, sel)
                if els:
                    offer_elements = els
                    break
            except:
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

def scrape_store_parallel_uc(url):
    driver = setup_driver_uc()
    try:
        return scrape_single_store_uc(driver, url)
    finally:
        driver.quit()

def parallel_scrape_all_stores_uc(urls, max_threads=5):
    total = len(urls)
    status_text = st.empty()
    all_offers = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(scrape_store_parallel_uc, url): url for url in urls}
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

def update_google_sheet(data):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_KEY).worksheet(WORKSHEET_NAME)
    sheet.clear()
    headers = ["store_name", "store_url", "title", "description"]
    rows = [headers] + [[row[h] for h in headers] for row in data]
    sheet.update(rows)

# ========== STREAMLIT APP ==========

st.title("🍔 Swiggy Discounts Scraper (Predefined URLs)")

if st.button("Scrape Discounts & Update Google Sheet"):
    total = len(STORE_URLS)
    st.write(f"Starting scraping 0 out of {total} URLs")
    with st.spinner("Scraping discounts from predefined stores..."):
        offers = parallel_scrape_all_stores_uc(STORE_URLS, max_threads=5)

    if offers:
        update_google_sheet(offers)
        st.success(f"✅ {len(offers)} discounts scraped and sheet updated.")
        st.dataframe(offers)
    else:
        st.warning("❌ No discounts found.")
