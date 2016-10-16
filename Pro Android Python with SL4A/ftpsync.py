import ftplib
import time
import os

import android
droid = android.Android()

HOST = '192.168.1.81'
USER = 'user'
PASS = 'pass'
REMOTE = 'phone-sync'
LOCAL = '/sdcard/sl4a/scripts/ftp-sync'

if not os.path.exists(LOCAL):
    os.makedirs(LOCAL)

while True:
    srv = ftplib.FTP(HOST)
    srv.login(USER, PASS)
    srv.cwd(REMOTE)
    
    os.chdir(LOCAL)
    
    remote = srv.nlst()
    local = os.listdir(os.curdir)
    for file in remote:
        if file not in local:
            srv.storlines('RETR ' + file,
                          open(file, 'w').write)
    
    srv.close()
    time.sleep(1)
