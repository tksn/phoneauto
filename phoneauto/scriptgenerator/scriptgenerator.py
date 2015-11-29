# -*- coding: utf-8 -*-
"""Script generating controller

:copyright: (c) 2015 by tksn
:license: MIT
"""
# pylint: disable=invalid-name

from __future__ import unicode_literals
import os
import tempfile
import uuid

from PIL import Image


class ScriptGenerator(object):
    """Script generation controller class"""

    def __init__(self, devices, writer):
        """Initialization

        Args:
            devices (iterable):
                An iterable object which contains device object instances.
            writer (object):
                An writer object which is used to generate a automation script
        """
        self.devices = devices
        self.writer = writer

    def update_view_dump(self, device_index=0):
        self.devices[device_index].update_view_hierarchy_dump()

    def get_screenshot(self, device_index=0):
        """Gets device's screenshot

        Args:
            device_index (integer):
                The index of the device from which a screenshot is taken
        Returns:
            PIL.Image: A screenshot image object if succeeded, otherwise, None.
        """
        file_path = os.path.join(tempfile.gettempdir(),
                                 'tmp_{0}.png'.format(uuid.uuid4()))
        success = self.devices[device_index].get_screenshot_as_file(file_path)
        if not success:
            return None
        return Image.open(file_path)

    def press_key(self, command_args, device_index=0):
        """Presses a key of the device

        Args:
            command_args['key_name'] (text):
                key name  ex) 'HOME', 'BACK' etc.
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].press_key(
            command_args['key_name'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def open_notification(self, _, device_index=0):
        """Opens notification panel

        Args:
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].open_notification(
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def open_quick_settings(self, _, device_index=0):
        """Opens Quick Settings panel

        Args:
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].open_quick_settings(
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def clear_text(self, command_args, device_index=0):
        """Clears text on the target UI object

        Args:
            command_args['start'] (tuple):
                Coordinate (x, y) of the target object
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].clear_text(
            command_args['start'],
            record=self.writer.get_recorder(device_index))

    def enter_text(self, command_args, device_index=0):
        """Sets text to the target UI object

        Args:
            command_args['start'] (tuple):
                Coordinate (x, y) of the target object
            command_args['text'] (text):
                characters which are sent to the target object
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].find_send_keys(
            command_args['start'], command_args['text'],
            record=self.writer.get_recorder(device_index))

    def click_xy(self, command_args, device_index=0):
        """Clicks on a pixel

        Args:
            command_args['start'] (tuple):
                Coordinate (x, y) of the target pixel
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].click_xy(
            command_args['start'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def click_object(self, command_args, device_index=0):
        """Clicks on a UI object

        Args:
            command_args['start'] (tuple):
                Coordinate (x, y) of a pixel which is contained
                in the target object
            command_args['wait'] (boolean):
                True if perform 'click and wait update', False otherwise
            command_args['timeout'] (integer):
                timeout for wait in milliseconds. not used when no wait
            device_index (integer):
                The index of the device
        """
        wait = None
        if command_args.get('wait', False):
            wait = {}
            timeout = command_args.get('timeout')
            if timeout is not None:
                wait['timeout'] = timeout
        self.devices[device_index].click_object(
            command_args['start'], wait,
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def long_click_xy(self, command_args, device_index=0):
        """Long-clicks on a pixel

        Args:
            command_args['start'] (tuple):
                Coordinate (x, y) of the target pixel
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].long_click_xy(
            command_args['start'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def long_click_object(self, command_args, device_index=0):
        """Long-clicks on a UI object

        Args:
            command_args['start'] (tuple):
                Coordinate (x, y) of the target UI object
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].long_click_object(
            command_args['start'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def drag_xy_to_xy(self, command_args, device_index=0):
        """Performs drag-and-drop action with specifying
        start and end point coordinates

        Args:
            command_args['start'] (tuple):
                Start point coordinate (x, y) of the drag action
            command_args['end'] (tuple):
                End point coordinate (x, y) of the drag action
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].drag_xy_to_xy(
            command_args['start'], command_args['end'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def drag_object_to_xy(self, command_args, device_index=0):
        """Performs drag-and-drop action with specifying
        a start UI object and an end point coordinate

        Args:
            command_args['start'] (tuple):
                The coordinate (x, y) of the UI element to drag
            command_args['end'] (tuple):
                The coordinate (x, y) on which the drag action ends
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].drag_object_to_xy(
            command_args['start'], command_args['end'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def drag_object_to_object(self, command_args, device_index=0):
        """Performs drag-and-drop action with specifying
        a start and an destination UI object

        Args:
            command_args['start'] (tuple):
                The coordinate (x, y) of the UI element to drag
            command_args['end'] (tuple):
                The coordinate (x, y) of the destination UI element
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].drag_object_to_object(
            command_args['start'], command_args['end'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def swipe_xy_to_xy(self, command_args, device_index=0):
        """Performs swipe action with specifying
        start and end point coordinates

        Args:
            command_args['start'] (tuple):
                Start point coordinate (x, y) of the swipe action
            command_args['end'] (tuple):
                End point coordinate (x, y) of the swipe action
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].swipe(
            command_args['start'], command_args['end'], steps=10,
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def swipe_object_with_direction(self, command_args, device_index=0):
        """Swipes a UI object toward specified direction

        Args:
            command_args['start'] (tuple):
                Start ui element's  coordinate (x, y)
            command_args['end'] (tuple):
                Destination coordinate (x, y) which is used to
                determine swipe direction
            device_index (integer):
                The index of the device
        """
        start, end = command_args['start'], command_args['end']
        xdiff, ydiff = end[0] - start[0], end[1] - start[1]
        if abs(xdiff) > abs(ydiff):
            direction = 'right' if xdiff >= 0 else 'left'
        else:
            direction = 'down' if ydiff >= 0 else 'up'
        self.devices[device_index].swipe_object(
            start, direction,
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def pinch(self, command_args, device_index=0):
        """Performs pinch-in(edge-to-center)/pinch-out(center-to-edge) action

        Args:
            command_args['in_or_out'] (tuple):
                'In'(edge-to-center) or 'Out'(center-to-edge)
            command_args['start'] (tuple):
                coordinate (x, y) of the UI object which is to pinch-in'ed
            command_args['percent'] (integer):
                percentage of the element's diagonal length
                for the pinch gesture
            command_args['steps'] (integer):
                the number of steps for the gesture.
                Steps are injected about 5 milliseconds apart,
                so 100 steps may take around 0.5 seconds to complete.
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].pinch(
            command_args['in_or_out'], command_args['start'],
            command_args['percent'], steps=command_args['steps'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    @staticmethod
    def _fling_scroll_args(start, end, to_end):
        """Prepares scroll/fling arguments (orientatin and action)"""
        xdiff, ydiff = end[0] - start[0], end[1] - start[1]
        args_dict = {}
        args_dict['start'] = start
        if abs(xdiff) > abs(ydiff):
            args_dict['orientation'] = 'horiz'
            diff = xdiff
        else:
            args_dict['orientation'] = 'vert'
            diff = ydiff
        forward = 'toEnd' if to_end else 'forward'
        backward = 'toBeginning' if to_end else 'backward'
        args_dict['action'] = backward if diff >= 0 else forward
        return args_dict

    def fling(self, command_args, device_index=0):
        """Performs fling action on a scrollable UI object

        Args:
            command_args['start'] (tuple):
                coordinate (x, y) which is contained in
                the scrollable UI object
            command_args['end'] (integer):
                coordinate (x, y) which is used to determine fling direction
            device_index (integer):
                The index of the device
        """
        args = self._fling_scroll_args(
            command_args['start'], command_args['end'], False)
        self.devices[device_index].fling(
            args['start'], args['orientation'], args['action'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def fling_to_end(self, command_args, device_index=0):
        """Performs fling action on a scrollable UI object until
        it reaches its beginning or end

        Args:
            command_args['start'] (tuple):
                coordinate (x, y) which is contained in
                the scrollable UI object
            command_args['end'] (integer):
                coordinate (x, y) which is used to determine fling direction
            device_index (integer):
                The index of the device
        """
        args = self._fling_scroll_args(
            command_args['start'], command_args['end'], True)
        self.devices[device_index].fling(
            args['start'], args['orientation'], args['action'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def scroll(self, command_args, device_index=0):
        """Performs scroll action on a scrollable UI object

        Args:
            command_args['start'] (tuple):
                coordinate (x, y) which is contained in
                the scrollable UI object
            command_args['end'] (integer):
                coordinate (x, y) which is used to determine scroll direction
            device_index (integer):
                The index of the device
        """
        args = self._fling_scroll_args(
            command_args['start'], command_args['end'], False)
        self.devices[device_index].scroll(
            args['start'], args['orientation'], args['action'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def scroll_to_end(self, command_args, device_index=0):
        """Performs scroll action on a scrollable UI object until
        it reaches its beginning or end

        Args:
            command_args['start'] (tuple):
                coordinate (x, y) which is contained in
                the scrollable UI object
            command_args['end'] (integer):
                coordinate (x, y) which is used to determine fling direction
            device_index (integer):
                The index of the device
        """
        args = self._fling_scroll_args(
            command_args['start'], command_args['end'], True)
        self.devices[device_index].scroll(
            args['start'], args['orientation'], args['action'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def scroll_to_text(self, command_args, device_index=0):
        """Performs scroll action on a scrollable UI object until
        an item of the object specified by text value is displayed

        Args:
            command_args['start'] (tuple):
                coordinate (x, y) which is contained in
                the scrollable UI object
            command_args['end'] (integer):
                coordinate (x, y) which is used to determine fling direction
            command_args['text'] (text):
                text value of the item which is to be displayed
            device_index (integer):
                The index of the device
        """
        args = self._fling_scroll_args(
            command_args['start'], command_args['end'], True)
        selector_kwargs = {'text': command_args['text']}
        self.devices[device_index].scroll_to(
            args['start'], args['orientation'], selector_kwargs,
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def get_object_info(self, command_args, device_index=0):
        """Returns UI object's information

        Args:
            command_args['start'] (tuple):
                coordinate (x, y) on which the UI object is located
            command_args['criteria'] (dict):
                UI object selector key-value pairs ex) {'text': 'OK'}
            device_index (integer):
                The index of the device
        Returns:
            dict: UI object's information
        """
        info = self.devices[device_index].get_info(
            command_args['start'],
            **command_args.get('criteria', {}))
        return info if info else {}

    def set_orientation(self, command_args, device_index=0):
        """sets the device's orientation

        Args:
            command_args['orientation'] (string):
                'natural', 'left', 'right', 'upsidedown' or 'unfreeze'
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].set_orientation(
            command_args['orientation'],
            record=self.writer.get_recorder(device_index))
        self.devices[device_index].invalidate_view_hierarchy_dump()

    def insert_screenshot_capture(self, _, device_index=0):
        """Insert screenshot capture statement into the script

        Args:
            device_index (integer):
                The index of the device
        """
        filename = ("datetime.today()"
                    ".strftime('screenshot_%Y%m%d_%H%M%S_%f.png')")
        self.devices[device_index].record_screenshot_capture(
            filename,
            record=self.writer.get_recorder(device_index))

    def insert_wait(self, command_args, device_index=0):
        """Insert wait statement into the script

        Args:
            command_args['for_what'] (string): 'idle' or 'update'
            command_args['timeout'] (integer): timeout in msec
            device_index (integer):
                The index of the device
        """
        for_what = command_args.get('for_what', 'idle')
        timeout = command_args.get('timeout')
        self.devices[device_index].record_wait(
            for_what, timeout,
            record=self.writer.get_recorder(device_index))

    def insert_wait_object(self, command_args, device_index=0):
        """Insert wait-object statement into the script

        Args:
            command_args['start'] (tuple):
                (x, y) coordinates on which the object locates
            command_args['for_what'] (string): 'exists' or 'gone'
            command_args['timeout'] (integer): timeout in msec
            device_index (integer):
                The index of the device
        """
        for_what = command_args.get('for_what', 'exists')
        timeout = command_args.get('timeout')
        self.devices[device_index].record_wait_object(
            command_args['start'],
            for_what, timeout,
            record=self.writer.get_recorder(device_index))
