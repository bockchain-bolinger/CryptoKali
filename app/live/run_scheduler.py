from apscheduler.schedulers.blocking import BlockingScheduler
from app.config import settings
from app.db import init_db
from app.live.scanner import scan_once
from app.logger import logger

def job():
    res = scan_once()
    logger.info(f"scan ok | returned {len(res)} plans")

def main():
    init_db()
    sched = BlockingScheduler()
    sched.add_job(job, "interval", seconds=settings.SCAN_INTERVAL_SECONDS, max_instances=1, coalesce=True)
    logger.info(f"Scheduler started: every {settings.SCAN_INTERVAL_SECONDS}s")
    sched.start()

if __name__ == "__main__":
    main()

