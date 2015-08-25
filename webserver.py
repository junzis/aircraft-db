import os, time, json, ast
import flask
import pymysql
import datetime
import collections

from flask import Flask, redirect, url_for, render_template, request, flash, session, send_from_directory

def readtime(timestamp):
    """Convert unix timestamp to human readable time"""
    return datetime.datetime.fromtimestamp(
            timestamp
        ).strftime('%Y-%m-%d %H:%M:%S')

def connect_db():
    return pymysql.connect(host='localhost',
                 user='aircraft',
                 password='aircraft',
                 db='aircraft',
                 charset='utf8',
                 cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__)
app.debug = True
app.secret_key = '$1$mxQd/Zad2f3L$QvjertyBgyJ5dctN0/lTNVfadfa3'
app.jinja_env.globals.update(readtime=readtime)


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
        
        # received query param
        try:
            dbconn = connect_db()
            cursor = dbconn.cursor()
            fetch_sql = "SELECT * FROM `ids` WHERE `icao`=%s OR `regid`=%s \
                        OR `mdl`=%s OR `fr24`=%s"
            cursor.execute(fetch_sql, [q]*4)
            results =  cursor.fetchall()
        except:
            results = None
        finally:
            dbconn.close()

        return render_template('results.html', results=results)

@app.route('/random')
def random():
    try:
        dbconn = connect_db()
        cursor = dbconn.cursor()
        fetch_sql = "SELECT * FROM `ids` ORDER BY RAND() LIMIT 100"
        cursor.execute(fetch_sql)
        results =  cursor.fetchall()
    except:
        results = None
    finally:
        dbconn.close()

    return render_template('results.html', results=results)

@app.route('/stats')
def stats():
    try:
        dbconn = connect_db()
        cursor = dbconn.cursor()
        data = {}

        # get number of aircrafts
        sql = "SELECT COUNT(DISTINCT `icao`) FROM `ids`";
        cursor.execute(sql)
        results =  cursor.fetchone()
        data['total_acs'] = results[results.keys()[0]]

        # get number of models
        sql = "SELECT `icao`, `regid`, `mdl`  FROM `ids`";
        cursor.execute(sql)
        results =  cursor.fetchall()
        models = [ r['mdl'] for r in results ]
        mdlcnt = collections.Counter(models)
        data['models'] = sorted(list(mdlcnt.items()), key=lambda x: x[1], reverse=True)
    except:
        data = None
    finally:
        dbconn.close()
    return render_template('stats.html', data=data)

@app.route('/download')
def download():
    folder = os.path.join(app.root_path, 'files')
    return send_from_directory(directory=folder, filename='aircrafts_dump.sql', as_attachment=True)

if __name__ == "__main__":
    app.run()