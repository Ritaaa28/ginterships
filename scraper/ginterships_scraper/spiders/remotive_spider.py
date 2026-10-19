import scrapy
from ginterships_scraper.items import OfferItem

KEYWORDS = ["intern", "internship", "trainee", "junior", "graduate", "apprentice"]

class RemotiveSpider(scrapy.Spider):
    name = "remotive"
    start_urls = ["https://remotive.com/api/remote-jobs?search=intern"]
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def parse(self, response):
        for j in response.json().get("jobs", []):
            title = j.get("title", "")
            if not any(k in title.lower() for k in KEYWORDS):
                continue
            yield OfferItem(
                title=title,
                company=j.get("company_name", ""),
                location=j.get("candidate_required_location", "Remote"),
                url=j.get("url", ""),
                source="remotive",
            )
