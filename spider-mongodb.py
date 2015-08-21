import requests
import json
import timeit
import time
import sys
import multiprocessing
from pymongo import MongoClient

def read_ac_data(key, data):
    if len(data) != 18:
        return None
    else:
        ac = {}
        ac['_id'] = data[0]         # ICAO ID
        ac['mdl'] = data[8]
        ac['regid'] = data[9]       # Registration ID
        ac['ts'] = data[10]
        ac['fn'] = data[13]         # Flight number
        ac['cs'] = data[16]
        ac['fr24'] = key            # FR24 ID
        return ac

def spider_run(urls, mcollection, timestamps):
    for url in urls:
        r = requests.get(url)
        if r.status_code != 200:
            pass

        try:
            jdata = r.json()
        except:
            pass

        if len(jdata) < 2:
            pass

        # remove some fields
        if 'version' in jdata:
            del jdata['version']

        if 'full_count' in jdata:
            del jdata['full_count']

        for key, val in jdata.iteritems():
            ac = read_ac_data(key, val)
            if ac:
                mcollection.update({'_id': ac['_id']}, ac, True)
            else:
                pass


base_url = "http://lhr.data.fr24.com/zones/fcgi/feed.js?faa=1&mlat=1&flarm=0" \
    "&adsb=1&gnd=1&air=1&vehicles=0&estimated=0&maxage=0&gliders=0&stats=1"

# """ Divid the earth surface into 252 zones for querying aircraft data """
# zones = []
# for i in xrange(7):
#     for j in xrange(18):
#         zones.append([70-20*i, 70-20*(i+1), -180+20*j, -180+20*(j+1)])

"""Manuelly divid the earth surface into zones optimized for flights density """
world_zones = [
    [90, 70, -180, 180],
    [70, 50, -180, -20],
    [70, 50, -20, 0],
    [70, 50, 0, 20],
    [70, 50, 20, 40],
    [70, 50, 40, 180],
    [50, 30, -180, -120],
    [50, 40, -120, -110],
    [50, 40, -110, -100],
    [40, 30, -120, -110],
    [40, 30, -110, -100],
    [50, 40, -100, -90],
    [50, 40, -90, -80],
    [40, 30, -100, -90],
    [40, 30, -90, -80],
    [50, 30, -80, -60],
    [50, 30, -60, -40],
    [50, 30, -40, -20],
    [50, 30, -20, 0],
    [50, 40, 0, 10],
    [50, 40, 10, 20],
    [40, 30, 0, 10],
    [40, 30, 10, 20],
    [50, 30, 20, 40],
    [50, 30, 40, 60],
    [50, 30, 60, 180],
    [30, 10, -180, -100],
    [30, 10, -100, -80],
    [30, 10, -80, 100],
    [30, 10, 100, 180],
    [10, -10, -180, 180],
    [-10, -30, -180, 180],
    [-30, -90, -180, 180]
]

west_europe_uk_zone = [
    [60,50,-15,5],
    [60,50,5,25],
    [50,35,-15,5],
    [50,35,-5,25],
]

# Generating fetching url for each zone
urls = []
for zone in world_zones:
    bounds = ','.join(str(d) for d in zone)
    url = base_url + "&bounds=" + bounds
    urls.append(url)

# in memory status for fast checking
timestamps = {}

mclient = MongoClient('localhost', 27017)
mdb = mclient.flightids
mcollection = mdb.ids

newrows = spider_run(urls, mcollection, timestamps)
