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

from .scrapers import HabrScraper, VcScraper
from bs4 import BeautifulSoup



@shared_task
def scrap_top_posts(source):
    if source == 'habr':
        scraper = HabrScraper()
        # IMPLEMENT LOGGING
        return scraper.scrap_top()
    elif source == 'vc':
        scraper = VcScraper()
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
    result = ''
    if source == 'habr':
        scraper = HabrScraper(path='https://account.habr.com/login/')
        result = scraper.scrap_feed(password, mailname, username)
    elif source == 'vc':
        scraper = VcScraper()
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
    source = post.source

    if source =='habr':
        scraper = HabrScraper(path=link)
    
    elif source == 'vc':
        scraper = VcScraper(path=link)

    return scraper.scrap_article_content(post)

@shared_task
def start_scraping_beat():
    '''
    Celery task, updating the feed every 24 hours
    '''
    # should get all the services in the arr
    # cuz if services grow, then ifs will grow as well
    users = User.objects.all()
    for user in users:
        print('Scraping for a specific user now!')
        # start habr scraping
        username = user.username

        if user.profile.habr_pass:
            mailname = user.profile.habr_email
            password = decrypt_pw_hash(user.profile.habr_pass)
            source = 'habr'

            return user_scraping.delay(password, mailname, source, username)

        if user.profile.vc_pass:
            mailname = user.profile.vc_email
            password = decrypt_pw_hash(user.profile.vc_pass)
            source = 'vc'

            return user_scraping.delay(password, mailname, source, username)

    return 'Main task finished, waiting for subtasks'
