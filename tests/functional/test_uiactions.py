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


def user_input(target_widget, event_name, **kwargs):
    input_item = {
        'widget': target_widget,
        'name': event_name
    }
    input_item.update(kwargs)
    return input_item


def perform_user_input(mocks, events):
    class _Object(object): pass
    for event in events:
        widget = mocks.uiroot.nametowidget(event['widget'])
        coord = event.get('coord')
        if coord:
            ev_arg = _Object()
            ev_arg.x, ev_arg.y = coord
            ev_arg.x_root, ev_arg.y_root = 0, 0 # not used in tests
            widget.process_event(event['name'], ev_arg)
        else:
            widget.process_event(event['name'])
    mocks.uiroot.process_after_func()


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
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-1>', coord=(10, 20)),
        user_input('mainframe.canvas', '<ButtonRelease-1>', coord=(10, 20)),
        user_input('menu', 'Click(xy)')
    ])
    mocks.device.click.assert_called_with(10, 20)
    assert '.click(10, 20)' in last_line(result_out)


@mainloop_testfunc
def test_long_click_xy(mocks, result_out):
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-1>', coord=(10, 20)),
        user_input('mainframe.canvas', '<ButtonRelease-1>', coord=(10, 20)),
        user_input('menu', 'Long click(xy)')
    ])
    mocks.device.long_click.assert_called_with(10, 20)
    assert '.long_click(10, 20)' in last_line(result_out)


@mainloop_testfunc
def test_swipe_xy_to_xy(mocks, result_out):
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-1>', coord=(10, 20)),
        user_input('mainframe.canvas', '<B1-Motion>', coord=(20, 30)),
        user_input('mainframe.canvas', '<ButtonRelease-1>', coord=(30, 40)),
        user_input('menu', 'Swipe(xy -> xy)')
    ])
    mocks.device.swipe.assert_called_with(10, 20, 30, 40, steps=10)
    assert '.swipe(10, 20, 30, 40' in last_line(result_out)


@mainloop_testfunc
def test_drag_xy_to_xy(mocks, result_out):
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-1>', coord=(10, 20)),
        user_input('mainframe.canvas', '<B1-Motion>', coord=(20, 30)),
        user_input('mainframe.canvas', '<ButtonRelease-1>', coord=(30, 40)),
        user_input('menu', 'Drag(xy -> xy)')
    ])
    mocks.device.drag.assert_called_with(10, 20, 30, 40)
    assert '.drag(10, 20, 30, 40' in last_line(result_out)


@mainloop_testfunc
def test_drag_object_to_xy(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-1>', coord=(10, 20)),
        user_input('mainframe.canvas', '<B1-Motion>', coord=(20, 30)),
        user_input('mainframe.canvas', '<ButtonRelease-1>', coord=(30, 40)),
        user_input('menu', 'Drag(object -> xy)')
    ])
    elem.drag.to.assert_called_with(30, 40)
    assert '.drag.to(30, 40' in last_line(result_out)


@mainloop_testfunc
def test_fling_vertical_forward(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-1>', coord=(10, 50)),
        user_input('mainframe.canvas', '<B1-Motion>', coord=(10, 30)),
        user_input('mainframe.canvas', '<ButtonRelease-1>', coord=(10, 10)),
        user_input('menu', 'Fling')
    ])
    elem.fling.vert.forward.assert_called_with()
    assert '.fling.vert.forward()' in last_line(result_out)


@mainloop_testfunc
def test_scroll_horizontal_backward(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-1>', coord=(10, 10)),
        user_input('mainframe.canvas', '<B1-Motion>', coord=(30, 10)),
        user_input('mainframe.canvas', '<ButtonRelease-1>', coord=(50, 10)),
        user_input('menu', 'Scroll')
    ])
    elem.scroll.horiz.backward.assert_called_with()
    assert '.scroll.horiz.backward()' in last_line(result_out)


# Mouse right button click actions

@mainloop_testfunc
def test_click_object(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(10, 20)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(10, 20)),
        user_input('menu', 'Click(object)')
    ])
    elem.click.assert_called_with()
    assert '.click()' in last_line(result_out)


@mainloop_testfunc
def test_long_click_object(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(10, 20)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(10, 20)),
        user_input('menu', 'Long click(object)')
    ])
    elem.long_click.assert_called_with()
    assert '.long_click()' in last_line(result_out)


def dialog_set_text_entry(dialog, text):
    textentry = dialog.nametowidget('textentry')
    textentry.get.return_value = text


def dialog_click_ok(dialog):
    ok_button = dialog.nametowidget('ok_button')
    ok_button.process_event(None)


def set_dialog_action(mocks, widget_name, action_func):
    canvas = mocks.uiroot.nametowidget(widget_name)
    canvas.wait_window.side_effect = action_func


