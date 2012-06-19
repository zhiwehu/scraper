__author__ = 'zhiwehu'

import unittest
import scraper
import main

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

        url='http://www.facebook.com/pages/173793155340?ref=ts'
        data = scraper.fb_scrape(url)
        self.assertEqual(0, data['likes'])
        self.assertEqual(0, data['talking_about_count'])
        self.assertEqual(0, data['checkins'])

        url='http://www.facebook.com/ATT'
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
        self.assertEqual(0, data['tweets'])

        url=''
        data = scraper.tw_scrape(url)
        self.assertEqual(0, data['followers_count'])
        self.assertEqual(0, data['tweets'])

        url='0'
        data = scraper.tw_scrape(url)
        self.assertEqual(0, data['followers_count'])
        self.assertEqual(0, data['tweets'])

        url='http://twitter.com/WalmartSpecials'
        data = scraper.tw_scrape(url)
        self.assertTrue(data['followers_count'] > 0)
        self.assertTrue(data['tweets'] > 0)

        url='https://twitter.com/#!/ExxonMobil_EU'
        data = scraper.tw_scrape(url)
        self.assertTrue(data['followers_count'] > 0)
        self.assertTrue(data['tweets'] > 0)

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

    def testReadCSV(self):
        file = None
        try:
            main.read_csv(file)
        except Exception as e:
            self.assertEqual('The file is none.', e.message)

        file = open('good_format.csv', 'rb')
        company_list = main.read_csv(file)
        self.assertTrue(len(company_list) > 0)
        list = main.get_social_media(company_list[0:1])
        self.assertEqual(1, len(list))
        c = list[0]
        self.assertTrue('Wal-Mart Stores', c.company_name)

        try:
            file = open('error_format.csv', 'rb')
            main.read_csv(file)
        except Exception as e:
            self.assertTrue(e)

if __name__ == '__main__':
    unittest.main()