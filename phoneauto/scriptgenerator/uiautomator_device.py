# -*- coding: utf-8 -*-
"""Interfaces to devices

:copyright: (c) 2015 by tksn
:license: MIT
"""
# pylint: disable=invalid-name

from __future__ import unicode_literals
import sys
import uiautomator


def _quote(text):
    """Encloses the string with quotation characters"""
    return '\'{0}\''.format(text)


def _build_swipe_drag_str(method_str, *args, **kwargs):
    """Makes a code fragment string which executes Swipe/Drag action"""
    fmt_str = '{0}({1}, {2}'
    fmt_str += ', {3}, {4}' if len(args) > 2 else ''
    text = fmt_str.format(method_str, *args)
    steps = kwargs.get('steps')
    text += ', steps={0})'.format(steps) if steps else ')'
    return '{instance}.' + text


def _null_record(_):
    """Dumb record function """
    pass


class UiautomatorUiElement(object):
    """UI element class"""

    def __init__(self, element, find_element_str):
        """Initialization

        Args:
            element (object):
                A selector object
                (return value of uiautomator's Device.__call__)
            find_element_str (text):
                A code fragment string which can be used in generated script
                in order to find this element.
        """
        self._impl = element
        self._find_element_str = find_element_str

    def __str__(self):
        """Gives a code fragment string

        Returns:
            text: A code fragment string which can be used in generated script
                in order to find this element.
        """
        return self._find_element_str

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

    def drag_to(self, *args, **kwargs):
        """Performs drag and drop operation on this element on the device

        Args:
            args (list): Arguments contains coordinate values
                args[0] (integer): Horizontal coordinate of drag destination
                args[1] (integer): Vertical coordinate of drag destination
            kwargs (dict): Keyword arguments
                passed to uiautomator.Device.drag.to()
        """
        x, y = args[0:2]
        self._impl.drag.to(x, y, **kwargs)


class UiautomatorDevice(object):
    """Device class"""

    KEYCODE = {
        'KEYCODE_0': 7,
        'KEYCODE_9': 16,
        'KEYCODE_A': 29,
        'KEYCODE_Z': 54,
        'HOME': 3,
        'BACK': 4,
        'APP_SWITCH': 187
    }

    def __init__(self, device_name=None):
        """Initialization

        Args:
            device_name (text): device name (serial number) of the device
                (what you see in adb devices outputs)
        """
        self._device = uiautomator.Device(device_name)

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

        def _create(args_str, index_str=''):
            """Creates UI element object"""
            str_expr = '{{instance}}({0}){1}'.format(args_str, index_str)
            return UiautomatorUiElement(uia_element, str_expr)

        # uses resource_id if it's available and unique
        resource_id = element_info['resourceName']
        if resource_id:
            uia_elements = self._device(resourceId=resource_id)
            if len(uia_elements) == 1:
                return _create('resourceId={0}'.format(_quote(resource_id)))

        # uses content-desc if it's available
        content_desc = element_info['contentDescription']
        if content_desc:
            return _create('description={0}'.format(_quote(content_desc)))

        # uses text if it's available
        if element_info['text']:
            return _create('text={0}'.format(_quote(element_info['text'])))

        # uses criteria which is what used for this element-finding
        criteria_str_list = []
        for k, v in criteria.items():
            val = _quote(v) if isinstance(type(v), type('')) else v
            criteria_str_list.append('{0}={1}'.format(k, val))
        args_str = ', '.join(criteria_str_list)
        return _create(args_str, '[{0}]'.format(index))

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

    def send_keys(self, uielement, keys, record=_null_record):
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
            return
        else:
            self.send_keys(uielement, keys, record=record)

    def press_key(self, key_name, record=_null_record):
        """Press the key specified

        Args:
            key_name (text): the name of the key. ex)HOME, BACK, etc.
            record (function): optional record() for generating a script
        """
        self._device.press(self.KEYCODE[key_name])
        format_str = '{{instance}}.press({0})'
        record(format_str.format(self.KEYCODE[key_name]))

    def click(self, coord, record=_null_record):
        """Clicks on the coordinate specified

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        self._device.click(*coord)
        record('{{instance}}.click({0}, {1})'.format(*coord))

    def click_element(self, uielement, record=_null_record):
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

    def long_click_element(self, uielement, record=_null_record):
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

    def drag(self, start, end, record=_null_record, **kwargs):
        """Performs drag action from start point to end point

        Args:
            start (tuple): Start point coordinate (xS, yS)
            end (tuple): End point coordinate (xE, yE)
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        (xS, yS), (xE, yE) = start, end
        self._device.drag(xS, yS, xE, yE, **kwargs)
        record(_build_swipe_drag_str('drag', xS, yS, xE, yE, **kwargs))

    def drag_element(self, uielement, end, record=_null_record, **kwargs):
        """Performs drag action on the UI element to the end point

        Args:
            uielement (object): the object to drag
            end (tuple): End point coordinate (xE, yE)
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        xE, yE = end
        uielement.drag_to(xE, yE, **kwargs)
        fmt_str = _build_swipe_drag_str('drag.to', xE, yE, **kwargs)
        record(fmt_str.format(instance=uielement))

    def find_drag(self, start, end, record=_null_record, **kwargs):
        """Find the best method to drag on the coordinate and
        executes drag

        Args:
            start (tuple): Start point coordinate (x, y)
            end (tuple): End point coordinate (x, y)
            record (function): optional record() for generating a script
            kwargs (dict): optional key-value pairs.  ex)steps=100
        """
        uielement = self.find_long_clickable_element_contains(start)
        if uielement is None:
            self.drag(start, end, record=record, **kwargs)
        else:
            self.drag_element(uielement, end, record=record, **kwargs)
