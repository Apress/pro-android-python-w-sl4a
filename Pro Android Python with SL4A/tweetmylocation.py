import android, datetime, time, tweepy

CONSUMER_KEY = 'my consumer key'
CONSUMER_SECRET = 'my consumer secret'

ACCESS_KEY = 'my access key'
ACCESS_SECRET = 'my access secret'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

droid = android.Android()
droid.startLocating()
time.sleep(15)
loc = droid.readLocation()
droid.stopLocating()

if 'gps' in loc.result:
    lat = str(loc.result['gps']['latitude'])
    lon = str(loc.result['gps']['longitude'])
else:
    lat = str(loc.result['network']['latitude'])
    lon = str(loc.result['network']['longitude'])

now = str(datetime.datetime.now())
outString = 'I am here: ' + now + ' ' + lat + ' ' + lon

api.update_status(outString)
