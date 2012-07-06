import cookielib
import os
import urllib
import urllib2

from logUtil import log

fb_username = "alex@alexanderpaley.com"
fb_password = "trackingsocial"

cookie_filename = "facebook.cookies"

class FacebookLogin(object):

    def __init__(self, login, password):
        """ Start up... """
        self.login = login
        self.password = password

        self.cj = cookielib.MozillaCookieJar(cookie_filename)
        if os.access(cookie_filename, os.F_OK):
            self.cj.load()
        self.opener = urllib2.build_opener(
            urllib2.HTTPRedirectHandler(),
            urllib2.HTTPHandler(debuglevel=0),
            urllib2.HTTPSHandler(debuglevel=0),
            urllib2.HTTPCookieProcessor(self.cj)
        )
        self.opener.addheaders = [
            ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
                            'Windows NT 5.2; .NET CLR 1.1.4322)'))
        ]

        # need this twice - once to set cookies, once to log in...
        self.loginToFacebook()
        self.loginToFacebook()

        self.cj.save()

    def loginToFacebook(self):
        """
        Handle login. This should populate our cookie jar.
        """
        login_data = urllib.urlencode({
            'email' : self.login,
            'pass' : self.password,
            })
        response = self.opener.open("https://login.facebook.com/login.php", login_data)
        return ''.join(response.readlines())

def fblogin():
    try:
        fblogin = FacebookLogin(fb_username, fb_password)
        urllib2.install_opener(fblogin.opener)
    except Exception as e:
        log.error(e)
    pass