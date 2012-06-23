__author__ = 'zhiwehu'

from urlparse import urlparse
import re
import logging

log = logging.getLogger('scraper')
log.setLevel(logging.DEBUG)
if not len(log.handlers):
    handler = logging.FileHandler(filename='log.txt')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    log.addHandler(handler)

import twitter
twitter_api = twitter.Api()

import gdata.youtube.service
youtube_api = gdata.youtube.service.YouTubeService()

import facebook
try:
    #access_token = facebook.get_app_access_token('193618104088301', '659217362b250bbdae0b61d1e437e8ca')
    access_token = None
except Exception as e:
    log.error(e)
    access_token = None
facebook_api = facebook.GraphAPI(access_token)

def check_url(url, netloc):
    return url and urlparse(url).netloc == netloc

def get_facebook_id(url):
    """
        Get facebook id or name from the url

        @type url: string
        @param url: facebook url

        @rtype:  string
        @return: facebook id or name
    """
    facebook_url = urlparse(url)
    path = facebook_url.path
    if path.startswith('/pages/'):
        pattern = re.compile(r'/pages/(?P<fb_name>[A-Za-z-/]+)/(?P<fb_id>\d+)')
        facebook_id = re.match(pattern, path)
        if facebook_id:
            return facebook_id.group('fb_id')
        else:
            return ''
    else:
        return path.replace('/', '')

def get_twitter_id(url):
    """
        Get twitter id from the url

        @type url: string
        @param url: twitter url

        @rtype:  string
        @return: twitter id
    """
    twitter_url = urlparse(url)
    if twitter_url.fragment:
        result = twitter_url.fragment.replace('!', '').replace('/', '')
    elif twitter_url.path:
        result = twitter_url.path.replace('/', '')
    else:
        result = ''
    return result

def get_youtube_id(url):
    """
        Get youtube id from the url

        @type url: string
        @param url: youtube url

        @rtype:  string
        @return: youtube id
    """
    youtube_url = urlparse(url)
    return youtube_url.path.replace('/user/', '').replace('/', '')

def fb_scrape(url):
    """
        Scripe facebook url, get likes, talking_about_count and checkins

        @type url: string
        @param url: facebook url

        @rtype:  dict
        @return: likes, talking_about_count and checkins dict data
    """
    data = {'likes': 0, 'talking_about_count': 0, 'checkins': 0}
    facebook_data = None
    if check_url(url, 'www.facebook.com'):
        facebook_id = get_facebook_id(url)
        try:
            facebook_data = facebook_api.request(facebook_id)
        except Exception as e:
            log.error(e)
            pass
    if facebook_data:
        data['likes'] = facebook_data.get('likes')
        data['talking_about_count'] = facebook_data.get('talking_about_count')
        if facebook_data.get('were_here_count'):
            data['checkins'] = facebook_data.get('were_here_count')
        else:
            data['checkins'] = 0
    return data

def tw_scrape(url):
    """
        Scripe twitter url, get followers_count, tweets

        @type url: string
        @param url: twitter url

        @rtype:  dict
        @return: followers_count, tweets dict data
    """
    data = {'followers_count': 0, 'tweets': 0}
    twitter_data = None
    if check_url(url, 'twitter.com'):
        twitter_id = get_twitter_id(url)
        try:
            twitter_data = twitter_api.GetUser(twitter_id)
        except Exception as e:
            log.error(e)
            pass
    if twitter_data:
        data['followers_count'] = twitter_data.followers_count
        data['tweets'] = twitter_data.statuses_count
    return data

def yt_scrape(url):
    """
        Scripe youtube url, get view_count, subscriber_count

        @type url: string
        @param url: youtube url

        @rtype:  dict
        @return: view_count, subscriber_count dict data
    """
    data = {'view_count': 0, 'subscriber_count': 0}
    youtube_data = None
    if check_url(url, 'www.youtube.com'):
        youtube_id = get_youtube_id(url)
        try:
            youtube_data = youtube_api.GetYouTubeUserEntry(username=youtube_id)
        except Exception as e:
            log.error(e)
            pass
    if youtube_data:
        data['view_count'] = int(youtube_data.statistics.view_count)
        data['subscriber_count'] = int(youtube_data.statistics.subscriber_count)
    return data