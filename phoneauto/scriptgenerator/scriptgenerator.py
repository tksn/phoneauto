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


# Command table instatnce to hold commands
_command_table = {}


def command(name):
    """Command decorator (decorator generator)

    Generates decorator which registers
    decorated function to the command table.

    Args:
        name (string):
            command name which is the key when
            client code invokes a command
    Returns:
        func: decorater function
    """
    def command_decorator(func):
        """Decorator function"""
        _command_table[name] = func
        return func
    return command_decorator


def _kwarg(name, to_name=None, default=None):
    """Keywork argument object generator

    Generates keyword argument object which specifies
    how keyword argument is extracted from
    the dictionary given from client code ,and how the extracted argument
    is passed to the command function.

    Args:
        name (string):
            argument name, which is used to extract the argument
            from dictionary which is passed from client.
            And also, this is used in place of to_name if to_name is not
            specified or is None.
        to_name (string):
            keyword argument name of the command function
            to which the extracted value is assigned.
        default (object):
            default value which is used when name is not found in
            the dictionary given from the client.
    Returns:
        object: keywork argument object
    """
    to_name = to_name or name

    def transform(kwargs):
        """Keyword argument object implementation"""
        return (to_name, kwargs.get(name, default))
    return transform


def _create_command(command_name,
                    device_method_name,
                    kwarg_list=()):
    """Creates generic command function and registers it to the command table.

    Args:
        command_name (string): command's name
        device_method_name (string):
            name of the device object's method to call.
        kwarg_list (tuple):
            tuple of keyword argument objects which is created using _kwargs
            function.
    Returns:
        command function object.
    """
    @command(command_name)
    def command_func(device, **command_kwargs):
        """Generic command impl"""
        method_kwargs = {}
        for kwarg_produce in kwarg_list:
            kwarg = kwarg_produce(command_kwargs)
            if isinstance(kwarg, list):
                method_kwargs.update(dict(kwarg))
            else:
                method_kwargs[kwarg[0]] = kwarg[1]
        device_method = getattr(device, device_method_name)
        return device_method(**method_kwargs)
    return command_func

_create_command(command_name='update_view_dump',
                device_method_name='update_view_hierarchy_dump')


@command('get_screenshot')
def _get_screenshot(device, **_):
    """get_screenshot command implementation"""
    file_path = os.path.join(tempfile.gettempdir(),
                             'tmp_{0}.png'.format(uuid.uuid4()))
    success = device.get_screenshot_as_file(file_path)
    if not success:
        return None
    return Image.open(file_path)

