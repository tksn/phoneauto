# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest
from mock import MagicMock
from phoneauto.scriptgenerator import scriptgenerator


def create_scriptgenerator():
    d = MagicMock()
    d.get_screenshot_as_file = MagicMock()
    w = MagicMock()
    return scriptgenerator.ScriptGenerator([d], w)


def test_get_screenshot(mocks):
    g = create_scriptgenerator()
    g.devices[0].get_screenshot_as_file.return_value = False
    assert g.get_screenshot() is None


def test_swipe_object_with_horiz_direction(mocks):
    g = create_scriptgenerator()
    g.swipe_object_with_direction({
        'start': (0, 0), 'end': (0, 30)
    })
    call_args = g.devices[0].swipe_object.call_args
    args, kwargs = call_args
    assert (0, 0) in args
    assert 'down' in args
