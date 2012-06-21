__author__ = 'jeffrey'

import sqlite3
from bottle import route, run, debug, static_file
from bottle import jinja2_view as view
import os.path

from main import Scraper

WEB_ROOT = os.path.abspath(os.path.dirname(__file__))

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=os.path.join(WEB_ROOT, 'static'))

@route('/')
@view('index.html')
def index():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    items = c.execute('SELECT * FROM COMPANY').fetchall()
    return dict(items = items)

@route('/scrape')
def scrape():
    file = open('good_format.csv')
    s = Scraper()
    s.write_db(s.get_social_media(s.read_csv(file)))
    return index()

debug(True)
run(host='localhost', port=8000, reloader=True)