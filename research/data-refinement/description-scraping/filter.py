from aesthetics_descriptions import aesthetics_descriptions
from listaesthetics import aesthetics as new
from listaestheticsmaster import aesthetics as master

# for a in new:
#     if a not in master:
#         print(a)
#         master.append(a)
# master.sort()
# # Write the aesthetics list to a file
# with open('listaesthetics-master.py', 'w') as file:
#     file.write(f"aesthetics = {master}\n")

# Assuming the aesthetics_descriptions list is already defined
# aesthetics_list = []
# descriptions_list = []

# for aesthetic, description in aesthetics_descriptions:
#     aesthetics_list.append(aesthetic)
#     descriptions_list.append(description)
    
from urllib.parse import quote
import webbrowser
BASE_URL = "https://aesthetics.fandom.com/wiki/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
aesthetics = [aesth for aesth, _ in aesthetics_descriptions]
descriptions = [desc for _, desc in aesthetics_descriptions]

# for a in aesthetics:
#     if a not in master:
# print(aesthetics)
# for aesthetic in aesthetics:
#     print(aesthetic)
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
