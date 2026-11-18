
import asyncio
import aiohttp
import pandas as pd
import random
import time
import os
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin


# =====================================================
# 1. CONFIGURATION
# =====================================================

BASE_URL = (
    "https://www.property24.co.ke/"
    "property-for-sale-in-nairobi-c1890"
)

# Highest page number detected from the pagination HTML
LAST_PAGE = 6073

CONCURRENCY = 3
MAX_RETRIES = 3

REQUEST_DELAY = (1.0, 2.0)

OUTPUT_FILE = "Property24Africa_all_pages.csv"
CHECKPOINT_FILE = "property24_checkpoint.json"
FAILED_FILE = "property24_failed_pages.txt"


HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-KE,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/137.0.0.0 Safari/537.36"
}


# =====================================================
# 2. EXTRACT PROPERTY DATA
# =====================================================

def extract_properties(html):

    soup = BeautifulSoup(html, "html.parser")

    homes = soup.select(".p24_regularTile")

    properties = []

    for home in homes:

        title = home.select_one(".p24_propertyTitle")
        price = home.select_one(".p24_price")
        location = home.select_one(".p24_location")

        link = home.select_one("a[href]")

        # Support both image and img HTML elements
        image = home.select_one(
            ".p24_image image, .p24_image img"
        )

        image_url = None

        if image:
            image_url = (
                image.get("data-src")
                or image.get("data-original")
                or image.get("data-lazy-src")
                or image.get("src")
            )

            if not image_url and image.get("srcset"):
                image_url = image["srcset"].split(",")[0].split()[0]

        property_url = (
            urljoin(BASE_URL, link["href"])
            if link else None
        )

        properties.append({

            "Title": title.get_text(strip=True) if title else None,

            "Price": price.get_text(strip=True) if price else None,

            "Location": location.get_text(strip=True) if location else None,

            "PropertyUrl": property_url,

            "Image_url": image_url

        })

    return properties


# =====================================================
# 3. SCRAPE ONE PAGE WITH RETRIES
# =====================================================

async def scrape_page(session, page):

    url = f"{BASE_URL}?page={page}"

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            await asyncio.sleep(
                random.uniform(*REQUEST_DELAY)
            )

            async with session.get(url) as response:

                if response.status == 429 or response.status >= 500:

                    retry_after = response.headers.get("Retry-After")

                    try:
                        wait = float(retry_after)
                    except (TypeError, ValueError):
                        wait = 2 ** attempt

                    if attempt < MAX_RETRIES:
                        print(
                            f"Page {page}: HTTP {response.status}. "
                            f"Retrying in {wait:.1f}s..."
                        )
                        await asyncio.sleep(wait)
                        continue

                    return [], False, f"HTTP {response.status}"

                if response.status != 200:

                    return [], False, f"HTTP {response.status}"

                html = await response.text(errors="replace")

            properties = extract_properties(html)

            if not properties:

                return [], False, "No property cards found"

            print(
                f"Page {page} completed: "
                f"{len(properties)} listings"
            )

            return properties, True, None

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:

            if attempt == MAX_RETRIES:

                return [], False, str(error)

            await asyncio.sleep(2 ** attempt)

        except Exception as error:

            return [], False, str(error)

    return [], False, "Maximum retries exceeded"


# =====================================================
# 4. WORKER FUNCTION
# =====================================================

async def worker(session, page_queue, result_queue):

    while True:

        page = await page_queue.get()

        if page is None:

            page_queue.task_done()
            break

        try:

            properties, success, error = await scrape_page(
                session, page
            )

            await result_queue.put(
                (page, properties, success, error)
            )

        finally:

            page_queue.task_done()


# =====================================================
# 5. CHECKPOINT MANAGEMENT
# =====================================================

def load_checkpoint():

    if os.path.exists(CHECKPOINT_FILE):

        with open(CHECKPOINT_FILE, "r") as file:

            return set(json.load(file))

    return set()


def save_checkpoint(completed_pages):

    temporary_file = CHECKPOINT_FILE + ".tmp"

    with open(temporary_file, "w") as file:

        json.dump(sorted(completed_pages), file)

    os.replace(temporary_file, CHECKPOINT_FILE)


# =====================================================
# 6. LOAD EXISTING PROPERTY URLS
# =====================================================

