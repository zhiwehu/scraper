__author__ = 'zhiwehu'

from apscheduler.scheduler import Scheduler
from main import Scraper
from logUtil import log

sched = Scheduler()
sched.start()

def doJob():
    file = open('good_format.csv')
    s = Scraper()
    count = s.write_db(s.get_social_media(s.read_csv(file)))
    log.info('%d records has been saved to database %s' % (count, 'data.db'))

def reSchedule(seconds=86400):
    try:
        sched.unschedule_func(doJob)
    except:
        pass
    sched.add_interval_job(doJob, seconds=seconds)
    sched.shutdown()
    sched.start()