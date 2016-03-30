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
import logging
import math
import platform
import tkinter
import tkinter.font
from tkinter import ttk
import time
from PIL import Image, ImageTk, ImageDraw, ImageFont

from phoneauto.scriptgenerator.exception import (
    UiInconsitencyError, UiObjectNotFound)
from phoneauto.scriptgenerator.screenrecord import Screenrecord


def get_filedialog():  # pragma: no cover
    """Returns filedialog module object

    Returns appropriate filedialog module depending on sys.version.
    The reason doing this is because python.future's tkinter.filedialog
    is alias to FileDialog, not to tkFileDialog.
    """
    import sys
    if sys.version_info.major >= 3:
        import tkinter.filedialog
        return tkinter.filedialog
    else:
        import tkFileDialog
        return tkFileDialog


@contextlib.contextmanager
def display_wait(root_window):
    """Displays wait icon while context is alive"""
    root_window.config(cursor='wait')
    root_window.update()
    yield
    root_window.config(cursor='')


class ScriptGeneratorUI(object):
    """Automation script generator UI"""

    _SCR_REFRESH_INTERVAL = 100
    _HVIEW_REFRESH_INTERVAL = 3
    _HVIEW_REFRESH_INTERVAL_AFTER_SCR_REFRESH = 1
    _MOUSE_MOVE_THRESH = 20
    _CLICKCIRCLE_RADIUS = 5

    def __init__(self,
                 screen_size=(480, 800),
                 platform_sys=None,
                 timeouts=None):
        """Initialization

        Args:
            scale (float):
                magnification scale which is used when screenshot
                is displayed in this UI
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('initialization start')
        self._controller = None
        self._scale = None
        self._screenshot = None
        self._mouse_action = None
        self.hierarchy_view_timestamp = 0

        timeouts = timeouts or {}
        self._wait_timeouts = {}
        default_timeouts = {
            'idle': 5000, 'update': 1000, 'exists': 5000, 'gone': 5000}
        for name, default_value in default_timeouts.items():
            self._wait_timeouts[name] = timeouts.get(name, default_value)

        self._hold_timer_id = None
        self._root = None
        self._platform = platform_sys or platform.system()
        self._screenrecord = Screenrecord(
            width=screen_size[0], height=screen_size[1])
        self._build_ui()
        self.logger.info('initialization end')

    def run(self, controller):
        """Launches UI and enter the event loop

        Args:
            controller (object):
                scriptgenerator object
        """
        self._controller = controller
        self._enable_ui()
        try:
            self._root.mainloop()
        finally:
            if self._screenrecord:
                self._screenrecord.join()
                self._screenrecord = None

    def _build_ui(self):
        """Creates UI components and builds up application UI"""
        from tkinter import N, W, E, S

        self._root = tkinter.Tk()
        self._root.title('phoneauto-scriptgenerator')

        mainframe = ttk.Frame(self._root, name='mainframe')
        mainframe.grid(row=0, column=0, sticky=(N, W, E, S))

        canvas = self._create_canvas(mainframe)
        canvas.grid(row=1, column=0, columnspan=3, sticky=(N, W, E, S))

        back_button = ttk.Button(
            mainframe, text='Back', name='back_button')
        back_button.grid(row=2, column=0, sticky=(N, W, E, S))
        home_button = ttk.Button(
            mainframe, text='Home', name='home_button')
        home_button.grid(row=2, column=1, sticky=(N, W, E, S))
        recent_button = ttk.Button(
            mainframe, text='Recent Apps', name='recent_button')
        recent_button.grid(row=2, column=2, sticky=(N, W, E, S))

        sidebar = ttk.Frame(self._root, name='sidebar')
        sidebar.grid(row=0, column=1, sticky=(N, W, E, S))
        self._build_sidebar(sidebar)
        self._root.update()

    def _create_canvas(self, parent):
        """Displays placeholder (Initializing message) screen
        before actual screenshot is aquired
        """
        from tkinter import NW

        screencap = self._screenrecord.capture_oneshot()

        placeholder_tk = ImageTk.PhotoImage(screencap)
        canvas = tkinter.Canvas(parent,
                                width=screencap.width, height=screencap.height,
                                name='canvas')
        image_id = canvas.create_image(0, 0, anchor=NW, image=placeholder_tk)

        text = 'Initializing'
        text_x, text_y = screencap.width / 2, screencap.height / 2
        text_id = canvas.create_text(
            text_x, text_y, text=text, fill='white',
            font=('Courier', 32), tag='init_text')
        bgrect_id = canvas.create_rectangle(
            canvas.bbox(text_id), fill='black', tag='init_text_bg')
        canvas.tag_lower(bgrect_id, text_id)

        self._screenshot = {'image': placeholder_tk, 'id': image_id,
                            'size': screencap.size}
        return canvas

    @staticmethod
    def _build_sidebar(sidebar):
        """Constructs side panel"""

        def button(master, widget_options, pack_options=None):
            """Creates a button"""
            pack_options = pack_options or {'fill': tkinter.X}
            btn = ttk.Button(master, **widget_options)
            btn.pack(**pack_options)

        def label(master, widget_options, pack_options=None):
            """Creates a label"""
            pack_options = (pack_options or
                            {'fill': tkinter.X, 'anchor': tkinter.NW})
            btn = ttk.Label(master, **widget_options)
            btn.pack(**pack_options)

        def separator(master, widget_options, pack_options=None):
            """Creates a separator"""
            pack_options = pack_options or {'fill': tkinter.X, 'pady': 5}
            sep = ttk.Separator(master, **widget_options)
            sep.pack(**pack_options)

        button(sidebar, {'name': 'refresh_button', 'text': 'Refresh'})
        button(sidebar, {'name': 'screenshot_button', 'text': 'Screenshot'})
        separator(sidebar, {'orient': tkinter.HORIZONTAL})
        button(sidebar, {'name': 'power_button', 'text': 'Power'})
        button(sidebar,
               {'name': 'notification_button', 'text': 'Notification'})
        button(sidebar,
               {'name': 'quicksettings_button', 'text': 'QuickSettings'})
        button(sidebar, {'name': 'volume_up_button', 'text': 'Volume Up'})
        button(sidebar, {'name': 'volume_down_button', 'text': 'Volume Down'})

        label(sidebar, {'text': 'Orientation:'})
        frm = ttk.Frame(sidebar, name='orientation_frame')

        def orient_button(name, text):
            """Orientation button"""
            button(frm, {'name': name, 'text': text, 'width': 2},
                   {'side': tkinter.LEFT})
        orient_button('orientation_natural', 'N')
        orient_button('orientation_left', 'L')
        orient_button('orientation_right', 'R')
        orient_button('orientation_upsidedown', 'U')
        orient_button('orientation_unfreeze', 'Z')
        frm.pack()

        separator(sidebar, {'orient': tkinter.HORIZONTAL})
        label(sidebar, {'text': 'Insert line to script:'})
        button(sidebar,
               {'name': 'ins_screenshot_cap',
                'text': 'screenshot capture'})
        button(sidebar,
               {'name': 'ins_wait_idle', 'text': 'wait.idle'})
        button(sidebar,
               {'name': 'ins_wait_update', 'text': 'wait.update'})

        separator(sidebar, {'orient': tkinter.HORIZONTAL})

        text = tkinter.Text(sidebar, width=30, name='infotext')
        text.pack(padx=3, pady=2)

    def _enable_ui(self):
        """2nd phase initialization - activate UI"""
        self._bind_commands_to_widgets()
        self._acquire_hierarchy_view()
        self._set_screen_scale()
        self._screenrecord.start()
        self._kick_video_update()
        self._refresh_screen()
        canvas = self._root.nametowidget('mainframe.canvas')
        canvas.delete('init_text')
        canvas.delete('init_text_bg')

    def _bind_commands_to_widgets(self):
        """Initialization after controller became available"""

        def bind_custom_command(widget_name, command):
            self._root.nametowidget(widget_name).config(command=command)

        def bind_command(widget_name, command_name, **command_kwargs):
            bind_custom_command(widget_name,
                                self.__get_command_wrap(command_name,
                                                        **command_kwargs))

        bind_command('mainframe.back_button', 'press_key',
                     key_name='BACK')
        bind_command('mainframe.home_button', 'press_key',
                     key_name='HOME')
        bind_command('mainframe.recent_button', 'press_key',
                     key_name='APP_SWITCH')
        bind_custom_command('sidebar.refresh_button',
                            lambda _: self._acquire_hierarchy_view())
        bind_custom_command('sidebar.screenshot_button',
                            self._take_screenshot)
        bind_command('sidebar.power_button', 'press_key',
                     key_name='POWER')
        bind_command('sidebar.notification_button',
                     'open_notification')
        bind_command('sidebar.quicksettings_button',
                     'open_quick_settings')
        bind_command('sidebar.volume_up_button', 'press_key',
                     key_name='VOLUME_UP')
        bind_command('sidebar.volume_down_button', 'press_key',
                     key_name='VOLUME_DOWN')

        bind_command('sidebar.orientation_frame.orientation_natural',
                     'set_orientation', orientation='natural')
        bind_command('sidebar.orientation_frame.orientation_left',
                     'set_orientation', orientation='left')
        bind_command('sidebar.orientation_frame.orientation_right',
                     'set_orientation', orientation='right')
        bind_command(
            'sidebar.orientation_frame.orientation_upsidedown',
            'set_orientation', orientation='upsidedown')
        bind_command('sidebar.orientation_frame.orientation_unfreeze',
                     'set_orientation', orientation='unfreeze')

        bind_command('sidebar.ins_screenshot_cap',
                     'insert_screenshot_capture')
        bind_command('sidebar.ins_wait_idle', 'insert_wait',
                     for_what='idle', timeout=self._wait_timeouts['idle'])
        bind_command('sidebar.ins_wait_update', 'insert_wait',
                     for_what='update',
                     timeout=self._wait_timeouts['update'])

        canvas = self._root.nametowidget('mainframe.canvas')
        canvas.bind('<Motion>', self._on_mouse_motion)
        canvas.bind('<Leave>', self._on_mouse_leave)
        canvas.bind('<Button-1>', self._on_mouse_left_down)
        canvas.bind('<ButtonRelease-1>', self._on_mouse_left_up)
        canvas.bind('<B1-Motion>', self._on_mouse_b1motion)

        rbutton_events = (
            ('<Button-2>', '<ButtonRelease-2>', '<B2-Motion>')
            if self._platform == 'Darwin'
            else ('<Button-3>', '<ButtonRelease-3>', '<B3-Motion>'))
        canvas.bind(rbutton_events[0], self._on_mouse_right_down)
        canvas.bind(rbutton_events[1], self._on_mouse_right_up)
        canvas.bind(rbutton_events[2], self._on_mouse_b1motion)

    def _kick_video_update(self):
        """Workaround: Some movements on the device's screen are needed
        in order to pull up first few frames from the device..
        """
        self._controller.execute('video_init')

    def _refresh_screen(self):
        from tkinter import NW
        frame = None
        while not self._screenrecord.queue.empty():
            frame = self._screenrecord.queue.get_nowait()

        hierarchy_view_age = time.time() - self.hierarchy_view_timestamp
        if frame:
            disp_frame = ImageTk.PhotoImage(frame)
            canvas = self._root.nametowidget('mainframe.canvas')
            canvas.delete(self._screenshot['id'])
            canvas.config(width=self._screenrecord.width,
                          height=self._screenrecord.height)
            all_other_items = canvas.find_all()
            image_id = canvas.create_image(0, 0, anchor=NW, image=disp_frame)
            if all_other_items:
                canvas.tag_lower(image_id, all_other_items[0])
            self._screenshot = {'image': disp_frame, 'id': image_id}
            if (hierarchy_view_age >
                    self._HVIEW_REFRESH_INTERVAL_AFTER_SCR_REFRESH):
                self._acquire_hierarchy_view()
        elif hierarchy_view_age > self._HVIEW_REFRESH_INTERVAL:
            self._acquire_hierarchy_view()
        self._root.after(self._SCR_REFRESH_INTERVAL, self._refresh_screen)

    def _acquire_hierarchy_view(self):
        """Acquires screenshot from the device, and place it on the UI's canvas

        Returns:
            Tkinter.Canvas: canvas object
        """
        self._controller.execute('update_view_dump')
        self.hierarchy_view_timestamp = time.time()

    def _set_screen_scale(self):
        """Sets screen scale information"""
        self._scale = self._screenrecord.get_scale()

    def _descale(self, coord):
        """Converts a coordinate from canvas-coordinats to
        device-screen-coorinates

        Args:
            coord (tuple): coordinats (x, y)
        """
        return int(coord[0] / self._scale[0]), int(coord[1] / self._scale[1])

    def _on_mouse_leave(self, event):
        """Callback for mouse leave event
        Args:
            event (object): event information which is passed by Tk framework
        """
        canvas = self._root.nametowidget('mainframe.canvas')
        canvas.delete('object_rect')

    def _on_mouse_motion(self, event):
        """Callback for mouse motion event
        Args:
            event (object): event information which is passed by Tk framework
        """
        canvas = self._root.nametowidget('mainframe.canvas')
        canvas.delete('object_rect')
        text = self._root.nametowidget('sidebar.infotext')
        text.delete(1.0, tkinter.END)

        command_args = {'start': self._descale((event.x, event.y))}
        obj_info = self._controller.execute(
            'get_hierarchy_view_object_info', command_args)
        if obj_info:
            bounds = obj_info['visibleBounds']

            def scale(coord):
                """Scale coordinates from actual screen -> view"""
                return (
                    int(coord[0] * self._scale[0]),
                    int(coord[1] * self._scale[1]))
            xy0 = scale((bounds['left'], bounds['top']))
            xy1 = scale((bounds['right'], bounds['bottom']))
            canvas.create_rectangle(
                xy0[0], xy0[1], xy1[0], xy1[1],
                outline='red', width=2, tag='object_rect')
            for k, v in obj_info.items():
                v = v or '-'
                text.insert(tkinter.END, '{0}: {1}\n'.format(k, v))

    def _on_mouse_b1motion(self, event):
        """Callback for left-button motion event
        Args:
            event (object): event information which is passed by Tk framework
        """
        self._mouse_action['current'] = event.x, event.y
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
        fill = color

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
            'left_or_right': 'left'
        }
        self._draw_mouse_action()

    def _on_mouse_left_up(self, event):
        """Callback for left-button-up event
        Args:
            event (object): Event information which is passed by Tk framework
        """
        cur = event.x, event.y
        self._mouse_action['current'] = cur

        if self._mouse_moved():
            self._left_2point_action_menu(cur)
        else:
            self._left_1point_action_menu(cur)

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
            'left_or_right': 'right'
        }
        self._draw_mouse_action()

    def _on_mouse_right_up(self, event):
        """Callback for right-button-up event
        Args:
            event (object): Event information which is passed by Tk framework
        """
        cur = event.x, event.y
        self._mouse_action['current'] = cur

        if self._mouse_moved():
            self._right_2point_action_menu(cur)
        else:
            self._right_1point_action_menu(cur)

        self._draw_mouse_action(erase=True)

    def __get_command_wrap(self, command_name, **aditional_args):
        """Returns wrapped controller command"""
        command_args = dict(aditional_args)
        if self._mouse_action:
            command_args['start'] = self._descale(self._mouse_action['start'])
            command_args['end'] = self._descale(self._mouse_action['current'])

        def command_wrap():
            """controller command execution"""
            try:
                with display_wait(self._root):
                    retval = self._controller.execute(
                        command_name, command_args)
                return retval
            except (UiObjectNotFound, UiInconsitencyError):
                self._acquire_hierarchy_view()
        return command_wrap

    def _left_1point_action_menu(self, position):
        """Displays 1-point left-click menu"""
        menu = tkinter.Menu(self._root, name='menu')
        menu.add_command(
            label='Click(xy)',
            command=self.__get_command_wrap('click_xy'))
        menu.add_command(
            label='Long click(xy)',
            command=self.__get_command_wrap('long_click_xy'))
        menu.post(*position)

    def _left_2point_action_menu(self, position):
        """Displays 2-points left-click menu"""
        menu = tkinter.Menu(self._root, name='menu')
        menu.add_command(
            label='Swipe(xy -> xy)',
            command=self.__get_command_wrap('swipe_xy_to_xy',
                                            options={'steps': 10}))
        menu.add_command(
            label='Drag(xy -> xy)',
            command=self.__get_command_wrap('drag_xy_to_xy'))
        menu.add_command(
            label='Drag(object -> xy)',
            command=self.__get_command_wrap('drag_object_to_xy'))
        menu.add_command(
            label='Fling',
            command=self.__get_command_wrap('fling'))
        menu.add_command(
            label='Scroll',
            command=self.__get_command_wrap('scroll'))
        menu.post(*position)

    def _right_1point_action_menu(self, position):
        """Displays 1-point right-click menu"""
        menu = tkinter.Menu(self._root, name='menu')
        menu.add_command(
            label='Click(object)',
            command=self.__get_command_wrap('click_object'))
        menu.add_command(
            label='Click(object) and wait',
            command=self.__get_command_wrap(
                'click_object', wait=self._wait_timeouts['update']))
        menu.add_command(
            label='Long click(object)',
            command=self.__get_command_wrap('long_click_object'))
        menu.add_command(
            label='Clear text',
            command=self.__get_command_wrap('clear_text'))
        menu.add_command(
            label='Enter text',
            command=lambda: self._text_action(
                'enter_text', lambda text: {'text': text}))
        menu.add_command(label='Pinch in', command=lambda: self._pinch('In'))
        menu.add_command(label='Pinch out', command=lambda: self._pinch('Out'))
        menu.add_separator()
        menu.add_command(
            label='Insert wait-exists',
            command=self.__get_command_wrap(
                'insert_wait_object',
                for_what='exists', timeout=self._wait_timeouts['exists']))
        menu.add_command(
            label='Insert wait-gone',
            command=self.__get_command_wrap(
                'insert_wait_object',
                for_what='gone', timeout=self._wait_timeouts['gone']))
        menu.post(*position)

    def _right_2point_action_menu(self, position):
        """Displays 2-points right-click menu"""
        menu = tkinter.Menu(self._root, name='menu')
        menu.add_command(
            label='Swipe(object + direction)',
            command=self.__get_command_wrap('swipe_object_with_direction'))
        menu.add_command(
            label='Drag(object -> object)',
            command=self.__get_command_wrap('drag_object_to_object'))
        menu.add_command(
            label='Fling to end',
            command=self.__get_command_wrap('fling_to_end'))
        menu.add_command(
            label='Scroll to end',
            command=self.__get_command_wrap('scroll_to_end'))
        menu.add_command(
            label='Scroll to text',
            command=lambda: self._text_action(
                'scroll_to', lambda text: {'options': {'text': text}}))
        menu.post(*position)

    def _text_action(self, command_name, command_kwargs_gen):
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
            self._root.after(
                0, self.__get_command_wrap(command_name,
                                           **command_kwargs_gen(text)))

        # Place a OK button on the dialog
        ok_button = ttk.Button(top, text='OK', command=on_ok, name='ok_button')
        ok_button.grid(row=0, column=1, sticky=NW)
        canvas.wait_window(top)

    def _pinch(self, in_or_out):
        """Pinch-in/out event handler implementation"""
        from tkinter import NW, SE, StringVar

        # Create a dialog on the canvas
        canvas = self._root.nametowidget('mainframe.canvas')
        top = tkinter.Toplevel(canvas, name='pinchwindow')
        # Place a TextEntry on the dialog
        pinch_label_text = 'Pinch {0}:'.format(in_or_out)
        lebel0 = ttk.Label(top, text=pinch_label_text, name='pinchlabel')
        lebel0.grid(row=0, column=0, sticky=NW)
        slider = ttk.Scale(top, value=1.0, name='pinchinslider')
        slider.grid(row=0, column=1, sticky=NW)
        lebel1 = ttk.Label(top, text='Steps:', name='steplabel')
        lebel1.grid(row=1, column=0, sticky=NW)
        stepsStr = StringVar(value='10')
        entry = ttk.Entry(top, textvariable=stepsStr, name='steps')
        entry.grid(row=1, column=1, sticky=NW)

        def on_ok():
            """Callback for ok-click"""
            percent = int(slider.get() * 100)
            steps = int(stepsStr.get())
            top.destroy()
            self._root.after(0, self.__get_command_wrap(
                'pinch',
                in_or_out=in_or_out,
                options={
                    'percent': percent,
                    'steps': steps
                }))

        # Place a OK button on the dialog
        ok_button = ttk.Button(top, text='OK', command=on_ok, name='ok_button')
        ok_button.grid(row=0, column=2, rowspan=2, sticky=(NW, SE))
        canvas.wait_window(top)

    def _take_screenshot(self):
        """Callback for Take Screenshot"""
        filename = get_filedialog().asksaveasfilename(defaultextension='.png')
        if not filename:
            return
        with display_wait(self._root):
            scr = self._controller.execute('get_screenshot')
        scr.save(filename)
