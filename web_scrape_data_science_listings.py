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

def initiate_scraper_job_listings(title, location):
    '''Function to initiate a selenium webdriver and input initial job search term and job location'''
    searchbar_job = title
    searchbar_loc = location
    '''Set global URL variables, to be used in every scrape'''
    chromedriver = "/Applications/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    baseurl = 'https://www.glassdoor.com'
    searchbar_link = 'https://www.glassdoor.com/sitedirectory/title-jobs.htm'
    '''Initialize Chrome Driver'''
    main = webdriver.Chrome(chromedriver)
    main.get(searchbar_link)
    '''Prepare for searchbar actions'''
    searchBar = main.find_element_by_name("clickSource")
    searchJob = main.find_element_by_name("sc.keyword")
    searchLocation = main.find_element_by_id("sc.location")
    '''Take searchbar actions'''
    searchJob.send_keys(searchbar_job)
    time.sleep(1)
    searchLocation.send_keys(searchbar_loc)
    time.sleep(1)
    searchLocation.send_keys(Keys.ENTER)
    time.sleep(5)
    '''Get info from main page: html and total pagination'''
    main_soup = BeautifulSoup(main.page_source, "html5lib")
    for div in main_soup.find_all('div', class_='cell middle hideMob padVertSm'):
        pages_str = div.text
    pages = [int(s) for s in pages_str.split() if s.isdigit()]       
    max_pagination = pages[-1]
    '''Return webdriver, and the total pagination of the job/city search terms'''
    return main

def loop_scraper_job_listings(selenium_webdriver, pages):
    '''Function to loop through each job listing and collect information from HTML elements and JSON scripts'''
    jobs_all = []
    page_links_all = []
    for _ in range(1, pages):    
        '''Get the links for all jobs on search page - approx 30 per each page'''
        page_links = []
        for link in selenium_webdriver.find_elements_by_xpath("//div[@class='logoWrap']/a"):
            page_links.append(link.get_attribute('href'))
        '''Loop through each job on the page, going to that job listing to scrape information '''   
        for link in page_links[0:3]:
            browser = webdriver.Chrome(chromedriver)
            browser.get(link)
            time.sleep(10)
            '''Collect job listing information, first by initializing variables to collect'''
            soup = BeautifulSoup(browser.page_source, "html5lib")
            print(soup)
            job = ''
            job_desc = ''
            city = ''
            company = ''
            company_details = ''
            jsonvar = ''
            ratings_n = ''
            ceo = ''
            friend = ''
            benefits_rating = ''
            benefits_n = ''
            ratings_dict = {}
            categories = []
            ratings = []
            '''Collect information from main job page, before iterating through each tab'''
            try:
                job_desc = browser.find_element_by_class_name("jobDesc").text
                city = browser.find_element_by_class_name("subtle.ib").text[3:]
                company = browser.find_element_by_class_name("strong.ib").text
                job = browser.find_element_by_class_name("noMargTop.margBotXs.strong").text
            except:
                pass
            print("Crawling {} job listed by {}.".format(job, company))
            '''Each job listing has info stored in JSON format. Collecting it here.'''
            try:
                json_dict = {}
                jsonvar = soup.find("script", type="application/ld+json").text
                '''Format the json data in the HTML code for interpretation'''
                jsonvar_p = jsonvar.replace("\n    ","").replace("\n                ","").replace("\n", "").replace("\t","").replace("    </script>","") 
                '''Push into a dictionary and then flatten it for better pandas processing'''
                json_dict = flatten(json.loads(jsonvar_p))
            except:
                pass
            '''Each job listing stores information in tabs that need to be opened for scraper to access'''
            try:
                a = browser.find_elements_by_class_name("link")
                for button in a:
                    button.click()
                    time.sleep(2)
                    '''Ratings information'''
                    try:
                        ratings_all = browser.find_element_by_class_name("stars").text
                        categories = re.findall(r"[-+]\d*\.\d+|\D+", ratings_all)
                        ratings = re.findall(r"[-+]?\d*\.\d+|\d+", ratings_all)
                        for i, item in enumerate(categories):
                            if item == '.':
                                del categories[i]
                        for i, item in enumerate(categories):
                            ratings_dict[categories[i].replace("\n","").replace(" ","").replace("/","").replace("&","")] = ratings[i]
                    except:
                        pass
                    '''Number of ratings submitted'''
                    try:
                        ratings_n = browser.find_element_by_class_name("minor.css-0.e1qhxspr2").text
                    except:
                        pass
                    '''Company info'''
                    try:
                        # The company details are collected as a string of text to be processed later
                        company_details = browser.find_element_by_class_name("empBasicInfo").text
                    except:
                        pass
                    '''CEO approval ratings'''
                    try:
                        ceo = browser.find_element_by_class_name("cell.middle.chart.ceoApprove").text
                    except:
                        pass
                    '''Would recommend to friend ratings'''
                    try:
                        friend = browser.find_element_by_class_name("cell.middle.chart").text
                    except:
                        pass
                    '''Benefit ratings values'''
                    try:
                        benefits_n = browser.find_element_by_class_name("minor.noMargTop.padSm").text
                    except:
                        pass
                    '''Benefit ratings counts'''
                    try:
                        benefits_rating = browser.find_element_by_class_name("ratingNum.margRtSm").text
                    except:
                        pass
            except:
                pass
            '''Push all scraped data into a list of dictionaries - each dictionary is a job listing'''
            job_vars = {
            "name": job,
            "company": company,
            "company_details": company_details,
            "ratings_count": ratings_n,
            "benefits_ratings": benefits_rating,
            "benefits_count": benefits_n,
            "ceo_approve": ceo,
            "friend_recommend": friend,
            "url": link,
            "description": job_desc
            }
            '''As data are in 2 or 3 dictionaries (depending on what was available) append differently'''
            try:
                all_vars = {**job_vars, **json_dict, **ratings_dict}
            except:
                all_vars = {**job_vars, **json_dict}
            '''Finished collecting - append into the list of dictionaries'''
            jobs_all.append(all_vars)
            time.sleep(5) 
            '''Close job listing page'''
            browser.quit()    
        '''Print job progress status'''
        page_links_all.extend(page_links)
        print("{} jobs scraped so far.".format(len(jobs_all)))
        '''Find next button to take action on'''
        next_button = selenium_webdriver.find_element_by_class_name("next")        
        '''Try and push the button. If there is a pop up in the way, close it and continue.'''
        try:
            next_button.click()
        except:
            popup = selenium_webdriver.find_element_by_id("prefix__icon-close-1")
            time.sleep(5)
            popup.click()      
            next_button.click()
    main.quit()
    return jobs_all
    