import android
import urlparse

droid = android.Android()
droid.webViewShow('file:///sdcard/sl4a/scripts/settings.html')
while True:
    result = droid.waitForEvent('save').result
    data = urlparse.parse_qs(result['data'][1:])
    
    droid.toggleAirplaneMode('airplane' in data)
    droid.toggleWifiState('wifi' in data)
    droid.setScreenBrightness('screen' in data and 255 or 0)