import android

droid = android.Android()
droid.webViewShow('file:///sdcard/sl4a/scripts/text_to_speech.html')
while True:
  result = droid.waitForEvent('say').result
  droid.ttsSpeak(result['data'])