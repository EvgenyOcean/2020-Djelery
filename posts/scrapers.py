import time
import os

from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Post

from accounts.utils import decrypt_pw_hash, generate_pw_hash

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SigningInError(Exception):
    pass
    

class MainScraper:
    def __init__(self, path, source, user=''):
        self.path = path
        self.source = source
        self.articles_list = []
        self.loop = 1
        self._PATH = "C:\Program Files (x86)\chromedriver.exe"
        self.user = user
        # self._PATH = "/usr/local/bin/chromedriver"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--disable-gpu')
        # ARE YOU SURE YOU WANNA START THE BROWSER RIGHT HERE?
        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=self._PATH)

    def save_top_articles(self):
        '''
        Saves the articles into the db
        '''
        # this is the last step, so I presume it's save to shut the browser down here
        print('shutting down the browser')
        self.driver.quit()

        print(f'starting saving {len(self.articles_list)} articles')
        new_count = 0

        for article in self.articles_list:
            try:
                Post.objects.create(
                    title = article['title'],
                    content = article['content'],
                    link = article['link'],
                    featured = 1,
                    source = self.source,
                )
                new_count += 1

            except IntegrityError as err:
                article = Post.objects.filter(link=article['link']).first()
                if not article.featured:
                    print('Making the post featured...')
                    article.featured = True
                    article.save()
                print('Post is featured already!')

            except Exception as e:
                # IMPLEMENT LOGING
                print('Something went wrong, see error below')
                print(e)

        # IMPLEMENT LOGGIN
        msg = f'found {new_count} new articles'
        if not self.articles_list:
            msg = 'Nothing for ya today! ;('
        return msg

    def save_users_articles(self):
        print('shutting down the browser')
        self.driver.quit()

        print(f'starting saving {len(self.articles_list)} feed articles')
        new_count = 0

        for article in self.articles_list:
            try:
                p = Post.objects.create(
                    title = article['title'],
                    content = article['content'],
                    link = article['link'],
                    featured = 0,
                    source = self.source,
                )
                p.users.add(self.user)
                new_count += 1

            except IntegrityError as err:
                print('The aricle already exists, adding user...')
                article = Post.objects.filter(link=article['link']).first()
                article.users.add(self.user)
            
            except Exception as e:
                print('Something went wrong, see error below')
                print(e)

        msg = f'Found {new_count} new feed articles'
        if not self.articles_list:
            msg = 'Nothing for ya today! ;('
        return msg


    def save_user_credintials(self, password, mailname, username):
        #everything seems to be correct => saving service pass and email
        #it need source, passwrod, mailname
        print('saving creds')
        try:
            self.user = User.objects.get(username=username)
            hashed_pw = generate_pw_hash(password)
            new_mail = self.source + '_email'
            new_pass = self.source + '_pass'
            print(new_mail, new_pass)
            setattr(self.user.profile, new_mail, mailname)
            setattr(self.user.profile, new_pass, hashed_pw)
            self.user.profile.save()
        except Exception as err: 
            # IMPLEMENT LOGGING; BUT HOW COULD IT POSSIBLY GO WRONG?
            raise Exception from err

    def schedule_top_articles_scrap(self):
        pass

    def schedule_users_articles_scrap(self):
        pass