_create_command(command_name='press_key',
                device_method_name='press_key',
                kwarg_list=(_kwarg('key_name'),
                            _kwarg('meta'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='open_notification',
                device_method_name='open_notification',
                kwarg_list=(_kwarg('recorder', to_name='record'),))

_create_command(command_name='open_quick_settings',
                device_method_name='open_quick_settings',
                kwarg_list=(_kwarg('recorder', to_name='record'),))

_create_command(command_name='clear_text',
                device_method_name='clear_text',
                kwarg_list=(_kwarg('start', to_name='coord'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='enter_text',
                device_method_name='find_send_keys',
                kwarg_list=(_kwarg('start', to_name='coord'),
                            _kwarg('text', to_name='keys'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='click_xy',
                device_method_name='click_xy',
                kwarg_list=(_kwarg('start', to_name='coord'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='click_object',
                device_method_name='click_object',
                kwarg_list=(_kwarg('start', to_name='coord'),
                            _kwarg('wait'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='long_click_xy',
                device_method_name='long_click_xy',
                kwarg_list=(_kwarg('start', to_name='coord'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='long_click_object',
                device_method_name='long_click_object',
                kwarg_list=(_kwarg('start', to_name='coord'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='drag_xy_to_xy',
                device_method_name='drag_xy_to_xy',
                kwarg_list=(_kwarg('start'),
                            _kwarg('end'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='drag_object_to_xy',
                device_method_name='drag_object_to_xy',
                kwarg_list=(_kwarg('start'),
                            _kwarg('end'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='drag_object_to_object',
                device_method_name='drag_object_to_object',
                kwarg_list=(_kwarg('start'),
                            _kwarg('end'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='swipe_xy_to_xy',
                device_method_name='swipe',
                kwarg_list=(_kwarg('start'),
                            _kwarg('end'),
                            _kwarg('recorder', to_name='record'),
                            _kwarg('steps')))


def _swipe_direction(kwargs):
    """Determines swipe direction from start and end point"""
    start, end = kwargs['start'], kwargs['end']
    xdiff, ydiff = end[0] - start[0], end[1] - start[1]
    if abs(xdiff) > abs(ydiff):
        direction = 'right' if xdiff >= 0 else 'left'
    else:
        direction = 'down' if ydiff >= 0 else 'up'
    return ('direction', direction)

_create_command(command_name='swipe_object_with_direction',
                device_method_name='swipe_object',
                kwarg_list=(_kwarg('start'),
                            _swipe_direction,
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='pinch',
                device_method_name='pinch',
                kwarg_list=(_kwarg('in_or_out'),
                            _kwarg('start', to_name='coord'),
                            _kwarg('percent'),
                            _kwarg('steps'),
                            _kwarg('recorder', to_name='record')))


def _fling_scroll_orientation(kwargs):
    """Determines fling or scroll orientation"""
    start, end = kwargs['start'], kwargs['end']
    xdiff, ydiff = end[0] - start[0], end[1] - start[1]
    if abs(xdiff) > abs(ydiff):
        return {'orientation': 'horiz', 'diff': xdiff}
    else:
        return {'orientation': 'vert', 'diff': ydiff}


def _fling_scroll_orientation_arg(kwargs):
    """Creates orientation argument of fling/scroll command"""
    return (
        'orientation',
        _fling_scroll_orientation(kwargs)['orientation'])


def _fling_scroll_action(to_end):
    """Creates action argument of fling/scroll command"""
    forward = 'toEnd' if to_end else 'forward'
    backward = 'toBeginning' if to_end else 'backward'

    def get_arg(kwargs):
        """Returns arguments for fling/scroll action"""
        diff = _fling_scroll_orientation(kwargs)['diff']
        return ('action', backward if diff >= 0 else forward)
    return get_arg


_create_command(command_name='fling',
                device_method_name='fling',
                kwarg_list=(_kwarg('start'),
                            _fling_scroll_orientation_arg,
                            _fling_scroll_action(to_end=False),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='fling_to_end',
                device_method_name='fling',
                kwarg_list=(_kwarg('start'),
                            _fling_scroll_orientation_arg,
                            _fling_scroll_action(to_end=True),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='scroll',
                device_method_name='scroll',
                kwarg_list=(_kwarg('start'),
                            _fling_scroll_orientation_arg,
                            _fling_scroll_action(to_end=False),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='scroll_to_end',
                device_method_name='scroll',
                kwarg_list=(_kwarg('start'),
                            _fling_scroll_orientation_arg,
                            _fling_scroll_action(to_end=True),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='scroll_to',
                device_method_name='scroll_to',
                kwarg_list=(lambda kwargs: list(kwargs.items()),
                            _fling_scroll_orientation_arg,
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='get_object_info',
                device_method_name='get_info',
                kwarg_list=(_kwarg('start'),
                            _kwarg('criteria', default={})))

_create_command(command_name='set_orientation',
                device_method_name='set_orientation',
                kwarg_list=(_kwarg('orientation'),
                            _kwarg('recorder', to_name='record')))


def _png_filename_generate(_):
    """Creates file argument of record_screenshot_capture"""
    filename = ("datetime.today()"
                ".strftime('screenshot_%Y%m%d_%H%M%S_%f.png')")
    return ('file', filename)

_create_command(command_name='insert_screenshot_capture',
                device_method_name='record_screenshot_capture',
                kwarg_list=(_png_filename_generate,
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='insert_wait',
                device_method_name='record_wait',
                kwarg_list=(_kwarg('for_what'),
                            _kwarg('timeout'),
                            _kwarg('recorder', to_name='record')))

_create_command(command_name='insert_wait_object',
                device_method_name='record_wait_object',
                kwarg_list=(_kwarg('start'),
                            _kwarg('for_what'),
                            _kwarg('timeout'),
                            _kwarg('recorder', to_name='record')))


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

    def execute(self, command_name, command_args=None, device_index=0):
        """Command dispatching

        Args:
            command_name (string): name of the command
            command_args (dict):
                a dictionary which contains arguments to the command
            device_index (integer):
                the index of a device object in devices iterable.
        """
        command_args = command_args or {}
        cmd = _command_table.get(command_name)
        kwargs = dict(command_args)
        kwargs['recorder'] = self.writer.get_recorder(device_index)
        return cmd(self.devices[device_index], **kwargs)
