__author__ = 'jeffrey'

import urllib2
from logUtil import log

api_key = 'E3C6EC74-F374-4B31-A298-07FEF594E3E3'

def get_tw_data(twitter_id):
    data = {'impact': 0, 'engagement': 0, 'influence': 0, 'retweeted': 0, 'klout_truereach': 0}
    url = 'http://www.twitalyzer.com/api/2/user.asp?k=%s&u=%s&f=JSON' % (api_key, twitter_id)
    try:
        tw_api_data = urllib2.urlopen(url).read()
        if 'error' in tw_api_data:
            log.error('TWITTER NAME: %s:%s' %(twitter_id, tw_api_data))
        tw_api_data = tw_api_data.replace('[{', '').replace('}]', '')
        tw_api_data_list = tw_api_data.split(',')
        for item in tw_api_data_list:
            key = item.split(':')[0].strip()
            value = item.split(':')[1]
            if data.has_key(key):
                data[key] = value
    except Exception as e:
        log.error('Get twitter data error for %s' % twitter_id)
        log.error(e)
        pass
    return data