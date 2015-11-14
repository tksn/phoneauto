# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import io

from mock import MagicMock, call

from phoneauto.scriptgenerator import scriptgenerator_main
from phoneauto.scriptgenerator.uiautomator_device import UiautomatorDevice
from phoneauto.scriptgenerator.keycode import get_keycode
from tests.uiautomator_mock import uia_element_info, bounds


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
        scriptgenerator_main(result_out, scale=1.0, platform='Darwin')
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


def set_element_find_result(mocks, **uia_attr):
    elem = MagicMock()
    elem.info = uia_element_info(**uia_attr)
    mocks.device.return_value = [elem]
    return elem


# Button actions

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


# Mouse left button click actions

@mainloop_testfunc
def test_click_xy(mocks, result_out):
    # left down-up is translated to click with coordinate
    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('<ButtonRelease-1>', (10, 20))
    ))
    mocks.device.click.assert_called_with(10, 20)
    assert '.click(10, 20)' in last_line(result_out)


@mainloop_testfunc
def test_long_click_xy(mocks, result_out):
    # left down-hold-up is translated to long click with coordinate
    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('##EXEC_AFTER', None),
        ('<ButtonRelease-1>', (10, 20))
    ))
    mocks.device.long_click.assert_called_with(10, 20)
    assert '.long_click(10, 20)' in last_line(result_out)


@mainloop_testfunc
def test_swipe_xy(mocks, result_out):
    # left down-move-up is translated to swipe with coordinate
    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('<B1-Motion>', (20, 30)),
        ('<ButtonRelease-1>', (30, 40))
    ))
    mocks.device.swipe.assert_called_with(10, 20, 30, 40, steps=10)
    assert '.swipe(10, 20, 30, 40' in last_line(result_out)


@mainloop_testfunc
def test_drag_xy(mocks, result_out):
    # left down-hold-move-up is translated to drag with
    #   start=uielement, end=coordinate
    # but becomes swipe if no ui element found on start position
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
    # left down-hold-move-up is translated to drag with
    #   start=uielement, end=coordinate
    elem = set_element_find_result(
        mocks, visibleBounds=bounds(20, 10, 21, 11), resourceName='abc')
    mouse_events(mocks, (
        ('<Button-1>', (10, 20)),
        ('##EXEC_AFTER', None),
        ('<B1-Motion>', (20, 30)),
        ('<ButtonRelease-1>', (30, 40))
    ))
    elem.drag.to.assert_called_with(30, 40)
    assert '.drag.to(30, 40' in last_line(result_out)


# Mouse right button click actions

@mainloop_testfunc
def test_swipe_element(mocks, result_out):
    # right down-move-up is translated to swipe with ui element
    elem = set_element_find_result(mocks, resourceName='abc')
    mouse_events(mocks, (
        ('<Button-2>', (10, 20)),
        ('<B2-Motion>', (30, 30)),
        ('<ButtonRelease-2>', (50, 40))
    ))
    elem.swipe.assert_called_with('right', steps=10)
    assert '.swipe(\'right\'' in last_line(result_out)


@mainloop_testfunc
def test_drag_element_to_element(mocks, result_out):
    # right down-hold-move-up is translated to drag with
    #   start=uielement, end=uielement
    elem = set_element_find_result(mocks, resourceName='abc')
    mouse_events(mocks, (
        ('<Button-2>', (10, 20)),
        ('##EXEC_AFTER', None),
        ('<B2-Motion>', (20, 30)),
        ('<ButtonRelease-2>', (30, 40))
    ))
    elem.drag.to.assert_called_with(resourceId='abc')
    assert '.drag.to(resourceId=\'abc\'' in last_line(result_out)


# Mouse right button click menu commands

def execute_rightclickmenu_command(mocks, command_tag, position):
    mouse_events(mocks, (
        ('<Button-2>', position),
        ('<ButtonRelease-2>', position),
    ))
    menu = mocks.uiroot.nametowidget('menu')
    menu.process_event(command_tag)


