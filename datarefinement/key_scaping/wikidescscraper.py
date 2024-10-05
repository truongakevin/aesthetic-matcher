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
# aesthetics_list = scrape_aesthetics()

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
    
    # Find the div with the class 'mw-parser-output'
    mw_parser_output = soup.find('div', class_='mw-parser-output')

    # Check for the specific <h3> element
    key_motifs_header = mw_parser_output.find('h3', class_='pi-data-label pi-secondary-font', string='Key motifs')
    key_values_header = mw_parser_output.find('h3', class_='pi-data-label pi-secondary-font', string='Key values')
    key_colours_header = mw_parser_output.find('h3', class_='pi-data-label pi-secondary-font', string='Key colours')
    related_aesthetics_header = mw_parser_output.find('h3', class_='pi-data-label pi-secondary-font', string='Related aesthetics')
    visuals_header = mw_parser_output.find('span', class_='mw-headline', string='Visuals')
    visual_header = mw_parser_output.find('span', class_='mw-headline', string='Visual')
    other_names_header = mw_parser_output.find('h3', class_='pi-data-label pi-secondary-font', string='Other names')

    # if not key_motifs_header and (key_values_header or key_colours_header):
    #     return False
    # else:
    #     return True
    # if not key_values_header and not key_motifs_header and key_colours_header:
    #     return False
    # else:
    #     return True
    if not related_aesthetics_header and not visuals_header and not visual_header and not other_names_header and not key_values_header and not key_motifs_header and not key_colours_header:
        return False
    else:
        return True
    # Check if the element was found
    # if key_values_header or key_colours_header or key_motifs_header or related_aesthetics_header:
    if key_values_header or key_colours_header or key_motifs_header:
        return True
        # print(aesthetic_name, "Found the 'Key values' header!")
    else:
        return False
        print(aesthetic_name, "The 'Key values' header was not found.")
    

from summarized_aesthetics import aesthetics as descriptions
aesthetics = []
for desc in descriptions:
    # pair = (desc.split(',')[0], [value.strip() for value in desc.split(',')[1:]])
    pair = (desc.split(',')[0], ','.join(desc.split(',')[1:]))
    aesthetics.append(pair)
    print(pair)
    
# Scrape images for each aesthetic in the list
aesthetics_descriptions = []
not_found = []
count = 0
for aesthetic, desc in aesthetics:
    # print(f"Scraping desciptions for {aesthetic}...")
    # print(scrape_aesthetic_description(aesthetic),aesthetic)
    if not scrape_aesthetic_description(aesthetic):
        print(aesthetic, desc)
        count += 1
    # description = scrape_aesthetic_description(aesthetic)
    # if description:
    #     aesthetics_descriptions.append((aesthetic, description))
    # else:
    #     not_found.append(aesthetic)
print(count)
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