# -*- coding: utf-8 -*-
"""Script generating controller

:copyright: (c) 2015 by tksn
:license: MIT
"""
# pylint: disable=invalid-name

from __future__ import unicode_literals
import os
import tempfile
import time
import uuid

from PIL import Image

from . import view_hierarchy_dump
from . import uiobjectfinder
from . import keycode
from phoneauto.scriptgenerator.exception import UiObjectNotFound


# Command table instatnce to hold commands
_command_table = {}


def command(name):
    """Command decorator (decorator generator)

    Generates decorator which registers
    decorated function to the command table.

    Args:
        name (string):
            Command name which is the key when
            client code invokes a command.
    Returns:
        func: decorater function
    """
    def command_decorator(func):
        """Decorator function"""
        _command_table[name] = func
        return func
    return command_decorator


def _kwarg(name, to_name=None, default=None):
    """Keyword argument object generator

    Generates keyword argument object which specifies
    how keyword argument is extracted from
    the dictionary given from client code ,and how the extracted argument
    is passed to the command function.

    Args:
        name (string):
            Argument name, which is used to extract the argument
            from dictionary passed from client.
            And also, this is used in place of to_name if to_name is not
            specified or is None.
        to_name (string):
            Keyword argument name of the command function
            to which the extracted value is assigned.
        default (object):
            Default value which is used when name is not found in
            the dictionary given from the client.
    Returns:
        object: keyword argument object
    """
    to_name = to_name or name

    def transform(_, command_kwargs):
        """Extract keyword arguments from command args"""
        return [(to_name, command_kwargs.get(name, default))]
    return transform


def _locator(criteria,
             coord_kwname='start',
             ignore_distant=True,
             to_name=None):
    """Generate locator extractor"""
    to_name = to_name or 'locator'

    def transform(objs, command_kwargs):
        """Extract locator from command args"""
        coord = command_kwargs[coord_kwname]
        locator = objs.finder.find_object_contains(
            coord=coord, ignore_distant=ignore_distant, **criteria)
        return [(to_name, locator)]
    return transform


def _create_command(command_name,
                    kwarg_list=(),
                    device_method_name=None,
                    device_code_method_name=None):
    """Create generic command function and registers it to the command table.

    Args:
        command_name (string): Command's name
        kwarg_list (tuple):
            Tuple of keyword argument objects which is to extract
            keyword arguments from command arguments and
            given to device method.
        device_method_name (string):
            Name of the device object's method to call.
            Defaults to command_name if None.
        device_code_method_name (string):
            Name of the coder object's method to call.
            Defaults to device_method_name if None.
    Returns:
        command function object.
    """
    device_method_name = device_method_name or command_name
    device_code_method_name = (
        device_code_method_name or 'get_code_' + device_method_name)

    @command(command_name)
    def command_func(objs, **command_kwargs):
        """Generic command implementation"""
        method_kwargs = {}
        for kwarg_produce in kwarg_list:
            kwarg = kwarg_produce(objs, command_kwargs)
            method_kwargs.update(dict(kwarg))
        coder_method = getattr(objs.coder, device_code_method_name)
        objs.record(coder_method(**method_kwargs))
        device_method = getattr(objs.device, device_method_name)
        return device_method(**method_kwargs)
    return command_func

# ====================================================
# Command definitions
# ====================================================


@command('update_view_dump')
def _update_view_dump(objs, **_):
    """Update hierarchy view dump
    Should be called whenever screen is updated.
    """
    dump_str = objs.device.dump()
    hierarchy_dump = view_hierarchy_dump.ViewHierarchyDump(
        objs.device.info, dump_str)
    objs.finder = uiobjectfinder.UiObjectFinder(hierarchy_dump)


@command('get_screenshot')
def _get_screenshot(objs, **_):
    """Get screenshot

    Returns:
        PIL.Image: Screenshot image if success, otherwise None.
    """
    file_path = os.path.join(tempfile.gettempdir(),
                             'tmp_{0}.png'.format(uuid.uuid4()))
    success = objs.device.get_screenshot_as_file(file_path)
    if not success:
        return None
    return Image.open(file_path)


