__author__ = 'jeffrey'

import sqlite3
from bottle import route, run, debug, static_file, jinja2_view as view, request, redirect
import os.path
from datetime import datetime
import threading
from logUtil import log

from main import Scraper

WEB_ROOT = os.path.abspath(os.path.dirname(__file__))

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=os.path.join(WEB_ROOT, 'static'))

@route('/')
@view('index')
def index():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    items = c.execute('SELECT * FROM COMPANY ORDER BY TIME_TAKEN DESC').fetchall()
    c.close()
    conn.close()
    return dict(items = items)

@route('/upload', method='GET')
@view('upload')
def upload(error_message=None):
    return dict(error_message = error_message)

@route('/upload', method='POST')
@view('upload')
def do_upload():
    csvfile = request.files.csvfile
    s = Scraper()
    try:
        if csvfile.file == None:
            raise Exception('The file is None')
        #s.read_csv(csvfile.file)
        #s.write_db(s.get_social_media(s.read_csv(csvfile.file)))
        do_scrape_async(s, csvfile.file)
    except Exception as e:
        return upload(error_message='Error: %s' % e.message)
    return redirect('/')

@route('/settings', method='GET')
@view('settings')
def settings(error_message = None, success_message = None):
    setting = get_setting()
    return dict(setting = setting, error_message = error_message, success_message = success_message)

def get_setting():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS SETTINGS
                 (
                 SCHEDULE_INTERVAL INTEGER,
                 LAST_MODIFIED_TIME TIMESTAMP)''')

    settings = c.execute('SELECT * FROM SETTINGS').fetchall()
    if len(settings) == 0:
        c.execute('INSERT INTO SETTINGS VALUES(?, ?)', (86400, datetime.now()))
        conn.commit()

    setting = c.execute('SELECT * FROM SETTINGS').fetchone()
    c.close()
    conn.close()
    return setting

class ScrapeThread(threading.Thread):
    def __init__(self, scraper, file):
        self.scraper = scraper
        self.file = file
        threading.Thread.__init__(self)

    def run(self):
        log.debug('run the scrape process async background')
        self.scraper.write_db(self.scraper.get_social_media(self.scraper.read_csv(self.file)))

def do_scrape_async(scraper, file):
    ScrapeThread(scraper, file).start()

@route('/settings', method='POST')
@view('settings')
def do_settings():
    schedule_interval = request.forms.schedule_interval
    try:
        schedule_interval = int(schedule_interval)
        if schedule_interval < 300:
            raise Exception('The min schedule interval should be more than 300 seconds')
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute('UPDATE SETTINGS SET SCHEDULE_INTERVAL = ?, LAST_MODIFIED_TIME = ?', (schedule_interval, datetime.now()))
        conn.commit()
        c.close()
        conn.close()
        cron.reSchedule(seconds=schedule_interval)
    except Exception as e:
        error_message = e.message
        return settings(error_message = error_message)
    return settings(success_message = 'Settings has been updated!')

import cron
schedule_interval = get_setting()[0]
cron.reSchedule(seconds=schedule_interval)

debug(True)
run(host='0.0.0.0', port=8880, reloader=True)
