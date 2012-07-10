__author__ = 'jeffrey'

import sqlite3
import os
from bottle import route, run, debug, static_file, jinja2_view as view, request, response, error, HTTPError
from pyloginfb import fblogin
from datetime import datetime

import uuid

from main import Scraper
from utils import *

WEB_ROOT = os.path.abspath(os.path.dirname(__file__))

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=os.path.join(WEB_ROOT, 'static'))

@route('/')
@view('index')
def index(error_message=None, success_message=None):
    csv_file_list, csv_file_name = get_csv_data(request)

    db_file_path = get_db_path(csv_file_name)
    items = None
    company_list = None
    company_name = None
    if db_file_path:
        company_name = request.params.get('company_name', None)
        conn = sqlite3.connect(db_file_path)
        create_company_table(db_file_path)
        c = conn.cursor()

        companies = c.execute('SELECT DISTINCT COMPANY_NAME FROM COMPANY').fetchall()
        company_list = []
        for company in companies:
            company_list.append(company[0])

        if (company_name == None or company_name == '') and len(company_list)>0:
            company_name = company_list[0]

        if company_name:
            items = c.execute('SELECT * FROM COMPANY WHERE COMPANY_NAME = ? ORDER BY TIME_TAKEN ASC',
                (company_name, )).fetchall()
        '''
        if company_name and company_name != 'ALL':
            items = c.execute('SELECT * FROM COMPANY WHERE COMPANY_NAME = ? ORDER BY TIME_TAKEN ASC',
                (company_name, )).fetchall()
        else:
            items = c.execute('SELECT * FROM COMPANY ORDER BY TIME_TAKEN ASC').fetchall()
        '''
        c.close()
        conn.close()
    return dict(items=items, error_message=error_message, success_message=success_message, companies=company_list,
        company_name=company_name, csv_file_list=csv_file_list, csv_file_name=csv_file_name)


@route('/csv/upload', method='GET')
@view('upload')
def csv_upload(success_message=None, error_message=None):
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

    csv_db_list = c.execute("SELECT CSV_FILE_NAME, CSV_FILE_PATH, DB_FILE_NAME, DB_FILE_PATH, strftime('%Y-%m-%d %H:%M:%S', LAST_MODIFIED_TIME)  FROM CSV_DB").fetchall()
    c.close()
    conn.close()
    return dict(error_message=error_message, success_message= success_message, csv_db_list = csv_db_list)

@route('/csv/download/<csv_file_name>')
def csv_download(csv_file_name):
    try:
        f = open('data/%s.csv' % csv_file_name, 'rb')
        response.content_type= 'text/csv'
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % csv_file_name
        return f
    except Exception as e:
        log.error(e)
        return HTTPError(code=404)

@route('/csv/delete/<csv_file_name>')
def csv_delete(csv_file_name):
    try:
        os.remove(os.path.join(WEB_ROOT, 'data/%s.csv' % csv_file_name))
    except Exception as e:
        log.error(e)
        pass

    try:
        conn = sqlite3.connect('data/setting.db')
        c = conn.cursor()
        c.execute("DELETE FROM CSV_DB WHERE CSV_FILE_NAME = ?", (csv_file_name, ))
        conn.commit()
        c.close()
        conn.close()
    except Exception as e:
        log.error(e)
        #return HTTPError(code=404)
        pass

    return csv_upload(success_message='CSV file %s has been deleted success.' % csv_file_name)

@route('/csv/upload', method='POST')
@view('upload')
def do_upload():
    csvfile = request.files.get('csvfile', None)
    fblogin()
    s = Scraper()
    try:
        if csvfile.file == None:
            raise Exception('The file is None')
        company_list = s.read_csv(csvfile.file)
        if len(company_list) > 0:
            # Save the file
            f = open('%s/data/%s' % (WEB_ROOT, csvfile.filename), 'wb')
            f.write(csvfile.value)
            f.seek(0)

            # Save to CSV_FILE db
            csv_file_path, db_file_path = save_csv_db(csvfile)
            # Run the scrape process in background
            # TODO just upload, not scrape
            do_scrape_async(s, csv_file_path, db_file_path)
        else:
            raise Exception('The file is not format as company list')
    except Exception as e:
        log.error(e)
        return csv_upload(error_message='Error: %s' % e.message)
        #return redirect('/')
    return csv_upload(
        success_message='The file updated success and will do scrape in background. Please refrush page later to view the new data.')


