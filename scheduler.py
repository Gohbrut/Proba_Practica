from apscheduler.schedulers.background import BackgroundScheduler

from scraper import scrape_products


scheduler = BackgroundScheduler()

# Schedule the scraping task to run every day at 12:00 PM, 1:00 PM, ..., 6:00 PM
def start_scheduler(app):
    scheduler.add_job(
        func=lambda: scrape_products(app),
        trigger='cron',
        hour='12-18',
        minute=0
    )

    scheduler.start()