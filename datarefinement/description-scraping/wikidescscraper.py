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

def scrape_aesthetics():
    # from listaesthetics import aesthetics
    # from not_found import not_found as aesthetics
    aesthetics = []
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

def scrape_aesthetic_description(aesthetic_name):
    # ignore_list = ["Grandparentcore", "Peach", "Softie", 'VSCO', 
    #                'Nazi Chic', 'American Revolution', 'Bauhaus', 'Color Pop',
    #                'Corporate Grunge', 'English Southern Girl', 'Imperial Aztec',
    #                'Italian Renaissance', 'Lichencore', 'Minivoid', 'Queer Villainy',
    #                'Stilyagi', 'Pretty Preppy'
    #             ]
    # ignore_list = ['Da De Los Muertos', 'Dizelai', 'Espaolada', 'Fesmo', 'Gangstxtemism', 
    #               'Graynacore', 'Mudjar', 'Nouveau Ralisme', 'Pokemn', 'Y-y Girl', 'Ykai',
    #             ]
    # if aesthetic_name in ignore_list:
    #     print(f"Aesthetic {aesthetic_name} in ingonore list")
    #     return None
    """Scrape description for a given aesthetic."""
    # Convert aesthetic name to URL format
    aesthetic_url_name = quote(aesthetic_name.replace(' ', '_'))
    url = f"{BASE_URL}{aesthetic_url_name}"
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        return None
    
    # Get aesthetic description
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the start element (aside with specific class and role attributes)
    start_element = soup.find('aside', {
        'class': 'portable-infobox pi-background pi-border-color pi-theme-wikia pi-layout-default'
    })
    # start_element = soup.find('div', {
    #     'class': 'mw-parser-output'
    # })
    
    # Find the end element (div with id="toc" and specific class and role)
    end_element = soup.find('h2', {
    })
    # end_element = soup.find('div', {
    #     'id': 'toc'
    #     # 'class': 'toc', 
    #     # 'role': 'navigation', 
    #     # 'aria-labelledby': 'mw-toc-heading'
    # })

    if not start_element or not end_element:
        print("Could not find the start or end element.")
        return None

    # Get all content between the start and end elements
    content_between = []
    
    # Start from the start_element
    element = start_element

    print("==================================================")
    print("=======", aesthetic_name)
    # Collect content until reaching the end_element
    # while element != end_element:
    while element.name != 'h2':
        if element:
            if element.name == 'aside' or element.name == 'table' or element.name == 'figure' or (element.name == 'div' and 'mbox' in element.get('class', [])):
                element = element.next_sibling
            # Elements to exclude
            blacklist = [
                'figure', 'figcaption', 'img', 'a', 'div', 'i', 'b', 'p', 'div', 'sup', 'br', 'noscript', 'svg', 
                'use', 'abbr', 'u', 'span', 'blockquote', 'li', 'ul', 'th', 'td', 'tr', 'th', 'table', 'caption', 
                'tbody', 'cite', 'strong', 'sub', 'small', 'big', 'h3'
            ]
            if element.name not in blacklist and str(element) != '\n':
                # print("-",str(element))
                content_between.append(str(element))
                element = element.next_element
            else:
                element = element.next_element

    # Now we join all the collected HTML content
    content_text = ''.join(content_between)
    
    # Remove the start and end elements to get only the content in between
    # content_without_tags = full_content_html.replace(str(start_element), '').replace(str(end_element), '').strip()
    # content_text = ' '.join([element.get_text(strip=True) for element in content_between])
    print(content_text)
    # print("==================================================")
    return content_text
    


# # Scrape images for each aesthetic in the list
# aesthetics_descriptions = []
# not_found = []
# for aesthetic in aesthetics_list:
#     print(f"Scraping desciptions for {aesthetic}...")
#     description = scrape_aesthetic_description(aesthetic)
#     if description:
#         aesthetics_descriptions.append((aesthetic, description))
#     else:
#         not_found.append(aesthetic)
        
# with open('aesthetics_descriptions.py', 'w') as file:
#     file.write(f"aesthetics_descriptions = {aesthetics_descriptions}\n")
# with open('not_found.py', 'w') as file:
#     file.write(f"not_found = {not_found}\n")

# double spaces
# \n
# \xa0
# \u200b\u200b

# import webbrowser

# from aesthetics_descriptions import aesthetics_descriptions
# # for a, d in aesthetics_descriptions:
# #     print(a,",",d,"\n")

# from not_found import not_found

# for aesthetic in not_found:
#     aesthetic_url_name = quote(aesthetic.replace(' ', '_'))
#     url = f"{BASE_URL}{aesthetic_url_name}"
#     webbrowser.open(url)

#     print(aesthetic, '\n')
#     print("Enter the description (type 'na' if not available or 'done' when finished):")
#     description = []
#     while True:
#         line = input()
#         if line.lower() == 'done':
#             break
#         if line.lower() == 'na':
#             description = ""
#             break
#         description.append(line)

#     if description != "":
#         full_description = '\n'.join(description)
#         aesthetics_descriptions.append((aesthetic, full_description))

# # Save to a file if needed
# with open('aesthetics_descriptions.py', 'w') as file:
#     file.write(f"aesthetics_descriptions = {aesthetics_descriptions}\n")