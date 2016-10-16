import android, socket, struct
import ftpserver

droid = android.Android()

authorizer = ftpserver.DummyAuthorizer()
authorizer.add_anonymous('/sdcard/downloads')
authorizer.add_user('user', 'password', '/sdcard/sl4a/scripts', perm='elradfmw')
handler = ftpserver.FTPHandler
handler.authorizer = authorizer
ipdec = droid.wifiGetConnectionInfo().result['ip_address']
ipstr = socket.inet_ntoa(struct.pack('L',ipdec))
droid.makeToast(ipstr)

server = ftpserver.FTPServer((ipstr, 8080), handler)
server.serve_forever()
