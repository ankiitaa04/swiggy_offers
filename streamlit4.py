import streamlit as st
import requests
from bs4 import BeautifulSoup

def scrape_offers(url):
    data = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(data, 'html.parser')
    offers = [d.get_text(strip=True) for d in soup.select('div') if 'OFF' in d.get_text()]
    return offers or ["No offers found"]

st.set_page_config(page_title="Swiggy Offers Scraper", page_icon="🍔")
st.title("🍔 Swiggy Discounts Scraper")

# ✅ Replace with your real Swiggy store URLs
STORE_URLS = [
   "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-ganeshguri-guwahati-579784",
    "https://www.swiggy.com/restaurants/burger-singh-big-punjabi-burgers-stational-club-durga-mandir-purnea-purnea-698848",
    "https://www.swiggy.com/restaurants/burger-singh-gaya-city-gaya-701361",
    "https://www.swiggy.com/restaurants/burger-singh-kankarbagh-patna-745653",]

if st.button("Scrape Discounts"):
    for i, url in enumerate(STORE_URLS, start=1):
        st.subheader(f"🔍 Restaurant {i}: {url}")
        for o in scrape_offers(url):
            st.write(f"- {o}")