class VcScraper(MainScraper):
    def __init__(self, path='https://vc.ru/', source='vc'):
        super().__init__(path, source)

    def try_login(self, password, mailname, username):
        try:
            self.driver.get(self.path)
            # gettings to the email and password form
            login_click = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "site-header-user-login")))
            login_click.click()
            email_login = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-auth-target="signin-email"]')))
            email_login.click()

            email_field = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[type="email"][name="login"]')))
            email_field.send_keys(mailname)
            pass_field = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[type="password"][name="password"]')))
            pass_field.send_keys(password)
            pass_field.send_keys(Keys.RETURN)

            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'site-header-user-profile')))

            # save user credentials
            try:
                self.save_user_credintials(password, mailname, username)
            except Exception as err:
                return str(err.__cause__)

        except Exception as err: 
            # IMPLEMENT LOGGING
            raise SigningInError('Credentials provided are incorrect! GG WP!')

    def scrap_top(self, times=2, user_feed=False):
        '''
        They load 12 article per scroll point, so if times == 2
        We will get 24 article, 3 -> 36 and etc...
        In this case scrap_top is also good for scraping feed
        '''
        self.driver.get(self.path)
        for i in range(0, times):
            try:
                # I need to wait for articles to be rendered
                articles = WebDriverWait(self.driver, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "feed__item")))
                self.serialize_articles(articles)
                # delete existing articles => scroll a little => get new ones
                self.driver.execute_script("document.querySelectorAll('.feed__item').forEach(el => el.remove()); window.scrollBy(0, 1500);")
                # how to decline prev articles
            except Exception as err:
                return str(err.__cause__)

        self.driver.quit()
        if user_feed:
            return self.save_users_articles()
        else:
            return self.save_top_articles()

    def serialize_articles(self, articles):
        for article in articles:
            # crazy, but sometimes there's no title, just nothing o_O
            try:
                title = article.find_element_by_tag_name('h2').get_attribute('innerText')
            except:
                title = 'No title for this article'
            # crazy, but sometimes there's no subtitle, just a figure lol
            try:
                content = article.find_element_by_tag_name('p').get_attribute('innerHTML')
            except:
                content = 'No subtitle for this article'
            try:
                link = article.find_element_by_class_name('content-feed__link').get_attribute('href')
            except:
                link = '/'

            self.articles_list.append({
                'title': title,
                'content': content,
                'link': link,
            })

    def scrap_feed(self, password, mailname, username):
        try:
            self.try_login(password, mailname, username)
        except SigningInError as err:
            # IMPLEMENT LOGGING HERE OR UPTHERE 
            return str(err)

        return self.scrap_top(times=5, user_feed=True)

    def scrap_article_content(self, post):
        self.driver.get(self.path)
        # page can be removed
        try: 
            content = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "content--full")))
            WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "l-island-a")))
            javascript = ('arguments[0].querySelectorAll("figure").forEach(el => el.remove());' \
                        'arguments[0].querySelectorAll("img").forEach(el => el.remove());' \
                        'arguments[0].querySelectorAll("video").forEach(el => el.remove());' \
                        'arguments[0].querySelectorAll("iframe").forEach(el => el.remove());' \
                        'arguments[0].querySelectorAll("svg").forEach(el => el.remove());' \
                        'document.querySelectorAll(".content--full > div").forEach(el => (el.querySelector("p") || el.querySelector("ul") || el.querySelector("h2") || el.querySelector("h3") || el.querySelector("ol")) ? undefined : el.remove());' \
                        'arguments[0].querySelectorAll("script").forEach(el => el.remove());')
            self.driver.execute_script(javascript, content)
            content = content.get_attribute('innerHTML')
            self.driver.quit()
            post.full_content = content
            post.save()
            return content
        except: 
            return 'Something went wrong! Please, consider reading original article!'


