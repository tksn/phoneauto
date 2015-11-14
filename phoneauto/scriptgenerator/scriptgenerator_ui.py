# -*- coding: utf-8 -*-
"""scriptgenerator GUI

:copyright: (c) 2015 by tksn
:license: MIT
"""
# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from __future__ import unicode_literals, print_function
import contextlib
import math
import platform
import tkinter
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw


@contextlib.contextmanager
def display_wait(root_window):
    """Displays wait icon while context is alive"""
    root_window.config(cursor='wait')
    root_window.update()
    yield
    root_window.config(cursor='')


class ScriptGeneratorUI(object):
    """Automation script generator UI"""

    _MOUSE_MOVE_THRESH = 20
    _MOUSE_HOLD_MS = 1000
    _CLICKCIRCLE_RADIUS = 5

    def __init__(self, scale=0.3, platform_sys=None):
        """Initialization

        Args:
            scale (float):
                magnification scale which is used when screenshot
                is displayed in this UI
        """
        self._controller = None
        self._scale = scale
        self._screenshot = None
        self._mouse_action = None

        self._hold_timer_id = None
        self._root = None
        self._platform = platform_sys or platform.system()
        self._create_components()

    def run(self, controller):
        """Launches UI and enter the event loop

        Args:
            controller (object):
                scriptgenerator object
        """
        self._controller = controller
        self._acquire_screen()
        self._root.mainloop()

    def _create_components(self):
        """Creates UI components and builds up application UI"""
        from tkinter import N, W, E, S

        self._root = tkinter.Tk()
        self._root.title('phoneauto-scriptgenerator')

        mainframe = ttk.Frame(self._root, name='mainframe')
        mainframe.grid(row=0, column=0, sticky=(N, W, E, S))

        canvas = self._display_placeholder_screen()
        canvas.grid(row=1, column=0, columnspan=3, sticky=(N, W, E, S))

        back_button = ttk.Button(mainframe, text='Back',
                                 command=self._back,
                                 name='back_button')
        back_button.grid(row=2, column=0, sticky=(N, W, E, S))
        home_button = ttk.Button(mainframe, text='Home',
                                 command=self._home,
                                 name='home_button')
        home_button.grid(row=2, column=1, sticky=(N, W, E, S))
        recent_button = ttk.Button(mainframe, text='Recent Apps',
                                   command=self._recent_apps,
                                   name='recent_button')
        recent_button.grid(row=2, column=2, sticky=(N, W, E, S))

        canvas.bind('<Button-1>', self._on_mouse_left_down)
        canvas.bind('<ButtonRelease-1>', self._on_mouse_left_up)
        canvas.bind('<B1-Motion>', self._on_mouse_move)

        rbutton_events = (
            ('<Button-2>', '<ButtonRelease-2>', '<B2-Motion>')
            if self._platform == 'Darwin'
            else ('<Button-3>', '<ButtonRelease-3>', '<B3-Motion>'))
        canvas.bind(rbutton_events[0], self._on_mouse_right_down)
        canvas.bind(rbutton_events[1], self._on_mouse_right_up)
        canvas.bind(rbutton_events[2], self._on_mouse_move)

        self._root.bind('r', self._acquire_screen)
        self._root.update()

    def _device_call(self, method, *args, **kwargs):
        """Call method which interacts with the device"""
        with display_wait(self._root):
            method(*args, **kwargs)

    def _display_placeholder_screen(self):
        """Displays placeholder (Initializing message) screen
        before actual screenshot is aquired
        """
        from tkinter import NW
        width, height = 400, 400
        placeholder = Image.new(mode='RGB', size=(width, height))
        draw = ImageDraw.Draw(placeholder)
        draw.text((10, 10), 'Initializing...')
        placeholder_tk = ImageTk.PhotoImage(placeholder)
        mainframe = self._root.nametowidget('mainframe')
        canvas = tkinter.Canvas(mainframe,
                                width=width, height=height, name='canvas')
        image_id = canvas.create_image(0, 0, anchor=NW, image=placeholder_tk)
        self._screenshot = {'image': placeholder_tk, 'id': image_id,
                            'size': (width, height)}
        return canvas

    def _acquire_screen(self, _=None):
        """Acquires screenshot from the device, and place it on the UI's canvas

        Returns:        self._cancel_hold_timer()
        self._mouse_action['current'] = event.x, event.y
        self._root.update()


            Tkinter.Canvas: canvas object
        """
        from tkinter import NW

        with display_wait(self._root):
            scr = self._controller.get_screenshot()
        if scr is None:
            raise RuntimeError('Failed to acquire screenshot')
        width, height = (int(scr.width * self._scale),
                         int(scr.height * self._scale))
        screenshot = ImageTk.PhotoImage(
            scr.resize((width, height), Image.ANTIALIAS))

        canvas = self._root.nametowidget('mainframe.canvas')
        canvas.delete(self._screenshot['id'])
        canvas.config(width=width, height=height)
        image_id = canvas.create_image(0, 0, anchor=NW, image=screenshot)
        self._screenshot = {'image': screenshot, 'id': image_id,
                            'size': (width, height)}
        return canvas

    def _back(self):
        """Callback for back button press event"""
        self._device_call(self._controller.back)

    def _home(self):
        """Callback for home button press event"""
        self._device_call(self._controller.home)

    def _recent_apps(self):
        """Callback for recent apps button press event"""
        self._device_call(self._controller.recent_apps)

    def _descale(self, coord):
        """Converts a coordinate from canvas-coordinats to
        device-screen-coorinates

        Args:
            coord (tuple): coordinats (x, y)
        """
        return int(coord[0] / self._scale), int(coord[1] / self._scale)

    def _click_uielement(self):
        """Callback for Click element event"""
        position = self._descale(self._mouse_action['start'])
        self._device_call(self._controller.click_uielement, position)

    def _long_click_uielement(self):
        """Callback for Long-click element event"""
        position = self._descale(self._mouse_action['start'])
        self._device_call(self._controller.long_click_uielement, position)

    def _enter_text(self):
        """Callback for Enter text event"""
        from tkinter import NW

        # Create a dialog on the canvas
        canvas = self._root.nametowidget('mainframe.canvas')
        top = tkinter.Toplevel(canvas, name='textentrywindow')
        # Place a TextEntry on the dialog
        entry = ttk.Entry(top, name='textentry')
        entry.grid(row=0, column=0, sticky=NW)

        def on_ok():
            """Callback for ok-click"""
            text = entry.get()
            top.destroy()
            position = self._descale(self._mouse_action['start'])
            self._device_call(self._controller.send_keys, position, text)

        # Place a OK button on the dialog
        ok_button = ttk.Button(top, text='OK', command=on_ok, name='ok_button')
        ok_button.grid(row=0, column=1, sticky=NW)
        canvas.wait_window(top)

    def _pinch_impl(self, pinch_label, pinch_method):
        """Pinch-in/out event handler implementation"""
        from tkinter import NW, SE, StringVar

        # Create a dialog on the canvas
        canvas = self._root.nametowidget('mainframe.canvas')
        top = tkinter.Toplevel(canvas, name='pinchwindow')
        # Place a TextEntry on the dialog
        lebel0 = ttk.Label(top, text=pinch_label, name='pinchlabel')
        lebel0.grid(row=0, column=0, sticky=NW)
        slider = ttk.Scale(top, value=1.0, name='pinchinslider')
        slider.grid(row=0, column=1, sticky=NW)
        lebel1 = ttk.Label(top, text='Steps:', name='steplabel')
        lebel1.grid(row=1, column=0, sticky=NW)
        stepsStr = StringVar(value='10')
        entry = ttk.Entry(top, textvariable=stepsStr, name='steps')
        entry.grid(row=1, column=1, sticky=NW)

        def exec_pinch(percent, steps):
            """Executes pinch action"""
            position = self._descale(self._mouse_action['start'])
            self._device_call(pinch_method, position, percent, steps=steps)

        def on_ok():
            """Callback for ok-click"""
            percent = int(slider.get() * 100)
            steps = int(stepsStr.get())
            top.destroy()
            self._root.after(0, exec_pinch, percent, steps)

        # Place a OK button on the dialog
        ok_button = ttk.Button(top, text='OK', command=on_ok, name='ok_button')
        ok_button.grid(row=0, column=2, rowspan=2, sticky=(NW, SE))
        canvas.wait_window(top)

    def _pinch_in(self):
        """Callback for Pinch-in event"""
        self._pinch_impl('Pinch In:', self._controller.pinch_in)

    def _pinch_out(self):
        """Callback for Pinch-in event"""
        self._pinch_impl('Pinch Out:', self._controller.pinch_out)

    def _fling(self):
        """Callback for fling command

        ToDo:
            Implementation
        """
        raise NotImplementedError()

    def _scroll(self):
        """Callback for scrool command

        ToDo:
            Implementation
        """
        raise NotImplementedError()

    def _set_hold_timer(self):
        """Sets a timer which counts mouse's button-down duration,
        and calls registered function when it is due
        """
        canvas = self._root.nametowidget('mainframe.canvas')
        self._hold_timer_id = canvas.after(self._MOUSE_HOLD_MS,
                                           self._on_mouse_hold)

    def _cancel_hold_timer(self):
        """Cancels mouse left-button-down timer"""
        if not self._hold_timer_id:
            return
        canvas = self._root.nametowidget('mainframe.canvas')
        canvas.after_cancel(self._hold_timer_id)
        self._hold_timer_id = None

    def _on_mouse_hold(self):
        """Callback for left-button-down time due
        Args:
            position (tuple): Current mouse position (x, y)
        """
        self._mouse_action['hold'] = True
        self._draw_mouse_action()

    def _on_mouse_move(self, event):
        """Callback for left-button motion event
        Args:
            event (object): event information which is passed by Tk framework
        """
        self._mouse_action['current'] = event.x, event.y
        if self._mouse_moved():
            self._cancel_hold_timer()
        self._draw_mouse_action()

    def _mouse_moved(self):
        """Queries if mouse is moved"""
        xS, yS = self._mouse_action['start']
        xC, yC = self._mouse_action['current']
        return math.hypot(xC - xS, yC - yS) > self._MOUSE_MOVE_THRESH

    def _draw_mouse_action(self, erase=False):
        """Draws mouse action (swipe, drag, etc) on the screen"""
        canvas = self._root.nametowidget('mainframe.canvas')
        canvas.delete('down_point')
        canvas.delete('move_line')

        if erase:
            return

        xS, yS = self._mouse_action['start']
        xC, yC = self._mouse_action['current']
        color = ('blue' if self._mouse_action['left_or_right'] == 'left'
                 else 'yellow')
        fill = color if self._mouse_action['hold'] else ''

        canvas.create_line(xS, yS, xC, yC,
                           fill=color, width=2, tag='move_line')

        def oval_coords(radius):
            """Returns oval coordinates"""
            tl = tuple(p - radius for p in (xS, yS))
            br = tuple(p + radius for p in (xS, yS))
            return (tl[0], tl[1], br[0], br[1])

        canvas.create_oval(*oval_coords(self._CLICKCIRCLE_RADIUS),
                           outline=color, fill=fill, tag='down_point')

    def _on_mouse_left_down(self, event):
        """Callback for mouse left-button-down event

        Args:
            event (object): event information which is passed by Tk framework
        """
        x, y = event.x, event.y
        self._mouse_action = {
            'start': (x, y),
            'current': (x, y),
            'left_or_right': 'left',
            'hold': False
        }
        self._draw_mouse_action()
        self._set_hold_timer()

    def _on_mouse_left_up(self, event):
        """Callback for left-button-up event
        Args:
            event (object): Event information which is passed by Tk framework
        """
        self._cancel_hold_timer()
        self._mouse_action['current'] = event.x, event.y

        if self._mouse_moved():
            xS, yS = self._descale(self._mouse_action['start'])
            xE, yE = self._descale((event.x, event.y))
            if self._mouse_action['hold']:
                self._device_call(self._controller.drag,
                                  (xS, yS), (xE, yE))
            else:
                self._device_call(self._controller.swipe,
                                  (xS, yS), (xE, yE))
        else:
            x, y = self._descale((event.x, event.y))
            if self._mouse_action['hold']:
                self._device_call(self._controller.long_click, (x, y))
            else:
                self._device_call(self._controller.click, (x, y))

        self._draw_mouse_action(erase=True)

    def _on_mouse_right_down(self, event):
        """Callback for mouse right-button-down event

        Args:
            event (object): event information which is passed by Tk framework
        """
        x, y = event.x, event.y
        self._mouse_action = {
            'start': (x, y),
            'current': (x, y),
            'left_or_right': 'right',
            'hold': False
        }
        self._draw_mouse_action()
        self._set_hold_timer()

    def _on_mouse_right_up(self, event):
        """Callback for right-button-up event
        Args:
            event (object): Event information which is passed by Tk framework
        """
        self._cancel_hold_timer()
        self._mouse_action['current'] = event.x, event.y

        if self._mouse_moved():
            xS, yS = self._descale(self._mouse_action['start'])
            xE, yE = self._descale((event.x, event.y))
            if self._mouse_action['hold']:
                self._device_call(self._controller.drag_to_other,
                                  (xS, yS), (xE, yE))
            else:
                self._device_call(self._controller.swipe_uielement,
                                  (xS, yS), (xE, yE))
        else:
            self._popup_menu((event.x, event.y))

        self._draw_mouse_action(erase=True)

    def _popup_menu(self, position):
        """Displays right-click menu"""
        menu = tkinter.Menu(self._root, name='menu')
        menu.add_command(label='Refresh', command=self._acquire_screen)
        menu.add_command(label='Click', command=self._click_uielement)
        menu.add_command(label='Long click',
                         command=self._long_click_uielement)
        menu.add_command(label='Enter text', command=self._enter_text)
        menu.add_command(label='Pinch in', command=self._pinch_in)
        menu.add_command(label='Pinch out', command=self._pinch_out)
        menu.add_command(label='Fling', command=self._fling)
        menu.add_command(label='Scroll', command=self._scroll)
        menu.post(*position)
