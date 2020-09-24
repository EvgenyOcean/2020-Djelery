from __future__ import absolute_import, unicode_literals

import time
import json
import os

# Create your tasks here
# shared_task does not depend on a particular project
# thus it's good for reusability
from django.contrib.auth.models import User
from posts.models import Post
from djelery.utils import run_browser, parse_received_data
from .utils import generate_pw_hash

### CELERY IMPORTS ###
from celery import shared_task

### SCRAPING IMPORTS ###
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
###// SCRAPING IMPORTS ###

# TO DO: 
# 1. Tasks should be saved in db to check their status later

@shared_task
def user_scraping(mailname, password, source, current_username):
    if not source in ['habr', 'vc']: 
        return 'Source is not available'
    driver = run_browser()
    driver.get("https://account.habr.com/login/")

    # FINDING USER, CUZ SERIALIER WAS 
    # COMPLAINING ABOUT USER OBJ
    user = User.objects.filter(username=current_username)
    # couldn't think of the situation that would return false
    # but better safe than sorry
    if not user.exists():
        return 'The user does not exist o_O'
    user = user.first()

    # HANDLE SIGNING IN
    email = driver.find_element_by_name('email')
    email.send_keys(mailname)
    pw = driver.find_element_by_name('password')
    pw.send_keys(password)
    pw.send_keys(Keys.RETURN)


    # GETTING TO THE FEED PAGE
    try:
        try:
            print('start waiting')
            link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "Хабр")))
            print('finish waiting')
            link.click()
        except: 
            link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "Habr")))
            print('finish waiting')
            link.click()
    except: 
        return 'Credentials are incorrect OR recaptcha appeared'

    try:
        try:
            feed_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "Моя лента")))
            feed_link.click()
            print('Im in')
        except:
            feed_link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "My feed")))
            feed_link.click()
            print('Im in')
    except: 
        return 'Wasn\'t able to get to the feed page'


    #everything seems to be correct => saving service pass and email
    try:
        hashed_pw = generate_pw_hash(password)
        new_mail = source + '_email'
        new_pass = source + '_pass'
        setattr(user.profile, new_mail, mailname)
        setattr(user.profile, new_pass, hashed_pw)
        user.profile.save()
    except: 
        return 'Something went wrong with saving creds'
    
    # you need to find a way to wait for a page to load
    # i think 1sec is too expensive, but will do for now
    time.sleep(1)

    article_els = driver.find_elements_by_tag_name('article')
    print(f'I found {len(article_els)} articles!')
    an = driver.execute_script('return document.getElementsByTagName("article").length')
    print(f'Js found {an} articles')
    parse_received_data(article_els, 0, user, source)
    driver.quit()
    return 'Done!'