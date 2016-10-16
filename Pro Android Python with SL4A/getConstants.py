import android
droid = android.Android()
myconst = droid.getConstants("android.content.Intent").result
for c in myconst:
    print c,"=",myconst[c]
