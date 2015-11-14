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

    def back(self, device_index=0):
        """Presses 'back' key of the device

        Args:
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].press_key(
            'BACK', record=self.writer.get_recorder(device_index))

    def home(self, device_index=0):
        """Presses 'home' key of the device

        Args:
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].press_key(
            'HOME', record=self.writer.get_recorder(device_index))

    def recent_apps(self, device_index=0):
        """Presses 'recent apps' key of the device

        Args:
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].press_key(
            'APP_SWITCH', record=self.writer.get_recorder(device_index))

    def send_keys(self, position, keys, device_index=0):
        """Sends keys to the target element on the device

        Args:
            position (tuple):
                Coordinate (x, y) of the target element
            keys (text):
                characters which are sent to the target
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].find_send_keys(
            position, keys, record=self.writer.get_recorder(device_index))

    def click(self, position, device_index=0):
        """Clicks on a pixel

        Args:
            position (tuple):
                Coordinate (x, y) of the target pixel
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].click(
            position, record=self.writer.get_recorder(device_index))

    def click_uielement(self, position, device_index=0):
        """Clicks on a UI element

        Args:
            position (tuple):
                Coordinate (x, y) of a pixel in the target element
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].find_click(
            position, record=self.writer.get_recorder(device_index))

    def long_click(self, position, device_index=0):
        """Long-clicks on a pixel

        Args:
            position (tuple):
                Coordinate (x, y) of the target pixel
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].long_click(
            position, record=self.writer.get_recorder(device_index))

    def long_click_uielement(self, position, device_index=0):
        """Long-clicks on a element

        Args:
            position (tuple):
                Coordinate (x, y) of the target element
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].find_long_click(
            position, record=self.writer.get_recorder(device_index))

    def swipe(self, start, end, device_index=0):
        """Performs swipe action on the device

        Args:
            start (tuple):
                Start point's coordinate (x, y) of the swipe action
            end (tuple):
                End point's coordinate (x, y) of the swipe action
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].swipe(
            start, end, steps=10,
            record=self.writer.get_recorder(device_index))

    def swipe_uielement(self, start, end, device_index=0):
        """Swipes a ui element on the device

        Args:
            start (tuple):
                Start ui element's  coordinate (x, y)
            end (tuple):
                Destination coordinate (x, y) which is used to
                determine swipe direction
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].find_swipe(
            start, end, steps=10,
            record=self.writer.get_recorder(device_index))

    def drag(self, start, end, device_index=0):
        """Performs drag-and-drop action on the device

        Args:
            start (tuple):
                Start point's coordinate (x, y) of the drag action
            end (tuple):
                End point's coordinate (x, y) of the drag action
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].find_drag(
            start, end,
            record=self.writer.get_recorder(device_index))

    def drag_to_other(self, start, end, device_index=0):
        """Performs drag-and-drop action on the device
        Drops the ui element on another ui element.

        Args:
            start (tuple):
                Start point's coordinate (x, y) of the drag action
            end (tuple):
                End point's coordinate (x, y) of the drag action
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].find_drag(
            start, end, find_target_element=True,
            record=self.writer.get_recorder(device_index))

    def pinch_in(self, position, percent, steps=10, device_index=0):
        """Performs pinch-in (edge-to-center) action on the device

        Args:
            position (tuple):
                coordinate (x, y) of the ui element which is to pinch-in'ed
            percent (tuple):
                percentage of the element's diagonal length
                for the pinch gesture
            steps (integer):
                the number of steps for the gesture.
                Steps are injected about 5 milliseconds apart,
                so 100 steps may take around 0.5 seconds to complete.
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].pinch_in(
            position, percent, steps=steps,
            record=self.writer.get_recorder(device_index))

    def pinch_out(self, position, percent, steps=10, device_index=0):
        """Performs pinch-out (center-to-edge) action on the device

        Args:
            position (tuple):
                coordinate (x, y) of the ui element which is to pinch-out'ed
            percent (tuple):
                percentage of the element's diagonal length
                for the pinch gesture
            steps (integer):
                the number of steps for the gesture.
                Steps are injected about 5 milliseconds apart,
                so 100 steps may take around 0.5 seconds to complete.
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].pinch_out(
            position, percent, steps=steps,
            record=self.writer.get_recorder(device_index))
