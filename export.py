import os
import csv
from webserver import mCollAC


def adb2csv():
    try:
        csvfilepath = os.path.dirname(os.path.realpath(__file__)) \
            + '/files/aircraft_db.csv'

        # check if tmp file is existing
        if os.path.isfile(csvfilepath):
            os.remove(csvfilepath)

        fcsv = open(csvfilepath, 'wt')
        csvout = csv.writer(fcsv, lineterminator="\n")

        fields = ['icao', 'regid', 'mdl', 'type', 'operator']

        csvout.writerow(fields)

        res = mCollAC.find()
        for r in res:
            line = []
            for f in fields:
                if f in r.keys():
                    if r[f]:
                        v = r[f].encode('ascii', 'ignore').upper()
                        line.append(v)
                    else:
                        line.append('NONE')
                else:
                    line.append('NONE')
            csvout.writerow(line)
        fcsv.close()

        print "success: file exported"
    except Exception, e:
        print 'error occoured...'
        print e
