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
        """Clicks on the pixel or the element on the device

        Args:
            position (tuple):
                Coordinate (x, y) of the target pixel/element
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].find_click(
            position, record=self.writer.get_recorder(device_index))

    def long_click(self, position, device_index=0):
        """Long-clicks on the pixel or the element on the device

        Args:
            position (tuple):
                Coordinate (x, y) of the target pixel/element
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
            emd (tuple):
                End point's coordinate (x, y) of the swipe action
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].swipe(
            start, end, record=self.writer.get_recorder(device_index))

    def drag(self, start, end, device_index=0):
        """Performs drag-and-drop action on the device

        Args:
            start (tuple):
                Start point's coordinate (x, y) of the drag action
            emd (tuple):
                End point's coordinate (x, y) of the drag action
            device_index (integer):
                The index of the device
        """
        self.devices[device_index].find_drag(
            start, end, record=self.writer.get_recorder(device_index))

    @staticmethod
    def query_touch_action(event_chain):
        """Queries if the event_chain can be handled by the device

        Args:
            event_chain (iterable):
                Series of mouse events, which is defined as an iterable,
                and consists tuple objects. Each tuple object represents event
                and is defined as (event_name, coordinate)
                where event_name is one of 'press', 'hold' and 'release',
                and coordinate is the mouse position (x, y).
        """
        MOVE, NOMOVE = True, False
        TOUCH_ACTION_PATTERNS = (
            (('press', ('release', NOMOVE)), 'click'),
            (('press', ('release', MOVE)), 'swipe'),
            (('press', ('hold', NOMOVE), ('release', MOVE)), 'drag'),
            (('press', ('hold', NOMOVE), ('release', NOMOVE)), 'long_click'),
            (('press', ('hold', MOVE), ('release', NOMOVE)), 'swipe'))

        def match_pattern(pattern_seq):
            """Returns if the pattern_seq matches to
            one of TOUCH_ACTION_PATTERNS
            """
            if len(pattern_seq) != len(event_chain):
                return False
            x0, y0 = event_chain[0]['coord']
            it = iter(pattern_seq[1:])
            for ev in event_chain[1:]:
                x1, y1 = ev['coord']
                moveflag = x0 != x1 or y0 != y1
                pat_ev = next(it)
                if ev['type'] != pat_ev[0] or moveflag != pat_ev[1]:
                    return False
            return True

        for pattern_seq, pattern_act in TOUCH_ACTION_PATTERNS:
            if match_pattern(pattern_seq):
                return pattern_act
        return None

    def touch_action(self, event_chain, device_index=0):
        """Performs touch action

        Args:
            event_chain (iterable):
                Series of mouse events, which is defined as an iterable,
                and consists tuple objects. Each tuple object represents event
                and is defined as (event_name, coordinate)
                where event_name is one of 'press', 'hold' and 'release',
                and coordinate is the mouse position (x, y).
        """
        xy = event_chain[0]['coord']
        xyS, xyE = event_chain[0]['coord'], event_chain[-1]['coord']

        def click():
            """Click command"""
            return self.click(xy, device_index=device_index)

        def long_click():
            """Long-click command"""
            return self.long_click(xy, device_index=device_index)

        def swipe():
            """Swipe command"""
            return self.swipe(xyS, xyE, device_index=device_index)

        def drag():
            """Drag command"""
            return self.drag(xyS, xyE, device_index=device_index)

        command_table = {'click': click, 'long_click': long_click,
                         'swipe': swipe, 'drag': drag}

        action = self.query_touch_action(event_chain)
        if action:
            command_table[action]()
            return
        raise NotImplementedError()
