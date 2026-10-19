import scrapy
from ginterships_scraper.items import OfferItem

class MuseSpider(scrapy.Spider):
    name = "themuse"
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def start_requests(self):
        for page in range(1, 4):   # 3 pages
            yield scrapy.Request(
                f"https://www.themuse.com/api/public/jobs?level=Internship&page={page}"
            )

    def parse(self, response):
        for j in response.json().get("results", []):
            url = (j.get("refs") or {}).get("landing_page", "")
            if not url:
                continue
            yield OfferItem(
                title=j.get("name", ""),
                company=(j.get("company") or {}).get("name", ""),
                location=", ".join(l.get("name", "") for l in j.get("locations", [])),
                url=url,
                source="themuse",
            )
