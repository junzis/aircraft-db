DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR/files

rm aircraft_db.csv

mongoexport -d adb -c aircraft --type=csv \
--fields icao,regid,mdl,type,operator --out aircraft_db.csv

zip aircraft_db.zip aircraft_db.csv LICENSE.txt README.txt
