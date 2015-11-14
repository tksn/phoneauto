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


def test_cancel_hold_time(mocks):
    ui = create_scriptgenerator_ui()
    ui._hold_timer_id = 1
    ui._root = MagicMock()
    canvas = MagicMock
    ui._root.return_value = canvas
    canvas.after_cancel = MagicMock()

    ui._cancel_hold_timer()
    canvas.after_cancel.assert_called_once_with(1)
    assert ui._hold_timer_id is None

