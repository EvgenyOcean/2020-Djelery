# Djelery (Djang + Celery news aggregator)
Aggregates news from the following sources:
1. habr
2. vc

### Technologies uesd: 
<hr />

1. Django 
2. Celery (celery-beat; django-celery-results)
3. RabbitMQ
4. Posgress
5. JS (mainly for ajax requests)
6. Django Rest Framework
7. Selenium

### Functionality:
<hr />

1. Scraping data from habr: top and user's feed (for this one you'll need to provide credentials)
2. Scraping data from vc: top and users' feed (for this one you'll need to provide credentials)
3. Using celery-beat we can schedule automatic users' feed scraping (default = 5 minutes)

### Installation:
<hr />
1. docker-compose up => should work right away, but make sure to add your env machine ip to ALLOWED_HOST
<br />
2. configurable: crontab() and 
<br />
scrapers.HabrScraper.scrap_feed(..., pages=3) how many pages you want to scrap from user feed (as far as I'm concerned, habr gives me 50 available pages by deafult, but I reduced that amount based on test reasons) 
<br />
scrapers.HabrScraper.scrap_feed* more precisely, .scrap_top(), yes, it's a little bit messed up for now, the point being is, if you want to change how many times the page should be scrolled down option, you wanna find the line: return self.scrap_top(times=5, user_feed=True) and change times argument.