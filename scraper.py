import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import json
import time
import random
import hashlib
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas




try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False
    logging.warning("Install cloudscraper for better scraping: pip install cloudscraper")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()]
)

class GeoPoliticalScraper:
    def __init__(self, keyword, trusted_websites):
        self.keyword = keyword
        self.trusted_websites = trusted_websites
        self.output_folder = f"{keyword.replace(' ', '_')}_data"
        self.session = self._create_session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
        self.data = {"keyword": keyword, "matched_urls": []}
        self._create_folders()

    def _create_session(self):
        """Create a requests session with retry mechanism"""
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    

    def _get_headers(self):
        """Return random headers to mimic browser behavior"""
        return {'User-Agent': random.choice(self.user_agents)}

    def _create_folders(self):
        """Create output folder structure"""
        folders = [self.output_folder, f"{self.output_folder}/images"]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            logging.info(f"Created folder: {folder}")

    def _search_duckduckgo(self):
        """Search DuckDuckGo and collect anchor tags"""
        search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(self.keyword)}"
        logging.info(f"Searching DuckDuckGo: {search_url}")
        try:
            response = self.session.get(search_url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            anchor_tags = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
            logging.info(f"Found {len(anchor_tags)} anchor tags")
            return anchor_tags
        except Exception as e:
            logging.error(f"Error searching DuckDuckGo: {e}")
            return []

    def _verify_trusted_urls(self, anchor_tags):
        """Filter anchor tags matching trusted websites"""
        trusted_urls = []
        for url in anchor_tags:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc.lower() or urllib.parse.urlparse(f"http://{parsed_url.path}").netloc.lower()
            for trusted in self.trusted_websites:
                trusted_domain = urllib.parse.urlparse(trusted).netloc.lower()
                if domain == trusted_domain or domain.endswith('.' + trusted_domain):
                    trusted_urls.append(url)
                    logging.info(f"Matched trusted URL: {url}")
                    break
        return trusted_urls

    def _scrape_images(self, url):
        """Scrape image source URLs from a webpage"""
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            image_urls = [img.get('src') or img.get('data-src') for img in soup.find_all('img') if img.get('src') or img.get('data-src')]
            absolute_urls = [urllib.parse.urljoin(url, img_url) for img_url in image_urls if img_url]
            logging.info(f"Found {len(absolute_urls)} images on {url}")
            return absolute_urls
        except Exception as e:
            logging.error(f"Error scraping images from {url}: {e}")
            return []

    def _download_image(self, img_url):
        """Download an image and return its local path"""
        try:
            img_name = f"{hashlib.md5(img_url.encode()).hexdigest()}{os.path.splitext(urllib.parse.urlparse(img_url).path)[-1] or '.jpg'}"
            img_path = f"{self.output_folder}/images/{img_name}"
            if not os.path.exists(img_path):
                response = self.session.get(img_url, headers=self._get_headers(), stream=True, timeout=10)
                response.raise_for_status()
                with open(img_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                logging.info(f"Downloaded image: {img_path}")
            return img_path
        except Exception as e:
            logging.error(f"Error downloading image {img_url}: {e}")
            return None

    def _save_to_json(self):
        """Save scraped data to a JSON file"""
        json_path = f"{self.output_folder}/scraped_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)
        logging.info(f"Saved data to {json_path}")

    def _create_pdf(self):
        """Create a PDF document with downloaded images"""
        pdf_path = f"{self.output_folder}/images_document.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        y_position = 750
        width, height = letter

        c.drawString(100, y_position, f"Scraped Images for '{self.keyword}'")
        y_position -= 40

        for entry in self.data["matched_urls"]:
            url = entry["anchor_tag"]
            images = entry.get("image_paths", [])
            if images:
                c.drawString(100, y_position, f"URL: {url}")
                y_position -= 20
                for img_path in images:
                    if os.path.exists(img_path) and y_position > 100:
                        c.drawImage(img_path, 100, y_position - 150, width=200, height=150, preserveAspectRatio=True)
                        y_position -= 170
                    if y_position <= 100:
                        c.showPage()
                        y_position = 750
        c.save()
        logging.info(f"Created PDF at {pdf_path}")

    def scrape(self):
        """Main method to execute the scraping process"""
        logging.info(f"Starting scrape for keyword: {self.keyword}")

        # Step 1: Search DuckDuckGo and collect anchor tags
        anchor_tags = self._search_duckduckgo()
        time.sleep(random.uniform(2, 3))  # Delay to avoid rate-limiting

        # Step 2: Verify against trusted websites
        trusted_urls = self._verify_trusted_urls(anchor_tags)

        # Step 3 & 4: Scrape images and store data
        for url in trusted_urls:
            image_urls = self._scrape_images(url)
            downloaded_paths = [self._download_image(img_url) for img_url in image_urls]
            downloaded_paths = [path for path in downloaded_paths if path]  # Filter out failed downloads
            if image_urls:
                self.data["matched_urls"].append({
                    "anchor_tag": url,
                    "image_urls": image_urls,
                    "image_paths": downloaded_paths
                })
            time.sleep(random.uniform(1, 3))  # Delay between page scrapes

        # Step 5: Save data to JSON
        self._save_to_json()

        # Step 6: Create PDF with images
        self._create_pdf()

        logging.info("Scraping complete")

# Example usage
if __name__ == "__main__":
    keyword = "Geo-political Tension"
    trusted_websites = ["https://www.foreignaffairs.com/topics/geopolitics", "https://www.spglobal.com/en/research-insights/market-insights/geopolitical-risk"]
    scraper = GeoPoliticalScraper(keyword=keyword, trusted_websites=trusted_websites)
    scraper.scrape()