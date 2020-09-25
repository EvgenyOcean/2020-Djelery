# Djelery (Djang + Celery news aggregator)
Aggregates news from such sources as: habr(implement); vc(to be implemented ;))

### Technologies uesd: 
<hr />

1. Django 
2. Celery (celery-beat; django-celery-results)
3. RabbitMQ
4. Posgress
5. JS (mainly for ajax requests)
6. Django Rest Framework
7. Beautifulsoup
8. Selenium

### Functionality:
<hr />

1. Scraping data from habr (top and user feed (for this one you'll need to provide credentials)
2. Scraping data from vc (to be implement)]
3. Using celery-beat we can configure users feed updates (default = 1 minute)

### Installation:
<hr />
1. docker-compose up => should work right away, but make sure to add your env machine ip to ALLOWED_HOST
2. configurable: crontab() and accounts.tasks for i in range(1, 4): => responsible for how many pages you want to scrap from your feed 
(habr has 50 I assume, but for testing purposes I lower the number)