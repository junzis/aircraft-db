import requests
import json
import timeit
import time
import sys
import multiprocessing
import pymysql
from bs4 import BeautifulSoup

def connect_db():
    return pymysql.connect(host='localhost',
                             user='aircraft',
                             password='aircraft',
                             db='aircraft',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

def update_aircraft_info(regid):
    info = []
    url = "http://www.flightradar24.com/data/airplanes/" + regid.lower()
    r = requests.get(url)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html5lib")
    for node in soup.find(id="cntAircraftDetails").dl.find_all('dd'):
        info.append(node.find_all(text=True)[0])
    
    if len(info) < 6:
        return None

    # update record
    try:
        dbconn = connect_db()
        cursor = dbconn.cursor()
        sql_update_ac_info = "UPDATE `ids` SET `type`=%s, `owner`=%s WHERE `regid`=%s"
        cursor.execute(sql_update_ac_info, (info[3], info[5], info[1]))
        dbconn.commit()
        print info
        print
    except:
        print "error occoured.."
    finally:
        dbconn.close()


# ---- Fetch all regid update aricraft info ----
try:
    dbconn = connect_db()
    cursor = dbconn.cursor()
    sql_fetch_all = "SELECT `regid`, `type`, `owner` FROM `ids` \
                    WHERE `owner` IS NULL OR `type` IS NULL "
    cursor.execute(sql_fetch_all)
    aircrafts = cursor.fetchall()
except:
    print 'error occoured...'
finally:
    dbconn.close()

# ---- update aircrafts info ----
for ac in aircrafts:
    if not (ac['type'] and ac['owner']):
        print 'processing: ' + ac['regid']
        update_aircraft_info(ac['regid'])
    time.sleep(1)
