__author__ = 'jeffrey'

import urllib2
import simplejson
from twitter import User
from logUtil import log

def UsersLookup(twitter_ids):
    url = 'https://api.twitter.com/1/users/lookup.json?screen_name=%s' % twitter_ids
    log.debug(url)
    f = urllib2.urlopen(url)
    json = f.read()
    f.close()
    data = _ParseAndCheckTwitter(json)
    return [User.NewFromJsonDict(u) for u in data]

def _CheckForTwitterError(data):
    """Raises a TwitterError if twitter returns an error message.

    Args:
      data:
        A python dict created from the Twitter json response

    Raises:
      TwitterError wrapping the twitter error message if one exists.
    """
    # Twitter errors are relatively unlikely, so it is faster
    # to check first, rather than try and catch the exception
    if 'error' in data:
        raise Exception(data['error'])

def _ParseAndCheckTwitter(json):
    """Try and parse the JSON returned from Twitter and return
    an empty dictionary if there is any error. This is a purely
    defensive check because during some Twitter network outages
    it will return an HTML failwhale page."""
    try:
        data = simplejson.loads(json)
        _CheckForTwitterError(data)
    except ValueError:
        if "<title>Twitter / Over capacity</title>" in json:
            raise Exception("Capacity Error")
        if "<title>Twitter / Error</title>" in json:
            raise Exception("Technical Error")
        raise Exception("json decoding")

    return data

def build_dict(twitter_user_list):
    result = {}

    for twitter_user in twitter_user_list:
        data = {'twitter_id': '', 'followers_count': 0, 'tweets': 0}
        data['twitter_id'] = twitter_user.screen_name
        data['followers_count'] = twitter_user.followers_count
        data['tweets'] = twitter_user.statuses_count

        result[twitter_user.screen_name.lower()] = data

    return result