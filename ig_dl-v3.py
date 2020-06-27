# Author: Sylvan Chouhan

from selenium import webdriver
from bs4 import BeautifulSoup as bs
import re
import os
import requests
import shutil
from time import sleep
import getpass

def get_info():
    print('Your info')
    user = input('Enter username: ')
    pw = getpass.getpass('Enter password: ')
    print('Their info')
    target_user = input('Enter target username: ')
    return (user, pw, target_user)

def load_page(driver):
    ## Define variables
    user, pw, target_user = get_info()
    url = str("https://instagram.com/" + target_user)
    
    ## Login
    driver.get("https://instagram.com")
    sleep(3)
    driver.find_element_by_xpath("//input[@name=\"username\"]").send_keys(user)
    driver.find_element_by_xpath("//input[@name=\"password\"]").send_keys(pw)
    driver.find_element_by_xpath('//button[@type="submit"]').click()
    sleep(5)

    ## Go to target account page
    driver.get(url)
    sleep(2)
    #scroll(driver, 2)

def get_post_list(driver):

    #scroll_pause_time = timeout

    ## Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    href_list=[]
    while True:
        ## Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        ## Wait to load page
        #sleep(scroll_pause_time)
        sleep(2)

        ## Define html source and parser
        source = driver.page_source
        data=bs(source, 'html.parser')

        ## Find all links in html
        
        for elt in data.findAll('a'):
            href = elt.get('href')
            #print(href)
        
            ## Find and create list of all post links
            if href[:3] == "/p/":
                href_list.append(href)
            
                #driver.get("https://instagram.com"+href)
                #break
        #print(len(set(href_list)))
        #print(href_list)

        ## Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            ## If heights are the same it will exit the function
            break
        last_height = new_height

    return set(href_list) # Returns list without duplicates

def download_media(driver):

    local_links=[] #Init empty list of source url links

    while True: # Repeats for each item in photoset
        ## Define html source and parser
        post_source = driver.page_source
        post_data = bs(post_source, 'html.parser')
        
        switcher = True
        media_type = 'video'
        while True: # Repeats process for multi-vid or img/vid mixed posts because IG is annoying
            for media in post_data.findAll(media_type):
                
                sizes = media.get('sizes')
                post_class = media.get('class')
                #print(str(media.parent), ' Par\n\n')
                #print(post_class)
                #print(sizes)

                if media_type == 'img':
                    if sizes != None: # Skips over 'other posts by x'
                        if int(str(sizes).split('p')[0])>350:
                            if post_class == ['FFVAD']: # Skips over user icons and other unwanted imgs
                                local_links.append(media.get('src'))
                                #print(local_links)
                else:
                    local_links.append(media.get('src'))
                    #print(local_links)
            
            if switcher:
                switcher = False
                media_type = 'img'
                continue
            else:
                break # Inner loop

        ## Check for multi-photo posts and navigate to next photo, or break the loop
        #print(len(set(local_links)))
        try:
            driver.find_element_by_xpath('//button[@class="  _6CZji "]').click()
        except:
            break # Outer loop
    
    ## Download media from post page
    #print(len(set(local_links)))
    for link in set(local_links):
        try:
            media_downloader(link)
        except:
            #print("ERR in download_media(): couldn't call media_downloader()")
            continue

def scroll(driver, timeout):
    scroll_pause_time = timeout

    ## Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        ## Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        ## Wait to load page
        sleep(scroll_pause_time)

        ## Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            ## If heights are the same it will exit the function
            break
        last_height = new_height

def media_downloader(url):

    ## Set up the media URL and filename
    if url[-9] == '=':
        filename = str(url[-9:-1]+'.jpg')
    elif url[-9] != '=':
        filename = str(url[-9:-1]+'.mp4')
    else:
        exit()

    ## Open the url, set stream to True, this will return the stream content.
    r = requests.get(url, stream = True)

    ## Check if the media was retrieved successfully
    if r.status_code == 200:
        ## Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
    
        ## Open a local file with wb ( write binary ) permission.
        with open(filename,'wb') as f:
            shutil.copyfileobj(r.raw, f)
        
        print('Successfully downloaded: ',filename)
    else:
        print('Couldn\'t be retrieved')

def ig_bot():
    
    ## Init webdriver
    driver = webdriver.Firefox()
    
    load_page(driver)
    
    post_list = get_post_list(driver)

    remaining_posts = len(post_list)

    ## Cycle through posts downloading their content
    for link in post_list:
        driver.get('https://instagram.com'+link)
        #sleep(2)
        download_media(driver)
        remaining_posts -= 1
        print(str(remaining_posts)+' posts remaining')

ig_bot()
