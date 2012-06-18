__author__ = 'zhiwehu'

import unittest
import scraper

class ScraperTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testFacebook(self):
        url=None
        data = scraper.fb_scrape(url)
        self.assertEqual(0, data['likes'])
        self.assertEqual(0, data['talking_about_count'])
        self.assertEqual(0, data['checkins'])

        url=''
        data = scraper.fb_scrape(url)
        self.assertEqual(0, data['likes'])
        self.assertEqual(0, data['talking_about_count'])
        self.assertEqual(0, data['checkins'])

        url='0'
        data = scraper.fb_scrape(url)
        self.assertEqual(0, data['likes'])
        self.assertEqual(0, data['talking_about_count'])
        self.assertEqual(0, data['checkins'])

        url='http://www.facebook.com/walmart'
        data = scraper.fb_scrape(url)
        self.assertTrue(data['likes'] > 0)
        self.assertTrue(data['talking_about_count'] > 0)
        # TODO >= should be change >
        self.assertTrue(data['checkins'] >= 0)

        url='http://www.facebook.com/pages/Exxon-Mobil/103179436431279'
        data = scraper.fb_scrape(url)
        self.assertTrue(data['likes'] > 0)
        self.assertTrue(data['talking_about_count'] > 0)
        # TODO >= should be change >
        self.assertTrue(data['checkins'] >= 0)

        url='http://www.facebook.com/pages/Houston-TX/ConocoPhillips/173793155340?ref=ts'
        data = scraper.fb_scrape(url)
        self.assertTrue(data['likes'] > 0)
        self.assertTrue(data['talking_about_count'] > 0)
        # TODO >= should be change >
        self.assertTrue(data['checkins'] >= 0)

    def testTwitter(self):
        url=None
        data = scraper.tw_scrape(url)
        self.assertEqual(0, data['followers_count'])
        self.assertEqual(0, data['statuses_count'])

        url=''
        data = scraper.tw_scrape(url)
        self.assertEqual(0, data['followers_count'])
        self.assertEqual(0, data['statuses_count'])

        url='0'
        data = scraper.tw_scrape(url)
        self.assertEqual(0, data['followers_count'])
        self.assertEqual(0, data['statuses_count'])

        url='http://twitter.com/WalmartSpecials'
        data = scraper.tw_scrape(url)
        self.assertTrue(data['followers_count'] > 0)
        self.assertTrue(data['statuses_count'] > 0)

        url='https://twitter.com/#!/ExxonMobil_EU'
        data = scraper.tw_scrape(url)
        self.assertTrue(data['followers_count'] > 0)
        self.assertTrue(data['statuses_count'] > 0)

    def testYoutube(self):
        url=None
        data = scraper.yt_scrape(url)
        self.assertEqual(0, data['view_count'])
        self.assertEqual(0, data['subscriber_count'])

        url=''
        data = scraper.yt_scrape(url)
        self.assertEqual(0, data['view_count'])
        self.assertEqual(0, data['subscriber_count'])

        url='0'
        data = scraper.yt_scrape(url)
        self.assertEqual(0, data['view_count'])
        self.assertEqual(0, data['subscriber_count'])

        url='http://www.youtube.com/user/Gereports'
        data = scraper.yt_scrape(url)
        self.assertTrue(data['view_count'] > 0)
        self.assertTrue(data['subscriber_count'] > 0)

        url='https://www.youtube.com/citi'
        data = scraper.yt_scrape(url)
        self.assertTrue(data['view_count'] > 0)
        self.assertTrue(data['subscriber_count'] > 0)

if __name__ == '__main__':
    unittest.main()