class MainScraper:
    def __init__(self, path):
        self.path = path
        self.articles_list = []
        self.loop = 1
        self._PATH = "C:\Program Files (x86)\chromedriver.exe"
        # self._PATH = "/usr/local/bin/chromedriver"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=self._PATH)

    def save_top_articles():
        pass 

    def save_users_articles():
        pass

    def schedule_top_articles_scrap():
        pass

    def schedule_top_articles_scrap():
        pass

class VcScraper(MainScraper):
    def __init__(self, path='https://vc.ru/'):
        super().__init__(path)

    def try_login(self):
        pass

    def scrap_top(self, times=2):
        '''
        They load 12 article per scroll point, so if times == 2
        We will get 24 article, 3 -> 36 and etc...
        '''
        self.driver.get(self.path)
        for i in range(0, times):
            # I need to wait for articles to be rendered
            articles = WebDriverWait(self.driver, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "feed__item")))
            self.serialize_articles(articles)
            # delete existing articles => scroll a little => get new ones
            self.driver.execute_script("document.querySelectorAll('.feed__item').forEach(el => el.remove()); window.scrollBy(0, 1500);")
            # how to decline prev articles

        self.driver.quit()
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
            # i don't know what else to expect :)
            try:
                link = article.find_element_by_class_name('content-feed__link').get_attribute('href')
            except:
                link = '/'

            self.articles_list.append({
                'title': title,
                'content': content,
                'link': link,
            })

    def scrap_feed(mailname, password):
        pass


class HabrScraper(MainScraper):
    def __init__(self, path='https://habr.com/ru/top/'):
        super().__init__(path)


    def try_login(self):
        pass

    def scrap_top(self, pages=1):
        '''
        Scrapes first page (20 articles) from habr
        TO IMPLEMENT AMOUNT OF PAGES [LOW]
        '''
        self.driver.get(self.path)

        article_els = driver.find_elements_by_tag_name('article')
        print(f'I found {len(article_els)} articles!')
        self.serialize_articles(article_els)
        driver.quit()
        return 'Scraping top articles is finished'

    def serialize_articles(self, articles):
        '''
        To parse data into the dict
        '''

        for article in article_els:
            # these ones are legit ^^
            header = article.find_element_by_tag_name('h2').find_element_by_tag_name('a').text
            content = article.find_element_by_tag_name('div').find_element_by_class_name('post__text').text
            link = article.find_element_by_tag_name('h2').find_element_by_tag_name('a').get_attribute('href')
            
            content.replace('/n', ' ')
        
            self.articles_list.append({
                'title': title,
                'content': content,
                'link': link,
            })
        
        return self.save_top_articles()
        
    def scrap_feed(mailname, password):
        pass