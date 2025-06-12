import streamlit as st
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sohna-road-gurgaon-392965",
    "https://www.swiggy.com/city/gurgaon/burger-singh-big-punjabi-burgers-sector-28-dlf-mega-mall-rest958152",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sonipat-city-sonipat-532253",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-rohtak-city-rohtak-552338",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sector-13-karnal-592314?sld=false",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-zirakpur-chandigarh-597155",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sector-79-faridabad-588858",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-lajpat-nagar-old-courts-commercial-complex-hisar-815834",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-barahi-road-dharampura-bahadurgarh-710453",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-mahaveer-chowk-narnaul-776981",
    "https://www.swiggy.com/city/rewari/burger-singh-big-punjabi-burgers-shopping-complex-sector-3-sector-3-huda-sco-rest966786",
    "https://www.swiggy.com/city/gurgaon/burger-singh-big-punjabi-burgers-sushant-lok-phase2-marengo-asia-hospitals-rest966497",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-imt-manesar-gurgaon-357658",
    "https://www.swiggy.com/city/sonipat/burger-singh-big-punjabi-burgers-opposite-ashoka-university-golden-hut-rest1024817",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-air-colony-kurukshetra-873181",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-nit-fbd-faridabad-263235",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-solan-town-solan-807190",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-trikuta-nagar-jammu-432078",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-bistupur-jamshedpur-873187",
    "https://www.swiggy.com/city/ranchi/burger-singh-big-punjabi-burgers-hatia-rest923138",
    "https://www.swiggy.com/city/jamshedpur/burger-singh-big-punjabi-burgers-kalimati-road-sakchi-sakchi-jamshedpur-rest1067752",
    "https://www.swiggy.com/city/bangalore/burger-singh-big-punjabi-burgers-9th-main-road-7th-sector-hsr-layout-rest1031311",
    "https://www.swiggy.com/city/bangalore/burger-singh-big-punjabi-burgers-btm-2nd-stage-btm-layout-rest1037980",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-jab-north-jabalpur-460360",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-mp-nagar-bhopal-572870",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-bhawar-kuan-indore-816024",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-civic-center-jab-jabalpur-791916?source=sharing",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-scheme-no-78-vijay-nagar-indore-860972",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-shradhanand-peth-bajaj-nagar-nagpur-769576",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sadar-nagpur-769581",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-magarpatta-pune-912028",
    "https://www.swiggy.com/city/pune/burger-singh-big-punjabi-burgers-baner-rest935435",
    "https://www.swiggy.com/city/pune/burger-singh-big-punjabi-burgers-city-vista-kharadi-kharadi-pune-rest1065032",
    "https://www.swiggy.com/city/pune/burger-singh-big-punjabi-burgers-wakad-rest939977",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-thane-panchpakhadi-mumbai-915429",
    "https://www.swiggy.com/city/nashik/burger-singh-big-punjabi-burgers-canada-corner-anandwan-colony-rest1006979",
    "https://www.swiggy.com/city/pune/burger-singh-big-punjabi-burgers-ground-floor-konark-industrial-viman-nagar-pune-rest1065025",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-police-bazar-shillong-792189",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-patia-bhubaneswar-829621",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-college-square-cuttack-779514",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-gt-road-east-amritsar-amritsar-311432",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-west-chd-chandigarh-497327",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-zirakpur-chandigarh-686074",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-south-jalandhar-jalandhar-808002",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-phase-3b2-sas-nagar-mohali-2-chandigarh-837398",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-basant-vihar-alwar-583144",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-vaishali-nagar-jaipur-577811",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-manasarovar-jaipur-656015?sld=false",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-malviya-nagar-jaipur-703699",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-central-bhiwadi-bhiwadi-846492",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-755831",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sardarpura-new-jodhpur-jodhpur-905138",
    "https://www.swiggy.com/city/udaipur/burger-singh-big-punjabi-burgers-gaurav-path-urban-square-mall-rest958117",
    "https://www.swiggy.com/city/jaipur/burger-singh-big-punjabi-burgers-opp-trinitymall-civil-lines-jaipur-rest1044103",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ballupur-dehradun-86369",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-jakhan-dehradun-428406",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-iit-roorkee-roorkee-615616?sld=false",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ram-jhula-rishikesh-804114?sld=false",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-shri-tej-singh-palace-haldwani-city-haldwani-916512",
    "https://www.swiggy.com/city/dehradun/burger-singh-big-punjabi-burgers-sector-5-harrawala-rest1006978",
    "https://www.swiggy.com/city/dehradun/burger-singh-big-punjabi-burgers-new-muncipal-no-266-10-475-rajpur-road-rajpur-road-dehradun-rest1064266",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-noida-expressway-noida-1-142009",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-raj-nagar-noida-311388",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-stellar-it-park-sector-64-noida-1-33796",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-greater-noida-noida-1-362954",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-gomti-nagar-lucknow-367778",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ashiyana-lucknow-364762",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-gwalior-road-civil-lines-jhansi-623940",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sector-50-sector-122-noida-1-391409",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-crossing-republic-noida-407925",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-shastri-nagar-meerut-460161",
    "https://www.swiggy.com/city/moradabad/burger-singh-big-punjabi-burgers-sector-02-delhi-road-buddhi-vihar-rest957964",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-meerut-cantt-meerut-574665",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-kaushambi-noida-616830?sld=false",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-subhash-nagar-faizabad-659425",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-sector-18-noida-1-596945",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-civil-lines-aligarh-615748?sld=false",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-avon-market-kakadeo-kanpur-676398",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-pd-tandon-road-civil-lines-allahabad-689243",
    "https://www.swiggy.com/city/kanpur/burger-singh-big-punjabi-burgers-15-60-civillines-nagar-nigam-civil-lines-kanpur-rest1056238",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-bhadur-nagar-lakhimpur-677794",
    "https://www.swiggy.com/city/mathura/burger-singh-big-punjabi-burgers-ajhai-kalan-vrindavan-rest873167",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-rajendra-nagar-shalimar-garden-noida-856754",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-b-23-shopping-arcade-sadar-bazar-civil-lines-agra-912026",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-aliganj-lucknow-798933",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ashiyana-moradabad-429003",
    "https://www.swiggy.com/city/gonda/burger-singh-big-punjabi-burgers-kachehari-road-malviya-nagar-lbs-chauraha-rest966602",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-mission-compound-saharanpur-612543",
    "https://www.swiggy.com/city/agra/burger-singh-big-punjabi-burgers-awas-vikas-colony-sikandra-sikandra-agra-rest1025813",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-city-centre-durgapur-762696",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-central-kolkata-kolkata-728292",
    "https://www.swiggy.com/restaurants/burger-singh-lake-town-kolkata-739703",
    "https://www.swiggy.com/restaurants/burger-singh-santoshpur-kolkata-737986"
]
# ==========================

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
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # Close cookie/accept if any
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
    # initialize progress display
    st.write(f"Starting scraping 0 out of {total} URLs")
    with st.spinner("Scraping discounts from predefined stores..."):
        offers = parallel_scrape_all_stores(STORE_URLS, max_threads=5)

    if offers:
        update_google_sheet(offers)
        st.success(f"✅ {len(offers)} discounts scraped and sheet updated.")
        st.dataframe(offers)
    else:
        st.warning("❌ No discounts found.")
