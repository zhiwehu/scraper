__author__ = 'jeffrey'

from apscheduler.scheduler import Scheduler
from main import Scraper
from logUtil import log
import sqlite3
from utils import ScrapeThread
from pyloginfb import fblogin

sched = Scheduler()
sched.start()

def doJob():
    '''
        Do the scrape every interval time
    '''
    #get all csv and db paths
    conn = sqlite3.connect('data/setting.db')
    c = conn.cursor()
    csv_db_file_list = c.execute('SELECT CSV_FILE_PATH, DB_FILE_PATH FROM CSV_DB').fetchall()
    c.close()
    conn.close()
    threads = []

    fblogin()

    for item in csv_db_file_list:
        csv_path = item[0]
        db_path  = item[1]
        s = Scraper()
        thread = ScrapeThread(s,csv_path, db_path)
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    log.info('all scraper threads finished in doJob()')
    return

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