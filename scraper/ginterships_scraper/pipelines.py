import sqlite3, os

class SaveOfferPipeline:
    def open_spider(self, spider):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ginterships.db"))
        self.conn = sqlite3.connect(path)

    def process_item(self, item, spider):
        self.conn.execute(
            "INSERT OR IGNORE INTO offers(title, company, location, url, source, category) VALUES (?,?,?,?,?,?)",
            (item["title"], item.get("company"), item.get("location"),
             item["url"], item["source"], item.get("category", "stage")),
        )
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.conn.close()