@mainloop_testfunc
def test_enter_text_on_object(mocks, result_out):

    def actions_when_dialog_displayed(dialog):
        dialog_set_text_entry(dialog, 'ABCDEF')
        dialog_click_ok(dialog)

    set_dialog_action(
        mocks, 'mainframe.canvas', actions_when_dialog_displayed)

    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(10, 20)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(10, 20)),
        user_input('menu', 'Enter text')
    ])

    elem.set_text.assert_called_with('ABCDEF')
    assert '.set_text(\'ABCDEF\')' in last_line(result_out)


@mainloop_testfunc
def test_enter_text_without_object(mocks, result_out):

    def actions_when_dialog_displayed(dialog):
        dialog_set_text_entry(dialog, 'aB')
        dialog_click_ok(dialog)

    set_dialog_action(
        mocks, 'mainframe.canvas', actions_when_dialog_displayed)

    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(10, 20)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(10, 20)),
        user_input('menu', 'Enter text')
    ])

    mocks.device.press.assert_has_calls([
        call(29, None), call(30, 1)])
    assert '.press(30, 1)'.format() in last_line(result_out)


def pinchdialog_set(dialog, percent, steps):
    slider = dialog.nametowidget('pinchinslider')
    slider.get.return_value = percent
    entry = dialog.nametowidget('steps')
    entry.textvariable.get.return_value = steps


@mainloop_testfunc
def test_pinch_in(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')

    def actions_when_pinchdialog_displayed(pinchdialog):
        pinchdialog_set(pinchdialog, 0.5, 5)
        dialog_click_ok(pinchdialog)

    set_dialog_action(
        mocks, 'mainframe.canvas', actions_when_pinchdialog_displayed)

    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(10, 20)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(10, 20)),
        user_input('menu', 'Pinch in')
    ])

    elem.pinch.In.assert_called_with(percent=50, steps=5)
    last_line_str = last_line(result_out)
    assert '.pinch.In(' in last_line_str
    assert 'percent=50' in last_line_str
    assert 'steps=5' in last_line_str


@mainloop_testfunc
def test_pinch_out(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')

    def actions_when_pinchdialog_displayed(pinchdialog):
        pinchdialog_set(pinchdialog, 0.5, 5)
        dialog_click_ok(pinchdialog)

    set_dialog_action(
        mocks, 'mainframe.canvas', actions_when_pinchdialog_displayed)

    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(10, 20)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(10, 20)),
        user_input('menu', 'Pinch out')
    ])

    elem.pinch.Out.assert_called_with(percent=50, steps=5)
    last_line_str = last_line(result_out)
    assert '.pinch.Out(' in last_line_str
    assert 'percent=50' in last_line_str
    assert 'steps=5' in last_line_str


@mainloop_testfunc
def test_swipe_object_with_direction(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(50, 10)),
        user_input('mainframe.canvas', '<B2-Motion>', coord=(30, 10)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(10, 10)),
        user_input('menu', 'Swipe(object + direction)')
    ])
    elem.swipe.assert_called_with('left')
    assert '.swipe(\'left\'' in last_line(result_out)


@mainloop_testfunc
def test_drag_object_to_object(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(10, 20)),
        user_input('mainframe.canvas', '<B2-Motion>', coord=(20, 30)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(30, 40)),
        user_input('menu', 'Drag(object -> object)')
    ])
    elem.drag.to.assert_called_with(resourceId='abc')
    assert '.drag.to(resourceId=\'abc\'' in last_line(result_out)


@mainloop_testfunc
def test_fling_vertical_to_beginning(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(10, 10)),
        user_input('mainframe.canvas', '<B2-Motion>', coord=(10, 30)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(10, 50)),
        user_input('menu', 'Fling to end')
    ])
    elem.fling.vert.toBeginning.assert_called_with()
    assert '.fling.vert.toBeginning()' in last_line(result_out)


@mainloop_testfunc
def test_scroll_horizontal_to_end(mocks, result_out):
    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(50, 10)),
        user_input('mainframe.canvas', '<B2-Motion>', coord=(30, 10)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(10, 10)),
        user_input('menu', 'Scroll to end')
    ])
    elem.scroll.horiz.toEnd.assert_called_with()
    assert '.scroll.horiz.toEnd()' in last_line(result_out)


@mainloop_testfunc
def test_scroll_vertical_to_text(mocks, result_out):

    def actions_when_dialog_displayed(dialog):
        dialog_set_text_entry(dialog, 'defgh')
        dialog_click_ok(dialog)

    set_dialog_action(
        mocks, 'mainframe.canvas', actions_when_dialog_displayed)

    elem = set_element_find_result(mocks, resourceName='abc')
    perform_user_input(mocks, [
        user_input('mainframe.canvas', '<Button-2>', coord=(10, 10)),
        user_input('mainframe.canvas', '<B2-Motion>', coord=(10, 30)),
        user_input('mainframe.canvas', '<ButtonRelease-2>', coord=(10, 50)),
        user_input('menu', 'Scroll to text')
    ])
    elem.scroll.vert.to.assert_called_with(text='defgh')
    assert '.scroll.vert.to(text=\'defgh\')' in last_line(result_out)
