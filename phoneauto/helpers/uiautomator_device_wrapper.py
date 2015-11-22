# -*- coding: utf-8 -*-
"""A wrapper provides extra functionalities to uiautomator.Device

:copyright: (c) 2015 by tksn
:license: MIT
"""

from __future__ import unicode_literals


class DeviceWrapper(object):
    """uiautomator.Device wrapper

    Calls wait.idle before click, press, etc.
    Calls wait.update after click, press, etc.
    """

    def __init__(self,
                 uiauto_device,
                 idle_timeout=5000,
                 update_timeout=1000):
        """Initialization

        Args:
            uiauto_device (object): uiautomator.Device instance
            idle_timeout (integer): timeout for wait.idle in milliseconds
            update_timeout (integer): timeout for wait.update in milliseconds
        """
        self.__dict__['_device'] = uiauto_device
        self.__dict__['_wait_idle_timeout'] = idle_timeout
        self.__dict__['_wait_update_timeout'] = update_timeout

    def pre_exec(self):
        """Procedure before click/press etc"""
        self._device.wait.idle(timeout=self._wait_idle_timeout)

    def post_exec(self):
        """Procedure after click/press etc"""
        self._device.wait.update(timeout=self._wait_update_timeout)
        self._device.wait.idle(timeout=self._wait_idle_timeout)

    def __call__(self, **kwargs):
        """Delegates to uiautomator.Device.__call__"""
        return self._device.__call__(**kwargs)

    def __getattr__(self, name):
        """Replaces return value of attribute get
        to wrapper objects for some attributes"""
        attr = getattr(self._device, name)

        wrap_methods = [
            'click', 'long_click', 'swipe', 'swipePoints',
            'drag', 'clear_traversed_text', 'wakeup', 'sleep']

        def _wrap_exec(*args, **kwargs):
            """wrap function for click/long_click/etc"""
            self.pre_exec()
            attr(*args, **kwargs)
            self.post_exec()

        if name in wrap_methods:
            return _wrap_exec

        wrap_properties = [
            'open', 'press', 'screen'
        ]

        class _Wrap(object):
            """property wrapper"""
            # pylint: disable=no-self-argument
            # pylint: disable=too-few-public-methods

            def __init__(wrap_self, prop_inst):
                """Initialization"""
                wrap_self._prop_inst = prop_inst

            def __call__(wrap_self, *args, **kwargs):
                """Delegation method __call__"""
                self.pre_exec()
                wrap_self._prop_inst.__call__(*args, **kwargs)
                self.post_exec()

            def __eq__(wrap_self, value):
                """Delegation method __eq__"""
                return wrap_self._prop_inst.__eq__(value)

            def __ne__(wrap_self, value):
                """Delegation method __ne__"""
                return wrap_self._prop_inst.__ne__(value)

            def __getattr__(wrap_self, name):
                """Replaces return value of some attribute get
                to wrapper function"""
                attr = getattr(wrap_self._prop_inst, name)

                def _wrap_exec(*args, **kwargs):
                    """wrapper function for screen.on/off etc"""
                    self.pre_exec()
                    attr(*args, **kwargs)
                    self.post_exec()

                return _wrap_exec

        if name in wrap_properties:
            return _Wrap(attr)

        return attr

    def __setattr__(self, name, value):
        """Inserts pre_exec/post_exec precedures before/after
        attributes set call for some attributes"""

        wrap_attrs = ['orientation']

        if name in wrap_attrs:
            self.pre_exec()
            setattr(self._device, name, value)
            self.post_exec()
        else:
            setattr(self._device, name, value)
