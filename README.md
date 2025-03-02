# Web_image_Scraper

Image Web Scraper is a Python-based tool that scrapes images from trusted websites based on a given keyword. It automates image collection, processes data efficiently, and stores the results in structured formats such as JSON and PDF.

## Features
- **Keyword-Based Image Scraping**: Extracts images related to any given keyword.
- **Trusted Websites Filtering**: Scrapes only from specified trusted domains to ensure data reliability.
- **Automated Search**: Uses DuckDuckGo to find relevant pages.
- **Efficient Web Scraping**: Supports Cloudflare-protected sites (with optional cloudscraper support).
- **Robust Session Handling**: Implements retries and user-agent rotation to avoid request blocks.
- **Data Storage**: Saves extracted image URLs in JSON format and generates a structured PDF report.

## Installation
### Prerequisites
Ensure you have Python 3 installed, then install the required dependencies:

pip install -r requirements.txt

If you want improved Cloudflare bypass support, install:

pip install cloudscraper


## Usage
1. Modify the script to specify your desired keyword and trusted websites.
2. Run the script:

python scraper.py
3. Extracted data will be saved in the `keyword_data` folder as:
   - `scraped_data.json`: Contains structured image URLs and their local paths.
   - `images_document.pdf`: A formatted PDF report with downloaded images.

## Output
- **JSON File**: Stores extracted image URLs and their local paths.
- **PDF Report**: Includes structured images embedded in a document.

## Example
If the keyword is **"Wildlife Photography"**, the tool will:
- Search relevant content on trusted sites.
- Scrape and store related images.
- Generate `scraped_data.json` and `images_document.pdf` in the output folder.

## License
This project is open-source. Feel free to modify and enhance it!

## Disclaimer
Use this scraper responsibly. Ensure compliance with website terms and conditions before extracting data.