@command('enter_text')
def _send_keys(objs, **command_args):
    """Send keys to the screen or a target UI object"""
    coord = command_args['start']
    keys = command_args['text']
    try:
        # First, try set text to the target UI object
        loc = objs.finder.find_object_contains(
            coord, True, className='android.widget.EditText')
        objs.device.set_text(loc, keys)
        objs.record(objs.coder.get_code_set_text(loc, keys))
    except uiobjectfinder.UiObjectNotFound:
        # If failed to set text to the target UI object,
        # send each character in text to the screen one by one
        for k in keycode.chars_to_keys_us(keys):
            objs.device.press_key(k[0], meta=k[1])
            objs.record(objs.coder.get_code_press_key(k[0], meta=k[1]))

# -------------------------------
# Commands which require locator

# Locator criteria definition
_CRITERIA_EDITTEXT = {'className': 'android.widget.EditText'}
_CRITERIA_CLICKABLE = {'clickable': True, 'enabled': True}

_create_command(command_name='clear_text',
                kwarg_list=(_locator(_CRITERIA_EDITTEXT),))

_create_command(command_name='click_object',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE),
                    _kwarg('wait')))

_create_command(command_name='long_click_object',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE),))

_create_command(command_name='drag_object_to_xy',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE),
                    _kwarg('end', to_name='coord'),
                    _kwarg('options', default={})))

_create_command(command_name='drag_object_to_object',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE),
                    _locator(_CRITERIA_CLICKABLE,
                             coord_kwname='end',
                             to_name='other_locator'),
                    _kwarg('options', default={})))


def _swipe_direction(_, kwargs):
    """Determines swipe direction from start and end point"""
    start, end = kwargs['start'], kwargs['end']
    xdiff, ydiff = end[0] - start[0], end[1] - start[1]
    if abs(xdiff) > abs(ydiff):
        direction = 'right' if xdiff >= 0 else 'left'
    else:
        direction = 'down' if ydiff >= 0 else 'up'
    return [('direction', direction)]

_create_command(command_name='swipe_object_with_direction',
                device_method_name='swipe_object',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE, ignore_distant=False),
                    _swipe_direction,
                    _kwarg('options', default={})))

_create_command(command_name='pinch',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE),
                    _kwarg('in_or_out'),
                    _kwarg('options', default={})))


def _get_move(kwargs):
    """Get move direction and amount of an action"""
    start, end = kwargs['start'], kwargs['end']
    xdiff, ydiff = end[0] - start[0], end[1] - start[1]
    if abs(xdiff) > abs(ydiff):
        return ('x', xdiff)
    else:
        return ('y', ydiff)


def _fling_scroll_orientation(_, kwargs):
    """Determine fling/scroll orientation"""
    orientation = 'horiz' if _get_move(kwargs)[0] == 'x' else 'vert'
    return [('orientation', orientation)]


def _fling_scroll_action(to_end):
    """Create action argument of fling/scroll command"""
    forward = 'toEnd' if to_end else 'forward'
    backward = 'toBeginning' if to_end else 'backward'

    def get_arg(_, kwargs):
        """Returns arguments for fling/scroll action"""
        diff = _get_move(kwargs)[1]
        return [('action', backward if diff >= 0 else forward)]
    return get_arg

_create_command(command_name='fling',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE, ignore_distant=False),
                    _fling_scroll_orientation,
                    _fling_scroll_action(to_end=False),
                    _kwarg('options', default={})))

_create_command(command_name='fling_to_end',
                device_method_name='fling',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE, ignore_distant=False),
                    _fling_scroll_orientation,
                    _fling_scroll_action(to_end=True),
                    _kwarg('options', default={})))

_create_command(command_name='scroll',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE, ignore_distant=False),
                    _fling_scroll_orientation,
                    _fling_scroll_action(to_end=False),
                    _kwarg('options', default={})))

_create_command(command_name='scroll_to_end',
                device_method_name='scroll',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE, ignore_distant=False),
                    _fling_scroll_orientation,
                    _fling_scroll_action(to_end=True),
                    _kwarg('options', default={})))

