import subprocess, sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from mailer import notify_all

SPIDERS = ["dreamjob", "arbeitnow"]
EVERY_HOURS = 6

def run_cycle():
    print(f"\n=== Cycle {datetime.now():%Y-%m-%d %H:%M} ===")
    for s in SPIDERS:
        r = subprocess.run([sys.executable, "-m", "scrapy", "crawl", s],
                           cwd="scraper", capture_output=True, text=True)
        print(f"spider {s} terminé (code {r.returncode})")
    print("emails envoyés :", notify_all())

if __name__ == "__main__":
    run_cycle()                                    # une fois au démarrage
    sched = BlockingScheduler()
    sched.add_job(run_cycle, "interval", hours=EVERY_HOURS)
    print(f"Ginterships surveille les sites toutes les {EVERY_HOURS} h. Ctrl+C pour arrêter.")
    sched.start()
