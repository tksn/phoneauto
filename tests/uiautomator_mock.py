# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import PIL.Image
from mock import MagicMock, Mock, create_autospec
import uiautomator

_SCREEN_WIDTH = 64
_SCREEN_HEIGHT = 64


def install(monkeypatch):
    DeviceMock = create_autospec(uiautomator.Device)
    device = DeviceMock()
    device.server = MagicMock()
    device.server.start = MagicMock()
    device.screenshot.return_value=True

    dummy_img = PIL.Image.new(
        mode='RGB', size=(_SCREEN_WIDTH, _SCREEN_HEIGHT))
    dummy_img.save = Mock()
    orig_img_open = PIL.Image.open
    def img_open_dispatch(*args, **kwargs):
        if isinstance(args[0], type('')):
            return dummy_img
        return orig_img_open(*args, **kwargs)
    img_open = MagicMock(side_effect=img_open_dispatch)
    monkeypatch.setattr('PIL.Image.open', img_open)

    monkeypatch.setattr('uiautomator.Device', lambda _: device)
    return (device, dummy_img)


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
