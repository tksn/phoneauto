# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import io

from mock import MagicMock, call

from phoneauto.scriptgenerator import scriptgenerator_main
from phoneauto.scriptgenerator.uiautomator_device import UiautomatorDevice
from phoneauto.scriptgenerator.keycode import get_keycode
from tests.uiautomator_mock import uia_element_info


def last_line(result_out):
    lines = result_out.getvalue().decode('utf-8').split('\n')
    for line in reversed(lines):
        l = line.strip()
        if l:
            return l
    raise AssertionError('There is no lines in result_out')


def mainloop_testfunc(testfunc):
    def wrap_testfunc(mocks):
        result_out = io.BytesIO()
        def side_effect():
            testfunc(mocks, result_out)
        mocks.uiroot.mainloop.side_effect = side_effect
        scriptgenerator_main(result_out, scale=1.0)
        assert mocks.uiroot.mainloop.called
    return wrap_testfunc


@mainloop_testfunc
def test_refresh_screen(mocks, result_out):
    prev_call_count = mocks.device.screenshot.call_count
    mocks.uiroot.process_event('r')
    assert mocks.device.screenshot.call_count == prev_call_count + 1


def mouse_events(mocks, events):
    class _Object(object): pass
    canvas = mocks.uiroot.nametowidget('mainframe.canvas')
    for ev_name, ev_coord in events:
        ev_arg = _Object()
        ev_arg.x, ev_arg.y = ev_coord if ev_coord is not None else (0, 0)
        ev_arg.x_root, ev_arg.y_root = 0, 0  # not used in tests
        if ev_name == '##EXEC_AFTER':
            canvas.execute_after_func()
        else:
            canvas.process_event(ev_name, ev_arg)
        pass


def set_element_find_result(mocks, **uia_attr):
    find_result = []
    for name, value in uia_attr.items():
        elem = MagicMock()
        elem.info = uia_element_info(**{name: value})
        find_result.append(elem)
    mocks.device.return_value = find_result
    return find_result[0] if len(find_result) == 1 else find_result


@mainloop_testfunc
def test_click_xy(mocks, result_out):
    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('<ButtonRelease-1>', (10, 20))
    ))
    mocks.device.click.assert_called_with(10, 20)
    assert '.click(10, 20)' in last_line(result_out)


@mainloop_testfunc
def test_click_element(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')

    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('<ButtonRelease-1>', (10, 20))
    ))
    elem.click.assert_called_once_with()
    assert 'resourceId=\'abc\').click()' in last_line(result_out)


@mainloop_testfunc
def test_long_click_xy(mocks, result_out):
    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('##EXEC_AFTER', None),
        ('<ButtonRelease-1>', (10, 20))
    ))
    mocks.device.long_click.assert_called_with(10, 20)
    assert '.long_click(10, 20)' in last_line(result_out)


@mainloop_testfunc
def test_long_click_element(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')

    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('##EXEC_AFTER', None),
        ('<ButtonRelease-1>', (10, 20))
    ))
    elem.long_click.assert_called_once_with()
    assert 'resourceId=\'abc\').long_click()' in last_line(result_out)


@mainloop_testfunc
def test_swipe(mocks, result_out):
    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('<B1-Motion>', (20, 30)),
        ('<ButtonRelease-1>', (30, 40))
    ))
    mocks.device.swipe.assert_called_with(10, 20, 30, 40)
    assert '.swipe(10, 20, 30, 40' in last_line(result_out)


@mainloop_testfunc
def test_drag_xy(mocks, result_out):
    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('##EXEC_AFTER', None),
        ('<B1-Motion>', (20, 30)),
        ('<ButtonRelease-1>', (30, 40))
    ))
    mocks.device.drag.assert_called_with(10, 20, 30, 40)
    assert '.drag(10, 20, 30, 40' in last_line(result_out)


@mainloop_testfunc
def test_drag_element(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')
    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('##EXEC_AFTER', None),
        ('<B1-Motion>', (20, 30)),
        ('<ButtonRelease-1>', (30, 40))
    ))
    elem.drag.to.assert_called_with(30, 40)
    assert '.drag.to(30, 40' in last_line(result_out)


def assert_press(mocks, result_out, button_name, key_name):
    button_widget_name = 'mainframe.{0}'.format(button_name)
    mocks.uiroot.nametowidget(button_widget_name).process_event(None)
    keycode = get_keycode(key_name)
    mocks.device.press.assert_called_with(keycode, None)
    assert '.press({0}, None)'.format(keycode) in last_line(result_out)


@mainloop_testfunc
def test_back(mocks, result_out):
    assert_press(mocks, result_out, 'back_button', 'BACK')


@mainloop_testfunc
def test_home(mocks, result_out):
    assert_press(mocks, result_out, 'home_button', 'HOME')


@mainloop_testfunc
def test_recent_apps(mocks, result_out):
    assert_press(mocks, result_out, 'recent_button', 'APP_SWITCH')


def textentrywindow_set_text_entry(textentrywindow, text):
    textentry = textentrywindow.nametowidget('textentry')
    textentry.get.return_value = text


def textentrywindow_click_ok(textentrywindow):
    ok_button = textentrywindow.nametowidget('ok_button')
    ok_button.process_event(None)


def execute_rightclickmenu_command(mocks, command_tag, position):
    mouse_events(mocks, (('<Button-2>', position),))
    menu = mocks.uiroot.nametowidget('mainframe.menu')
    menu.process_event(command_tag)


@mainloop_testfunc
def test_enter_text_element(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')

    def actions_when_textentrywindow_displayed(textentrywindow):
        textentrywindow_set_text_entry(textentrywindow, 'ABCDEF')
        textentrywindow_click_ok(textentrywindow)

    canvas = mocks.uiroot.nametowidget('mainframe.canvas')
    canvas.wait_window.side_effect = actions_when_textentrywindow_displayed

    execute_rightclickmenu_command(mocks, 'Enter text', (10, 20))

    elem.set_text.assert_called_with('ABCDEF')
    assert '.set_text(\'ABCDEF\')' in last_line(result_out)


@mainloop_testfunc
def test_enter_text_nonelement(mocks, result_out):

    def actions_when_textentrywindow_displayed(textentrywindow):
        textentrywindow_set_text_entry(textentrywindow, 'aB')
        textentrywindow_click_ok(textentrywindow)

    canvas = mocks.uiroot.nametowidget('mainframe.canvas')
    canvas.wait_window.side_effect = actions_when_textentrywindow_displayed

    execute_rightclickmenu_command(mocks, 'Enter text', (10, 20))

    mocks.device.press.assert_has_calls([
        call(29, None), call(30, 1)])
    assert '.press(30, 1)'.format() in last_line(result_out)
