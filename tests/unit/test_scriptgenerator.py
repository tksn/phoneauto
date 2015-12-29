# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from mock import Mock
from phoneauto.scriptgenerator import scriptgenerator


def create_scriptgenerator():
    d = Mock()
    d.get_screenshot_as_file = Mock()
    f = Mock()
    f.find_object_contains = Mock()
    conf = {
        'devices': [d],
        'coder': Mock(),
        'finder': f,
        'writer': Mock()
    }
    return scriptgenerator.ScriptGenerator(conf)


def test_get_screenshot():
    g = create_scriptgenerator()
    g.devices[0].get_screenshot_as_file.return_value = False
    assert g.execute('get_screenshot') is None


def test_swipe_object_with_horiz_direction():
    g = create_scriptgenerator()
    g.execute('swipe_object_with_direction', {
        'start': (0, 0), 'end': (0, 30)
    })
    _, findobj_kwargs = g.finder.find_object_contains.call_args
    _, swipe_kwargs = g.devices[0].swipe_object.call_args
    assert findobj_kwargs['coord'] == (0, 0)
    assert swipe_kwargs['direction'] == 'down'
