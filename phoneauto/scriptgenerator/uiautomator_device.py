# -*- coding: utf-8 -*-
"""Interfaces to devices

:copyright: (c) 2015 by tksn
:license: MIT
"""
# pylint: disable=invalid-name

from __future__ import unicode_literals
import sys
import uiautomator
from . import keycode


def _quote(text):
    """Encloses the string with quotation characters"""
    return '\'{0}\''.format(text)


def _quote_if_str(value):
    """Encloses the string with quotation characters if the value is a str"""
    return (_quote(value) if isinstance(value, type(''))
            else str(value))


def _build_method_call_str(method_name, *args, **kwargs):
    """Makes a method call code fragment string"""
    all_args = [_quote_if_str(a) for a in args]
    all_args.extend(
        '{0}={1}'.format(k, _quote_if_str(v)) for k, v in kwargs.items())
    all_args_str = ', '.join(all_args)
    return '{0}({1})'.format(method_name, all_args_str)


def _build_swipe_drag_str(method_str, *args, **kwargs):
    """Makes a code fragment string which executes Swipe/Drag action"""
    return '{instance}.' + _build_method_call_str(method_str, *args, **kwargs)


def _null_record(_):
    """Dumb record function """
    pass


class UiElement(object):
    """UI element class"""

    def __init__(self, element, *selector_args, **selector_kwargs):
        """Initialization

        Args:
            element (object):
                A selector object
                (return value of uiautomator's Device.__call__)
            selector_args (list):
                arguments which are used to select this element
            selector_kwargs (dict):
                keyword arguments which are used to select this element
        """
        self._impl = element
        self._args = selector_args
        self._kwargs = selector_kwargs
        self._index = None

    @property
    def selector_args(self):
        """args used to create selector"""
        return self._args

    @property
    def selector_kwargs(self):
        """kwargs used to create selector"""
        return self._kwargs

    def set_index(self, index):
        """Set index of this element in the collection of elements
        by the same selector args/kwargs

        Args:
            index (integer):
                index of this element in the collection of elements
                found by the same selector args/kwargs
        Returns:
            UiElement: self
        """
        self._index = index
        return self

    def __str__(self):
        """Gives a code fragment string

        Returns:
            text: A code fragment string to get this element,
                which can be used in generated script.
        """
        method_call_str = _build_method_call_str(
            '{instance}', *self.selector_args, **self.selector_kwargs)
        if self._index is not None:
            method_call_str += '[{0}]'.format(self._index)
        return method_call_str

    def send_keys(self, keys):
        """Sends keys to this element on the device

        Args:
            keys: Characters to be sent to the device
        """
        self._impl.set_text(keys)

    def click(self):
        """Clicks on this element on the device"""
        self._impl.click()

    def long_click(self):
        """Long-clicks on this element on the device"""
        self._impl.long_click()

    def swipe(self, direction, **kwargs):
        """Performs swipe operation on this element on the device

        Args:
            direction: 'right', 'left', 'up' or 'down'
            kwargs (dict): Keyword arguments passed to uiautomator's swipe
        """
        self._impl.swipe(direction, **kwargs)

    def drag_to(self, *args, **kwargs):
        """Performs drag and drop operation on this element on the device

        Args:
            args (list): Arguments passed to uiautomator's drag.to
            kwargs (dict): Keyword arguments passed to uiautomator's drag.to
        """
        self._impl.drag.to(*args, **kwargs)

    def pinch_in(self, **kwargs):
        """Performs pinch-in operation on this element on the device

        Args:
            kwargs (dict): Keyword arguments passed to uiautomator's pinch.In
        """
        self._impl.pinch.In(**kwargs)

    def pinch_out(self, **kwargs):
        """Performs pinch-out operation on this element on the device

        Args:
            kwargs (dict): Keyword arguments passed to uiautomator's pinch.Out
        """
        self._impl.pinch.Out(**kwargs)


