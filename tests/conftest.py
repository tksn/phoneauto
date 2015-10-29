# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest


def pytest_addoption(parser):
    parser.addoption('--use_real_device',
                     action='store_true',
                     help='use real emulator/devices')
