import scrapy
from ginterships_scraper.items import OfferItem

class DreamjobSpider(scrapy.Spider):
    name = "dreamjob"
    start_urls = [
        "https://www.dreamjob.ma/stage/feed/",
        "https://www.dreamjob.ma/emploi/feed/",
    ]
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "Mozilla/5.0 (Ginterships student project)",
    }

    def parse(self, response):
        for item in response.xpath("//item"):
            title = item.xpath("title/text()").get(default="").strip()
            url = item.xpath("link/text()").get(default="").strip()
            if not (title and url):
                continue
            # étiquette selon le lien
            category = "stage" if "/stage/" in url or "stage" in title.lower() else "emploi"
            yield OfferItem(
                title=title, company="", location="Maroc",
                url=url, source="dreamjob.ma", category=category,
            )