@route('/settings', method='GET')
@view('settings')
def settings(error_message=None, success_message=None):
    setting = get_setting()
    return dict(setting=setting, error_message=error_message, success_message=success_message)

@route('/settings', method='POST')
@view('settings')
def do_settings():
    schedule_interval = request.forms.schedule_interval
    try:
        schedule_interval = int(schedule_interval)
        if schedule_interval < 300:
            raise Exception('The min schedule interval should be more than 300 seconds')
        conn = sqlite3.connect('data/setting.db')
        c = conn.cursor()
        c.execute('UPDATE SETTINGS SET SCHEDULE_INTERVAL = ?, LAST_MODIFIED_TIME = ?',
            (schedule_interval, datetime.now()))
        conn.commit()
        c.close()
        conn.close()
        # Re schedule with new interval seconds
        cron.reSchedule(seconds=schedule_interval)
    except Exception as e:
        return settings(error_message=e.message)
    return settings(success_message='Settings has been updated!')

@route('/company_chart')
@view('company_chart')
def company_chart(error_message=None, success_message=None):
    company_name = request.GET.get('company_name', None)

    csv_file_list, csv_file_name = get_csv_data(request)
    db_file_path = get_db_path(csv_file_name)

    items = None
    company_list = None
    if db_file_path:
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        companies = c.execute('SELECT DISTINCT COMPANY_NAME FROM COMPANY').fetchall()
        company_list = []
        for company in companies:
            company_list.append(company[0])

        if (company_name == None or company_name == '') and len(company_list)>0:
            company_name = company_list[0]

        if company_name:
            items = c.execute(
                "SELECT TSSH_PWR_REDUCED, strftime('%Y-%m-%d %H:%M', TIME_TAKEN) FROM COMPANY WHERE COMPANY_NAME = ? ORDER BY TIME_TAKEN ASC"
                , (company_name,)).fetchall()
        c.close()
        conn.close()
    return dict(items=items, error_message=error_message, success_message=success_message, companies=company_list,
        company_name=company_name, csv_file_list=csv_file_list, csv_file_name=csv_file_name)

@route('/macro_level_chart', method='GET')
@view('macro_level_chart')
def macro_level_chart(error_message=None, success_message=None):
    return do_macro_level_chart(error_message, success_message)

@route('/macro_level_chart', method='POST')
@view('macro_level_chart')
def do_macro_level_chart(error_message=None, success_message=None):
    selected_company_list =  request.forms.getlist('company')
    csv_file_list, csv_file_name = get_csv_data(request)

    db_file_path = get_db_path(csv_file_name)
    items = None
    company_list = None
    company_name = None
    if db_file_path:
        company_name = request.GET.get('company_name', None)
        conn = sqlite3.connect(db_file_path)
        create_company_table(db_file_path)
        c = conn.cursor()

        companies = c.execute('SELECT DISTINCT COMPANY_NAME FROM COMPANY').fetchall()
        company_list = []
        for company in companies:
            company_list.append(company[0])

        if not selected_company_list:
            selected_company_list = company_list

        sql="SELECT AVG(TSSH_PWR_REDUCED), strftime('%Y-%m-%d %H:%M', TIME_TAKEN) FROM COMPANY WHERE COMPANY_NAME IN ({company_list}) GROUP BY strftime('%Y-%m-%d %H:%M', TIME_TAKEN)".format(
            company_list=','.join(['?']*len(selected_company_list)))
        avg_company_data = c.execute(sql, selected_company_list).fetchall()

        c.close()
        conn.close()
    return dict(error_message=error_message, success_message=success_message, companies=company_list,
        company_name=company_name, csv_file_list=csv_file_list, csv_file_name=csv_file_name, avg_company_data= avg_company_data, selected_company_list= selected_company_list)

