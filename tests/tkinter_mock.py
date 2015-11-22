# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from mock import Mock


def install(monkeypatch):
    root = Tk()
    root_factory = lambda: root
    monkeypatch.setattr('tkinter.Tk', root_factory)
    monkeypatch.setattr('tkinter.Toplevel', Widget)
    monkeypatch.setattr('tkinter.Menu', Menu)
    monkeypatch.setattr('tkinter.Canvas', Canvas)
    monkeypatch.setattr('tkinter.ttk.Frame', Widget)
    monkeypatch.setattr('tkinter.ttk.Button', Button)
    monkeypatch.setattr('tkinter.ttk.Entry', Entry)
    monkeypatch.setattr('tkinter.ttk.Label', Widget)
    monkeypatch.setattr('tkinter.ttk.Scale', Scale)
    monkeypatch.setattr('tkinter.StringVar', Mock())
    monkeypatch.setattr('tkinter.ttk.Separator', Widget)
    monkeypatch.setattr('tkinter.Text', Text)
    monkeypatch.setattr('PIL.ImageTk.PhotoImage', Mock())
    return root


class Widget(object):

    def __init__(self, *args, **options):
        if len(args) > 0:
            args[0].add_child(options.get('name'), self)
        self.children = {}
        self.callbacks = []
        self.after_func = None

        mock_methods = ['grid', 'pack', 'destroy', 'focus_set', 'update']
        for m in mock_methods:
            setattr(self, m, Mock())

    def add_child(self, name, child_inst):
        if name:
            self.children[name] = child_inst

    def bind(self, event_name, callback):
        self.callbacks.append((event_name, callback))

    def config(self, *args, **kwargs):
        command_func = kwargs.get('command')
        if command_func:
            self.bind(None, command_func)

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

    def after(self, ms, after_func, *args):
        def after_func_wrap():
            after_func(*args)
        self.after_func = after_func_wrap

    def after_cancel(self, timer_id):
        self.after_func = None

    def process_after_func(self):
        if self.after_func is not None:
            self.after_func()


class Tk(Widget):

    def __init__(self):
        Widget.__init__(self)
        self.mainloop = Mock()
        self.title = Mock()


class Menu(Widget):

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self.add_separator = Mock()
        self.post = Mock()

    def add_command(self, label, command):
        self.bind(label, command)


class Canvas(Widget):

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self.delete = Mock()
        self.create_image = Mock()
        self.create_line = Mock()
        self.create_oval = Mock()
        self.wait_window = Mock()


class Button(Widget):

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        command = kwargs.get('command')
        if command:
            self.config(command=command)


class Entry(Widget):

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self.textvariable = kwargs.get('textvariable')
        self.get = Mock()


class Scale(Widget):

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self.get = Mock()


class Text(Widget):

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self.insert = Mock()
