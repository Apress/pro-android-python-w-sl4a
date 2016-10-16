import android, os, time

droid = android.Android()

# Specify our root podcasts directory and make sure it exists.
base_dir = '/sdcard/sl4a/scripts/podcasts'
if not os.path.exists(base_dir): os.makedirs(base_dir)

def show_dir(path=base_dir):
    """Shows the contents of a directory in a list view."""
    
    # The files & directories under "path".
    nodes = os.listdir(path)
    
    # Make a way to go up a level.
    if path != base_dir: nodes.insert(0, '..')
    
    droid.dialogCreateAlert(os.path.basename(path).title())
    droid.dialogSetItems(nodes)
    droid.dialogShow()
    
    # Get the selected file or directory.
    result = droid.dialogGetResponse().result
    droid.dialogDismiss()
    if 'item' not in result:
        return
    target = nodes[result['item']]
    target_path = os.path.join(path, target)
    
    if target == '..': target_path = os.path.dirname(path)
    
    # If a directory, show its contents.
    if os.path.isdir(target_path): show_dir(target_path)

    # If an MP3, play it.
    elif os.path.splitext(target)[1].lower() == '.mp3':
        droid.startActivity('android.intent.action.VIEW', 
                            'file://' + target_path, 'audio/mp3')
    
    # If not, inform the user.
    else:
        droid.dialogCreateAlert('Invalid File',
                                'Only .mp3 files are currently supported!')
        droid.dialogSetPositiveButtonText('Ok')
        droid.dialogShow()
        droid.dialogGetResponse()
        show_dir(path)

if __name__ == '__main__':
    show_dir()
