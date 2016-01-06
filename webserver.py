from flask import render_template as page
from flask import Flask, redirect, url_for, request, \
                  send_from_directory, Response
import os
import json
import re
import pymongo
import random
import statistics

app = Flask(__name__)
app.debug = True
app.secret_key = '$1$rrxQdds52Zad2f3L$Qdqpy5ertyJ5dctHFd0/lTNsa35fa3'

mclient = pymongo.MongoClient()
mcoll = mclient.aif.aircraft


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

    results = list(mcoll.find({'icao': q}))

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
    total_count = mcoll.find({n: {'$regex': q}}).count()

    results = list(mcoll.find({n: {'$regex': q}}).skip(p*100).limit(100))

    return page('results.html', results=results,
                total_count=total_count, n=n, q=q, p=p)


@app.route('/rand')
def rand():
    count = mcoll.find().count()
    r = random.randint(1, count)
    results = list(mcoll.find().skip(r).limit(30))
    return page('results.html', results=results, total_count=30, p=0)


@app.route('/stats')
def stats():
    return page('stats.html')


@app.route('/statdata')
def statdata():
    data = {
        'mdls': statistics.mdls(),
        'types': statistics.types(),
        'operators': statistics.operators()
    }

    r = Response(response=json.dumps(data), status=200,
                 mimetype="application/json")
    return(r)


@app.route('/download')
def download():
    folder = os.path.join(app.root_path, 'files')
    return send_from_directory(
        directory=folder, filename='aircrafts_dump.csv', as_attachment=True
    )


if __name__ == "__main__":
    app.run()
