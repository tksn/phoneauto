# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import PIL.Image
from mock import MagicMock, create_autospec
import uiautomator

_SCREEN_WIDTH = 64
_SCREEN_HEIGHT = 64


def install(monkeypatch):
    DeviceMock = create_autospec(uiautomator.Device)
    device = DeviceMock()
    device.server = MagicMock()
    device.server.start = MagicMock()
    device.screenshot.return_value=True

    screen_img = PIL.Image.new(
        mode='RGB', size=(_SCREEN_WIDTH, _SCREEN_HEIGHT))
    orig_img_open = PIL.Image.open
    def img_open_dispatch(*args, **kwargs):
        if isinstance(args[0], type('')):
            return screen_img
        return orig_img_open(*args, **kwargs)
    img_open = MagicMock(side_effect=img_open_dispatch)
    monkeypatch.setattr('uiautomator.Device', lambda _: device)
    monkeypatch.setattr('PIL.Image.open', img_open)
    return device


def bounds(t, l, b, r):
    return {'top': t, 'left': l, 'bottom': b, 'right': r}


def uia_element_info(**kwvalues):
    elem = {
        'visibleBounds': bounds(0, 0, _SCREEN_HEIGHT, _SCREEN_WIDTH),
        'resourceName': '',
        'contentDescription': '',
        'text': '',
        'className': ''
    }
    elem.update(kwvalues)
    return elem

# class Selector(object):
#
#     def __init__(self, **kwargs):
#         pass
#
#     def send_keys(self, keys):
#         pass
#
#     def click(self):
#         pass
#
#     def long_click(self):
#         pass
#
#     @property
#     def drag(self):
#         class Drag(object):
#             def to(self, x, y, steps):
#                 pass
#         return Drag()
#
#
# class Device(object):
#
#     def __init__(self, device_serial=None):
#         self._device_serial = device_serial or 'dummy-device'
#         self.screenshot = MagicMock(return_value=True)
#         self.click = MagicMock()
#
#     def device_serial(self):
#         return self._device_serial
#
#     def __call__(self, **kwargs):
#         return []
#
#     def press(self, keycode):
#         pass
#
#     def long_click(self, x, y):
#         pass
#
#     def swipe(self, x0, y0, x1, y1, steps):
#         pass
#
#     def drag(self, x0, y0, x1, y1, steps):
#         pass
#
