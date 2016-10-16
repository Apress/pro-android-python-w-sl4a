import android
import time

def main():
    global droid
    droid = android.Android()

    # Wait until the scan finishes.
    while not droid.wifiStartScan().result: time.sleep(0.25)
    
    # Build a dictionary of available networks.
    networks = {}
    while not networks:
        for ap in droid.wifiGetScanResults().result:
            networks[ap['bssid']] = ap.copy()
    
    droid.dialogCreateAlert('Access Points')
    droid.dialogSetItems(['%(ssid)s, %(level)s, %(capabilities)s' % ap
                          for ap in networks.values()])
    droid.dialogSetPositiveButtonText('OK')
    droid.dialogShow()

if __name__ == '__main__':
    main()
