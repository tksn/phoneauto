# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest
from mock import MagicMock
from phoneauto.scriptgenerator import scriptgenerator_ui


def create_scriptgenerator_ui():
    ui = scriptgenerator_ui.ScriptGeneratorUI()
    ui._controller = MagicMock()
    return ui


def test_acquire_screen(mocks):
    ui = create_scriptgenerator_ui()
    ui._controller.get_screenshot = MagicMock()
    ui._controller.get_screenshot.return_value = None
    with pytest.raises(RuntimeError):
        ui._acquire_screen()
