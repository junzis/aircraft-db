import os, time, json, ast
import flask
import pymysql
import datetime

from flask import Flask, redirect, url_for, render_template, request, flash, session, send_from_directory

def readtime(timestamp):
    """Convert unix timestamp to human readable time"""
    return datetime.datetime.fromtimestamp(
            timestamp
        ).strftime('%Y-%m-%d %H:%M:%S')


app = Flask(__name__)
app.debug = False
app.secret_key = '$1$mxQd/Zad2f3L$QvjertyBgyJ5dctN0/lTNVfadfa3'
app.jinja_env.globals.update(readtime=readtime)


dbconn = pymysql.connect(host='localhost',
                         user='aircraft',
                         password='aircraft',
                         db='aircraft',
                         charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)

fetch_sql = "SELECT * FROM `ids` WHERE `icao`=%s OR `regid`=%s \
            OR `mdl`=%s OR `fr24`=%s"


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html', e=e), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        q = request.form['q']
        return redirect( url_for('index', q=q))
    else:
        q = request.args.get('q', '')
        if not q:
            return render_template('index.html')

        try:
            cursor = dbconn.cursor()
            cursor.execute(fetch_sql, [q]*4)
            results =  cursor.fetchall()
        except:
            results = None
        return render_template('results.html', results=results)


@app.route('/download')
def download():
    folder = os.path.join(app.root_path, 'files')
    return send_from_directory(directory=folder, filename='aircrafts_dump.sql', as_attachment=True)

if __name__ == "__main__":
    app.run()