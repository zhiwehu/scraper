__author__ = 'zhiwehu'

from urlparse import urlparse
import re

import twitter
twitter_api = twitter.Api()

import gdata.youtube.service
youtube_api = gdata.youtube.service.YouTubeService()

import facebook
facebook_api = facebook.GraphAPI()

def check_url(url, netloc):
    return urlparse(url).netloc == netloc

def get_facebook_id(url):
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
    twitter_url = urlparse(url)
    if twitter_url.fragment:
        result = twitter_url.fragment.replace('!', '').replace('/', '')
    elif twitter_url.path:
        result = twitter_url.path.replace('/', '')
    else:
        result = ''
    return result

def get_youtube_id(url):
    youtube_url = urlparse(url)
    if youtube_url.path:
        result = youtube_url.path.replace('/user/', '').replace('/', '')
    else:
        result = ''
    return result

def fb_scrape(url):
    if check_url(url, 'www.facebook.com'):
        facebook_id = get_facebook_id(url)
        try:
            facebook_data = facebook_api.request(facebook_id)
            return facebook_data.get('likes'), facebook_data.get('talking_about_count'), 0
        except Exception as e:
            return 0, 0, 0
    else:
        return 0, 0, 0

def tw_scrape(url):
    if check_url(url, 'twitter.com'):
        twitter_id = get_twitter_id(url)
        try:
            twitter_data = twitter_api.GetUser(twitter_id)
            return twitter_data.statuses_count, twitter_data.followers_count
        except :
            return 0, 0
    else:
        return 0, 0

def yt_scrape(url):
    if check_url(url, 'www.youtube.com'):
        youtube_id = get_youtube_id(url)
        try:
            youtube_data = youtube_api.GetYouTubeUserEntry(username=youtube_id)
            return youtube_data.statistics.view_count, youtube_data.statistics.subscriber_count
        except :
            return 0, 0
    else:
        return 0, 0

if __name__ == '__main__':
    print tw_scrape('https://twitter.com/GM/')
    print tw_scrape('https://twitter.com/Citibank/')
    print yt_scrape('http://www.youtube.com/user/walmart')
    print yt_scrape('http://www.youtube.com/user/McKessonCorporation')
    print fb_scrape('http://www.facebook.com/pages/Houston-TX/ConocoPhillips/173793155340?ref=ts')
    print fb_scrape('http://www.facebook.com/walmart')
    print fb_scrape('http://www.facebook.com/pages/Berkshire-Hathaway/112244468787782')