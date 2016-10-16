import android
droid = android.Android()
myconst = droid.getConstants("android.provider.CallLog$Calls").result
# print myconst
calls=droid.queryContent(myconst["CONTENT_URI"],["name","number","duration"]).result
for call in calls:
    print call
