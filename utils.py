__author__ = 'zhiwehu'

import sqlite3
import threading
from datetime import datetime
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
        f = open(self.csv_file_path, 'r')
        self.scraper.write_db(self.scraper.get_social_media(self.scraper.read_csv(f, close=True)),self.db_file_path)


def do_scrape_async(scraper, csv_file_path, db_file_path):
    ScrapeThread(scraper, csv_file_path, db_file_path).start()

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