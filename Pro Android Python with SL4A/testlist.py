# Test of Lists
import android,sys
droid=android.Android()

#Choose which list type you want.
def getlist():
  droid.dialogCreateAlert("List Types")
  droid.dialogSetItems(["Items","Single","Multi"])
  droid.dialogShow()
  result=droid.dialogGetResponse().result
  if result.has_key("item"):
    return result["item"]
  else:
    return -1

#Choose List
listtype=getlist()
if listtype<0:
  print "No item chosen"
  sys.exit()

options=["Red","White","Blue","Charcoal"]
droid.dialogCreateAlert("Colors")
if listtype==0:
  droid.dialogSetItems(options)
elif listtype==1:
  droid.dialogSetSingleChoiceItems(options)
elif listtype==2:
  droid.dialogSetMultiChoiceItems(options)
droid.dialogSetPositiveButtonText("OK")
droid.dialogSetNegativeButtonText("Cancel")
droid.dialogShow()
result=droid.dialogGetResponse().result
# droid.dialogDismiss() # In most modes this is not needed.
if result==None:
  print "Time out"
elif result.has_key("item"):
  item=result["item"];
  print "Chosen item=",item,"=",options[item]
else:
  print "Result=",result
  print "Selected=",droid.dialogGetSelectedItems().result
print "Done"
