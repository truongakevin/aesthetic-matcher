import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote, urlunparse
import re
import time
from requests.exceptions import ChunkedEncodingError, RequestException

# Define the base URL and headers
BASE_URL = "https://aesthetics.fandom.com/wiki/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Create a directory to store images if it doesn't exist
IMAGE_FOLDER = 'aesthetics_images_3'
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)
    
def sanitize_filename(filename):
    """Sanitize the filename to ensure it is valid."""
    # Replace invalid characters with an underscore
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', ' ', filename)[:255]

def download_image(image_url, folder_name, image_name, retries=3, delay=2):
    """Download an image and save it to a folder with retry logic."""
    # Sanitize the image name
    image_name = sanitize_filename(image_name)

    file_path = os.path.join(folder_name, image_name)    
    if os.path.exists(file_path):
        print(f"File {file_path} already exists. Skipping download.")
        return
    
    print(f"Attempting to download {image_url}")
    
    for attempt in range(retries):
        try:
            response = requests.get(image_url, headers=HEADERS, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            with open(os.path.join(folder_name, image_name), 'wb') as file:
                file.write(response.content)
            print(f"Successfully downloaded {image_url}")
            return  # Exit function on success
        except (ChunkedEncodingError, RequestException) as e:
            print(f"Attempt {attempt + 1} failed to download {image_url}. Reason: {e}")
            time.sleep(delay)  # Wait before retrying
    print(f"Failed to download {image_url} after {retries} attempts.")

def scrape_aesthetic_images(aesthetic_name):
    """Scrape images for a given aesthetic."""
    # Convert aesthetic name to URL format
    aesthetic_url_name = quote(aesthetic_name.replace(' ', '_'))
    url = f"{BASE_URL}{aesthetic_url_name}"
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    image_div = soup.find('div', class_='mw-parser-output')
    if not image_div:
        print(f"No images found for {aesthetic_name}")
        return
    
    # Create a folder for the aesthetic if it doesn't exist
    folder_name = (os.path.join(IMAGE_FOLDER, sanitize_filename(aesthetic_name)))
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Find and download images
    images = image_div.find_all('img')
    for i, img in enumerate(images):
        img_url = img.get('src')
        if img_url and not img_url.startswith('data:'):
            # Ensure the image URL is complete
            if not img_url.startswith('http'):
                img_url = 'https:' + img_url
            
            # Parse the URL and remove everything after the image file name
            parsed_url = urlparse(img_url)
            clean_path = parsed_url.path.split('/revision/')[0]
            clean_url = urlunparse(parsed_url._replace(path=clean_path, query=''))
            
            # Extract the file name from the URL
            file_name = os.path.basename(clean_url)
            
            download_image(clean_url, folder_name, file_name)

def scrape_aesthetics():
    from listaesthetics import aesthetics
    # aesthetics = []
    # URL of the website you want to scrape
    url = "https://aesthetics.fandom.com/wiki/List_of_Aesthetics"

    # Send a GET request to the website
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all divs with the class "twocolumn"
    twocolumn_divs = soup.find_all('div', class_='twocolumn')

    # Iterate over each twocolumn div and extract the li text
    for div in twocolumn_divs:
        list_items = div.find_all('li')
        for li in list_items:
            text = li.get_text(strip=True)
            clean_text = text.encode('ascii', 'ignore').decode('ascii')
            if clean_text not in aesthetics:
                print(clean_text)
                aesthetics.append(clean_text)
            
    # Write the aesthetics list to a file
    with open('listaesthetics.py', 'w') as file:
        file.write(f"aesthetics = {aesthetics}\n")
            
    return aesthetics
            
# Scrape wiki for every aesthetic
aesthetics_list = scrape_aesthetics()

# Scrape images for each aesthetic in the list
for aesthetic in aesthetics_list:
    print(f"Scraping images for {aesthetic}...")
    scrape_aesthetic_images(aesthetic)
