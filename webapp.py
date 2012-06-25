__author__ = 'jeffrey'

import sqlite3
from bottle import route, run, debug, static_file, jinja2_view as view, request, redirect
import os.path

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
        s.write_db(s.get_social_media(s.read_csv(csvfile.file)))
    except Exception as e:
        return upload(error_message='Error: %s' % e.message)
    return redirect('/')

@route('/get_progress')
def progress():
    return{'total': 100, 'current':50}

debug(True)
run(host='0.0.0.0', port=8880, reloader=True)
