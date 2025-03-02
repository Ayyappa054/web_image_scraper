wed Image Scraper

Overview

The Geo-Political Image Scraper is a Python-based web scraper that searches for images related to a given keyword from trusted websites using DuckDuckGo. It downloads images, saves metadata in JSON format, and generates a PDF report.

Features

Searches for images using DuckDuckGo search engine

Filters results from trusted websites

Downloads images and stores them locally

Saves metadata in JSON format

Generates a PDF report with images

Implements request retries and user-agent rotation to avoid blocking

Installation

Prerequisites

Ensure you have Python 3.7+ installed. You also need to install dependencies.

Steps

Clone the Repository

git clone https://github.com/your-username/geo-political-image-scraper.git
cd geo-political-image-scraper

Install Dependencies

pip install -r requirements.txt

Usage

Run the Scraper

python scraper.py

Modify Keyword & Trusted Websites

Edit the following lines in scraper.py:

keyword = "your keyword"
trusted_websites = [your trusted websites]

Output

Images: Stored in keyword_data/images/

Metadata: Stored in keyword/scraped_data.json

PDF Report: Geo- keyword/images_document.pdf

Dependencies

requests

beautifulsoup4

urllib3

cloudscraper (optional but recommended)

reportlab

Logging

All activities are logged in scraper.log.

License

This project is licensed under the MIT License.

