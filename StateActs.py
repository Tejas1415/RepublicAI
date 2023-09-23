# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 11:48:40 2023

@author: Tejas

StateActs Download Sep 23rd
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import fitz
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt



########################################################### META DATA

## There are only 139 pages. 
## to check no of pages - go to https://prsindia.org/acts/states?page=99999
df_per_page = []
for i in list(range(1,139)):
    print(i)
    
    try:
        # URL of the web page to scrape
        url = "https://prsindia.org/acts/states?page={}".format(i)  
        
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
        df_temp = pd.DataFrame(pdf_data)
        df_per_page.append(df_temp)
    except:
        ## Run till the pages don't exist anymore and break
        break


df = pd.concat(df_per_page, axis = 0)



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






############################################### CONTENT DOWNLOAD

#### Now for each of these links, go to the pdf and extract the content to put it on the csv.

def remove_empty_lines(text):
    lines = text.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def clean_text(text):
    # Check if the input is a string, otherwise return the input unchanged
    if isinstance(text, str):
        text = remove_empty_lines(text)
        text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
        text = text.replace('...', ' ').replace('.....', ' ')
        # Replace non-standard characters with an empty string
        return re.sub(r'[^\x00-\x7F]+', ' ', text)
    else:
        return text


################## GOOGLE CLOUD VISION API
from google.cloud import vision_v1
import os

# Set the path to your JSON key file
json_key_path = "C:/Users/Tejas/Desktop/PrivateKeys/affable-visitor-399816-221829282aba.json"

# Initialize the Google Cloud Vision API client with the JSON key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_path
client = vision_v1.ImageAnnotatorClient()



    
content = []
for i in range(0, df.shape[0]):
    link = df['pdf_link'].iloc[i]
    
    ## print the progress
    print("In ", i, " Out of ", df.shape[0])
    
    # Fetch the PDF content from the URL
    response = requests.get(link)
    
    if response.status_code == 200:
        pdf_content = response.content
        
        # Open the PDF with PyMuPDF (fitz)
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        
        text = ''
        # Iterate through the pages and extract text
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            pdf_text = page.get_text()
            if pdf_text:
                text = text + pdf_text
            else:
                pixmap = page.get_pixmap(alpha=False)
                image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
                #image.show()
                image_bytes = BytesIO()
                image.save(image_bytes, format="PNG")
                image_bytes.seek(0)
                
                # Use Google Cloud Vision API to extract text from the image
                image_content = image_bytes.read()
                image = vision_v1.Image(content=image_content)
                response = client.text_detection(image=image)
                
                if response.text_annotations:
                    text += response.text_annotations[0].description + ' '

        
        text = clean_text(text)
        content.append(text)



df['content'] = content



# Replace missing values in the 'date_column' with '01/01/1950'
df['date'].fillna('01/01/1950', inplace=True)


## Save the csv
path = "C:/Users/Tejas/Desktop/RepublicAI/StateActs/"
df.to_csv(path + "StateActs_23sep23.csv", index = False)









