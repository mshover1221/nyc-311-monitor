from apscheduler.schedulers.blocking import BlockingScheduler
from run import main

scheduler = BlockingScheduler()

# Run every 15 minutes
scheduler.add_job(main, 'interval', minutes=15)

print("Scheduler started. Fetching data every 15 minutes...")
scheduler.start()

