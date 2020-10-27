#!/usr/bin/env python3

# gnome-shell-mousewheel-zoom

# (c) Sep 2011, Tobias Quinn <tobias@tobiasquinn.com>
# GPLv3

import sys

from gi.repository import Gio

from Xlib.display import Display
from Xlib import X
from Xlib.error import ConnectionClosedError

from signal import signal, SIGINT

buttons = [X.Button4, X.Button5]
masks = [0, X.LockMask, X.Mod2Mask, X.LockMask | X.Mod2Mask]
incr = 0.1

APP_BASE_KEY = "org.gnome.desktop.a11y.applications"
MAG_BASE_KEY = "org.gnome.desktop.a11y.magnifier"

class Zoomer:
    def __init__(self):
        self._app_settings = Gio.Settings.new(APP_BASE_KEY)
        self._mag_settings = Gio.Settings.new(MAG_BASE_KEY)
        self._app_settings.set_boolean("screen-magnifier-enabled", False)
        self._active = False
        self._currentZoom = self._mag_settings.get_double("mag-factor")

    def zoomIn(self):
        if self._active:
            self._currentZoom *= (1.0+incr)
            self._mag_settings.set_double("mag-factor", self._currentZoom)
        else:
            self._currentZoom = 1 + incr
            self._mag_settings.set_double("mag-factor", self._currentZoom)
            self._app_settings.set_boolean("screen-magnifier-enabled", True)
            self._active = True

    def zoomOut(self):
        if self._active:
            self._currentZoom *= (1.0-incr)
            if self._currentZoom <= 1:
                self._app_settings.set_boolean("screen-magnifier-enabled", False)
                self._active = False
            else:
                self._mag_settings.set_double("mag-factor", self._currentZoom)

    def disable_magnifier(self):
        self._app_settings.set_boolean("screen-magnifier-enabled", False)

z = Zoomer()
def handler(signal_received, frame):
    print("SIGINT received, reverting to stored zoom")
    z.disable_magnifier()
    sys.exit(0)

def main():
    signal(SIGINT, handler)
    # setup xlib
    disp = Display()
    root = disp.screen().root
    # grab a buttons with a modifier
    for mask in masks:
        for button in buttons:
            root.grab_button(button,
                    X.Mod1Mask | mask,
                    root,
                    False,
                    X.GrabModeAsync,
                    X.GrabModeAsync,
                    X.NONE,
                    X.NONE)

    while 1:
        try:
            event = root.display.next_event()
            if event.detail == X.Button4:
                z.zoomIn()
            elif event.detail == X.Button5:
                z.zoomOut()
        except AttributeError:
            pass
        except ConnectionClosedError:
            sys.exit()

if __name__ == '__main__':
    main()

