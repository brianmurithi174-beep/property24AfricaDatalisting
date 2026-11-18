from bs4 import BeautifulSoup
from urllib.parse import urljoin

with open("property24_debug.html", "r", encoding="utf-8") as file:
    html = file.read()

soup = BeautifulSoup(html, "html.parser")

first_home = soup.select_one(".p24_regularTile")

if first_home:
    title = first_home.select_one(".p24_propertyTitle")
    price = first_home.select_one(".p24_price")
    location = first_home.select_one(".p24_location")

    link = first_home.select_one("a[href]")
    image = first_home.select_one(".p24_image image")

    property_url = (
        urljoin("https://www.property24.co.ke", link["href"])
        if link else "N/A"
    )

    image_url = image.get("src") if image else "N/A"

    print("TITLE:", title.get_text(strip=True) if title else "N/A")
    print("PRICE:", price.get_text(strip=True) if price else "N/A")
    print("LOCATION:", location.get_text(strip=True) if location else "N/A")
    print("PROPERTY URL:", property_url)
    print("IMAGE URL:", image_url)

else:
    print("No property card found.")
