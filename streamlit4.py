import streamlit as st
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

STORE_URLS = [
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-santoshpur-kolkata-737986"
    # add more URLs as needed
]

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

def scrape_single_store(url):
    offers = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        # Attempt to find discount information
        offer_elements = soup.select("div[data-testid^='offer-card-container']")  # Updated selector

        if not offer_elements:
            st.warning(f"No offer elements found for {url}. Please check the selectors.")

        for el in offer_elements:
            title_element = el.select_one("div.sc-aXZVg.hsuIwO")  # Title selector
            desc_element = el.select_one("div.sc-aXZVg.foYDCM")  # Description selector
            
            title = title_element.get_text(strip=True) if title_element else "No Title"
            desc = desc_element.get_text(strip=True) if desc_element else "No Description"
            
            offers.append({
                "store_name": get_store_name_from_url(url),
                "store_url": url,
                "title": title,
                "description": desc
            })
    except Exception as e:
        st.error(f"❌ Error scraping {url}: {e}")
    return offers

def parallel_scrape_all_stores(urls, max_threads=5):
    total = len(urls)
    all_offers = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(scrape_single_store, url): url for url in urls}
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
