import android, os, time, datetime

droid = android.Android()
droid.startLocating()
 
while not droid.readLocation()[1].has_key('gps') :
    print "Waiting on gps to turn on"
    time.sleep(1)

if not os.path.exists('/sdcard/logs'):
    os.mkdir('/sdcard/logs')

# Now we'll loop until the user closes the application

while True:
    loc = droid.readLocation()

    lat = str(loc.result['gps']['latitude'])
    lon = str(loc.result['gps']['longitude'])
    alt = str(loc.result['gps']['altitude'])

    now = str(datetime.datetime.now())
    f = open('/sdcard/logs/logfile.txt','a')
    outString = now + ',' + lat + ',' + lon + ',' + alt
    f.write(outString)
    print outString
    f.close()

    time.sleep(1)
