__author__ = 'zhiwehu'

import sys
import csv
import sqlite3
import logging
from urlparse import urlparse
from datetime import datetime

import scraper
from progress_bar import ProgressBar

log = logging.getLogger('log.txt')

class CompanyURL(object):
    def __init__(self, company_name, fb_url, tw_url, yt_url):
        """
            Init method for CompanyUrl object

            @type company_name: string
            @param company_name: company name
            @type fb_url: string
            @param fb_url: facebook url
            @type tw_url: string
            @param tw_url: twitter url
            @type yt_url: string
            @param yt_url: youtube url

            @rtype:  None
            @return: None
        """
        self.company_name = company_name
        self.fb_url = fb_url
        self.tw_url = tw_url
        self.yt_url = yt_url

class CompanySocialMedia(object):
    def __init__(self,
                 company_name,
                 fb_likes=None,
                 fb_talking_about_count=None,
                 fb_chickins=None,
                 tw_followers_count=None,
                 tw_tweets=None,
                 yt_subscriber_count=None,
                 yt_view_count=None,
                 time_taken=datetime.now()):
        """
            Init method for CompanySocialMedia object

            @type company_name: string
            @param company_name: company name
            @type fb_likes: int
            @param fb_likes: facebook like count
            @type fb_talking_about_count: int
            @param fb_talking_about_count: facebook talking about count
            @type fb_chickins: int
            @param fb_chickins: facebook checkins
            @type tw_followers_count: int
            @param tw_followers_count: twitter followers count
            @type tw_tweets: int
            @param tw_tweets: twitter tweets
            @type yt_subscriber_count: int
            @param yt_subscriber_count: youtube subscriber count
            @type yt_view_count: int
            @param yt_view_count: youtube view count
            @type time_taken: datetime.datetime
            @param time_taken: time taken

            @rtype:  None
            @return: None
        """
        self.company_name = company_name
        self.fb_likes = fb_likes
        self.fb_talking_about_count = fb_talking_about_count
        self.fb_chickins = fb_chickins
        self.tw_followers_count = tw_followers_count
        self.tw_tweets = tw_tweets
        self.yt_subscriber_count = yt_subscriber_count
        self.yt_view_count = yt_view_count
        self.time_taken = time_taken

def read_csv(file):
    """
        Read csv into list

        @type file: file
        @param file: the read file

        @rtype: list
        @return: the CompanyURL object list
    """
    if not file:
        raise Exception('The file is none.')

    company_list = []
    reader = csv.reader(file)

    for row in reader:
        if row and len(row) == 4:
            company_name = row[0].strip()
            fb_url = row[1].strip()
            tw_url = row[2].strip()
            yt_url = row[3].strip()
            # If no urls, ignore this row
            if urlparse(fb_url).netloc == '' and urlparse(tw_url).netloc == '' and urlparse(yt_url).netloc == '':
                continue
            company = CompanyURL(company_name, fb_url, tw_url, yt_url)
            company_list.append(company)

    file.close()
    return company_list

def get_social_media(company_list):
    """
        Call scraper to get company social media data

        @type company_list: list
        @param company_list: the CompanyURL object list

        @rtype: list
        @return: the CompanySocialMedia object list
    """
    # Define a progress bar on console
    limit = len(company_list)
    prog = ProgressBar(0, limit, 70, mode='fixed')
    oldprog = str(prog)
    i = 0

    result = []
    current_datetime = datetime.now()
    for company in company_list:
        company_sm_data = CompanySocialMedia(company.company_name)
        fb_data = scraper.fb_scrape(company.fb_url)
        tw_data = scraper.tw_scrape(company.tw_url)
        yt_data = scraper.yt_scrape(company.yt_url)
        company_sm_data.fb_likes = fb_data['likes']
        company_sm_data.fb_talking_about_count = fb_data['talking_about_count']
        company_sm_data.fb_chickins = fb_data['checkins']
        company_sm_data.tw_followers_count = tw_data['followers_count']
        company_sm_data.tw_tweets = tw_data['tweets']
        company_sm_data.yt_subscriber_count = yt_data['subscriber_count']
        company_sm_data.yt_view_count = yt_data['view_count']
        # Keep same time_taken for this batch operation
        company_sm_data.time_taken = current_datetime
        result.append(company_sm_data)

        # Print a progress bar on console
        i += 1
        prog.update_amount(i)
        if oldprog != str(prog):
            print str(prog), '\r',
            sys.stdout.flush()
            oldprog=str(prog)

    return result

def write_db(company_list):
    """
        write CompanySocialMedia object list into sqlite3 database

        @type company_list: list
        @param company_list: the CompanySocialMedia object list

        @rtype: int
        @return: insert total count
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS COMPANY
             (
             COMPANY_NAME TEXT,
             FB_LIKES INTEGER,
             FB_TALKING_ABOUT_COUNT INTEGER,
             FB_CHICKINS INTEGER,
             TW_FOLLOWERS_COUNT INTEGER,
             TW_TWEETS INTEGER,
             YT_SUBSCRIBER_COUNT INTEGER,
             YT_VIEW_COUNT INTEGER,
             TIME_TAKEN TIMESTAMP
             )''')
    count = 0
    for company in company_list:
        # Insert a row of data
        try:
            c.execute("INSERT INTO COMPANY VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (company.company_name,
                 company.fb_likes,
                 company.fb_talking_about_count,
                 company.fb_chickins,
                 company.tw_followers_count,
                 company.tw_tweets,
                 company.yt_subscriber_count,
                 company.yt_view_count,
                 company.time_taken
                    ))
            count += 1
        except Exception as e:
            log.error(e)

    conn.commit()
    c.close()
    conn.close()
    return count

if __name__ == '__main__':
    log.info('begin')
    args = sys.argv
    if len(args) >= 2:
        file = open(args[1], 'r')
        count = write_db(get_social_media(read_csv(file)))
        print '%d records has been saved to database %s' % (count, 'data.db')
    else:
        print 'Please input the file name as the first parameter.'
    log.info('end')