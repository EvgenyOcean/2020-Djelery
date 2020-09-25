from django.db import IntegrityError
from posts.models import Post

from selenium import webdriver

def run_browser():
    '''
    Запускает браузер
    '''
    # PATH = "C:\Program Files (x86)\chromedriver.exe"
    PATH = '/usr/local/bin/chromedriver'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=PATH)
    return driver


def save_results_db(articles, featured, user, source):
    '''
    Сохраняет результаты в дб
    '''
    print('starting saving')
    new_count = 0

    for article in articles:
        try:
            p = Post.objects.create(
                title = article['title'],
                content = article['content'],
                link = article['link'],
                featured = featured,
                source = source,
            )
            p.users.add(user)
            new_count += 1

        # UNIQUE CONSTRAIN MAY FAIL, MEANING I NEED TO SIMPLE ADD THE USER TO THE USERS
        except IntegrityError as err:
            print('The aricle already exists, adding user...')
            article = Post.objects.filter(link=article['link']).first()
            article.users.add(user)
        
        
        except Exception as e:
            print('Something went wrong, see error below')
            print(e)

    return print(f'found {new_count} new articles')