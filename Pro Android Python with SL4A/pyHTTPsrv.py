import android, socket, SimpleHTTPServer, struct
from os import chdir

droid = android.Android()

ipdec = droid.wifiGetConnectionInfo().result['ip_address']
ipstr = socket.inet_ntoa(struct.pack('L',ipdec))

chdir('/sdcard/DCIM/100MEDIA')

print "connect to %s" % ipstr
SimpleHTTPServer.test()
