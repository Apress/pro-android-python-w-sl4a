import time
import android

if __name__ == '__main__':
    droid = android.Android()
    
    # Show the HTML page immediately.
    droid.webViewShow('file:///sdcard/sl4a/scripts/wifi.html')

    # Mainloop
    while True:

        # Wait until the scan finishes.
        while not droid.wifiStartScan().result: time.sleep(0.25)
        
        # Send results to HTML page.
        droid.postEvent('show_networks', droid.wifiGetScanResults().result)
        
        time.sleep(1)