class UiautomatorDevice(object):
    """Device class"""

    def __init__(self, device_name=None):
        """Initialization

        Args:
            device_name (text): device name (serial number) of the device
                (what you see in adb devices outputs)
        """
        self._device = uiautomator.Device(device_name)
        self._device.server.start()  # to make sure jsonrpc is running
        self._chars_to_keys = keycode.chars_to_keys_us

    def close(self):
        """Closes device"""
        self._device = None

    @property
    def device_name(self):
        """The device's name (serial number)"""
        return self._device.server.adb.device_serial()

    @staticmethod
    def get_device_open_code(device_name=None):
        """Gives a code fragment to open the device

        Args:
            device_name (text): device name (serial number) of the device
        Returns:
            list: list of code lines to open the device
        """
        device_name = _quote(device_name) if device_name else ''
        lines = [
            'import uiautomator',
            'return uiautomator.Device({0})'.format(device_name)
            ]
        return lines

    @staticmethod
    def get_device_close_code(_):
        """Gives a code fragment to close the device

        Args:
            instance_name (text): instance name of the object to be closed
        Returns:
            list: list of code lines to close the device
        """
        return ['pass']

    def find_clickable_element_contains(self, coord):
        """Finds the clickable element which contains given coordinate

        Args:
            coord (tuple): coordinate (x, y)
        Returns:
            element (object): UI element object
        """
        criteria = {'clickable': True, 'enabled': True}
        return self.find_element_contains(coord, **criteria)

    def find_long_clickable_element_contains(self, coord):
        """Finds the long-clickable element which contains given coordinate

        Args:
            coord (tuple): coordinate (x, y)
        Returns:
            element (object): UI element object
        """
        criteria = {'longClickable': True, 'enabled': True}
        return self.find_element_contains(coord, **criteria)

    def find_class_element_contains(self, coord, class_name):
        """Finds the element which contains given coordinate and class name

        Args:
            coord (tuple): coordinate (x, y)
        Returns:
            element (object): UI element object
        """
        criteria = {'className': class_name}
        return self.find_element_contains(coord, **criteria)

    def find_element_contains(self, coord, **criteria):
        """Finds the element which contains given coordinate and
        meets given criteria

        Args:
            coord (tuple): coordinate (x, y)
            criteria (dict): criteria ex)clickable=True, enabled=True
        Returns:
            element (object): UI element object
        """
        element = self._get_element_contains(coord, criteria)
        if not element:
            return None
        return self._create_element_obj(element, criteria)

    def _get_element_contains(self, coord, criteria):
        """Returns the information of element which contains given
        coordinate and meets given criteria
        """
        T, L, B, R = 'top', 'left', 'bottom', 'right'
        x, y = coord

        def xy_in_rect(r):
            """Check xy is in rect r"""
            return r[L] <= x < r[R] and r[T] <= y < r[B]

        def rect_area(r):
            """Returns area of rect r"""
            return (r[B] - r[T]) * (r[R] - r[L])

        uia_elements = self._device(**criteria)
        min_element = (sys.maxsize, )
        for i, uia_element in enumerate(uia_elements):
            info = uia_element.info
            rect = info['visibleBounds']
            area = rect_area(rect)
            if xy_in_rect(rect) and area < min_element[0]:
                min_element = (area, uia_element, info, i)
        return min_element[1:]

    def _create_element_obj(self, element, criteria):
        """Determines locator and creates UI element object"""
        uia_element, element_info, index = element

        # uses resource_id if it's available and unique
        resource_id = element_info['resourceName']
        if resource_id:
            uia_elements = self._device(resourceId=resource_id)
            if len(uia_elements) == 1:
                return UiElement(uia_element, resourceId=resource_id)

        # uses content-desc if it's available
        content_desc = element_info['contentDescription']
        if content_desc:
            return UiElement(uia_element, description=content_desc)

        # uses text if it's available
        if element_info['text']:
            return UiElement(uia_element, text=element_info['text'])

        # uses criteria which is what used for this element-finding
        return UiElement(uia_element, **criteria).set_index(index)

    def get_screenshot_as_file(self, file_path):
        """Aquires screenshot from the device and save it as a file

        Args:
            file_path (text): save file path
        """
        return self._device.screenshot(file_path)

    @staticmethod
    def str_get_screenshot_as_file(file_path):
        """Returns code fragment for screenshot aquisition

        See Also: get_screenshot_as_file
        """
        format_str = '{{instance}}.get_screenshot_as_file({0})'
        return format_str.format(_quote(file_path))

    @staticmethod
    def send_keys(uielement, keys, record=_null_record):
        """Sends characters to the UI element

        Args:
            uielement (object): Target UI element
            keys: Characters to be sent
            record (function): optional record() for generating a script
        """
        uielement.send_keys(keys)
        record('{0}.set_text({1})'.format(uielement, _quote(keys)))

    def find_send_keys(self, coord, keys, record=_null_record):
        """Find the best method to send the keys and executes sending

        Args:
            coord (tuple): The target's coordinate (x, y)
            keys (text): The keys to be sent
            record (function): optional record() for generating a script
        """
        uielement = self.find_class_element_contains(
            coord, class_name='android.widget.EditText')
        if uielement is None:
            for k in self._chars_to_keys(keys):
                self.press_key(k[0], meta=k[1], record=record)
        else:
            self.send_keys(uielement, keys, record=record)

    def press_key(self, key_name, meta=None, record=_null_record):
        """Press the key specified

        Args:
            key_name (text): the name of the key. ex)HOME, BACK, etc.
            record (function): optional record() for generating a script
        """
        kc = keycode.get_keycode(key_name)
        self._device.press(kc, meta)
        record('{{instance}}.press({0}, {1})'.format(kc, meta))

    def click(self, coord, record=_null_record):
        """Clicks on the coordinate specified

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        self._device.click(*coord)
        record('{{instance}}.click({0}, {1})'.format(*coord))

    @staticmethod
    def click_element(uielement, record=_null_record):
        """Clicks on the UI element specified

        Args:
            uielement (object): The target UI element object
            record (function): optional record() for generating a script
        """
        uielement.click()
        record('{0}.click()'.format(uielement))

    def find_click(self, coord, record=_null_record):
        """Find the best method to click on the coordinate and executes click

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        uielement = self.find_clickable_element_contains(coord)
        if uielement is None:
            self.click(coord, record=record)
        else:
            self.click_element(uielement, record=record)

    def long_click(self, coord, record=_null_record):
        """Long-clicks on the coordinate specified

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        self._device.long_click(*coord)
        record('{{instance}}.long_click({0}, {1})'.format(*coord))

    @staticmethod
    def long_click_element(uielement, record=_null_record):
        """Long-clicks on the UI element specified

        Args:
            uielement (object): The target UI element object
            record (function): optional record() for generating a script
        """
        uielement.long_click()
        record('{0}.long_click()'.format(uielement))

    def find_long_click(self, coord, record=_null_record):
        """Find the best method to long-click on the coordinate and
        executes long-click

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        uielement = self.find_long_clickable_element_contains(coord)
        if uielement is None:
            self.long_click(coord, record=record)
        else:
            self.long_click_element(uielement, record=record)

    def swipe(self, start, end, record=_null_record, **kwargs):
        """Performs swipe action from start point to end point

        Args:
            start (tuple): Start point coordinate (xS, yS)
            end (tuple): End point coordinate (xE, yE)
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        (xS, yS), (xE, yE) = start, end
        self._device.swipe(xS, yS, xE, yE, **kwargs)
        record(_build_swipe_drag_str('swipe', xS, yS, xE, yE, **kwargs))

    @staticmethod
    def swipe_element(uielement, direction,
                      record=_null_record, **kwargs):
        """Performs swipe action on the UI element

        Args:
            uielement (object): the object to swipe
            direct (text): swipe direction ('right', 'left', 'up', 'down')
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        uielement.swipe(direction, **kwargs)
        method_call_str = _build_method_call_str(
            '{0}.swipe'.format(uielement), direction, **kwargs)
        record(method_call_str)

    def find_swipe(self, start, end, record=_null_record, **kwargs):
        """Finds the best method to swipe the ui element specified by
        its coordinate, then executes the swipe.

        Args:
            start (tuple): Start point coordinate (x, y)
            end (tuple): End point coordinate (x, y)
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        uielement = self.find_element_contains(start)
        if uielement is None:
            self.swipe(start, end, record=record, **kwargs)
        else:
            xdiff, ydiff = end[0] - start[0], end[1] - start[1]
            if abs(xdiff) > abs(ydiff):
                direction = 'right' if xdiff >= 0 else 'left'
            else:
                direction = 'down' if ydiff >= 0 else 'up'
            self.swipe_element(uielement, direction, record=record, **kwargs)

    @staticmethod
    def drag_element(uielement, end, record=_null_record, **kwargs):
        """Performs drag action on the UI element to the end point

        Args:
            uielement (object): the object to drag
            end (tuple): End point coordinate (xE, yE)
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        xE, yE = end
        uielement.drag_to(xE, yE, **kwargs)
        method_call_str = _build_method_call_str(
            '{0}.drag.to'.format(uielement), xE, yE, **kwargs)
        record(method_call_str)

    @staticmethod
    def drag_element_to_element(uielementS, uielementE,
                                record=_null_record, **kwargs):
        """Drags an UI element oto another UI element

        Args:
            uielementS (object): the object to drag
            uielementE (object): destination element
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        drag_kwargs = dict(uielementE.selector_kwargs)
        drag_kwargs.update(kwargs)
        uielementS.drag_to(*uielementE.selector_args, **drag_kwargs)
        method_call_str = _build_method_call_str(
            '{0}.drag.to'.format(uielementS),
            *uielementE.selector_args, **drag_kwargs)
        record(method_call_str)

    def find_drag(self, start, end, find_target_element=False,
                  record=_null_record, **kwargs):
        """Finds the best method to drag the ui element specified by
        its coordinate, then executes the drag.

        Args:
            start (tuple): Start point coordinate (x, y)
            end (tuple): End point coordinate (x, y)
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        uielementS = self.find_element_contains(start)
        if uielementS is None:
            self.swipe(start, end, record=record, **kwargs)
        elif not find_target_element:
            self.drag_element(uielementS, end, record=record, **kwargs)
        else:
            uielementE = self.find_element_contains(end)
            if uielementE is None:
                self.drag_element(uielementS, end, record=record, **kwargs)
            else:
                self.drag_element_to_element(
                    uielementS, uielementE, record=record, **kwargs)

    def pinch_in(self, coord, percent, record=_null_record, **kwargs):
        """Performs pinch-in(edge-to-center) touch action

        Args:
            coord (tuple):
                (x, y) coordinate which is contained in the ui element
            percent (integer):
                percentage of the element's diagonal length
                for the pinch gesture
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        uielement = self.find_element_contains(
            coord, className='android.view.View', enabled=True)
        if uielement is not None:
            kwargs.update({'percent': percent})
            uielement.pinch_in(**kwargs)
            mthcall_str = _build_method_call_str('pinch.In', **kwargs)
            record('{0}.{1}'.format(uielement, mthcall_str))

    def pinch_out(self, coord, percent, record=_null_record, **kwargs):
        """Performs pinch-out(center-to-edge) touch action

        Args:
            coord (tuple):
                (x, y) coordinate which is contained in the ui element
            percent (integer):
                percentage of the element's diagonal length
                for the pinch gesture
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        uielement = self.find_element_contains(
            coord, className='android.view.View', enabled=True)
        if uielement is not None:
            kwargs.update({'percent': percent})
            uielement.pinch_out(**kwargs)
            mthcall_str = _build_method_call_str('pinch.Out', **kwargs)
            record('{0}.{1}'.format(uielement, mthcall_str))
