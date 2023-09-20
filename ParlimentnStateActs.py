# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 22:02:22 2023

@author: Tejas

Parliment and state acts data download
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

# URL of the web page to scrape
url = "https://prsindia.org/acts/parliament"  

# Send an HTTP GET request to fetch the web page
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the web page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the <a> (anchor) elements
    all_links = soup.find_all('a')

    # Extract the PDF links and their associated text
    pdf_data = []
    for link in all_links:
        if link['href'].endswith('.pdf'):
            pdf_url = link['href']
            link_text = link.get_text()
            pdf_data.append({'text': link_text, 'url': pdf_url})

# Create a DataFrame from the extracted data
df = pd.DataFrame(pdf_data)



## df url - update the url, since they are faulty when read in.
df['url'] = df['url'].apply(lambda x: "https://prsindia.org" + x)


## Rename the columns and extract dates
df.columns = ['hyperlink_text', 'pdf_link']

def extract_year_and_format(text):
    year_match = re.search(r'\b\d{4}\b', text)
    
    # If a year is found, extract it and format it as "dd/mm/yyyy"
    if year_match:
        year = year_match.group()
        return f"01/01/{year}"  
    else:
        return None  


df['date'] = df['hyperlink_text'].apply(extract_year_and_format)





#### Now for each of these links, go to the pdf and extract the content to put it on the csv.


















