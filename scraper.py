__author__ = 'jeffrey'

from urlparse import urlparse
import re
from contextlib import closing
import urllib2
from logUtil import log

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
        result = twitter_url.fragment.replace('!', '').replace('/', '').replace('@', '')
    elif twitter_url.path:
        result = twitter_url.path.replace('/', '').replace('@', '')
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
        if facebook_data.get('likes'):
            data['likes'] = facebook_data.get('likes')
        else:
            data['likes'] = 0
        if facebook_data.get('talking_about_count'):
            data['talking_about_count'] = facebook_data.get('talking_about_count')
        else:
            data['talking_about_count'] = 0
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
    data = {'twitter_id': '', 'followers_count': 0, 'tweets': 0}
    twitter_data = None
    if check_url(url, 'twitter.com'):
        twitter_id = get_twitter_id(url)
        data['twitter_id'] = twitter_id
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
            log.error('Youtube %s scrape error' % url)
            log.error(e)
            pass
    if youtube_data:
        data['view_count'] = int(youtube_data.statistics.view_count)
        data['subscriber_count'] = int(youtube_data.statistics.subscriber_count)
    return data

def scrap_facebook_raw_data(url):
    data = {'likes': 0, 'talking_about_count': 0, 'checkins': 0}
    if check_url(url, 'www.facebook.com'):
        number_pat = "[0-9]+"
        stat_pat ='<div class="fsm fwn fcg"><div class="fsm fwn fcg">([0-9]+)(.*)([0-9]+)(.*)([0-9]+)(.*)\w+</div></div>'
        try:
            with closing(urllib2.urlopen(url=url, timeout=30)) as page:
                content = page.read()
                content= re.sub(',', '', content)
                result = re.search(stat_pat, content)
                if result:
                    #print result.group()
                    result = re.findall(number_pat, result.group())
                    if len(result)>=3:
                        data['likes']=int(result[0])
                        data['talking_about_count']=int(result[1])
                        data['checkins']=int(result[2])
                        return data
                    elif len(result)>=2:
                        data['likes']=int(result[0])
                        data['talking_about_count']=int(result[1])
        except Exception as e:
            log.error('Facebook url %s scrape error!' % url)
            log.error(e)
            pass
    return data