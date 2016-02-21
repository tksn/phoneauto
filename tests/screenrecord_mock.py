# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from mock import Mock
import PIL

_SCREEN_WIDTH = 64
_SCREEN_HEIGHT = 64

def install(monkeypatch):
    m = Mock()
    m_class = Mock()
    m_class.return_value = m

    dummy_img = PIL.Image.new(
        mode='RGB', size=(_SCREEN_WIDTH, _SCREEN_HEIGHT))
    m.capture_oneshot.return_value = dummy_img

    monkeypatch.setattr(
        'phoneauto.scriptgenerator.screenrecord.Screenrecord', m_class)
    monkeypatch.setattr(
        'phoneauto.scriptgenerator.scriptgenerator_ui.Screenrecord', m_class)
    return m
