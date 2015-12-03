# -*- coding: utf-8 -*-
"""Interfaces to devices

:copyright: (c) 2015 by tksn
:license: MIT
"""
# pylint: disable=invalid-name

from __future__ import unicode_literals
import uiautomator
from . import keycode
from . import uiobjectfinder
from . import view_hierarchy_dump


def _quote(text):
    """Encloses the string with quotation characters"""
    return '\'{0}\''.format(text)


def _quote_if_str(value):
    """Encloses the string with quotation characters if the value is a str"""
    return (_quote(value)
            if isinstance(value, type(u'')) or isinstance(value, type(b''))
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

    @property
    def info(self):
        """Information of this UI element"""
        return self._impl.info

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

    def set_text(self, text, record=_null_record):
        """Sets text

        Args:
            text: Characters to be sent to the device
        """
        self._impl.set_text(text)
        record('{0}.set_text({1})'.format(self, _quote(text)))

    def clear_text(self, record=_null_record):
        """Clears text"""
        self._impl.clear_text()
        record('{0}.clear_text()'.format(self))

    def click(self, wait=None, record=_null_record):
        """Clicks on this element on the device"""
        if wait is None:
            self._impl.click()
            method_str = 'click()'
        else:
            self._impl.click.wait(timeout=wait)
            method_str = _build_method_call_str('click.wait', timeout=wait)
        record('{0}.{1}'.format(self, method_str))

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


def create_uielem(find_result):
    uielem = UiElement(find_result['object'], **find_result['locator'])
    index = find_result.get('index')
    if index is not None:
        uielem = uielem.set_index(index)
    return uielem


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
        self._objfinder = uiobjectfinder.UiObjectFinder(self._device)
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
        """Gives a code fragment to close the device

        Args:
            instance_name (text): instance name of the object to be closed
        Returns:
            list: list of code lines to close the device
        """
        return ['pass']

    def update_view_hierarchy_dump(self):
        """Update view hierarchy dump"""
        dump_str = self._device.dump()
        hierarchy_dump = view_hierarchy_dump.ViewHierarchyDump(
            self._device.info, dump_str)
        self._objfinder.set_hierarchy_dump(hierarchy_dump)

    def invalidate_view_hierarchy_dump(self):
        """Invalidate existing view hierarchy dump
        in order to mark it is obsolete"""
        self._objfinder.set_hierarchy_dump(None)

    def get_screenshot_as_file(self, file_path):
        """Aquires screenshot from the device and save it as a file

        Args:
            file_path (text): save file path
        """
        return self._device.screenshot(file_path)

    @staticmethod
    def set_text(uielement, keys, record=_null_record):
        """Sends characters to the UI element

        Args:
            uielement (object): Target UI element
            keys: Characters to be sent
            record (function): optional record() for generating a script
        """
        uielement.set_text(keys, record=record)

    def find_send_keys(self, coord, keys, record=_null_record):
        """Find the best method to send the keys and executes sending

        Args:
            coord (tuple): The target's coordinate (x, y)
            keys (text): The keys to be sent
            record (function): optional record() for generating a script
        """
        try:
            uielement = create_uielem(
                self._objfinder.find_object_contains(
                    coord, True, className='android.widget.EditText'))
            self.set_text(uielement, keys, record=record)
        except uiobjectfinder.UiObjectNotFound:
            for k in self._chars_to_keys(keys):
                self.press_key(k[0], meta=k[1], record=record)

    def clear_text(self, coord, record=_null_record):
        """Clears text in a EditText object on a object
        which contains the specified coordinate

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        uielement = create_uielem(
            self._objfinder.find_object_contains(
                coord, True, className='android.widget.EditText'))
        uielement.clear_text(record=record)

    def press_key(self, key_name, meta=None, record=_null_record):
        """Press the key specified

        Args:
            key_name (text): the name of the key. ex)HOME, BACK, etc.
            record (function): optional record() for generating a script
        """
        kc = keycode.get_keycode(key_name)
        self._device.press(kc, meta)
        record(
            '{{instance}}.press({0}, {1})  # {2}'.format(kc, meta, key_name))

    def open_notification(self, record=_null_record):
        """Opens notification

        Args:
            record (function): optional record() for generating a script
        """
        self._device.open.notification()
        record('{instance}.open.notification()')

    def open_quick_settings(self, record=_null_record):
        """Opens quick settings

        Args:
            record (function): optional record() for generating a script
        """
        self._device.open.quick_settings()
        record('{instance}.open.quick_settings()')

    def click_xy(self, coord, record=_null_record):
        """Clicks on a coordinate

        Args:
            coord (tuple): Coordinate (x, y)
            record (function): optional record() for generating a script
        """
        self._device.click(*coord)
        record('{{instance}}.click({0}, {1})'.format(*coord))

    def click_object(self, coord, wait=None, record=_null_record):
        """Clicks on a object which contains the specified coordinate

        Args:
            coord (tuple): Coordinate (x, y)
            wait (integer): wait timeout in milliseconds. None means no-wait
            record (function): optional record() for generating a script
        """
        uielement = create_uielem(
            self._objfinder.find_object_contains(
                coord, True, clickable=True, enabled=True))
        uielement.click(wait=wait, record=record)

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
        uielement = create_uielem(
            self._objfinder.find_object_contains(
                coord, True, longClickable=True, enabled=True))
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
        uielementS = create_uielem(
            self._objfinder.find_object_contains(start, True))
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
        uielementS = create_uielem(
            self._objfinder.find_object_contains(start, True))
        uielementE = create_uielem(
            self._objfinder.find_object_contains(end, True))
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
        uielement = create_uielem(
            self._objfinder.find_object_contains(
                start, False, scrollable=True))
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
        uielement = create_uielem(
            self._objfinder.find_object_contains(
                coord, True, className='android.view.View', enabled=True))
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
        uielement = create_uielem(
            self._objfinder.find_object_contains(
                start, False, scrollable=True))
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
        uielement = create_uielem(
            self._objfinder.find_object_contains(
                start, False, scrollable=True))
        uielement.scroll(orientation, action, record=record, **options)

    def scroll_to(self, start, orientation,
                  record=_null_record, **kwargs):
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
            kwargs (dict):
                dict which contain key-value pairs to locate the target.
                ex) {'text': 'Lock screen'}
        """
        uielement = create_uielem(
            self._objfinder.find_object_contains(
                start, False, scrollable=True))
        uielement.scroll(orientation, 'to', record=record, **kwargs)

    def get_info(self, start, criteria):
        """Returns UI object inforamtion

        Args:
            start (tuple):
                the coordinates of the UI object's location
            criteria (dict):
                a dictionary which contains search criteria
                (see python uiautomator's document)
        Returns:
            dict: UI object's information
        """
        uielement = create_uielem(
            self._objfinder.find_object_contains(start, True, **criteria))
        return dict(uielement.info)

    def set_orientation(self, orientation, record=_null_record):
        """Sets the device's orientation

        Args:
            orientation (string):
                'natural', 'left', 'right', 'upsidedown' or 'unfreeze'
            record (function): optional record() for generating a script
        """
        if orientation == 'unfreeze':
            self._device.freeze_rotation(freeze=False)
            record('{instance}.freeze_rotation(freeze=False)')
        else:
            self._device.orientation = orientation
            record(
                '{{instance}}.orientation = {0}'.format(_quote(orientation)))

    @staticmethod
    def record_screenshot_capture(file, record):
        """Records screenshot_capture code string

        Args:
            file (string):
                file path or expression that yields file path
            record (function): record function for generating a script
        """
        format_str = '{{instance}}.screenshot({0})'
        record(format_str.format(file))

    @staticmethod
    def record_wait(for_what, timeout, record):
        """Records wait code string

        Args:
            for_what (string): 'idle' or 'update'
            timeout (integer): timeout in msec
            record (function): record function for generating a script
        """
        options = {}
        if timeout is not None:
            options['timeout'] = timeout
        mstr = _build_method_call_str('wait.{0}'.format(for_what), **options)
        record('{{instance}}.{0}'.format(mstr))

    def record_wait_object(self, start, for_what, timeout, record):
        """Records wait-object code string

        Args:
            start (tuple): (x, y) coordinates on which the object locates
            for_what (string): 'exists' or 'gone'
            timeout (integer): timeout in msec
            record (function): record function for generating a script
        """
        uielement = create_uielem(
            self._objfinder.find_object_contains(
                start, True, enabled=True))
        options = {}
        if timeout is not None:
            options['timeout'] = timeout
        record(_build_method_call_str(
            '{0}.wait.{1}'.format(uielement, for_what), **options))
