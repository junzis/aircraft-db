import os, shutil
import pymysql

tmp_file = '/tmp/aircrafts_dump.csv'

try:

    # check if tmp file is existing
    if os.path.isfile(tmp_file):
        os.remove(tmp_file)

    dbconn = pymysql.connect(host='localhost',
                             user='aircraft',
                             password='aircraft',
                             db='aircraft',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

    cursor = dbconn.cursor()
    sql_export = "SELECT * FROM `ids` \
                    INTO OUTFILE '/tmp/aircrafts_dump.csv' \
                    FIELDS TERMINATED BY ',' \
                    ENCLOSED BY '\"' \
                    LINES TERMINATED BY '\\n';"
    cursor.execute(sql_export)
    
    # move the csv file to downloadable location
    new_file =  os.path.dirname(os.path.realpath(__file__)) \
            +'/files/aircrafts_dump.csv'
    shutil.move(tmp_file, new_file)
    print "success: file exported"
except Exception, e:
    print 'error occoured...'
    print e
finally:
    dbconn.close()