@mainloop_testfunc
def test_click_element(mocks, result_out):
    # right click menu - click
    elem = set_element_find_result(mocks, resourceName='abc')
    execute_rightclickmenu_command(mocks, 'Click', (10, 20))
    elem.click.assert_called_with()
    assert '.click' in last_line(result_out)


@mainloop_testfunc
def test_long_click_element(mocks, result_out):
    # right click menu - long click
    elem = set_element_find_result(mocks, resourceName='abc')
    execute_rightclickmenu_command(mocks, 'Long click', (10, 20))
    elem.long_click.assert_called_with()
    assert '.long_click' in last_line(result_out)


def textentrywindow_set_text_entry(textentrywindow, text):
    textentry = textentrywindow.nametowidget('textentry')
    textentry.get.return_value = text


def dialog_click_ok(dialog):
    ok_button = dialog.nametowidget('ok_button')
    ok_button.process_event(None)


@mainloop_testfunc
def test_enter_text_element(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')

    def actions_when_textentrywindow_displayed(textentrywindow):
        textentrywindow_set_text_entry(textentrywindow, 'ABCDEF')
        dialog_click_ok(textentrywindow)

    canvas = mocks.uiroot.nametowidget('mainframe.canvas')
    canvas.wait_window.side_effect = actions_when_textentrywindow_displayed

    execute_rightclickmenu_command(mocks, 'Enter text', (10, 20))

    elem.set_text.assert_called_with('ABCDEF')
    assert '.set_text(\'ABCDEF\')' in last_line(result_out)


@mainloop_testfunc
def test_enter_text_nonelement(mocks, result_out):

    def actions_when_textentrywindow_displayed(textentrywindow):
        textentrywindow_set_text_entry(textentrywindow, 'aB')
        dialog_click_ok(textentrywindow)

    canvas = mocks.uiroot.nametowidget('mainframe.canvas')
    canvas.wait_window.side_effect = actions_when_textentrywindow_displayed

    execute_rightclickmenu_command(mocks, 'Enter text', (10, 20))

    mocks.device.press.assert_has_calls([
        call(29, None), call(30, 1)])
    assert '.press(30, 1)'.format() in last_line(result_out)


def pinchwindow_set(pinchwindow, percent, steps):
    slider = pinchwindow.nametowidget('pinchinslider')
    slider.get.return_value = percent
    entry = pinchwindow.nametowidget('steps')
    entry.textvariable.get.return_value = steps


@mainloop_testfunc
def test_pinch_in_element(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')

    def actions_when_pinchwindow_displayed(pinchwindow):
        pinchwindow_set(pinchwindow, 0.5, 5)
        dialog_click_ok(pinchwindow)

    canvas = mocks.uiroot.nametowidget('mainframe.canvas')
    canvas.wait_window.side_effect = actions_when_pinchwindow_displayed

    execute_rightclickmenu_command(mocks, 'Pinch in', (10, 20))
    mocks.uiroot.execute_after_func()

    elem.pinch.In.assert_called_with(percent=50, steps=5)
    last_line_str = last_line(result_out)
    assert '.pinch.In(' in last_line_str
    assert 'percent=50' in last_line_str
    assert 'steps=5' in last_line_str


@mainloop_testfunc
def test_pinch_out_element(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')

    def actions_when_pinchwindow_displayed(pinchwindow):
        pinchwindow_set(pinchwindow, 0.5, 5)
        dialog_click_ok(pinchwindow)

    canvas = mocks.uiroot.nametowidget('mainframe.canvas')
    canvas.wait_window.side_effect = actions_when_pinchwindow_displayed

    execute_rightclickmenu_command(mocks, 'Pinch out', (10, 20))
    mocks.uiroot.execute_after_func()

    elem.pinch.Out.assert_called_with(percent=50, steps=5)
    last_line_str = last_line(result_out)
    assert '.pinch.Out(' in last_line_str
    assert 'percent=50' in last_line_str
    assert 'steps=5' in last_line_str
