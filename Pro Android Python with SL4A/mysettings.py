import android, os

script_dir = '/sdcard/sl4a/scripts/profiles/'

if not os.path.exists(script_dir):
    os.makedirs(script_dir)

droid = android.Android()

toggles = [
    ('droid.toggleAirplaneMode(True)', 'droid.toggleAirplaneMode(False)'),
    ('droid.toggleBluetoothState(True)', 'droid.toggleBluetoothState(False)'),
    ('droid.toggleRingerSilentMode(True)', 'droid.toggleRingerSilentMode(False)'),
    ('droid.setScreenBrightness(0)', 'droid.setScreenBrightness(255)'),
    ('droid.toggleWifiState(True)', 'droid.toggleWifiState(False)'),
]

droid.dialogCreateAlert('Settings Dialog', 'Chose any number of items and then press OK')
droid.dialogSetPositiveButtonText('Done')
droid.dialogSetNegativeButtonText('Cancel')

droid.dialogSetMultiChoiceItems(['Airplane Mode',
                                 'Bluetooth On',
                                 'Ringer Silent',
                                 'Screen Off',
                                 'Wifi On'])

droid.dialogShow()
response = droid.dialogGetResponse().result

if 'canceled' in response:
    droid.exit()
else:
    response = droid.dialogGetSelectedItems().result

droid.dialogDismiss()
res = droid.dialogGetInput('Script Name', 'Enter a name for the profile script.', 'default').result

script = '''import android

droid = android.Android()
'''

for i, toggle in enumerate(toggles):
    if i in response:
        script += toggles[i][0]
    else:
        script += toggles[i][1]
    script += '\n'

script += '''
droid.dialogCreateAlert('Profile Enabled', 'The "%s" profile has been activated.')
droid.dialogSetPositiveButtonText('OK')
droid.dialogShow()''' % res

f = open(script_dir + res + '.py', 'w')
f.write(script)
f.close()