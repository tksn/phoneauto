# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest
from phoneauto.scriptgenerator import keycode


def test_char_to_key():
    assert keycode.char_to_key_us('a') == ('a', None)
    assert keycode.char_to_key_us('A') == ('a', 1)

def test_chars_to_keys():
    assert tuple(keycode.chars_to_keys_us('aA \t')) == (
        ('a', None), ('a', 1), (' ', None), ('\t', None))

def test_keycode_of_symbol_from_char():
    assert keycode.get_keycode('`') == 68

def test_keycode_of_symbol_from_keyname():
    assert keycode.get_keycode('GRAVE') == 68

def test_keycode_of_specialkey_from_keyname():
    assert keycode.get_keycode('HOME') == 3

def test_keycode_of_alphabet():
    assert keycode.get_keycode('a') == 29

def test_keycode_of_digit():
    assert keycode.get_keycode('0') == 7

def test_keycode_not_found():
    with pytest.raises(ValueError):
        keycode.get_keycode('INVALID_KEYNAME')
