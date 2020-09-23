from __future__ import absolute_import, unicode_literals

import time
import json
import os

# Create your tasks here
# shared_task does not depend on a particular project
# thus it's good for reusability
from celery import shared_task
from .models import Post

### SCRAPING IMPORTS ###
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
###// SCRAPING IMPORTS ###


# later on, add can be called in any view funciton
# with .delay() method
@shared_task
def start_scraping():
    PATH = "C:\Program Files (x86)\chromedriver.exe"
    # PATH = '/usr/local/bin/chromedriver'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=PATH)


    driver.get("https://account.habr.com/login/")

    # HANDLE SIGNING IN
    email = driver.find_element_by_name('email')
    email.send_keys(os.environ.get('DJ_EMAIL'))

    pw = driver.find_element_by_name('password')
    pw.send_keys(os.environ.get('DJ_PASS'))

    # emulate enter
    pw.send_keys(Keys.RETURN)
    try:
        print('start waiting')
        link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Хабр")))
        print('finish waiting')
        link.click()
    except: 
        link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Habr")))
        print('finish waiting')
        link.click()
    try:
        feed_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Моя лента")))
        feed_link.click()
        print('Im in')
    except:
        try:
            feed_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "My feed")))
            feed_link.click()
            print('Im in')
        except: 
            print(driver.execute_script("return document.body.innerHTML"))
    
    # you need to find a way to wait for a page to load
    time.sleep(1)

    article_els = driver.find_elements_by_tag_name('article')
    print(f'I found {len(article_els)} articles!')
    an = driver.execute_script('return document.getElementsByTagName("article").length')
    print(f'Js found {an} articles')
    parse_received_data(article_els)
    driver.quit()
    return 'Take it sloooww! Quite literally lol!'

# do i need to use share task inhere?
@shared_task
def parse_received_data(article_els):
    articles = []

    print('Parsing received data...')
    for article in article_els:
        header = article.find_element_by_tag_name('h2').find_element_by_tag_name('a').text
        content = article.find_element_by_tag_name('div').find_element_by_class_name('post__text').text
        link = article.find_element_by_tag_name('h2').find_element_by_tag_name('a').get_attribute('href')
        
        # replacer does not work, gotta use regex for /n/n and /n/n/n/n cases
        content.replace('/n', ' ')
    
        # here you should go with your db
        articles.append({
            "title": header,
            "content": content,
            "link": link
        })

    return save_results_db(articles)

# do i need to use share task inhere?
@shared_task
def save_results_db(articles):
    print('starting saving')
    new_count = 0

    for article in articles:
        try:
            Post.objects.create(
                title = article['title'],
                content = article['content'],
                link = article['link'],
                featured = 1,
                source = 'habr',
            )
            new_count += 1
        except Exception as e:
            print('failed at latest_article is none')
            print(e)
    return print(f'found {new_count} new articles')