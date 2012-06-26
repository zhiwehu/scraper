__author__ = 'zhiwehu'

from threading import Timer
from main import Scraper
from logUtil import log

#second
t = 300

def cronjob():
    def scrape():
        file = open('good_format.csv')
        s = Scraper()
        count = s.write_db(s.get_social_media(s.read_csv(file)))
        log.info('%d records has been saved to database %s' % (count, 'data.db'))

    scrape()
    Timer(t, cronjob).start()

cronjob()
