from apscheduler.schedulers.blocking import BlockingScheduler
from scheduler.jobs import register_jobs


class LeadScheduler:

    def __init__(self):

        self.scheduler = BlockingScheduler()

    def start(self):

        register_jobs(self.scheduler)

        print("Lead AI Scheduler Started...")

        self.scheduler.start()