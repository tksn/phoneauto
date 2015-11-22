# -*- coding: utf-8 -*-
"""notfound_handlers: handler functions/objects

:copyright: (c) 2015 by tksn
:license: MIT
"""

from __future__ import unicode_literals


class UnexpectedUIStateException(Exception):
    """Base exception class for unexpected UI state"""

    def __init__(self, message):
        """Initialization"""
        super(UnexpectedUIStateException, self).__init__(self)
        self.message = message


class ANRException(UnexpectedUIStateException):
    """Application Not Responded"""

    def __init__(self, message):
        """Initialization"""
        super(ANRException, self).__init__(message)


class AppCrashException(UnexpectedUIStateException):
    """Application Crash"""

    def __init__(self, message):
        """Initialization"""
        super(AppCrashException, self).__init__(message)


def handle_anr(device):
    """ANR handler"""
    message = device(packageName='android', resourceId='android:id/message')
    if message:
        text = message.info['text']
        if 'isn\'t responding' in text:
            raise ANRException('ANR occurred')


def handle_appcrash(device):
    """App Crash handler"""
    message = device(packageName='android', resourceId='android:id/message')
    if message:
        text = message.info['text']
        if 'Unfortunately' in text:
            raise AppCrashException('App Crash occurred')


def install_standard_handlers(device):
    """Installs standard handlers for Unexpected UI State exceptions"""
    device.handlers.on(handle_anr)
    device.handlers.on(handle_appcrash)
