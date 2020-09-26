from __future__ import absolute_import, unicode_literals

# import time
# import json
# import os

# from django.contrib.auth.models import User
# from posts.scrapers import HabrScraper
# from posts.models import Post
# from djelery.utils import run_browser, save_results_db
# from .utils import generate_pw_hash


# from celery import shared_task


# @shared_task
# def user_scraping(password, mailname, source, username):
#     '''
#     Gets data to enter the server; + server; + username
#     Then runs the browser and parses the feed
#     '''
#     if not source in ['habr', 'vc']: 
#         # IMPLEMENT user notifier for this case
#         return 'Source is not available'

#     scraper = HabrScraper(path='https://account.habr.com/login/')
#     result = scraper.scrap_feed(password, mailname, username)
#     return result