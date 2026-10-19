import scrapy
from ginterships_scraper.items import OfferItem

KEYWORDS = ["intern", "praktik", "werkstudent", "trainee", "stage", "stagiaire"]

class ArbeitnowSpider(scrapy.Spider):
    name = "arbeitnow"
    start_urls = ["https://www.arbeitnow.com/api/job-board-api"]
    custom_settings = {"ROBOTSTXT_OBEY": False}   # API publique faite pour les programmes

    def parse(self, response):
        for j in response.json().get("data", []):
            texte = (j.get("title", "") + " " + " ".join(j.get("job_types", []))).lower()
            if any(k in texte for k in KEYWORDS):          # on garde seulement les stages
                yield OfferItem(
                    title=j.get("title", ""),
                    company=j.get("company_name", ""),
                    location=j.get("location", ""),
                    url=j.get("url", ""),
                    source="arbeitnow",
                )
