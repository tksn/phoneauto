# -*- coding: utf-8 -*-
"""String expression generator for device manipulation

:copyright: (c) 2015 by tksn
:license: MIT
"""

from __future__ import unicode_literals
from . import keycode


def _quote(text):
    """Enclose the string with quotation characters"""
    return '\'{0}\''.format(text)


def _quote_if_str(value):
    """Enclose the string with quotation characters if the value is a str"""
    return (_quote(value)
            if isinstance(value, type(u'')) or isinstance(value, type(b''))
            else str(value))


def _make_method_call_string(method_name, *args, **kwargs):
    """Make a method call code fragment string"""
    all_args = [_quote_if_str(a) for a in args]
    all_args.extend(
        '{0}={1}'.format(k, _quote_if_str(v)) for k, v in kwargs.items())
    all_args_str = ', '.join(all_args)
    return '{0}({1})'.format(method_name, all_args_str)


def _make_instance_string(locator):
    """Make a instance code fragment string"""
    method_call_str = _make_method_call_string('{instance}', **locator.filters)
    method_call_str += ('' if locator.index is None
                        else '[{0}]'.format(locator.index))
    return method_call_str


class UiautomatorCoder(object):
    """Code fragment generator for generating device manipulation code
    using uiautomator
    """

    def __init__(self):
        """Initialize coder object"""
        pass

    @staticmethod
    def get_device_open_code(device_name=None):
        """Returns a code fragment to open the device

        Args:
            device_name (string): device name (serial number) of the device
        Returns:
            list: list of code lines to open the device
        """
        device_name = _quote(device_name) if device_name else ''
        lines = [
            'import uiautomator',
            ('from phoneauto.helpers.uiautomator_notfound_handlers '
             'import install_standard_handlers'),
            ('from phoneauto.helpers.uiautomator_device_wrapper '
             'import DeviceWrapper'),
            'device = DeviceWrapper(uiautomator.Device({0}))'.format(
                device_name),
            'install_standard_handlers(device)',
            'return device'
            ]
        return lines

    @staticmethod
    def get_device_close_code(_):
        """Returns a code fragment to close the device

        Args:
            _ (string): Unused instance name of the object to be closed
        Returns:
            list: list of code lines to close the device
        """
        return ['pass']

    @staticmethod
    def get_code_set_text(locator, text):
        """Returns a code fragment which performs set_text

        Args:
            locator (object): Locator to locate the target UI object.
            text (string): The text which is set to the target UI object.
        Returns:
            string: Code fragment string
        """
        return '{0}.set_text({1})'.format(
            _make_instance_string(locator), _quote(text))

    @staticmethod
    def get_code_clear_text(locator):
        """Returns a code fragment which performs clear_text

        Args:
            locator (object): Locator to locate the target UI object.
        Returns:
            string: Code fragment string
        """
        return '{0}.clear_text()'.format(_make_instance_string(locator))

    @staticmethod
    def get_code_click_object(locator, wait):
        """Returns a code fragment which performs click_object

        Args:
            locator (object): Locator to locate the target UI object.
            wait (int): Duration in milliseconds to wait for updating
                after click, or None if no-wait.
        Returns:
            string: Code fragment string
        """
        if wait is None:
            method_str = 'click()'
        else:
            method_str = _make_method_call_string('click.wait', timeout=wait)
        return '{0}.{1}'.format(_make_instance_string(locator), method_str)

    @staticmethod
    def get_code_long_click_object(locator):
        """Returns a code fragment which performs long_click_object

        Args:
            locator (object): Locator to locate the target UI object.
        Returns:
            string: Code fragment string
        """
        return '{0}.long_click()'.format(_make_instance_string(locator))

    @staticmethod
    def get_code_drag_object_to_xy(locator, coord, options):
        """Returns a code fragment which performs drag_object_to_xy

        Args:
            locator (object): Locator to locate the target UI object.
            coord (tuple): Destination coordinates (x, y)
            options (dict): Dictionary contains optional parameters
                such as steps.
        Returns:
            string: Code fragment string
        """
        return '{0}.{1}'.format(
            _make_instance_string(locator),
            _make_method_call_string('drag.to', *coord, **options))

    @staticmethod
    def get_code_drag_object_to_object(locator, other_locator, options):
        """Returns a code fragment which performs drag_object_to_object

        Args:
            locator (object): Locator to locate the target UI object.
            other_locator (object): Destination locator
            options (dict): Dictionary contains optional parameters
                such as steps.
        Returns:
            string: Code fragment string
        """
        drag_kwargs = dict(other_locator.filters)
        drag_kwargs.update(options)
        return '{0}.{1}'.format(
            _make_instance_string(locator),
            _make_method_call_string('drag.to', **drag_kwargs))

    @staticmethod
    def get_code_swipe_object(locator, direction, options):
        """Returns a code fragment which performs swipe_object

        Args:
            locator (object): Locator to locate the target UI object.
            direction (string): 'right', 'left, 'up' or 'down'
            options (dict): Dictionary contains optional parameters
                such as steps.
        Returns:
            string: Code fragment string
        """
        return '{0}.{1}'.format(
            _make_instance_string(locator),
            _make_method_call_string('swipe', direction, **options))

    @staticmethod
    def get_code_pinch(locator, in_or_out, options):
        """Returns a code fragment which performs pinch

        Args:
            locator (object): Locator to locate the target UI object.
            in_or_out (string): 'In' or 'Out'
            options (dict): Dictionary contains optional parameters
                such as steps.
        Returns:
            string: Code fragment string
        """
        return '{0}.{1}'.format(
            _make_instance_string(locator),
            _make_method_call_string('pinch.{0}'.format(in_or_out), **options))

    @staticmethod
    def get_code_fling(locator, orientation, action, options):
        """Returns a code fragment which performs fling

        Args:
            locator (object): Locator to locate the target UI object.
            orientation (string): 'horiz' or 'vert'
            action (string): 'forward', 'barckword', 'toBeginning' or 'toEnd'
            options (dict): Dictionary contains optional parameters
                such as steps.
        Returns:
            string: Code fragment string
        """
        return '{0}.{1}'.format(
            _make_instance_string(locator),
            _make_method_call_string(
                'fling.{0}.{1}'.format(orientation, action), **options))

    @staticmethod
    def get_code_scroll(locator, orientation, action, options):
        """Returns a code fragment which performs scroll

        Args:
            locator (object): Locator to locate the target UI object.
            orientation (string): 'horiz' or 'vert'
            action (string): 'forward', 'barckword', 'toBeginning',
                'toEnd' or 'to'
            options (dict): Dictionary contains optional parameters
                such as steps.
        Returns:
            string: Code fragment string
        """
        return '{0}.{1}'.format(
            _make_instance_string(locator),
            _make_method_call_string(
                'scroll.{0}.{1}'.format(orientation, action), **options))

    @staticmethod
    def get_code_press_key(key_name, meta):
        """Returns a code fragment which performs press_key

        Args:
            key_name (text): Name of the key, such as 'APP_SWITCH' and 'ENTER',
                or 'a' and '0'. See keecode.py.
            meta (integer): Meta-key code such as 1(SHIFT), 2(ALT).
        Returns:
            string: Code fragment string
        """
        key_code = keycode.get_keycode(key_name)
        return '{{instance}}.press({0}, {1}){2}'.format(
            key_code, meta, ('  # ' + key_name) if key_name else '')

    @staticmethod
    def get_code_open_notification():
        """Returns a code fragment which performs open_notification

        Returns:
            string: Code fragment string
        """
        return '{instance}.open.notification()'

    @staticmethod
    def get_code_open_quick_settings():
        """Returns a code fragment which performs open_quick_settings

        Returns:
            string: Code fragment string
        """
        return '{instance}.open.quick_settings()'

    @staticmethod
    def get_code_click_xy(coord):
        """Returns a code fragment which performs click_xy

        Args:
            coord (tuple): Coordinates (x, y)
        Returns:
            string: Code fragment string
        """
        return '{{instance}}.click({0}, {1})'.format(*coord)

    @staticmethod
    def get_code_long_click_xy(coord):
        """Returns a code fragment which performs long_click_xy

        Args:
            coord (tuple): Coordinates (x, y)
        Returns:
            string: Code fragment string
        """
        return '{{instance}}.long_click({0}, {1})'.format(*coord)

    @staticmethod
    def get_code_drag_xy_to_xy(start, end, options):
        """Returns a code fragment which performs drag_xy_to_xy

        Args:
            start (tuple): Start point coordinates (xS, yS)
            end (tuple): End point coordinates (xE, yE)
            options (dict): optional key-value pairs, such as steps=100.
        Returns:
            string: Code fragment string
        """
        coords = start + end
        return '{{instance}}.{0}'.format(
            _make_method_call_string('drag', *coords, **options))

    @staticmethod
    def get_code_swipe(start, end, options):
        """Returns a code fragment which performs swipe

        Args:
            start (tuple): Start point coordinates (xS, yS)
            end (tuple): End point coordinates (xE, yE)
            options (dict): optional key-value pairs, such as steps=100.
        Returns:
            string: Code fragment string
        """
        coords = start + end
        return '{{instance}}.{0}'.format(
            _make_method_call_string('swipe', *coords, **options))

    @staticmethod
    def get_code_set_orientation(orientation):
        """Returns a code fragment which performs set_orientation

        Args:
            orientation (string):
                'natural', 'left', 'right', 'upsidedown' or 'unfreeze'.
        Returns:
            string: Code fragment string
        """
        if orientation == 'unfreeze':
            return '{instance}.freeze_rotation(freeze=False)'
        else:
            return '{{instance}}.orientation = {0}'.format(_quote(orientation))

    @staticmethod
    def get_code_screenshot(file):
        """Returns a code fragment which performs screenshot capture

        Args:
            file (string): file path to the output image file
        Returns:
            string: Code fragment string
        """
        return '{{instance}}.screenshot({0})'.format(file)

    @staticmethod
    def get_code_wait(for_what, timeout):
        """Returns a code fragment which performs screen state wait operation

        Args:
            for_what (string): Wait subject. One of 'update' or 'idle'.
            timeout (int): Maximam wait duration in milliseconds.
                uiautomator's default is used if None.
        Returns:
            string: Code fragment string
        """
        options = {} if timeout is None else {'timeout': timeout}
        return '{{instance}}.{0}'.format(
            _make_method_call_string('wait.{0}'.format(for_what), **options))

    @staticmethod
    def get_code_wait_object(locator, for_what, timeout):
        """Returns a code fragment which performs object state wait operation

        Args:
            locator (object): Locator to locate the target UI object
            for_what (string): Wait subject. One of 'gone' or 'exists'.
            timeout (int): Maximam wait duration in milliseconds.
                uiautomator's default is used if None.
        Returns:
            string: Code fragment string
        """
        options = {} if timeout is None else {'timeout': timeout}
        return '{0}.{1}'.format(
            _make_instance_string(locator),
            _make_method_call_string('wait.{0}'.format(for_what), **options))
