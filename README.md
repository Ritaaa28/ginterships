# Ginterships

A web application that periodically scrapes several internship sources, detects **newly published offers**, and emails each subscriber only the offers that match their interests and that they have not received yet.

## Features
- Scrapy spiders: RSS (dreamjob.ma, Morocco) and public JSON API (Arbeitnow, Europe)
- SQLite storage with de-duplication by URL (INSERT OR IGNORE)
- Flask web app: home, sign up / sign in, profile (choose interests), "My offers" page
- Email alerts with memory of what was already sent (table `sent`)
- APScheduler: runs the spiders and the notifications every 6 hours
- Offers are labelled stage / emploi (an "Emplois" page is planned)

## Architecture
Websites -> Scrapy spiders -> pipeline -> SQLite <- Flask app <- user

Scheduler -> spiders -> mailer -> email only for new, matching offers

## Quick start

    pip install -r requirements.txt
    python db.py
    python seed_demo.py
    python app.py
    python scheduler.py

`python app.py` starts the site on http://127.0.0.1:5000. Run `python scheduler.py` in a second terminal.

To scrape real offers manually: go to the `scraper` folder, then run `python -m scrapy crawl dreamjob` (or `arbeitnow`).

## Email
Without configuration, emails are saved as HTML files in the `outbox` folder (test mode).
For real sending, set the environment variables GINTERSHIPS_EMAIL and GINTERSHIPS_APP_PASSWORD (a Gmail app password). Never commit them.

## Responsible scraping
Only sources that allow programmatic access are used (RSS feeds and public APIs), with an honest User-Agent and a download delay.

Student project By Ghayta EL ferrassy.
