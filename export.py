import os
import shutil

tmp_file = '/tmp/aircrafts_dump.csv'

try:

    # check if tmp file is existing
    if os.path.isfile(tmp_file):
        os.remove(tmp_file)

    # TODO: add process to export mongo DB to csv

    # move the csv file to downloadable location
    new_file = os.path.dirname(os.path.realpath(__file__)) \
        + '/files/aircrafts_dump.csv'

    shutil.move(tmp_file, new_file)
    print "success: file exported"
except Exception, e:
    print 'error occoured...'
    print e
