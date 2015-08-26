import requests
import json
import time
import pymysql

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

def connect_db():
    return pymysql.connect(host='localhost',
                             user='aircraft',
                             password='aircraft',
                             db='aircraft',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

def upsert_ac_data(cursor, key, data):
    if len(data) != 18:
        return None

    # get aircraft ids
    icao = data[0]
    mdl = data[8]
    regid = data[9]
    ts = data[10]
    fn = data[13]
    cs = data[16]
    fr24 = key

    if not (icao and mdl and regid) :
        return None

    # insert or update record in database
    sql_fetch_all = "SELECT * FROM `ids` WHERE `icao` = %s"
    cursor.execute(sql_fetch_all, (icao))
    result =  cursor.fetchone()
    if result:
        sql_update_ac = "UPDATE `ids` \
                    SET `icao`=%s, `regid`=%s, `mdl`=%s, `fr24`=%s, `cs`=%s, `fn`=%s, `ts`=%s \
                    WHERE `icao`=%s"
        cursor.execute(sql_update_ac, (icao, regid, mdl, fr24, cs, fn, ts, icao))
    else:
        sql_insert_ac = "INSERT INTO `ids` (`icao`, `regid`, `mdl`, `fr24`, `cs`, `fn`, `ts`) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql_insert_ac, (icao, regid, mdl, fr24, cs, fn, ts))


# ---- Generating fetching url for each zone ----
zone_urls = []
for zone in world_zones:
    bounds = ','.join(str(d) for d in zone)
    url = base_url + "&bounds=" + bounds
    zone_urls.append(url)

# ---- Get all the online aircraft from FR24 and update DB ----
try:
    dbconn = connect_db()
    cursor = dbconn.cursor()

    for url in zone_urls:
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
            upsert_ac_data(cursor, key, val)
            dbconn.commit()
except:
    print 'error occoured...'
finally:
    dbconn.close()
