
import requests
from bs4 import BeautifulSoup

URL = "https://www.property24.co.ke/property-for-sale-in-nairobi-c1890?page=2"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

print("Status:", response.status_code)
print("Final URL:", response.url)
print("Content-Type:", response.headers.get("Content-Type"))
print("HTML length:", len(response.text))

soup = BeautifulSoup(response.text, "html.parser")

print("\nPage title:")
print(soup.title.get_text(strip=True) if soup.title else "No title")

print("\nChecking previous selectors:")

for selector in [
    ".p24_content",
    ".p24_propertyTitle",
    ".p24_price",
    ".p24_location",
]:
    matches = soup.select(selector)
    print(f"{selector}: {len(matches)} matches")

# Save HTML for inspection
with open("property24_debug.html", "w", encoding="utf-8") as file:
    file.write(response.text)

print("\nHTML saved to property24_debug.html")
