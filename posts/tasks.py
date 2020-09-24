from __future__ import absolute_import, unicode_literals

import time
import json
import os

# Create your tasks here
# shared_task does not depend on a particular project
# thus it's good for reusability
from celery import shared_task
from .models import Post
from django.db import IntegrityError

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


    driver.get("https://habr.com/ru/top/")


    article_els = driver.find_elements_by_tag_name('article')
    print(f'I found {len(article_els)} articles!')
    an = driver.execute_script('return document.getElementsByTagName("article").length')
    print(f'Js found {an} articles')
    parse_received_data(article_els, 1)
    driver.quit()
    return 'Take it sloooww! Quite literally lol!'

# do i need to use shared task inhere?
@shared_task
def parse_received_data(article_els, featured):
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

    return save_results_db(articles, featured)

# do i need to use shared task inhere?
@shared_task
def save_results_db(articles, featured):
    print('starting saving')
    new_count = 0

    for article in articles:
        try:
            Post.objects.create(
                title = article['title'],
                content = article['content'],
                link = article['link'],
                featured = featured,
                source = 'habr',
            )
            new_count += 1

        except IntegrityError as err:
            article = Post.objects.filter(link=article['link']).first()
            article.featured = True
            article.save()

        except Exception as e:
            print('Something went wrong, see error below')
            print(e)

    return print(f'found {new_count} new articles')