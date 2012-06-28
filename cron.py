__author__ = 'jeffrey'

from apscheduler.scheduler import Scheduler
from main import Scraper
from logUtil import log

sched = Scheduler()
sched.start()

def doJob():
    '''
        Do the scrape every interval time
    '''
    file = open('data/good_format.csv')
    s = Scraper()
    count = s.write_db(s.get_social_media(s.read_csv(file)),'data.db')
    log.info('%d records has been saved to database %s' % (count, 'data.db'))

def reSchedule(seconds=86400):
    '''
        Re-schedule the job with new interval.

        @type seconds: int
        @param seconds: the new interval seconds

        @rtype: None
        @return: None
    '''
    log.debug('job reschedule seconds %d' % seconds)
    try:
        sched.unschedule_func(doJob)
    except Exception as e:
        log.error(e)
        pass
    sched.add_interval_job(doJob, seconds=seconds)