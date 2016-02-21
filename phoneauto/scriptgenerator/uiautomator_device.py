# -*- coding: utf-8 -*-
"""Interfaces to devices

:copyright: (c) 2015 by tksn
:license: MIT
"""

from __future__ import unicode_literals
import uiautomator
from . import keycode
from phoneauto.scriptgenerator.exception import UiInconsitencyError


class UiautomatorDevice(object):
    """Device for interacting with android device via uiautomator"""

    def __init__(self, device_name=None):
        """Initialize the device object

        Args:
            device_name (string): device name (serial number) of the device
                (what you see in output of adb devices)
        """
        self._device = uiautomator.Device(device_name)

        # WORKAROUND:
        #   Some methods of uiautomator fails if jsonrpc server
        #   has not been started. So I force it start here.
        self._device.server.start()

    def close(self):
        """Close the device"""
        self._device = None

    def dump(self):
        """Provide hierarchy dump xml string"""
        return self._device.dump()

    @property
    def info(self):
        """Device info such as screen dimension"""
        return self._device.info

    @property
    def device_name(self):
        """The device's name (serial number)"""
        return self._device.server.adb.device_serial()

    def get_screenshot_as_file(self, file_path):
        """Aquire screenshot from the device and save it as a file.

        Args:
            file_path (string): save file path
        """
        return self._device.screenshot(file_path)

    def _find(self, locator):
        """Find UI object using locator."""
        index = locator.index or 0
        objs = self._device(**locator.filters)
        if len(objs) <= index:
            raise UiInconsitencyError(
                    'locator.index not found on device screen')
        return objs[index]

    def set_text(self, locator, text):
        """Set text to a UI object which is specified by the locator

        Args:
            locator (object): Locator object to locate the UI object.
            text (string): Text which is set to the UI object.
        """
        self._find(locator).set_text(text)

    def clear_text(self, locator):
        """Clear text on a UI object which is specified by the locator.

        Args:
            locator (object): Locator object to locate the UI object.
        """
        self._find(locator).clear_text()

    def click_object(self, locator, wait):
        """Click on a UI object which is specified by the locator.

        Args:
            locator (object): Locator object to locate the UI object.
            wait (integer): wait time in milliseconds if wait update
                after click, None if no-wait.
        """
        if wait is None:
            self._find(locator).click()
        else:
            self._find(locator).click.wait(timeout=wait)

    def long_click_object(self, locator):
        """Long-click on a UI object which is specified by the locator.

        Args:
            locator (object): locator object to locate the UI object.
        """
        self._find(locator).long_click()

    def drag_object_to_xy(self, locator, coord, options):
        """Drag a UI object to given coordinates xy

        UI object is specified by the locator.
        Args:
            locator (object): Locator object to locate the UI object
                which is to be dragged.
            coord (tuple): Destination coordinates (x, y)
            options (dict): Key-value pairs which contains optional
                parameters to uiautomator.Device, such as steps
        """
        self._find(locator).drag.to(*coord, **options)

    def drag_object_to_object(self, locator, other_locator, options):
        """Drag a UI object onto another UI object

        Dragged UI object, and destination UI object are each
        specified by the locator.
        Args:
            locator (object): Locator object to locate the UI object
                which is to be dragged.
            other_locator (object): Locator object to locate the destination
                UI object.
            options (dict): Key-value pairs which contains optional
                parameters to uiautomator.Device, such as steps
        """
        drag_kwargs = dict(other_locator.filters)
        drag_kwargs.update(options)
        self._find(locator).drag.to(**drag_kwargs)

    def swipe_object(self, locator, direction, options):
        """Swipe a UI object which is specified by the locator.

        Args:
            locator (object): Locator object to locate the UI object
            direction (string): 'right', 'left, 'up' or 'down'
            options (dict): Key-value pairs which contains optional
                parameters to uiautomator.Device, such as steps
        """
        self._find(locator).swipe(direction, **options)

    def pinch(self, locator, in_or_out, options):
        """Pinch a UI object which is specified by the locator.

        Args:
            locator (object): Locator object to locate the UI object
            in_or_out (string): 'In' which means edge-to-center,
                or 'Out' which means center-to-edge.
            options (dict): Key-value pairs which contains optional
                parameters to uiautomator.Device, such as steps
        """
        pinch_method = getattr(self._find(locator).pinch, in_or_out)
        pinch_method(**options)

    def fling(self, locator, orientation, action, options):
        """Fling a UI object which is specified by the locator

        Args:
            locator (object): Locator object to locate the UI object
            orientation (string): 'horiz' or 'vert'
            action (string): 'forward', 'barckword', 'toBeginning' or 'toEnd'
            options (dict): Key-value pairs which contains optional
                parameters to uiautomator.Device, such as steps
        """
        fling_method = getattr(
            getattr(self._find(locator).fling, orientation), action)
        fling_method(**options)

    def scroll(self, locator, orientation, action, options):
        """Scroll a UI object which is specified by the locator

        Args:
            locator (object): Locator object to locate the UI object
            orientation (string): 'horiz' or 'vert'
            action (string):
                'forward', 'barckword', 'toBeginning', 'toEnd' or 'to'
                When 'to' is given, the UI object is scrolled until
                an inner UI object which is specified in options parameter
                becomes visible.
            options (dict): Key-value pairs which contains optional
                parameters to uiautomator.Device, such as steps.
                When action is 'to', options must contain key-value pairs
                which is enough to identify the destination UI object.
        """
        scroll_method = getattr(
            getattr(self._find(locator).scroll, orientation), action)
        scroll_method(**options)

    def press_key(self, key_name, meta):
        """Press a key

        Args:
            key_name (text): Name of the key, such as 'APP_SWITCH' and 'ENTER',
                or 'a' and '0'. See keecode.py.
            meta (integer): Meta-key code such as 1(SHIFT), 2(ALT).

        See Also:
            `Android KeyEvent`_ for key code and meta key code.

        .. _Android KeyEvent:
            http://developer.android.com/reference/android/view/KeyEvent.html

        """
        key_code = keycode.get_keycode(key_name)
        self._device.press(key_code, meta)

    def open_notification(self):
        """Open notification"""
        self._device.open.notification()

    def open_quick_settings(self):
        """Open quick settings"""
        self._device.open.quick_settings()

    def click_xy(self, coord):
        """Click on the screen at coordinates (x, y)

        Args:
            coord (tuple): Coordinates (x, y)
        """
        self._device.click(*coord)

    def long_click_xy(self, coord):
        """Long-click on the screen at coordinates (x, y)

        Args:
            coord (tuple): Coordinates (x, y)
        """
        self._device.long_click(*coord)

    def drag_xy_to_xy(self, start, end, options):
        """Drag from start coordinates (xS, yS) to end coordinates (xE, yE)

        Args:
            start (tuple): Start point coordinates (xS, yS)
            end (tuple): End point coordinates (xE, yE)
            options (dict): optional key-value pairs, such as {'steps': 100}.
        """
        coords = start + end
        self._device.drag(*coords, **options)

    def swipe(self, start, end, options):
        """Swipe from start coordinates (xS, yS) to end coordinates (xE, yE)

        Args:
            start (tuple): Start point coordinates (xS, yS)
            end (tuple): End point coordinates (xE, yE)
            options (dict): optional key-value pairs, such as {'steps': 100}.
        """
        coords = start + end
        self._device.swipe(*coords, **options)

    def set_orientation(self, orientation):
        """Fix the device's orientation to a state such as 'left'

        Args:
            orientation (string):
                'natural', 'left', 'right', 'upsidedown' or 'unfreeze'.
                When 'unfreeze' is given, the effect of
                previous `set_orientation` is cancelled.
        """
        if orientation == 'unfreeze':
            self._device.freeze_rotation(freeze=False)
        else:
            self._device.orientation = orientation

    def get_info(self, locator):
        """Returns information of a UI object specified by the locator

        Args:
            locator (object): Locator to locate a UI object

        Returns:
            dict: the UI object's meta information such as
                text, contentDescription, bounds and visibleBounds.
        """
        return dict(self._find(locator).info)
