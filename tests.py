__author__ = 'jeffrey'
from logUtil import log

import unittest
import scraper
import main
import sqlite3

class ScraperTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testFacebook(self):
        # Test None url
        url=None
        data = scraper.fb_scrape(url)
        self.assertEqual(0, data['likes'])
        self.assertEqual(0, data['talking_about_count'])
        self.assertEqual(0, data['checkins'])

        # Test empty url
        url=''
        data = scraper.fb_scrape(url)
        self.assertEqual(0, data['likes'])
        self.assertEqual(0, data['talking_about_count'])
        self.assertEqual(0, data['checkins'])

        # Test 0 url
        url='0'
        data = scraper.fb_scrape(url)
        self.assertEqual(0, data['likes'])
        self.assertEqual(0, data['talking_about_count'])
        self.assertEqual(0, data['checkins'])

        # Test facebook id with parameters
        url='http://www.facebook.com/pages/173793155340?ref=ts'
        data = scraper.fb_scrape(url)
        self.assertEqual(0, data['likes'])
        self.assertEqual(0, data['talking_about_count'])
        self.assertEqual(0, data['checkins'])

        # Test facebook name
        url='http://www.facebook.com/ConocoPhillips'
        data = scraper.fb_scrape(url)
        self.assertTrue(data['likes'] > 0)
        self.assertTrue(data['talking_about_count'] > 0)
        self.assertTrue(data['checkins'] > 0)

        # Test facebook id
        url='http://www.facebook.com/pages/Exxon-Mobil/103179436431279'
        data = scraper.fb_scrape(url)
        self.assertTrue(data['likes'] > 0)
        self.assertTrue(data['talking_about_count'] > 0)
        self.assertTrue(data['checkins'] >= 0)

        # Test facebook id with parameters again
        url='http://www.facebook.com/pages/Houston-TX/ConocoPhillips/173793155340?ref=ts'
        data = scraper.fb_scrape(url)
        self.assertTrue(data['likes'] > 0)
        self.assertTrue(data['talking_about_count'] > 0)
        self.assertTrue(data['checkins'] >= 0)

    def testTwitter(self):
        # Test None url
        url=None
        data = scraper.tw_scrape(url)
        self.assertEqual(0, data['followers_count'])
        self.assertEqual(0, data['tweets'])

        # Test empty url
        url=''
        data = scraper.tw_scrape(url)
        self.assertEqual(0, data['followers_count'])
        self.assertEqual(0, data['tweets'])

        # Test 0 url
        url='0'
        data = scraper.tw_scrape(url)
        self.assertEqual(0, data['followers_count'])
        self.assertEqual(0, data['tweets'])

        # Test twitter id
        url='http://twitter.com/WalmartSpecials'
        data = scraper.tw_scrape(url)
        self.assertTrue(data['followers_count'] > 0)
        self.assertTrue(data['tweets'] > 0)

        # Test another format url
        url='https://twitter.com/#!/ExxonMobil_EU'
        data = scraper.tw_scrape(url)
        self.assertTrue(data['followers_count'] > 0)
        self.assertTrue(data['tweets'] > 0)

    def testYoutube(self):
        # Test None url
        url=None
        data = scraper.yt_scrape(url)
        self.assertEqual(0, data['view_count'])
        self.assertEqual(0, data['subscriber_count'])

        # Test empty url
        url=''
        data = scraper.yt_scrape(url)
        self.assertEqual(0, data['view_count'])
        self.assertEqual(0, data['subscriber_count'])

        # Test 0 url
        url='0'
        data = scraper.yt_scrape(url)
        self.assertEqual(0, data['view_count'])
        self.assertEqual(0, data['subscriber_count'])

        # Test youtube id
        url='http://www.youtube.com/user/Gereports'
        data = scraper.yt_scrape(url)
        self.assertTrue(data['view_count'] > 0)
        self.assertTrue(data['subscriber_count'] > 0)

        # Test another format url
        url='https://www.youtube.com/citi'
        data = scraper.yt_scrape(url)
        self.assertTrue(data['view_count'] > 0)
        self.assertTrue(data['subscriber_count'] > 0)

    def testMain(self):
        s = main.Scraper()

        # Test None file
        file = None
        try:
            s.read_csv(file)
        except Exception as e:
            self.assertEqual('The file is none.', e.message)

        # Test good format csv
        file = open('testdata/good_format.csv', 'rb')
        company_list = s.read_csv(file)
        self.assertTrue(len(company_list) > 0)
        list = s.get_social_media(company_list[0:1])
        self.assertEqual(1, len(list))
        c = list[0]
        self.assertTrue('Wal-Mart Stores', c.company_name)

        # Test error format csv
        try:
            file = open('testdata/error_format.csv', 'rb')
            s.read_csv(file)
        except Exception as e:
            self.assertTrue(e)

        # Test write db
        s.write_db(list,'testdata/data.db')
        conn = sqlite3.connect('testdata/data.db')
        c = conn.cursor()
        # Create table
        c.execute('DELETE FROM COMPANY')
        conn.commit()
        c.close()
        conn.close()

    """
    def testSchedule(self):
        cron.reSchedule(5)
        time.sleep(11)
        cron.reSchedule(10)
        time.sleep(21)
    """

if __name__ == '__main__':
    unittest.main()