# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 11:13:16 2023

@author: Tejas

Download Supreme Court Data
"""


import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def supreme_court_year(year):
    # URL to scrape
    url = "http://www.liiofindia.org/in/cases/cen/INSC/{}/".format(year)
    
    # Create a Chrome WebDriver using webdriver_manager
    driver = webdriver.Chrome(executable_path='C:/Users/Tejas/.wdm/drivers/chromedriver/win64/116.0.5845.187/chromedriver.exe')
    
    # Open the URL in the browser
    driver.get(url)
    
    # Find all <h3> elements
    h3_elements = driver.find_elements(By.TAG_NAME, 'h3')
    
    # Initialize empty lists to store data
    headings = []
    hyperlink_texts = []
    hyperlinks = []
    
    # Iterate through each <h3> element
    for h3_element in h3_elements:
        # Get the heading text
        heading = h3_element.text.strip()
        
    
        # Find the <ul> element with class "make-database" following the current <h3>
        ul_element = h3_element.find_element(By.XPATH, 'following-sibling::ul[@class="make-database"]')
    
        # Find all <li> elements inside the current <ul>
        li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
    
        for li_element in li_elements:
            # Get the hyperlink text and hyperlink
            hyperlink_text = li_element.text.strip()
            hyperlink = li_element.find_element(By.TAG_NAME, 'a').get_attribute('href')
    
            # Append data to respective lists
            headings.append(heading)
            hyperlink_texts.append(hyperlink_text)
            hyperlinks.append(hyperlink)
    
    
    # Create a DataFrame
    data = {
        'Heading': headings,
        'Hyperlink Text': hyperlink_texts,
        'Hyperlink': hyperlinks
    }
    
    df = pd.DataFrame(data)
    
    
    import time
    content = []
    for i in range(0, df.shape[0]):
        link = df['Hyperlink'].iloc[i]
        driver.get(link)
        time.sleep(0.5)
        
        # Find all <p> elements
        p_elements = driver.find_elements(By.TAG_NAME, 'p')
        
        # Initialize a variable to store the content
        all_content = []
        
        # Loop through each <p> element
        for p_element in p_elements:
            # Get the text content of the <p> element
            p_text = p_element.text
            
            # Append the content to the list
            all_content.append(p_text)
        
        # Combine all the content into one string
        all_content = all_content[:-1]  ## Last disclaimer notice is not needed.
        combined_content = ' \n '.join(all_content)
        content.append(combined_content)
    
    lawyers = all_content[2]
    df['content'] = content
    df['lawyers'] = lawyers

    # Close the browser
    driver.quit()
    
    return df











############################################ Main Code
import time
path = "C:/Users/Tejas/Desktop/RepublicAI/SupremeCourt/"
years = list(range(2008, 2024))

for y in years:
    df = supreme_court_year(y)
    df.to_csv(path + "SupremeCourt_{}.csv".format(y), index = False)
    time.sleep(4)





































