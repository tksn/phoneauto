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