@route('/export')
@view('export')
def export():
    csv_file_name = request.params.get('csv_file_name', None)
    if csv_file_name:
        db_file_path = get_db_path(csv_file_name)
        if db_file_path == None:
            return HTTPError(code=404)

        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()

        companies = c.execute('SELECT * FROM COMPANY').fetchall()
        c.close()
        conn.close()

        unique_filename = uuid.uuid4()
        write = UnicodeWriter(f=open('data/%s.csv' % unique_filename, 'wb'))
        write.writerow(['COMPANY_NAME',
                        'FB_LIKES',
                        'FB_TALKING_ABOUT_COUNT',
                        'FB_CHECKINS',
                        'FB_TL',
                        'FB_CHL',
                        'FB_COMBINED',
                        'FB_LIKES_SQRT',
                        'FB_TCHK_SQRT',
                        'FB_HEALTH REAL',
                        'TW_FOLLOWERS_COUNT',
                        'TW_TWEETS',
                        'TW_IMPACT',
                        'TW_ENGAGEMENT',
                        'TW_INFLUENCE',
                        'TW_RETWEETED',
                        'TW_KLOUT_TRUEREACH',
                        'TW_HEALTH',
                        'YT_SUBSCRIBER_COUNT',
                        'YT_VIEW_COUNT',
                        'YT_HEALTH',
                        'TSSH_RAW',
                        'TSSH_PWR_REDUCED',
                        'FB_PERCENT',
                        'TW_PERCENT',
                        'YT_PERCENT',
                        'FB_ABS',
                        'TW_ABS',
                        'YT_ABS',
                        'TIME_TAKEN'])
        write.writerows(companies)

        response.content_type= 'text/csv'
        response['Content-Disposition'] = 'attachment; filename=%s_db.csv' % csv_file_name
        f = open('data/%s.csv' % unique_filename, 'rb')
        os.remove('data/%s.csv' % unique_filename)
        return f
    else:
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

        csv_db_list = c.execute("SELECT CSV_FILE_NAME, DB_FILE_NAME, DB_FILE_PATH, strftime('%Y-%m-%d %H:%M:%S', LAST_MODIFIED_TIME)  FROM CSV_DB").fetchall()
        c.close()
        conn.close()
        return dict(csv_db_list = csv_db_list)

@error(404)
def error404(error):
    return '404 Not found.'

@route('/rescrape')
def re_scrape_schedule():
    conn = sqlite3.connect('data/setting.db')
    c = conn.cursor()
    schedule_interval = c.execute('SELECT SCHEDULE_INTERVAL FROM SETTINGS').fetchone()[0]
    c.close()
    conn.close()

    conn = sqlite3.connect('data/setting.db')
    c = conn.cursor()
    csv_db_file_list = c.execute('SELECT CSV_FILE_PATH, DB_FILE_PATH FROM CSV_DB').fetchall()
    c.close()
    conn.close()

    fblogin()

    for item in csv_db_file_list:
        csv_path = item[0]
        db_path  = item[1]
        s = Scraper()
        thread = ScrapeThread(s,csv_path, db_path)
        thread.start()
    # Re schedule with new interval seconds
    cron.reSchedule(seconds=schedule_interval)
    return settings(success_message='The cron job has been started in background and rescheduled.')

@route('/sort_summary_chart')
@view('sort_summary_chart')
def sort_summary_chart(error_message=None, success_message=None):
    csv_file_list, csv_file_name = get_csv_data(request)
    db_file_path = get_db_path(csv_file_name)

    if db_file_path:
        conn = sqlite3.connect(db_file_path)
        create_company_table(db_file_path)
        c = conn.cursor()

        items = c.execute('''
        SELECT COMPANY_NAME, FB_ABS*10, TW_ABS*10, YT_ABS*10, TSSH_PWR_REDUCED*10, strftime('%Y-%m-%d %H:%M', TIME_TAKEN)
        FROM COMPANY
        WHERE TIME_TAKEN IN (
        SELECT MAX(TIME_TAKEN) FROM COMPANY
        )
        ORDER BY TSSH_PWR_REDUCED DESC
        ''').fetchall()

        c.close()
        conn.close()
    return dict(
        items=items,
        error_message=error_message,
        success_message=success_message,
        csv_file_list=csv_file_list,
        csv_file_name=csv_file_name)

# Call cron.reSchedule to schedule the job with default interval(86400, 1 day) when start the webapp
import cron

schedule_interval = get_setting()[0]
cron.reSchedule(seconds=schedule_interval)

debug(True)
run(host='0.0.0.0', port=8880, reloader=True)
