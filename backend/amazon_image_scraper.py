from bs4 import BeautifulSoup
import requests

def get_amazon_image(url, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    img_tag = soup.find("img", id="landingImage")
    if img_tag:
        return img_tag["src"]
    return None

