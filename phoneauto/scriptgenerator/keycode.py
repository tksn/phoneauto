# -*- coding: utf-8 -*-
"""Key-Keycode conversion

:copyright: (c) 2015 by tksn
:license: MIT
"""

from __future__ import unicode_literals


_META_SHIFT_ON = 1

_ALPHA_LOWERCASE = 'abcdefghijklmnopqrstuvwxyz'
_ALPHA_UPPERCASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
_OTHER_PRIMARY = '`1234567890-=[];\\\',./ \t\n'
_OTHER_SECONDARY = '~!@#$%^&*()_+{}|:"<>?'

_CHARS_PRIMARY = _ALPHA_LOWERCASE + _OTHER_PRIMARY
_CHARS_SECONDARY = _ALPHA_UPPERCASE + _OTHER_SECONDARY


def char_to_key_us(char):
    """Converts character to key name on US keyboard

    Args:
        char (text): character to be converted
    Returns:
        tuple: (key name, meta key)
    Example:
        >>> char_to_key_us('A') == ('a', 1)  # True
        1 is meta key which means SHIFT is pressed at the same time
    """
    found_i = _CHARS_SECONDARY.find(char)
    if found_i >= 0:
        return (_CHARS_PRIMARY[found_i], _META_SHIFT_ON)
    return (char, None)


def chars_to_keys_us(chars):
    """Returns iterator to converted characters
    Args:
        chars (text): characters to be converted
    Yields:
        tuple: (key name, meta key)
    """
    for char in chars:
        yield char_to_key_us(char)


_ALPHA = _ALPHA_LOWERCASE
_ALPHA_START = 29
_ALPHA_KEYCODE = range(_ALPHA_START, _ALPHA_START + len(_ALPHA))

_DIGIT = '0123456789'
_DIGIT_START = 7
_DIGIT_KEYCODE = range(_DIGIT_START, _DIGIT_START + len(_DIGIT))

_SYMBOL = (('\'', 'APOSTROPHE', 75), ('@', 'AT', 77), ('\\', 'BACKSLASH', 73),
           (',', 'COMMA', 55), ('\n', 'ENTER', 66), ('=', 'EQUALS', 70),
           ('`', 'GRAVE', 68), ('[', 'LEFT_BRACKET', 71), ('-', 'MINUS', 69),
           ('.', 'PERIOD', 56), ('+', 'PLUS', 81), ('#', 'POUND', 18),
           (']', 'RIGHT_BRACKET', 72), (';', 'SEMICOLON', 74),
           ('/', 'SLASH', 76), (' ', 'SPACE', 62), ('*', 'STAR', 17),
           ('\t', 'TAB', 61))
_SYMBOL_DICT = dict((s[0], s[2]) for s in _SYMBOL)
_SYMBOL_DICT2 = dict((s[1], s[2]) for s in _SYMBOL)

_SPECIAL = (('APP_SWITCH', 187), ('BACK', 4), ('BRIGHTNESS_DOWN', 220),
            ('BRIGHTNESS_UP', 221), ('CALL', 5), ('CAMERA', 27),
            ('CAPS_LOCK', 115), ('CLEAR', 28), ('DEL', 67),
            ('DPAD_CENTER', 23), ('DPAD_DOWN', 20), ('DPAD_LEFT', 21),
            ('DPAD_RIGHT', 22), ('DPAD_UP', 19), ('ENDCALL', 6),
            ('ESCAPE', 111), ('FOCUS', 80), ('FORWARD_DEL', 112),
            ('HOME', 3), ('MENU', 82), ('NOTIFICATION', 83),
            ('POWER', 26), ('SEARCH', 74), ('SETTINGS', 176), ('SLEEP', 223),
            ('SOFT_LEFT', 1), ('SOFT_RIGHT', 2), ('SYM', 63),
            ('UNKNOWN', 0), ('VOLUME_DOWN', 25), ('VOLUME_UP', 24),
            ('WAKEUP', 224), ('ZOOM_IN', 168), ('ZOOM_OUT', 169))
_SPECIAL_DICT = dict(_SPECIAL)


def get_keycode(key):
    """Returns key code from key name

    Args:
        key (text): key name
    Returns:
        integer: keycode
    """
    symbol = _SYMBOL_DICT.get(key, None)
    if symbol is not None:
        return symbol
    symbol = _SYMBOL_DICT2.get(key, None)
    if symbol is not None:
        return symbol
    special = _SPECIAL_DICT.get(key, None)
    if special is not None:
        return special
    found_i = _ALPHA.find(key)
    if found_i >= 0:
        return _ALPHA_KEYCODE[found_i]
    found_i = _DIGIT.find(key)
    if found_i >= 0:
        return _DIGIT_KEYCODE[found_i]
    raise ValueError('Unknown key:{0}'.format(key))
