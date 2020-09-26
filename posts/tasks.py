from __future__ import absolute_import, unicode_literals

import time
import json
import os
import requests


# Create your tasks here
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Post

from celery import shared_task
from accounts.utils import decrypt_pw_hash

from .scrapers import HabrScraper
from bs4 import BeautifulSoup



@shared_task
def scrap_top_posts():
    scraper = HabrScraper()
    # IMPLEMENT LOGGING
    return scraper.scrap_top()


@shared_task
def user_scraping(password, mailname, source, username):
    '''
    Gets data to enter the server; + server; + username
    Then runs the browser and parses the feed
    '''
    if not source in ['habr', 'vc']: 
        # IMPLEMENT user notifier for this case
        return 'Source is not available'

    scraper = HabrScraper(path='https://account.habr.com/login/')
    result = scraper.scrap_feed(password, mailname, username)
    return result


@shared_task
def get_full_content(post_id):
    '''
    Gets full content of the article
    '''
    post = Post.objects.filter(id=post_id).first()

    if post.full_content:
        print('Loading article from db!')
        return post.full_content

    link = post.link

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    }

    try:
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')
        content_strings = soup.find('article', class_='post').stripped_strings
        content = " ".join(list(content_strings))
        post.full_content = content
        post.save()
    except: 
        # idk some articles just don't load right
        # should go with selenium here as well as a back up option
        return 'Something went wrong, please consider reading original article by clicking Read More'

    return content

@shared_task
def start_scraping_beat():
    '''
    Celery task, updating the feed every 24 hours
    '''
    # should get all the services in the arr
    # cuz if services grow, then ifs will grow as well
    users = User.objects.all()
    for user in users:
        # I need to find if user has vc and habr credentials 
        if user.profile.habr_pass:
            print('Scraping for a specific user now!')
            # start habr scraping
            mailname = user.profile.habr_email
            password = decrypt_pw_hash(user.profile.habr_pass)
            source = 'habr'
            current_username = user.username
            # print(password, mailname, source, current_username)
            user_scraping.delay(mailname, password, source, current_username)
        if user.profile.vc_pass:
            # start vc scraping
            pass

    return 'Main Beat finished, waiting for subtasks'
