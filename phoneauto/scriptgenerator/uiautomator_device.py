# -*- coding: utf-8 -*-
"""Interfaces to devices

:copyright: (c) 2015 by tksn
:license: MIT
"""
# pylint: disable=invalid-name

from __future__ import unicode_literals
import math
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

    def click(self, record=_null_record):
        """Clicks on this element on the device"""
        self._impl.click()
        record('{0}.click()'.format(self))

    def long_click(self, record=_null_record):
        """Long-clicks on this element on the device"""
        self._impl.long_click()
        record('{0}.long_click()'.format(self))

    def drag_to_xy(self, x, y, record=_null_record, **options):
        """Drags this object to (x, y)

        Args:
            x (integer): Destination coordinate x
            y (integer): Destination coordinate y
            options (dict): Keyword arguments passed to uiautomator's drag.to
        """
        self._impl.drag.to(x, y, **options)
        method_name = '{0}.drag.to'.format(self)
        record(_build_method_call_str(method_name, *(x, y), **options))

    def drag_to_object(self, other, record=_null_record, **options):
        """Drags this object to another object

        Args:
            other (object): Destination object
            options (dict): Keyword arguments passed to uiautomator's drag.to
        """
        drag_kwargs = dict(other.selector_kwargs)
        drag_kwargs.update(options)
        self._impl.drag.to(**drag_kwargs)
        method_call_str = _build_method_call_str(
            '{0}.drag.to'.format(self),
            *other.selector_args, **drag_kwargs)
        record(method_call_str)

    def swipe(self, direction, record=_null_record, **options):
        """Swipes this object to the specified direction

        Args:
            direction: 'right', 'left', 'up' or 'down'
            options (dict): Keyword arguments passed to uiautomator's swipe
        """
        self._impl.swipe(direction, **options)
        method_call_str = _build_method_call_str(
            '{0}.swipe'.format(self), direction, **options)
        record(method_call_str)

    def pinch(self, in_or_out, record=_null_record, **options):
        """Performs pinch-in/out operation on this object

        Args:
            in_or_out (text): 'In' or 'Out'
            options (dict): Keyword arguments passed to uiautomator's pinch
        """
        call_method = getattr(self._impl.pinch, in_or_out)
        call_method(**options)
        method_call_str = _build_method_call_str(
            '{0}.pinch.{1}'.format(self, in_or_out), **options)
        record(method_call_str)

    def fling(self, orientation, action, record=_null_record, **kwargs):
        """Performs fling action on a scrollable element on the device

        Args:
            orientation (text): 'horizontal' or 'vertical'
            action (text): 'forward', 'backward', 'toBeginning' or 'toEnd'
            kwargs (dict): Keyword arguments passed to uiautomator's fling
        """
        call_method = getattr(getattr(self._impl.fling, orientation), action)
        call_method(**kwargs)
        method_name = '{0}.fling.{1}.{2}'.format(self, orientation, action)
        record(_build_method_call_str(method_name, **kwargs))

    def scroll(self, orientation, action, record=_null_record, **kwargs):
        """Performs scroll action on a scrollable element on the device

        Args:
            orientation (text): 'horizontal' or 'vertical'
            action (text):
                'forward', 'backward', 'toBeginning', 'toEnd' or 'to'
            kwargs (dict): Keyword arguments passed to uiautomator's scroll
        """
        call_method = getattr(getattr(self._impl.scroll, orientation), action)
        call_method(**kwargs)
        method_name = '{0}.scroll.{1}.{2}'.format(self, orientation, action)
        record(_build_method_call_str(method_name, **kwargs))


