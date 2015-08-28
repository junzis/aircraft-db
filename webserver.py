import os, time, json, re
import flask
import pymysql
import datetime
import collections

from flask import Flask, redirect, url_for, render_template, request, \
    flash, session, send_from_directory

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

    # GET Method
    q = request.args.get('q', '')
    if not q:
        return render_template('index.html')
    
    # received query param
    try:
        dbconn = connect_db()
        cursor = dbconn.cursor()
        fetch_sql = "SELECT * FROM `ids` WHERE `icao`=%s OR `regid`=%s"
        cursor.execute(fetch_sql, [q.upper(), q])
        results =  cursor.fetchall()
        total_count = len(results)
    except:
        results = None
    finally:
        dbconn.close()

    return render_template('results.html', results=results, 
            total_count=total_count, n=0, q=q, p=0)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        n = request.form['n']
        q = request.form['q']
        return redirect(url_for('search', n=n, q=q))

    # GET request
    n = request.args.get('n', '')
    n = " ".join(re.findall("[a-zA-Z]+", n))    # security, only letters
    q = request.args.get('q', '')
    p = request.args.get('p', '')
    try:
        p = int(p)
        if p < 0:
            p = 0
    except:
        p = 0
        pass

    # ICAO all upper cases
    if n == 'icao':
        q = q.upper()

    if not q or not n:
        return redirect(url_for('index'))
    
    # received query param
    try:
        dbconn = connect_db()
        cursor = dbconn.cursor()

        count_sql = "SELECT COUNT(*) FROM `ids` WHERE `" + n + "` LIKE %s"
        cursor.execute(count_sql, '%'+q+'%')
        count =  cursor.fetchone()
        total_count = count[count.keys()[0]]

        fetch_sql = "SELECT * FROM `ids` WHERE `" + n + "` LIKE %s LIMIT %s,%s"
        cursor.execute(fetch_sql, ('%'+q+'%', p*100, 100))
        results =  cursor.fetchall()
        # print cursor._last_executed
    except Exception, e:
        results = None
        total_count = 0
        print e
    finally:
        dbconn.close()

    return render_template('results.html', results=results, 
            total_count=total_count, n=n, q=q, p=p)

@app.route('/random')
def random():
    try:
        dbconn = connect_db()
        cursor = dbconn.cursor()
        fetch_sql = "SELECT * FROM `ids` ORDER BY RAND() LIMIT 100"
        cursor.execute(fetch_sql)
        results =  cursor.fetchall()
        total_count = len(results)
    except:
        results = None
    finally:
        dbconn.close()

    return render_template('results.html', results=results, 
            total_count=total_count, p=0, q=0, n=0)

@app.route('/stats')
def stats():
    try:
        dbconn = connect_db()
        cursor = dbconn.cursor()
        data = {}

        sql = "SELECT `icao`, `regid`, `mdl`, `owner`  FROM `ids`";
        cursor.execute(sql)
        results =  cursor.fetchall()

        # total count
        data['total_acs'] = len(results)

        # owners stat
        owners = [ r['owner'] for r in results ]
        owner_counts = collections.Counter(owners)
        data['owners'] = sorted(list(owner_counts.items()), 
                key=lambda x: x[1], reverse=True)

        # models stat
        models = [ r['mdl'] for r in results ]
        model_counts = collections.Counter(models)
        data['models'] = sorted(list(model_counts.items()), 
                key=lambda x: x[1], reverse=True)
    except:
        data = None
    finally:
        dbconn.close()
    return render_template('stats.html', data=data)

@app.route('/download')
def download():
    folder = os.path.join(app.root_path, 'files')
    return send_from_directory(directory=folder, 
            filename='aircrafts_dump.csv', as_attachment=True)

if __name__ == "__main__":
    app.run()