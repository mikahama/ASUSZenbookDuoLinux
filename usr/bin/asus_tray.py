#!/usr/bin/python
import configparser
import os
import subprocess
from pathlib import Path

import pystray
from PIL import Image



image = Image.open("/usr/bin/asus.png")

CONFIG_PATH = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "asus-duo" / "fnkeys.conf"
fnkeys_process = None


def ensure_fnkeys_config():
    if CONFIG_PATH.exists():
        return

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        """# Commands run when the matching top-row key is pressed.
# Leave a command blank to use the normal F7-F12 key.

[settings]
enabled = true

[commands]
# f7 = duo toggle
# f8 =
# f9 =
# f10 =
# f11 =
# f12 =
""",
        encoding="utf-8",
    )


def fnkeys_enabled():
    ensure_fnkeys_config()
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config.getboolean("settings", "enabled", fallback=True)


def set_fnkeys_enabled(enabled):
    ensure_fnkeys_config()
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if not config.has_section("settings"):
        config.add_section("settings")
    config.set("settings", "enabled", str(enabled).lower())
    with CONFIG_PATH.open("w", encoding="utf-8") as config_file:
        config.write(config_file)


def start_fnkeys():
    global fnkeys_process
    if fnkeys_process is None or fnkeys_process.poll() is not None:
        fnkeys_process = subprocess.Popen(["/usr/bin/asus-duo-fnkeys", "--config", str(CONFIG_PATH)])


def stop_fnkeys():
    global fnkeys_process
    if fnkeys_process is not None and fnkeys_process.poll() is None:
        fnkeys_process.terminate()
    fnkeys_process = None


def toggle_fnkeys(icon, _item):
    enabled = not fnkeys_enabled()
    set_fnkeys_enabled(enabled)
    if enabled:
        start_fnkeys()
    else:
        stop_fnkeys()


def configure_fnkey_commands(icon, _item):
    subprocess.Popen(["/usr/bin/asus-duo-fnkeys-config"])


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
        stop_fnkeys()
        icon.stop()


ensure_fnkeys_config()
if fnkeys_enabled():
    start_fnkeys()

icon = pystray.Icon("GFG", image, "ASUS Zenbook Duo",
                    menu=pystray.Menu(
    pystray.MenuItem("Top display only", 
                     after_click),
    pystray.MenuItem("Keyboard light on", 
                     after_click),
    pystray.MenuItem("Keyboard light off", 
                     after_click),
    pystray.MenuItem(
        lambda _item: "Function keys enabled" if fnkeys_enabled() else "Function keys disabled",
        toggle_fnkeys,
        checked=lambda _item: fnkeys_enabled(),
    ),
    pystray.MenuItem("Configure F7-F12 commands", configure_fnkey_commands),
    pystray.MenuItem("Exit", after_click)))

icon.run()
