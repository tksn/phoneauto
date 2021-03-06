# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest


@pytest.fixture(autouse=True)
def mocks(request, monkeypatch):
    from tests import tkinter_mock
    from tests import uiautomator_mock
    from tests import screenrecord_mock

    class Mocks(object): pass

    m = Mocks()
    m.uiroot = tkinter_mock.install(monkeypatch)
    m.screenrecord = screenrecord_mock.install(monkeypatch)

    if not request.config.getoption('--use_real_device'):
        m.device, m.dummy_img = uiautomator_mock.install(monkeypatch)
    return m