class HabrScraper(MainScraper):
    def __init__(self, path='https://habr.com/ru/top/', source='habr'):
        super().__init__(path, source)


    def try_login(self, password, mailname):
        self.driver.get("https://account.habr.com/login/")
        email = self.driver.find_element_by_name('email')
        email.send_keys(mailname)
        pw = self.driver.find_element_by_name('password')
        pw.send_keys(password)
        pw.send_keys(Keys.RETURN)

        # GETTING TO THE FEED PAGE
        print('Try to access habr.ru if success => credentials are correct')
        # ideally I need to run both waiters and find which one comes first...
        # => you need to identify needed link by its class name or id or whatever is on it ^^
        try:
            # assuming its original english-based linux container
            try:
                link = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "Habr")))
                link.click()
            # for patriotic ones :)
            except: 
                link = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "Хабр")))
                link.click()
        except: 
            # thas ggwp cuz next time ill have to use proxy to bypass recaptcha
            # or buy some indian forces :D 
            # IMPLEMENT LOGGING
            raise SigningInError('Credentials provided are incorrect! GG WP!')

        return 'OK'

    def scrap_top(self, pages=1):
        '''
        Scrapes first page (20 articles) from habr
        TO IMPLEMENT AMOUNT OF PAGES [LOW]
        '''
        # JUST IN CASE
        if pages != 1:
            pages = 1
        print('Start finding elements!')
        self.driver.get(self.path)

        try:
            articles = self.driver.find_elements_by_tag_name('article')
            print(f'I found {len(articles)} articles!')
            return self.serialize_articles(articles, saving=True)
        except: 
            # IMPLEMENT LOGGING
            return 'Could not locate article tags!'

    def serialize_articles(self, articles, saving=False):
        '''
        To parse data into the dict
        '''

        for article in articles:
            try:
                # these ones are legit ^^
                title = article.find_element_by_tag_name('h2').find_element_by_tag_name('a').text
                content = article.find_element_by_tag_name('div').find_element_by_class_name('post__text').text
                link = article.find_element_by_tag_name('h2').find_element_by_tag_name('a').get_attribute('href')
            except: 
                # IMPLEMENT LOGGING
                return 'Unexpected DOM sctructure'
            
            content.replace('/n', ' ')

            self.articles_list.append({
                'title': title,
                'content': content,
                'link': link,
            })

        # only if there's no more pages to scrap
        if saving:
            if self.path == 'https://habr.com/ru/top/':
                print("Before saving top articles!")
                return self.save_top_articles()
            else:
                print("Before saving feed articles!")
                return self.save_users_articles()
        print('Not the final page!')
        
    def scrap_feed(self, password, mailname, username, pages=3):
        try:
            self.try_login(password, mailname)
        except SigningInError as err:
            # IMPLEMENT LOGGING OR UPTHERE 
            return str(err)
        
        for i in range(1, pages+1):
            try:
                url = f'https://habr.com/ru/feed/page{i}/'
                print(f'scraping in {url}')
                self.driver.get(url)
                articles = WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.TAG_NAME, "article")))
                if i == pages:
                    try:
                        self.save_user_credintials(password, mailname, username)
                    except Exception as err:
                        return str(err.__cause__)
                    # all the pages scraped, it's time for final serialization and then saving to the db
                    return self.serialize_articles(articles, saving=True)
                self.serialize_articles(articles)

            except: 
                # A little bit of RY
                if i == pages:
                    articles = []
                    try:
                        self.save_user_credintials(password, mailname, username)
                    except Exception as err:
                        return str(err.__cause__)
                    # all the pages scraped, it's time for final serialization and then saving to the db
                    return self.serialize_articles(articles, saving=True)

    def scrap_article_content(self, post):
        self.driver.get(self.path)
        # page can be removed
        try: 
            content = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "post__text")))
            javascript = ('arguments[0].querySelectorAll("figure").forEach(el => el.remove());' \
                          'arguments[0].querySelectorAll("img").forEach(el => el.remove());' \
                          'arguments[0].querySelectorAll("video").forEach(el => el.remove());' \
                          'arguments[0].querySelectorAll("iframe").forEach(el => el.remove());' \
                          'arguments[0].querySelectorAll("svg").forEach(el => el.remove());' \
                          'arguments[0].querySelectorAll(".spoiler").forEach(el => el.remove());' \
                          'arguments[0].querySelectorAll("script").forEach(el => el.remove());')
            self.driver.execute_script(javascript, content)
            content = content.get_attribute('innerHTML')
            self.driver.quit()
            post.full_content = content
            post.save()
            return content
        except: 
            return 'Something went wrong! Please, consider reading original article!'