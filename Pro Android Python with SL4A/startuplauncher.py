import android

STARTUP_SCRIPTS = (
    'facedown.py',
    'logGPS.py',
    'silentnight.py'
)

droid = android.Android()

LOG = "../logtest.py.log"
if os.path.exists(LOG) is False:
	f = open(LOG, "w")
	f.close()
LOG = open(LOG, "a")

for script in STARTUP_SCRIPTS:
    extras = {"com.googlecode.android_scripting.extra.SCRIPT_PATH":
             "/sdcard/sl4a/scripts/%s" % script}
    myintent = droid.makeIntent("com.googlecode.android_scripting.action.LAUNCH_BACKGROUND_SCRIPT",
                                None, None, extras, None,
                                "com.googlecode.android_scripting",
                                "com.googlecode.android_scripting.activity.ScriptingLayerServiceLauncher").result
    droid.startActivityIntent(myintent)
    LOG.write("Starting %s\n" % script)
