import requests
import re
import time
import pymongo
from bs4 import BeautifulSoup

base_url = "http://lhr.data.fr24.com/zones/fcgi/feed.js?faa=1&mlat=1&flarm=0" \
    "&adsb=1&gnd=1&air=1&vehicles=0&estimated=0&maxage=0&gliders=0&stats=1"

flight_url = "https://api.flightradar24.com/common/v1/flight-playback.json?flightId=%s"

# """ Divid the earth surface into 252 zones for querying aircraft data """
# zones = []
# for i in xrange(7):
#     for j in xrange(18):
#         zones.append([70-20*i, 70-20*(i+1), -180+20*j, -180+20*(j+1)])

# Manuelly divid the earth surface into zones optimized for flights density
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

# using requests session to increace http performance
s = requests.Session()
s.headers.update({'user-agent': 'Mozilla/5.0'})

mclient = pymongo.MongoClient()
mCollAC = mclient.adb.aircraft


def trim_label(label):
    """
    Trim label, for example:
    Lufthansa (Star Alliance Livery) to Lufthansa
    """
    regex = re.compile('\(.+')
    trimed = regex.sub('', label).strip()
    return trimed


def get_ac(key, data):
    if len(data) != 18:
        raise RuntimeError('wrong data length')

    # get aircraft ids
    icao = data[0]
    regid = data[9]
    mdl = data[8]
    fr24id = key

    if not (icao and mdl and regid):
        raise RuntimeError('some field missing in data')

    ac = {
        'icao': icao.lower(),
        'regid': regid.lower(),
        'mdl': mdl.lower(),
        'fr24id': fr24id.lower(),
        'ts': int(time.time()),
    }

    return ac


def fetch_online_aircraft():
    urls = []
    for zone in world_zones:
        bounds = ','.join(str(d) for d in zone)
        url = base_url + "&bounds=" + bounds
        urls.append(url)

    acs = []

    # ---- Get all the online aircraft from FR24 and update DB ----
    for url in urls:
        try:
            response = s.get(url)
            data = response.json()
        except Exception, e:
            print e
            continue

        for key, val in data.iteritems():
            try:
                ac = get_ac(key, val)
                acs.append(ac)
            except Exception, e:
                # print e
                continue

    # Update or insert record
    for ac in acs:
        ac_old = mCollAC.find_one({'icao': ac['icao']})
        if ac_old:
            if 'type' in ac_old:
                ac['type'] = ac_old['type']
            if 'operator' in ac_old:
                ac['operator'] = ac_old['operator']

        mCollAC.update({'icao': ac['icao']}, ac, upsert=True)

    return acs


def update_info(ac):
    url = flight_url % ac['fr24id'].lower()

    try:
        response = s.get(url)
        data = response.json()

        d = data['result']['response']['data']['flight']['aircraft']

        ac['operator'] = trim_label(d['owner'])
        ac['type'] = d['model']['text']

        mCollAC.update({'icao': ac['icao']}, ac)
        return True
    except:
        return False


def update_new_acs_info():
    acs = mCollAC.find({
        '$or': [
            {'type': {'$exists': False}},
            {'operator': {'$exists': False}}
        ]
    })

    total_count = acs.count()
    count = 0

    for ac in acs:
        count += 1
        print "%d of %d updated" % (count, total_count)

        update_info(ac)
        time.sleep(0.5)


def trim_all_oeprator_labels():
    acs = mCollAC.find()
    for ac in acs:
        if 'operator' in ac:
            ac['operator'] = trim_label(ac['operator'])
            mCollAC.update({'icao': ac['icao']}, ac, upsert=True)
