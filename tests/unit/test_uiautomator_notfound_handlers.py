# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import call
import pytest
from tests.uiautomator_mock import uia_element_info
from phoneauto.helpers.uiautomator_notfound_handlers import *


def test_install_standard_handlers(mocks):
    install_standard_handlers(mocks.device)
    assert mocks.device.handlers.on.mock_calls == [
        call(handle_anr), call(handle_appcrash)
    ]


def uiobj(*args, **kwargs):
    class _Object(object): pass
    o = _Object()
    o.info = uia_element_info(*args, **kwargs)
    return o


def test_handle_anr_no_message_found(mocks):
    mocks.device.return_value = None
    handle_anr(mocks.device)


def test_handle_anr_anr_occured(mocks):
    mocks.device.return_value = uiobj(text='ABC isn\'t responding')
    with pytest.raises(ANRException):
        handle_anr(mocks.device)


def test_handle_anr_no_anr(mocks):
    mocks.device.return_value = uiobj(text='ABC is doing good')
    handle_anr(mocks.device)


def test_handle_appcrash_no_message_found(mocks):
    mocks.device.return_value = None
    handle_appcrash(mocks.device)


def test_handle_appcrash_appcrash_occured(mocks):
    mocks.device.return_value = uiobj(text='Unfortunately, ')
    with pytest.raises(AppCrashException):
        handle_appcrash(mocks.device)


def test_handle_appcrash_no_appcrash(mocks):
    mocks.device.return_value = uiobj(text='Good')
    handle_appcrash(mocks.device)
