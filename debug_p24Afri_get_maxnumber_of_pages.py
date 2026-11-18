
import re
import requests
from bs4 import BeautifulSoup

base_url = "https://www.property24.co.ke/property-for-sale-in-nairobi-c1890"

response = requests.get(base_url + "?page=1",headers={"User-Agent": "Mozilla/5.0"}, timeout=20,)
soup = BeautifulSoup(response.text, "html.parser")

page_numbers = []

for link in soup.select("a[href*='page=']"):
    match = re.search(r'[?&]page=(\d+)', link["href"])

    if match:
        page_numbers.append(int(match.group(1)))

if page_numbers:
    last_page = max(page_numbers)
    print("Last page detected:", last_page)
else:
    print("No pagination numbers found.")