#!/usr/bin/env python

import subprocess

ADB = r'C:\Program Files (x86)\Android\android-sdk-windows\platform-tools\adb.exe'
APPLICATION = 'hello_world.py'
TARGET = '/sdcard/sl4a/scripts/'

def main():
    # Upload the application.
    subprocess.call([ADB, '-e', 'push', APPLICATION, TARGET + APPLICATION])
    
    # Launch the application.
    subprocess.call('"%s" -e shell am start \
                  -a com.googlecode.android_scripting.action.LAUNCH_BACKGROUND_SCRIPT \
                  -n \
                  com.googlecode.android_scripting/.activity.ScriptingLayerServiceLauncher \
                  -e com.googlecode.android_scripting.extra.SCRIPT_PATH \
                  "%s%s"' % (ADB, TARGET, APPLICATION))

if __name__ == '__main__':
    main()