_create_command(command_name='scroll_to',
                device_method_name='scroll',
                kwarg_list=(
                    _locator(_CRITERIA_CLICKABLE, ignore_distant=False),
                    _fling_scroll_orientation,
                    lambda _, __: [('action', 'to')],
                    _kwarg('options')))

# ------------------------------------
# Commands which don't require locator

_create_command(command_name='press_key',
                kwarg_list=(_kwarg('key_name'),
                            _kwarg('meta')))

_create_command(command_name='open_notification')

_create_command(command_name='open_quick_settings')

_create_command(command_name='click_xy',
                kwarg_list=(_kwarg('start', to_name='coord'),))

_create_command(command_name='long_click_xy',
                kwarg_list=(_kwarg('start', to_name='coord'),))

_create_command(command_name='drag_xy_to_xy',
                kwarg_list=(_kwarg('start'),
                            _kwarg('end'),
                            _kwarg('options', default={})))

_create_command(command_name='swipe_xy_to_xy',
                device_method_name='swipe',
                kwarg_list=(_kwarg('start'),
                            _kwarg('end'),
                            _kwarg('options', default={})))

_create_command(command_name='set_orientation',
                kwarg_list=(_kwarg('orientation'),))


@command('video_init')
def _video_init(objs, **_):
    for kn in ('APP_SWITCH', 'HOME', 'APP_SWITCH', 'HOME'):
        objs.device.press_key(kn, meta=None)
        time.sleep(1)


@command('get_hierarchy_view_object_info')
def _get_hierarchy_view_object_info(objs, **command_args):
    """Get object's inforamtion such as text, contentDescription and boudns"""
    coord = command_args['start']
    options = command_args.get('options', {})
    try:
        locator = objs.finder.find_object_contains(coord, True, **options)
    except UiObjectNotFound:
        return None
    return locator.meta


@command('get_screen_size')
def _get_screen_size(objs, **_):
    """Get screen size"""
    device_info = objs.device.info
    return (device_info['displayWidth'], device_info['displayHeight'])


@command('insert_screenshot_capture')
def _insert_screenshot_capture(objs, **_):
    """Insert screenshot capture operation into script"""
    filename = ("datetime.today()"
                ".strftime('screenshot_%Y%m%d_%H%M%S_%f.png')")
    objs.record(objs.coder.get_code_screenshot(filename))


@command('insert_wait')
def _insert_wait(objs, **command_args):
    """Insert screen state wait operation into script"""
    objs.record(objs.coder.get_code_wait(
        command_args['for_what'], command_args['timeout']))


@command('insert_wait_object')
def _insert_wait_object(objs, **command_args):
    """Insert object state wait operation into script"""
    coord = command_args['start']
    options = command_args.get('options', {})
    locator = objs.finder.find_object_contains(coord, True, **options)
    objs.record(objs.coder.get_code_wait_object(
        locator, command_args['for_what'], command_args['timeout']))


# ------------------------------------
# Generator class definition


class ScriptGenerator(object):
    """Script generation controller"""

    def __init__(self, conf):
        """Initialize generator object

        Args:
            conf (dict):
                Configuration parameter which includes
                'devices', 'writer', 'coder'.
                'devices' is an iterable object which contains
                device object instances.
                'writer' is an writer object which is used to generate
                an automation script.
                'coder' is an object which is used to generate code fragment
                which performs device manipulation.
        """
        self.devices = conf['devices']
        self.coder = conf['coder']
        self.writer = conf['writer']
        # For test purpose, finder can be given by client.
        self.finder = conf.get('finder')

    def execute(self, command_name, command_args=None, device_index=0):
        """Execute command

        Args:
            command_name (string): Name of the command
            command_args (dict):
                The dictionary which contains arguments to the command
            device_index (integer):
                The index of a device object in devices iterable.
        """
        command_args = command_args or {}
        command_function = _command_table.get(command_name)
        command_args_copy = dict(command_args)

        class _Container(object):

            def __init__(c_self):
                c_self.device = self.devices[device_index]
                c_self.coder = self.coder
                c_self.finder = self.finder
                c_self.record = self.writer.get_recorder(device_index)

        objs = _Container()
        command_return_value = command_function(objs, **command_args_copy)

        # finder can be updated by commands.
        self.finder = objs.finder

        return command_return_value
