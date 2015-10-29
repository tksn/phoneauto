# -*- coding: utf-8 -*-
"""scriptgenerator GUI

:copyright: (c) 2015 by tksn
:license: MIT
"""
# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from __future__ import unicode_literals, print_function
import tkinter
from tkinter import ttk
from PIL import Image, ImageTk


class ScriptGeneratorUI(object):
    """Automation script generator UI"""

    _MOUSEMOVE_NORM_THRESHOULD = 60.0
    _MOUSEDRAG_HOLD_MS = 1000
    _HOLDCIRCLE_RADIUS = 10

    def __init__(self, controller, scale=0.3):
        """Initialization

        Args:
            controller (object):
                scriptgenerator object
            scale (float):
                magnification scale which is used when screenshot
                is displayed in this UI
        """
        self._controller = controller
        self._scale = scale
        self._screenshot = None
        self._left_click_events = []
        self._right_click_pos = None
        self._hold_timer_id = None
        self._root = None
        self._menu = None

    def run(self):
        """Launches UI and enter the event loop"""
        self._create_components()
        self._root.mainloop()

    def _create_components(self):
        """Creates UI components and builds up application UI"""
        from tkinter import N, W, E, S

        self._root = tkinter.Tk()
        self._root.title('phoneauto-scriptgenerator')

        mainframe = ttk.Frame(self._root, name='mainframe')
        mainframe.grid(row=0, column=0, sticky=(N, W, E, S))

        canvas = self._acquire_screen()
        canvas.focus_set()
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

        menu = tkinter.Menu(mainframe, name='menu')
        menu.add_command(label='Refresh', command=self._acquire_screen)
        menu.add_command(label='Enter text', command=self._enter_text)
        self._menu = menu

        canvas.bind('<Button-1>', self._on_mouse_left_down)
        canvas.bind('<ButtonRelease-1>', self._on_mouse_left_up)
        canvas.bind('<B1-Motion>', self._on_mouse_left_motion)
        canvas.bind('<Button-2>', self._on_mouse_right)
        self._root.bind('r', self._acquire_screen)

    def _acquire_screen(self, _=None):
        """Aquires screenshot from the device, and place it on the UI's canvas

        Returns:
            Tkinter.Canvas: canvas object
        """
        from tkinter import NW

        scr = self._controller.get_screenshot()
        if scr is None:
            raise RuntimeError('Failed to acquire screenshot')
        width, height = (int(scr.width * self._scale),
                         int(scr.height * self._scale))
        screenshot = ImageTk.PhotoImage(
            scr.resize((width, height), Image.ANTIALIAS))

        if self._screenshot is None:  # when called from _create_components
            mainframe = self._root.nametowidget('mainframe')
            canvas = tkinter.Canvas(mainframe,
                                    width=screenshot.width(),
                                    height=screenshot.height(),
                                    name='canvas')
        else:  # when called in response to refresh event
            canvas = self._root.nametowidget('mainframe.canvas')
            canvas.delete(self._screenshot['id'])
        image_id = canvas.create_image(0, 0, anchor=NW, image=screenshot)
        self._screenshot = {'image': screenshot, 'id': image_id}
        return canvas

    def _back(self):
        """Callback for back button press event"""
        self._controller.back()

    def _home(self):
        """Callback for home button press event"""
        self._controller.home()

    def _recent_apps(self):
        """Callback for recent apps button press event"""
        self._controller.recent_apps()

    def _descale(self, coord):
        """Converts a coordinate from canvas-coordinats to
        device-screen-coorinates

        Args:
            coord (tuple): coordinats (x, y)
        """
        return int(coord[0] / self._scale), int(coord[1] / self._scale)

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
            position = self._descale(self._right_click_pos)
            self._controller.send_keys(position, text)

        # Place a OK button on the dialog
        ok_button = ttk.Button(top, text='OK', command=on_ok, name='ok_button')
        ok_button.grid(row=0, column=1, sticky=NW)

        canvas.wait_window(top)

    def _set_hold_timer(self, position):
        """Sets a timer which counts mouse's left-button-down duration,
        and calls registered function when it is due

        Args:
            position (tuple): mouse position (x, y)
        """
        canvas = self._root.nametowidget('mainframe.canvas')
        self._hold_timer_id = canvas.after(self._MOUSEDRAG_HOLD_MS,
                                           self._on_mouse_left_hold,
                                           position)

    def _cancel_hold_timer(self):
        """Cancels mouse left-button-down timer"""
        if not self._hold_timer_id:
            return
        canvas = self._root.nametowidget('mainframe.canvas')
        canvas.after_cancel(self._hold_timer_id)
        self._hold_timer_id = None

    def _on_mouse_left_down(self, event):
        """Callback for mouse left-button-down event

        Args:
            event (object): event information which is passed by Tk framework
        """
        x, y = event.x, event.y
        self._left_click_events = [{'type': 'press', 'coord': (x, y)}]
        self._set_hold_timer((x, y))

    def _draw_mouse_actions(self, current_position):
        """Draw mouse locus on the canvas

        Args:
            current_position (tuple): Current mouse position (x, y)
        """
        canvas = self._root.nametowidget('mainframe.canvas')
        canvas.delete('hold_point')
        canvas.delete('mouse_move')

        line_coords = []
        for evt in self._left_click_events:
            line_coords.extend(evt['coord'])
        line_coords.extend(current_position)
        canvas.create_line(*line_coords,
                           fill='blue', width=2, tag='mouse_move')

        for evt in self._left_click_events[1:]:
            topleft = tuple(
                p - self._HOLDCIRCLE_RADIUS for p in evt['coord'])
            bottomright = tuple(
                p + self._HOLDCIRCLE_RADIUS for p in evt['coord'])
            canvas.create_oval(topleft[0], topleft[1],
                               bottomright[0], bottomright[1],
                               outline='blue', tag='hold_point')

    def _erase_mouse_actions(self):
        """Erase mouse locus drawings from the canvas"""
        canvas = self._root.nametowidget('mainframe.canvas')
        canvas.delete('hold_point')
        canvas.delete('mouse_move')

    def _on_mouse_left_hold(self, position):
        """Callback for left-button-down time due
        Args:
            position (tuple): Current mouse position (x, y)
        """
        x, y = position
        hold_events = self._left_click_events[1:]
        last_hold_pos = next((ev['coord'] for ev in reversed(hold_events)),
                             (-1, -1))
        if x != last_hold_pos[0] or y != last_hold_pos[1]:
            hold_event = {
                'type': 'hold', 'coord': (x, y),
                'duration': self._MOUSEDRAG_HOLD_MS}
            dummy_release_event = {'type': 'release', 'coord': (x, y)}
            event_chain = (self._left_click_events +
                           [hold_event, dummy_release_event])
            if self._controller.query_touch_action(event_chain):
                self._left_click_events += [hold_event]
                self._draw_mouse_actions((x, y))
        self._set_hold_timer(position)

    def _on_mouse_left_motion(self, event):
        """Callback for left-button motion event
        Args:
            event (object): Event information which is passed by Tk framework
        """
        x, y = event.x, event.y
        self._cancel_hold_timer()
        self._set_hold_timer((x, y))
        dummy_release_event = {'type': 'release', 'coord': (x, y)}
        event_chain = self._left_click_events + [dummy_release_event]
        if self._controller.query_touch_action(event_chain):
            self._draw_mouse_actions((x, y))

    def _on_mouse_left_up(self, event):
        """Callback for left-button-up event
        Args:
            event (object): Event information which is passed by Tk framework
        """
        x, y = event.x, event.y
        self._cancel_hold_timer()
        self._erase_mouse_actions()

        event_chain = []
        for evt in self._left_click_events:
            ev1 = dict(evt)
            ev1['coord'] = self._descale(evt['coord'])
            event_chain.append(ev1)
        x, y = self._descale((x, y))
        event_chain.append({'type': 'release', 'coord': (x, y)})
        self._controller.touch_action(event_chain)

    def _on_mouse_right(self, event):
        """Callback for right-button-click event
        Args:
            event (object): Event information which is passed by Tk framework
        """
        self._right_click_pos = (event.x, event.y)
        self._menu.post(event.x_root, event.y_root)
