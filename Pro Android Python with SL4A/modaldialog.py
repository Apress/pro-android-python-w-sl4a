# Demonstrate use of modal dialog. Process location events while
# waiting for user input.
import android
droid=android.Android()
droid.dialogCreateAlert("I like swords.","Do you like swords?")
droid.dialogSetPositiveButtonText("Yes")
droid.dialogSetNegativeButtonText("No")
droid.dialogShow()
droid.startLocating()
while True: # Wait for events for up to 10 seconds.
  response=droid.eventWait(10000).result
  if response==None: # No events to process. exit.
    break
  if response["name"]=="dialog": # When you get a dialog event, exit loop
    break
  print response # Probably a location event.

# Have fallen out of loop. Close the dialog 
droid.dialogDismiss()
if response==None:
  print "Timed out."
else:
  rdialog=response["data"] # dialog response is stored in data.
  if  rdialog.has_key("which"):
    result=rdialog["which"]
    if result=="positive":
      print "Yay! I like swords too!"
    elif result=="negative":
      print "Oh. How sad."
  elif rdialog.has_key("canceled"): # Yes, I know it's mispelled.
    print "You can't even make up your mind?"
  else:
    print "Unknown response=",response
print droid.stopLocating()
print "Done"
