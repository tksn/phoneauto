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

    def back(self, _, device_index=0):
        """Presses 'back' key of the device

        Args:
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].press_key(
            'BACK', record=self.writer.get_recorder(device_index))

    def home(self, _, device_index=0):
        """Presses 'home' key of the device

        Args:
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].press_key(
            'HOME', record=self.writer.get_recorder(device_index))

    def recent_apps(self, _, device_index=0):
        """Presses 'recent apps' key of the device

        Args:
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].press_key(
            'APP_SWITCH', record=self.writer.get_recorder(device_index))

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

    def click_object(self, command_args, device_index=0):
        """Clicks on a UI object

        Args:
            command_args['start'] (tuple):
                Coordinate (x, y) of a pixel which is contained
                in the target object
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].click_object(
            command_args['start'],
            record=self.writer.get_recorder(device_index))

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
