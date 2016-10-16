import android
import urllib
import os

downloads = '/sdcard/download/'

def _reporthook(numblocks, blocksize, filesize, url=None):
    base = os.path.basename(url)
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
    except:
        percent = 100
    if numblocks != 0:
        droid.dialogSetMaxProgress(filesize)
        droid.dialogSetCurrentProgress(numblocks * blocksize)

def main():
    global droid
    droid = android.Android()
    
    url = droid.getClipboard().result
    if url is None: return
    
    dst = droid.dialogGetInput('Filename', 'Save file as:', os.path.basename(url)).result
    droid.dialogCreateHorizontalProgress('Downloading...', 'Saving %s from web.' % dst)
    droid.dialogShow()
    urllib.urlretrieve(url, downloads + dst,
        lambda nb, bs, fs, url=url: _reporthook(nb,bs,fs,url))
    droid.dialogDismiss()
    
    droid.dialogCreateAlert('Operation Finished', 
                            '%s has been saved to %s.' % (url, downloads + dst))
    droid.dialogSetPositiveButtonText('OK')
    droid.dialogShow()

if __name__ == '__main__':
    main()
