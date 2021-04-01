A webscraper which scrapes my Uni's placement website, and checks for new placement notices.
The new placement notices are sent to the users using telegram_send library. This entire
functionality of scraping and sending messsages is triggered periodically using a CRON job hosted at cron-job.org. 

The motive behind this bot was to not miss out on important placements and saving us the hassle of checking the Uni website for new notices and deadlines to apply. 

**Libraries Used:**
- Flask
- BeautifulSoup
- telegram_send
- PyMongo

