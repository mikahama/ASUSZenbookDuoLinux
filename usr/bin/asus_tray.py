#!/usr/bin/python
import pystray
from PIL import Image
import subprocess



image = Image.open("asus.png")


def after_click(icon, query):
    if str(query) == "Top display only":
        subprocess.run(["duo", "top"]) 
        # icon.stop()
    elif str(query) == "Keyboard light on":
        subprocess.run('bk.py 3', shell=True)
        # icon.stop()
    elif str(query) == "Keyboard light off":
        subprocess.run('bk.py 0', shell=True)
    elif str(query) == "Exit":
        icon.stop()


icon = pystray.Icon("GFG", image, "GeeksforGeeks", 
                    menu=pystray.Menu(
    pystray.MenuItem("Top display only", 
                     after_click),
    pystray.MenuItem("Keyboard light on", 
                     after_click),
    pystray.MenuItem("Keyboard light off", 
                     after_click),
    pystray.MenuItem("Exit", after_click)))

icon.run()
