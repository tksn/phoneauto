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


def get_filedialog():  # pragma: no cover
    """Returns filedialog module object

    Returns appropriate filedialong module depending on sys.version.
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

    _MOUSE_MOVE_THRESH = 20
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

        self._wait_idle_timeout = 5000
        self._wait_update_timeout = 1000
        self._wait_exists_timeout = 5000
        self._wait_gone_timeout = 5000

        self._hold_timer_id = None
        self._root = None
        self._platform = platform_sys or platform.system()
        self._create_components()

    def set_timeouts(self, timeouts):
        """Sets timeout values"""
        self._wait_idle_timeout = timeouts.get(
            'idle', self._wait_idle_timeout)
        self._wait_update_timeout = timeouts.get(
            'update', self._wait_update_timeout)
        self._wait_exists_timeout = timeouts.get(
            'exists', self._wait_exists_timeout)
        self._wait_gone_timeout = timeouts.get(
            'gone', self._wait_gone_timeout)

    def run(self, controller):
        """Launches UI and enter the event loop

        Args:
            controller (object):
                scriptgenerator object
        """
        self._controller = controller
        self._initialize()
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
        self._construct_sidebar(sidebar)
        self._root.update()

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

    @staticmethod
    def _construct_sidebar(sidebar):
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
        label(sidebar, {'text': 'Keys\n  r: Refresh'})

    def _initialize(self):
        """Initialization after controller became available"""
        self._root.nametowidget('mainframe.back_button').config(
            command=self.__get_command_wrap('press_key', key_name='BACK'))
        self._root.nametowidget('mainframe.home_button').config(
            command=self.__get_command_wrap('press_key', key_name='HOME'))
        self._root.nametowidget('mainframe.recent_button').config(
            command=self.__get_command_wrap('press_key',
                                            key_name='APP_SWITCH'))

        self._root.nametowidget('sidebar.refresh_button').config(
            command=self._acquire_screen)
        self._root.nametowidget('sidebar.screenshot_button').config(
            command=self._take_screenshot)
        self._root.nametowidget('sidebar.power_button').config(
            command=self.__get_command_wrap('press_key', key_name='POWER'))
        self._root.nametowidget('sidebar.notification_button').config(
            command=self.__get_command_wrap('open_notification'))
        self._root.nametowidget('sidebar.quicksettings_button').config(
            command=self.__get_command_wrap('open_quick_settings'))
        self._root.nametowidget('sidebar.volume_up_button').config(
            command=self.__get_command_wrap('press_key', key_name='VOLUME_UP'))
        self._root.nametowidget('sidebar.volume_down_button').config(
            command=self.__get_command_wrap('press_key',
                                            key_name='VOLUME_DOWN'))

        orient_frm = self._root.nametowidget('sidebar.orientation_frame')
        orient_frm.nametowidget('orientation_natural').config(
            command=self.__get_command_wrap('set_orientation',
                                            orientation='natural'))
        orient_frm.nametowidget('orientation_left').config(
            command=self.__get_command_wrap('set_orientation',
                                            orientation='left'))
        orient_frm.nametowidget('orientation_right').config(
            command=self.__get_command_wrap('set_orientation',
                                            orientation='right'))
        orient_frm.nametowidget('orientation_upsidedown').config(
            command=self.__get_command_wrap('set_orientation',
                                            orientation='upsidedown'))
        orient_frm.nametowidget('orientation_unfreeze').config(
            command=self.__get_command_wrap('set_orientation',
                                            orientation='unfreeze'))

        self._root.nametowidget('sidebar.ins_screenshot_cap').config(
            command=self.__get_command_wrap('insert_screenshot_capture'))
        self._root.nametowidget('sidebar.ins_wait_idle').config(
            command=self.__get_command_wrap(
                'insert_wait', for_what='idle',
                timeout=self._wait_idle_timeout))
        self._root.nametowidget('sidebar.ins_wait_update').config(
            command=self.__get_command_wrap(
                'insert_wait', for_what='update',
                timeout=self._wait_update_timeout))

        canvas = self._root.nametowidget('mainframe.canvas')
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
        self._acquire_screen()

    def _acquire_screen(self, _=None):
        """Acquires screenshot from the device, and place it on the UI's canvas

        Returns:        self._cancel_hold_timer()
        self._mouse_action['current'] = event.x, event.y
        self._root.update()


            Tkinter.Canvas: canvas object
        """
        from tkinter import NW

        with display_wait(self._root):
            scr = self._controller.execute('get_screenshot')
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
        self._controller.execute('update_view_dump')
        return canvas

    def _descale(self, coord):
        """Converts a coordinate from canvas-coordinats to
        device-screen-coorinates

        Args:
            coord (tuple): coordinats (x, y)
        """
        return int(coord[0] / self._scale), int(coord[1] / self._scale)

    def _on_mouse_move(self, event):
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
            with display_wait(self._root):
                retval = self._controller.execute(command_name, command_args)
            return retval
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
                'click_object', wait=self._wait_update_timeout))
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
            label='Display info', command=self._display_info)
        menu.add_command(
            label='Insert wait-exists',
            command=self.__get_command_wrap(
                'insert_wait_object',
                for_what='exists', timeout=self._wait_exists_timeout))
        menu.add_command(
            label='Insert wait-gone',
            command=self.__get_command_wrap(
                'insert_wait_object',
                for_what='gone', timeout=self._wait_gone_timeout))
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

    def _display_info(self):
        """Callback for Display info"""
        from tkinter import NW

        command_wrap = self.__get_command_wrap('get_object_info')
        result = command_wrap()

        # Create a dialog on the canvas
        canvas = self._root.nametowidget('mainframe.canvas')
        top = tkinter.Toplevel(canvas, name='info')

        result_str = '\n'.join(
            '{0}: {1}'.format(k, v) for k, v in result.items())

        text = tkinter.Text(top, width=40, height=20, name='infotext')
        text.insert(tkinter.END, result_str)
        text.grid(row=0, column=0, sticky=NW)

        # Place a OK button on the dialog
        ok_button = ttk.Button(top, text='OK',
                               command=top.destroy,
                               name='ok_button')
        ok_button.grid(row=1, column=0, sticky=NW)
        canvas.wait_window(top)
