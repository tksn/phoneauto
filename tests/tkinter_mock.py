# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import PIL.ImageTk
from mock import MagicMock, create_autospec


def install(monkeypatch):
    root = Tk()
    root_factory = lambda: root
    monkeypatch.setattr('tkinter.Tk', root_factory)
    monkeypatch.setattr('tkinter.Toplevel', Toplevel)
    monkeypatch.setattr('tkinter.Menu', Menu)
    monkeypatch.setattr('tkinter.Canvas', Canvas)
    monkeypatch.setattr('tkinter.ttk.Frame', Frame)
    monkeypatch.setattr('tkinter.ttk.Button', Button)
    monkeypatch.setattr('tkinter.ttk.Entry', Entry)
    monkeypatch.setattr(
        'PIL.ImageTk.PhotoImage',
        create_autospec(PIL.ImageTk.PhotoImage))
    return root


class Widget(object):

    def __init__(self):
        self.children = {}
        self.callbacks = []

    def add_child(self, name, child_inst):
        if name:
            self.children[name] = child_inst

    def bind(self, event_name, callback):
        self.callbacks.append((event_name, callback))

    def process_event(self, event_name, *args, **kwargs):
        for evt, cb in self.callbacks:
            if event_name is None or evt == event_name:
                cb(*args, **kwargs)

    def nametowidget(self, name):
        descs = name.split('.')
        childname = descs[0]
        desc_inst = self.children[childname]
        if descs[1:]:
            desc_inst = desc_inst.nametowidget('.'.join(descs[1:]))
        return desc_inst


class Tk(Widget):

    def __init__(self):
        Widget.__init__(self)
        self.mainloop = MagicMock()

    def title(self, title_str):
        pass


class Toplevel(Widget):

    def __init__(self, root, name=None):
        Widget.__init__(self)
        root.add_child(name, self)
        pass

    def destroy(self):
        pass


class Menu(Widget):

    def __init__(self, root, name=None):
        Widget.__init__(self)
        root.add_child(name, self)

    def add_command(self, label, command):
        self.bind(label, command)

    def post(self, x, y):
        pass


class Canvas(Widget):

    def __init__(self, root, width, height, name):
        Widget.__init__(self)
        root.add_child(name, self)
        self.wait_window = MagicMock()

    def focus_set(self):
        pass

    def grid(self, row, column, columnspan, sticky):
        pass

    def delete(self, id):
        pass

    def create_image(self, x, y, anchor, image):
        pass

    def after(self, ms, after_func, *args):
        def after_func_wrap():
            after_func(*args)
        self.after_func = after_func_wrap

    def after_cancel(self, timer_id):
        self.after_func = None

    def create_line(self, *args, **kwargs):
        pass

    def create_oval(self, tx, ty, bx, by, outline, tag):
        pass

    def execute_after_func(self):
        self.after_func()


class Frame(Widget):

    def __init__(self, root, name):
        Widget.__init__(self)
        root.add_child(name, self)

    def grid(self, row, column, sticky):
        pass


class Button(Widget):

    def __init__(self, root, text, command, name):
        Widget.__init__(self)
        root.add_child(name, self)
        self.bind(None, command)

    def grid(self, row, column, sticky):
        pass


class Entry(Widget):

    def __init__(self, root, name=None):
        Widget.__init__(self)
        root.add_child(name, self)
        self.get = MagicMock()

    def grid(self, row, column, sticky):
        pass


# import tkinter
# from mock import MagicMock, create_autospec
#
# def install(monkeypatch):
#     root = widget_factory()
#     root_factory = lambda: root
#     monkeypatch.setattr('tkinter.Tk', root_factory)
#     monkeypatch.setattr('tkinter.Toplevel', widget_factory)
#     monkeypatch.setattr('tkinter.Menu', widget_factory)
#     monkeypatch.setattr('tkinter.Canvas', widget_factory)
#     monkeypatch.setattr('tkinter.ttk.Frame', widget_factory)
#     monkeypatch.setattr('tkinter.ttk.Button', widget_factory)
#     monkeypatch.setattr('tkinter.ttk.Entry', widget_factory)
#     monkeypatch.setattr(
#         'PIL.ImageTk.PhotoImage',
#         create_autospec(PIL.ImageTk.PhotoImage))
#
#     class Accessor(object): pass
#     acc = Accessor()
#     acc.root = root
#     return acc
#
#
# def widget_factory(*args, **kwargs):
#
#     inst = MagicMock()
#     inst.name = kwargs.get('name')
#     inst.actions = []
#     inst.children = {}
#
#     parent = args[0] if args else None
#     if parent and inst.name:
#         parent.children[inst.name] = inst
#
#     command = kwargs.get('command')
#     if command:
#         inst.actions.append((None, command))
#
#     def bind(trigger, action):
#         inst.actions.append((trigger, action))
#     inst.bind.side_effect = bind
#
#     def add_command(label, command):
#         inst.actions.append((label, command))
#     inst.add_command.side_effect = add_command
#
#     def execute_action(trigger=None, *args, **kwargs):
#         for trig, act in inst.actions:
#             if trig == trigger:
#                 act(*args, **kwargs)
#     inst.execute_action.side_effect = execute_action
#
#     def nametowidget(name):
#         descs = name.split('.')
#         childname = descs[0]
#         desc_inst = inst.children[childname]
#         if descs[1:]:
#             desc_inst = desc_inst.nametowidget('.'.join(descs[1:]))
#         return desc_inst
#     inst.nametowidget.side_effect = nametowidget
#
#     return inst
#
