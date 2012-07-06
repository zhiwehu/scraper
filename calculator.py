__author__ = 'jeffrey'

from logUtil import log
from twitalyzer import get_tw_data

def cal_fb_hm(fb_likes, fb_talking_about_count, fb_checkins):
    fb_metrics = {'fb_likes': fb_likes,
                  'fb_talking_about_count': fb_talking_about_count,
                  'fb_checkins': fb_checkins,
                  'fb_tl': 0,
                  'fb_chl': 0,
                  'fb_combined': 0,
                  'fb_likes_sqrt': 0,
                  'fb_tchk_sqrt': 0,
                  'fb_health': 0
    }
    if fb_likes == 0 and fb_talking_about_count == 0 and fb_checkins == 0:
        return fb_metrics
    try:
        fb_tl = float(fb_talking_about_count) / float(fb_likes) * 1500
        fb_chl = float(fb_checkins) / float(fb_likes) * 100
        fb_combined = fb_tl + fb_chl
        fb_likes_sqrt = float(fb_likes) ** 0.9
        fb_tchk_sqrt = (float(fb_talking_about_count) + float(fb_checkins)) ** 0.2
        fb_health = (((fb_combined ** 0.5) * fb_likes_sqrt * fb_tchk_sqrt) / 30000000) ** 0.65
        fb_metrics['fb_tl'] = fb_tl
        fb_metrics['fb_chl'] = fb_chl
        fb_metrics['fb_combined'] = fb_combined
        fb_metrics['fb_likes_sqrt'] = fb_likes_sqrt
        fb_metrics['fb_tchk_sqrt'] = fb_tchk_sqrt
        fb_metrics['fb_health'] = fb_health
    except Exception as e:
        log.error(e)
        pass
    return fb_metrics

def cal_tw_hm(twitter_id, tw_followers_count, tw_tweets):
    tw_metrics = get_tw_data(twitter_id)
    #log.debug(tw_metrics)
    tw_health = (((float(tw_followers_count) ** 0.9) * ((float(tw_tweets) / 2) ** 0.2) * (
        float(tw_metrics['impact']) ** 0.3) * (float(tw_metrics['engagement']) ** 0.2) * (
    float(tw_metrics['influence']) ** 0.3) * (
        float(tw_metrics['retweeted']) ** 0.4) * (float(tw_metrics['klout_truereach']) ** 0.3)) ** 0.4) / 1000
    tw_metrics['tw_followers_count'] = tw_followers_count
    tw_metrics['tw_tweets'] = tw_tweets
    tw_metrics['tw_health'] = tw_health

    #If (Klout True Reach / TW Followers) is less than 0.1,
    # set it to (TW followers * 0.10); this makes Klout True Reach equivalent to 10% of the follower base
    if float(tw_metrics['tw_followers_count']) > 0 and (float(tw_metrics['klout_truereach'])/float(tw_metrics['tw_followers_count'])) < 0.1:
        tw_metrics['klout_truereach'] = float(tw_metrics['tw_followers_count']) * 0.1

    # If the Retweeted value is less than 10, set it to 10
    if float(tw_metrics['retweeted']) < 50:
        tw_metrics['retweeted'] = 50

    # If the Impact score is less than 0.1 set it to 0.1;
    if float(tw_metrics['impact']) < 0.1:
        tw_metrics['impact'] = 0.1

    # Also, individually do the same for Engagement and Influence; so that essentially whatever value is zero, will become 0.1
    if float(tw_metrics['engagement']) == 0:
        tw_metrics['engagement'] = 0.1
    if float(tw_metrics['influence']) == 0:
        tw_metrics['influence'] = 0.1

    return tw_metrics

def cal_yt_hm(yt_subscriber_count, yt_view_count):
    yt_metrics = {'yt_subscriber_count': yt_subscriber_count,
                  'yt_view_count': yt_view_count,
                  'yt_health': (float(yt_subscriber_count) * 0.3 + float(yt_view_count) ** 0.6) / 2900}
    return yt_metrics

def cal_macro_metrics(fb_health, tw_health, yt_health):
    macro_metrics = {'tssh_raw': 0, 'tssh_pwr_reduced': 0, 'fb_percent': 0, 'tw_percent': 0, 'yt_percent': 0,
                     'fb_abs': 0, 'tw_abs': 0, 'yt_abs': 0}
    if fb_health == 0 and tw_health == 0 and yt_health == 0:
        return macro_metrics
    fb_weight = 0.65
    tw_weight = 0.2
    yt_weight = 0.15
    tssh_raw = (float(fb_health) * fb_weight) + (float(tw_health) * tw_weight) + (float(yt_health) * yt_weight)
    tssh_pwr_reduced = (tssh_raw ** 0.6) * 3
    fb_percent = (float(fb_health) * fb_weight) / tssh_raw
    tw_percent = (float(tw_health) * tw_weight) / tssh_raw
    yt_percent = (float(yt_health) * yt_weight) / tssh_raw
    fb_abs = tssh_pwr_reduced * fb_percent
    tw_abs = tssh_pwr_reduced * tw_percent
    yt_abs = tssh_pwr_reduced * yt_percent
    macro_metrics['tssh_raw'] = tssh_raw
    macro_metrics['tssh_pwr_reduced'] = tssh_pwr_reduced
    macro_metrics['fb_percent'] = fb_percent
    macro_metrics['tw_percent'] = tw_percent
    macro_metrics['yt_percent'] = yt_percent
    macro_metrics['fb_abs'] = fb_abs
    macro_metrics['tw_abs'] = tw_abs
    macro_metrics['yt_abs'] = yt_abs
    return macro_metrics