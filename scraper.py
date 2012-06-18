__author__ = 'zhiwehu'

from urlparse import urlparse
import re

import twitter
twitter_api = twitter.Api()

import gdata.youtube.service
youtube_api = gdata.youtube.service.YouTubeService()

import facebook
try:
    access_token = facebook.get_app_access_token('193618104088301', '659217362b250bbdae0b61d1e437e8ca')
except:
    access_token = None
facebook_api = facebook.GraphAPI(access_token)

def check_url(url, netloc):
    return url and urlparse(url).netloc == netloc

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
    data = {'likes': 0, 'talking_about_count': 0, 'checkins': 0}
    facebook_data = None
    if check_url(url, 'www.facebook.com'):
        facebook_id = get_facebook_id(url)
        try:
            facebook_data = facebook_api.request(facebook_id)
        except Exception as e:
            pass
    if facebook_data:
        data['likes'] = facebook_data.get('likes')
        data['talking_about_count'] = facebook_data.get('talking_about_count')
        if facebook_data.get('user_checkins'):
            data['checkins'] = facebook_data.get('user_checkins')
        else:
            data['checkins'] = 0
    return data

def tw_scrape(url):
    data = {'followers_count': 0, 'statuses_count': 0}
    twitter_data = None
    if check_url(url, 'twitter.com'):
        twitter_id = get_twitter_id(url)
        try:
            twitter_data = twitter_api.GetUser(twitter_id)
        except Exception as e:
            pass
    if twitter_data:
        data['followers_count'] = twitter_data.followers_count
        data['statuses_count'] = twitter_data.statuses_count
    return data

def yt_scrape(url):
    data = {'view_count': 0, 'subscriber_count': 0}
    youtube_data = None
    if check_url(url, 'www.youtube.com'):
        youtube_id = get_youtube_id(url)
        try:
            youtube_data = youtube_api.GetYouTubeUserEntry(username=youtube_id)
        except Exception as e:
            pass
    if youtube_data:
        data['view_count'] = youtube_data.statistics.view_count
        data['subscriber_count'] = youtube_data.statistics.subscriber_count
    return data