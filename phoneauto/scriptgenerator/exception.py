# -*- coding: utf-8 -*-
"""Exceptions

:copyright: (c) 2015 by tksn
:license: MIT
"""

from __future__ import unicode_literals


class ScriptGeneratorError(Exception):
    """Common exception base """

    def __init__(self, message):
        """Initialize exception object"""
        super(ScriptGeneratorError, self).__init__()
        self.message = message

    def __str__(self):
        """String representation of the exception"""
        return 'ScriptGeneratorError: ' + self.message


class UiInconsitencyError(Exception):
    """Common exception base """

    def __init__(self, message):
        """Initialize exception object"""
        super(UiInconsitencyError, self).__init__(message)


class UiObjectNotFound(ScriptGeneratorError):
    """Exception raised when the UI object is not found on the screen"""

    def __init__(self, message):
        """Initialize exception object"""
        super(UiObjectNotFound, self).__init__(message)
