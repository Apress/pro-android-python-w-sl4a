import android
droid=android.Android()

droid.addOptionsMenuItem("Silly","silly",None,"star_on")
droid.addOptionsMenuItem("Sensible","sensible","I bet.","star_off")
droid.addOptionsMenuItem("Off","off",None,"ic_menu_revert")
 
print "Hit menu to see extra options."
print "Will timeout in 10 seconds if you hit nothing."

droid.webViewShow('file://sdcard/sl4a/scripts/blank.html')
 
while True: # Wait for events from the menu.
    response=droid.eventWait(10000).result
    if response==None:
        break
    print response
    if response["name"]=="off":
        break
print "And done."
