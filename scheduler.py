# ============================================================
#   SCHEDULER.PY — APScheduler se automatic daily schedule
#   Usage: python scheduler.py
#   Runs 24/7 — uploads at configured UPLOAD_TIMES each day
# ============================================================

import time
import signal
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from main import make_one_video
from logger import logger, get_today_count
from config import UPLOAD_TIMES, VIDEOS_PER_DAY


scheduler = BlockingScheduler(timezone="Asia/Karachi")


def scheduled_job():
    """Scheduled time pe ek video banao (agar daily limit nahi bhari)."""
    today_count = get_today_count()

    if today_count >= VIDEOS_PER_DAY:
        logger.info(f"⏭️  Skipping — already {today_count}/{VIDEOS_PER_DAY} videos today")
        return

    logger.info(f"\n🕐 Scheduled job started at {datetime.now().strftime('%H:%M:%S')}")
    logger.info(f"   Today's count: {today_count}/{VIDEOS_PER_DAY}")

    result = make_one_video()
    if result["success"]:
        logger.info(f"✅ Scheduled video done: {result['title']}")
    else:
        logger.error(f"❌ Scheduled video failed: {result['error']}")


def setup_schedule():
    """UPLOAD_TIMES ke mutabiq jobs add karo."""
    for time_str in UPLOAD_TIMES:
        hour, minute = time_str.split(":")
        scheduler.add_job(
            scheduled_job,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            id=f"video_{time_str.replace(':', '')}",
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 min late hoga toh bhi chale
        )
        logger.info(f"  ⏰ Scheduled: {time_str} (PKT)")


def graceful_shutdown(signum, frame):
    logger.info("🛑 Shutdown signal received — stopping scheduler...")
    scheduler.shutdown(wait=False)
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    logger.info("=" * 55)
    logger.info("  YouTube Bot Scheduler — Starting")
    logger.info(f"  Videos per day : {VIDEOS_PER_DAY}")
    logger.info(f"  Upload times   : {', '.join(UPLOAD_TIMES)} (PKT)")
    logger.info("=" * 55)

    setup_schedule()

    # Show next scheduled jobs
    for job in scheduler.get_jobs():
        logger.info(f"  Next run: {job.next_run_time} — {job.id}")

    logger.info("\n✅ Scheduler running... Press Ctrl+C to stop\n")

    try:
        scheduler.start()
    except Exception as e:
        logger.error(f"❌ Scheduler crashed: {e}")
        sys.exit(1)
