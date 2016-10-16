import android, time
droid = android.Android()

lat1 = 33.111111
lon1 = 90.000000

droid.startLocating()

time.sleep(15)
while True:
    loc = droid.readLocation().result
    if loc = {}:
        loc = getLastKnownLocation().result
    if loc != {}:
        try:
            n = loc['gps']
        except KeyError:
            n = loc['network'] 
    la = n['latitude'] 
    lo = n['longitude']

    if haversine(la, lo, lat1, lon1) < 1:
        droid.toggleRingerSilentMode(True)
    else:
        droid.toggleRingerSilentMode(False)
