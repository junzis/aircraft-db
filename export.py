import os
import csv
import gzip
from webserver import mCollAC


def adb2csv():
    csvfilepath = os.path.dirname(os.path.realpath(__file__)) \
        + '/files/aircraft_db.csv'
    csvgzpath = os.path.dirname(os.path.realpath(__file__)) \
        + '/files/aircraft_db.csv.gz'
    try:
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

        print "csv file exported"

        print 'compress csv to gzip'
        f_in = open(csvfilepath)
        f_out = gzip.open(csvgzpath, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()

    except Exception, e:
        print 'error occoured...'
        print e