def load_existing_urls():

    if not os.path.exists(OUTPUT_FILE):
        return set()

    try:

        df = pd.read_csv(
            OUTPUT_FILE,
            usecols=["PropertyUrl"],
            dtype=str
        )

        return set(
            df["PropertyUrl"].dropna()
        )

    except (ValueError, pd.errors.EmptyDataError):

        return set()


# =====================================================
# 7. MAIN ASYNCHRONOUS SCRAPER
# =====================================================

async def main():

    start_time = time.perf_counter()

    completed_pages = load_checkpoint()

    seen_urls = load_existing_urls()

    total_pages = set(range(1, LAST_PAGE + 1))

    remaining_pages = sorted(
        total_pages - completed_pages
    )

    print("=" * 55)
    print("PROPERTY24 AFRICA ASYNC SCRAPER")
    print("=" * 55)

    print("Total pages:", LAST_PAGE)
    print("Previously completed:", len(completed_pages))
    print("Remaining pages:", len(remaining_pages))
    print("Existing unique properties:", len(seen_urls))

    if not remaining_pages:

        print("\nAll pages have already been processed.")
        return

    page_queue = asyncio.Queue()

    result_queue = asyncio.Queue(
        maxsize=CONCURRENCY * 2
    )

    for page in remaining_pages:

        await page_queue.put(page)

    timeout = aiohttp.ClientTimeout(
        total=45,
        connect=15,
        sock_read=30
    )

    connector = aiohttp.TCPConnector(
        limit=CONCURRENCY,
        limit_per_host=CONCURRENCY
    )

    failed_pages = []

    extracted_count = 0

    file_exists = (
        os.path.exists(OUTPUT_FILE)
        and os.path.getsize(OUTPUT_FILE) > 0
    )

    async with aiohttp.ClientSession(

        connector=connector,
        timeout=timeout,
        headers=HEADERS

    ) as session:

        # Start a limited number of workers

        workers = [

            asyncio.create_task(
                worker(session, page_queue, result_queue)
            )

            for _ in range(CONCURRENCY)

        ]

        processed = 0

        for _ in range(len(remaining_pages)):

            page, properties, success, error = (
                await result_queue.get()
            )

            if success:

                extracted_count += len(properties)

                new_properties = []

                for prop in properties:

                    property_url = prop["PropertyUrl"]

                    if property_url and property_url not in seen_urls:

                        seen_urls.add(property_url)

                        new_properties.append(prop)

                # Save newly discovered properties immediately

                if new_properties:

                    df = pd.DataFrame(new_properties)

                    df.to_csv(

                        OUTPUT_FILE,

                        mode="a",

                        header=not file_exists,

                        index=False,

                        encoding="utf-8"

                    )

                    file_exists = True

                completed_pages.add(page)

            else:

                failed_pages.append(page)

                print(
                    f"Page {page} failed: {error}"
                )

            processed += 1

            # Update checkpoint after every successful page

            if success:
                save_checkpoint(completed_pages)

            if processed % 10 == 0:

                print(
                    f"\nProgress: {processed}/"
                    f"{len(remaining_pages)} pages"
                )

                print(
                    f"Unique properties: {len(seen_urls)}"
                )

            result_queue.task_done()

        # Stop workers

        for _ in workers:

            await page_queue.put(None)

        await asyncio.gather(*workers)

    # =================================================
    # 8. SAVE FAILED PAGES
    # =================================================

    with open(FAILED_FILE, "w") as file:

        for page in sorted(failed_pages):

            file.write(f"{page}\n")

    # Final checkpoint

    save_checkpoint(completed_pages)

    # =================================================
    # 9. FINAL REPORT
    # =================================================

    elapsed = time.perf_counter() - start_time

    print("\n" + "=" * 55)

    print("SCRAPING COMPLETED")

    print("=" * 55)

    print("Pages completed:", len(completed_pages))

    print("Properties extracted:", extracted_count)

    print("Unique properties saved:", len(seen_urls))

    print("Failed pages:", len(failed_pages))

    print(f"Time taken: {elapsed / 60:.2f} minutes")

    print("CSV file:", OUTPUT_FILE)

    print("Checkpoint:", CHECKPOINT_FILE)

    if failed_pages:

        print(
            "Failed page numbers saved in:",
            FAILED_FILE
        )

    print("=" * 55)


# =====================================================
# 10. EXECUTION
# =====================================================

if __name__ == "__main__":

    asyncio.run(main())
