# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest
from mock import Mock, patch
from phoneauto.scriptgenerator import scriptgenerator_ui


def create_scriptgenerator_ui():
    ui = scriptgenerator_ui.ScriptGeneratorUI()
    ui._controller = Mock()
    return ui


def test_acquire_screen(mocks):
    ui = create_scriptgenerator_ui()
    ui._controller.get_screenshot = Mock()
    ui._controller.get_screenshot.return_value = None
    with pytest.raises(RuntimeError):
        ui._acquire_screen()


def test_take_screenshot_cancel(mocks):
    ui = create_scriptgenerator_ui()
    with patch.object(
            scriptgenerator_ui.get_filedialog(),
            'asksaveasfilename', return_value=''):
        ui._take_screenshot()

