DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR

mongoexport -d adb -c aircraft --type=csv \
--fields icao,regid,mdl,type,operator --out files/aircraft_db.csv

tar -zcf files/aircraft_db.csv.gz files/aircraft_db.csv