class UiautomatorDevice(object):
    """Device class"""

    _FIND_ELEMENT_DISTANCE_THRESH = 200

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

    def find_element_contains(self, coord, **criteria):
        """Finds the element which contains given coordinate and
        meets given criteria

        Args:
            coord (tuple): coordinate (x, y)
            criteria (dict): criteria ex)clickable=True, enabled=True
        Returns:
            element (object): UI element object
        """
        uia_criteria = dict(criteria)
        ignore_distant_element = uia_criteria.pop(
            'ignore_distant_element', True)
        element = self._get_element_contains(coord, uia_criteria,
                                             ignore_distant_element)
        if not element:
            return None
        return self._create_element_obj(element, uia_criteria)

    def _get_element_contains(self, coord, criteria,
                              ignore_distant_element):
        """Returns the information of element which contains given
        coordinate and meets given criteria
        """
        T, L, B, R = 'top', 'left', 'bottom', 'right'
        x, y = coord

        def xy_in_rect(r):
            """Check xy is in rect r"""
            if x < r[L] or r[R] <= x or y < r[T] or r[B] <= y:
                return False
            if ignore_distant_element:
                r_x, r_y = r[L] + (r[R] - r[L]) / 2, r[T] + (r[B] - r[T]) / 2
                distance = math.hypot(x - r_x, y - r_y)
                return distance < self._FIND_ELEMENT_DISTANCE_THRESH
            return True

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
        uielement = self.find_element_contains(
            coord, className='android.widget.EditText')
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

    def click_xy(self, coord, record=_null_record):
        """Clicks on a coordinate

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        self._device.click(*coord)
        record('{{instance}}.click({0}, {1})'.format(*coord))

    def click_object(self, coord, record=_null_record):
        """Clicks on a object which contains the specified coordinate

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        uielement = self.find_element_contains(coord,
                                               clickable=True, enabled=True)
        uielement.click(record=record)

    def long_click_xy(self, coord, record=_null_record):
        """Long-clicks on a coordinate

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        self._device.long_click(*coord)
        record('{{instance}}.long_click({0}, {1})'.format(*coord))

    def long_click_object(self, coord, record=_null_record):
        """Long-clicks on a object which contains the specified coordinate

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        uielement = self.find_element_contains(coord,
                                               longClickable=True,
                                               enabled=True)
        if uielement is not None:
            uielement.long_click(record=record)

    def drag_xy_to_xy(self, start, end, record=_null_record, **options):
        """Performs drag action from start point to end point

        Args:
            start (tuple): Start point coordinate (xS, yS)
            end (tuple): End point coordinate (xE, yE)
            record (function): optional record() for generating a script
            options (dict): optional key-value pairs.  ex)steps=100
        """
        (xS, yS), (xE, yE) = start, end
        self._device.drag(xS, yS, xE, yE, **options)
        record(_build_swipe_drag_str('drag', xS, yS, xE, yE, **options))

    def drag_object_to_xy(self, start, end,
                          record=_null_record, **options):
        """Drags an object which locates 'start'
        to other location which coordinates are 'end'

        Args:
            start (tuple): The coordinate (xS, yS) of the object to drag
            end (tuple): End point coordinate (xE, yE)
            record (function): optional record() for generating a script
            options (dict): optional key-value pairs.  ex)steps=100
        """
        uielementS = self.find_element_contains(start)
        if uielementS is not None:
            uielementS.drag_to_xy(*end, record=record, **options)

    def drag_object_to_object(self, start, end,
                              record=_null_record, **options):
        """Drags an object which locates 'start'
        onto another object which locates 'end'

        Args:
            start (tuple): The coordinate (xS, yS) of the object to drag
            end (tuple): The coordinate (xS, yS) of the destination object
            record (function): optional record() for generating a script
            options (dict): optional key-value pairs.  ex)steps=100
        """
        uielementS = self.find_element_contains(start)
        if uielementS is not None:
            uielementE = self.find_element_contains(end)
            if uielementE is not None:
                uielementS.drag_to_object(uielementE, record=record, **options)

    def swipe(self, start, end, record=_null_record, **options):
        """Performs swipe action from start point to end point

        Args:
            start (tuple): Start point coordinate (xS, yS)
            end (tuple): End point coordinate (xE, yE)
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        (xS, yS), (xE, yE) = start, end
        self._device.swipe(xS, yS, xE, yE, **options)
        record(_build_swipe_drag_str('swipe', xS, yS, xE, yE, **options))

    def swipe_object(self, start, direction, record=_null_record, **options):
        """Swipes an object which locates 'start'
         to the specified direction

        Args:
            start (tuple): Start point coordinate (xS, yS)
            direction (text): 'right', 'left', 'up' or 'down'
            record (function): optional record() for generating a script
            options (dict): optional key-value pairs.  ex)steps=100
        """
        uielement = self.find_element_contains(start,
                                               scrollable=True,
                                               ignore_distant_element=False)
        if uielement is not None:
            uielement.swipe(direction, record=record, **options)

    def pinch(self, in_or_out, coord, percent, record=_null_record, **options):
        """Performs pinch action on the object locates on coord

        Args:
            in_or_out (text):
                'In': Pinch-in (edge to center pinch)
                'Out': Pinch-in (center to edge pinch)
            coord (tuple):
                (x, y) coordinate which is contained in the object
            percent (integer):
                percentage of the element's diagonal length
                for the pinch gesture
            record (function): optional record() for generating a script
            options (dict): optional key-value pairs.  ex)steps=100
        """
        uielement = self.find_element_contains(
            coord, className='android.view.View', enabled=True)
        if uielement is not None:
            kwargs = dict(options)
            kwargs.update({'percent': percent})
            uielement.pinch(in_or_out, record=record, **kwargs)

    def fling(self, start, orientation, action,
              record=_null_record, **options):
        """Performs fling action on a scrollable object

        Args:
            start (tuple):
                The coordinates (x, y) of the scrollable object
            orientation (text):
                'horizontal' or 'vertical'
            action (text):
                'forward', 'backward', 'toBeginning' or 'toEnd'
            record (function): optional record() for generating a script
            options (dict): optional key-value pairs.  ex)steps=100
        """
        uielement = self.find_element_contains(start,
                                               scrollable=True,
                                               ignore_distant_element=False)
        if uielement is not None:
            uielement.fling(orientation, action, record=record, **options)

    def scroll(self, start, orientation, action,
               record=_null_record, **options):
        """Performs scroll action on a scrollable object

        Args:
            start (tuple):
                The coordinates (x, y) of the scrollable object
            orientation (text):
                'horizontal' or 'vertical'
            action (text):
                'forward', 'backward', 'toBeginning' or 'toEnd'
            record (function): optional record() for generating a script
            options (dict): optional key-value pairs.  ex)steps=100
        """
        uielement = self.find_element_contains(start,
                                               scrollable=True,
                                               ignore_distant_element=False)
        if uielement is not None:
            uielement.scroll(orientation, action, record=record, **options)

    def scroll_to(self, start, orientation, target_selector_kwargs,
                  record=_null_record, **options):
        """Scroll until the item determined by target_selector_kwargs
        is displayed

        Args:
            start (tuple):
                The coordinates (x, y) of the scrollable object
            orientation (text):
                'horizontal' or 'vertical'
            target_selector_kwargs (dict):
                dict which contain key-value pairs to locate the target.
                ex) {'text': 'Lock screen'}
            record (function): optional record() for generating a script
            options (dict): optional key-value pairs.  ex)steps=100
        """
        uielement = self.find_element_contains(start,
                                               scrollable=True,
                                               ignore_distant_element=False)
        if uielement is not None:
            scroll_kwargs = dict(target_selector_kwargs)
            scroll_kwargs.update(options)
            uielement.scroll(orientation, 'to', record=record, **scroll_kwargs)
