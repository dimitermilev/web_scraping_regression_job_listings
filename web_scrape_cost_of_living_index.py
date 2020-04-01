from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup 
import requests
import pandas as pd
import numpy as np
import sys
import re
import os
import json
import time
from collections import MutableMapping

def scrape_cost_index_by_city(jobs_data):
    '''Pull city and state information from the scraped jobs dataset'''
    jobs_data['CityState'] = jobs_data['jobLocation_address_addressLocality'].map(str) +", "+jobs_data['jobLocation_address_addressRegion']
    chromedriver = "/Applications/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    '''Create city links that match the cost index website'''
    link_cities = [city.replace(", ", "-").replace(" ", "-").lower() for city in list(raw_read['CityState'].dropna().unique())]
    link_cities_dict = {}
    for i, city in enumerate(link_cities):
        link_cities_dict[city] = list(raw_read['CityState'].dropna().unique())[i]
    '''Scrape cost index information from the bestplaces.net adding each city to the link'''
    main = webdriver.Chrome(chromedriver)
    cost_index = []
    for city in link_cities[0:2]:
        link = 'https://www.bestplaces.net/cost-of-living/{}/san-francisco-ca/50000'.format(city)
        city_info = {}
        '''Initialize Chrome Driver'''
        main.get(link)
        time.sleep(3)
        table_id = main.find_element(By.ID, 'mainContent_dgCOL')
        rows = table_id.find_elements(By.TAG_NAME, "tr") 
        for i, row in enumerate(rows):
            if i == 1:
                cols = row.find_elements(By.TAG_NAME, "td")
                for j, col in enumerate(cols):
                    if j == 1:
                        city_info[city] = col.text 
        cost_index.append(city_info)
        time.sleep(5)
    main.quit()
    return cost_index

def process_cost_index_data(cost_index_scrape):
    '''Turn raw scraped data from cost of index site into a formatted data frame'''
    chromedriver = "/Applications/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    result = {}
    for d in cost_index_scrape:
        result.update(d)
    score  = pd.DataFrame(pd.Series(result,index=result.keys()))
    score.columns = ['cost_index']
    score = score.reset_index()
    score.columns = ['city', 'cost_index']
    name  = pd.DataFrame(pd.Series(link_cities_dict,index=result.keys()))
    name.columns = ['city_full']
    name = name.reset_index()
    name.columns = ['city', 'city_full']
    final_cost_index = score.merge(name)
    return final_cost_index
