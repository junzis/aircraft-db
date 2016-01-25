from flask import render_template as page
from flask import Flask, redirect, url_for, request, \
                  send_from_directory
import os
import json
import re
import pymongo
import random
import datetime
import statistics

app = Flask(__name__)
app.debug = True
app.secret_key = '$1$rrxQdds52Zad2f3L$Qdqpy5ertyJ5dctHFd0/lTNsa35fa3'

mclient = pymongo.MongoClient()
mCollAC = mclient.adb.aircraft
mCollStatMdl = mclient.adb.stat_mdl
mCollStatOperator = mclient.adb.stat_operator
mCollStatType = mclient.adb.stat_type


def readtime(timestamp):
    """Convert unix timestamp to human readable time"""
    return datetime.datetime.fromtimestamp(
            timestamp
        ).strftime('%Y-%m-%d %H:%M:%S')

app.jinja_env.globals.update(readtime=readtime)


@app.errorhandler(404)
def page_not_found(e):
    return page('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return page('500.html', e=e), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        q = request.form['q']
        return redirect(url_for('index', q=q))

    # GET Method
    q = request.args.get('q', '').lower()
    if not q:
        return page('index.html')

    results = list(mCollAC.find({'icao': q}))

    return page('results.html', results=results,
                total_count=len(results), n=0, q=q, p=0)


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

    if n in ['regid', 'icao', 'mdl']:
        q = q.lower()

    if not q or not n:
        return redirect(url_for('index'))

    # Now, let's query
    total_count = mCollAC.find({n: {'$regex': q}}).count()

    results = list(mCollAC.find({n: {'$regex': q}}).skip(p*100).limit(100))

    return page('results.html', results=results,
                total_count=total_count, n=n, q=q, p=p)


@app.route('/rand')
def rand():
    count = mCollAC.find().count()
    r = random.randint(1, count)
    results = list(mCollAC.find().skip(r).limit(30))
    return page('results.html', results=results, total_count=30, p=0)


@app.route('/download')
def download():
    folder = os.path.join(app.root_path, 'files')
    return send_from_directory(
        directory=folder, filename='aircraft_db.csv', as_attachment=True
    )


@app.route('/stats')
def stats():
    return page('stats.html')


@app.route('/stats/top')
def top20():
    scripts = []
    divs = []

    s, d = statistics.top_mdl()
    scripts.append(s)
    divs.append(d)

    s, d = statistics.top_operator()
    scripts.append(s)
    divs.append(d)

    return page('stats/top.html', plots=zip(scripts, divs))


@app.route('/stats/treemap')
def treemap():
    data1, data2 = statistics.treemaps()
    return page('stats/treemap.html', data1=json.dumps(data1),
                data2=json.dumps(data2))


@app.route('/stats/realtime/density')
def realtime_density():
    flag = request.args.get('flag')
    data = statistics.realtime_density(flag)
    return page('stats/realtime-density.html', data=json.dumps(data))


@app.route('/stats/realtime/traffic')
def realtime_traffic():
    data = statistics.realtime_traffic()
    return page('stats/realtime-traffic.html', data=json.dumps(data))


if __name__ == "__main__":
    app.run()
