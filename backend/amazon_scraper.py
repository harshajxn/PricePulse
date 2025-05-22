import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime

# Generate a random user-agent to mimic browser
ua = UserAgent()

def fetch_amazon_data(url):
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9" 
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Request failed: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        

        title = soup.find(id='productTitle')
        title = title.get_text(strip=True) if title else "Title not found"

        price = soup.find('span', {'class': 'a-price-whole'})
        if not price:
            price = soup.find('span', {'class': 'a-offscreen'})
        price = price.get_text(strip=True) if price else "Price not found"

        return {
            'title': title,
            'price': price,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

