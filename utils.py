__author__ = 'zhiwehu'

import sqlite3
import threading
from datetime import datetime
import csv
import cStringIO
import codecs
import math
from logUtil import log

def get_setting():
    conn = sqlite3.connect('data/setting.db')
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
    def __init__(self, scraper, csv_file_path, db_file_path):
        self.scraper = scraper
        self.csv_file_path = csv_file_path
        self.db_file_path = db_file_path
        threading.Thread.__init__(self)

    def run(self):
        f = open(self.csv_file_path, 'rb')
        self.scraper.write_db(self.scraper.get_social_media(self.scraper.read_csv(f, close=True),self.db_file_path),self.db_file_path)


def do_scrape_async(scraper, csv_file_path, db_file_path):
    ScrapeThread(scraper, csv_file_path, db_file_path).start()

def get_db_path(csv_name):
    if csv_name == None:
        return None

    conn = sqlite3.connect('data/setting.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS CSV_DB
                 (
                 CSV_FILE_NAME TEXT,
                 CSV_FILE_PATH TEXT,
                 DB_FILE_NAME TEXT,
                 DB_FILE_PATH TEXT,
                 LAST_MODIFIED_TIME TIMESTAMP
                 )''')

    csv = c.execute('SELECT DB_FILE_PATH FROM CSV_DB WHERE CSV_FILE_NAME = ?', (csv_name.strip(), )).fetchone()
    c.close()
    conn.close()

    #print csv

    if csv:
        return csv[0]
    else:
        return None

def save_csv_db(csvfile):
    csv_file_name = csvfile.filename.split('.')[0]
    db_file_name = csv_file_name + '.db'
    conn = sqlite3.connect('data/setting.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS CSV_DB
                 (
                 CSV_FILE_NAME TEXT,
                 CSV_FILE_PATH TEXT,
                 DB_FILE_NAME TEXT,
                 DB_FILE_PATH TEXT,
                 LAST_MODIFIED_TIME TIMESTAMP
                 )''')

    csv_file_db = c.execute('SELECT * FROM CSV_DB WHERE CSV_FILE_NAME = ?', (csv_file_name, )).fetchone()
    if csv_file_db:
        c.execute('UPDATE CSV_DB SET LAST_MODIFIED_TIME = ? WHERE CSV_FILE_NAME = ?', (datetime.now(), csv_file_name))
    else:
        c.execute('INSERT INTO CSV_DB VALUES(?, ?, ?, ?, ?)', (csv_file_name, 'data/%s' % csvfile.filename, csv_file_name, 'data/%s' % db_file_name, datetime.now()))
    conn.commit()
    c.close()
    conn.close()

    return 'data/%s' % csvfile.filename, 'data/%s' % db_file_name

def create_company_table(db_file_path):
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS COMPANY
                 (
                 COMPANY_NAME TEXT,
                 FB_LIKES INTEGER,
                 FB_TALKING_ABOUT_COUNT INTEGER,
                 FB_CHECKINS INTEGER,
                 FB_TL REAL,
                 FB_CHL REAL,
                 FB_COMBINED REAL,
                 FB_LIKES_SQRT REAL,
                 FB_TCHK_SQRT REAL,
                 FB_HEALTH REAL,
                 TW_FOLLOWERS_COUNT INTEGER,
                 TW_TWEETS INTEGER,
                 TW_IMPACT REAL,
                 TW_ENGAGEMENT REAL,
                 TW_INFLUENCE REAL,
                 TW_RETWEETED REAL,
                 TW_KLOUT_TRUEREACH REAL,
                 TW_HEALTH REAL,
                 YT_SUBSCRIBER_COUNT INTEGER,
                 YT_VIEW_COUNT INTEGER,
                 YT_HEALTH REAL,
                 TSSH_RAW REAL,
                 TSSH_PWR_REDUCED REAL,
                 FB_PERCENT REAL,
                 TW_PERCENT REAL,
                 YT_PERCENT REAL,
                 FB_ABS REAL,
                 TW_ABS REAL,
                 YT_ABS REAL,
                 TIME_TAKEN TIMESTAMP
                 )''')
    conn.commit()
    c.close()
    conn.close()

def get_csv_data(request):
    conn = sqlite3.connect('data/setting.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS CSV_DB
                 (
                 CSV_FILE_NAME TEXT,
                 CSV_FILE_PATH TEXT,
                 DB_FILE_NAME TEXT,
                 DB_FILE_PATH TEXT,
                 LAST_MODIFIED_TIME TIMESTAMP
                 )''')
    csv_files = c.execute('SELECT CSV_FILE_NAME FROM CSV_DB').fetchall()
    csv_file_list = []
    for csv in csv_files:
        csv_file_list.append(csv[0])
    c.close()
    conn.close()

    csv_file_name = request.params.get('csv_file_name', None)
    if csv_file_name == None and len(csv_file_list) > 0:
        csv_file_name = csv_file_list[0]

    return csv_file_list, csv_file_name

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def handleFBData(fb_data):
    """
        If the FB check-in value is less than 50, set it to (FB Likes * 0.0123)
    """
    if fb_data['checkins'] <= 50:
        fb_data['checkins'] = int(math.ceil(float(fb_data['likes']) * 0.0123))
    return fb_data

def getMaxCheckins(company_name, db_filename):
    max_checkins = 0
    if company_name and db_filename:
        conn = sqlite3.connect(db_filename)
        c = conn.cursor()
        result = c.execute('SELECT MAX(FB_CHECKINS) FROM COMPANY WHERE COMPANY_NAME =?',(company_name, )).fetchone()
        max_checkins = result[0] or 0
        c.close()
        conn.close()
    return max_checkins