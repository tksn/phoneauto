# -*- coding: utf-8 -*-
"""An automation script writer, generates a script which utilizes pytest

:copyright: (c) 2015 by tksn
:license: MIT
"""

from __future__ import unicode_literals


class PytestScriptWriter(object):
    """Automation script writer which uses pytest as tests runner"""

    def __init__(self, file_obj, devices):
        """Initialization

        Args:
            file_obj (file):
                file or file-like object to which
                an automation script is written
            devices (iterable):
                An iterable object which contains device object instances.
        """
        self.file = file_obj
        self.devices = devices

    def start(self):
        """Writes beginning part of the script

        Writes import statements, initialization codes, etc.
        """

        lines = [
            '# -*- coding: utf-8 -*-',
            '',
            'from __future__ import unicode_literals',
            'import os',
            'import time',
            'import pytest',
            '',
            ''
        ]

        for i, device in enumerate(self.devices):
            device_name = device.device_name if len(self.devices) > 1 else None
            lines.append(
                'def device_open_{0}():'.format(i))
            lines.extend(
                '    ' + line
                for line in device.get_device_open_code(device_name))
            lines.extend((
                '',
                ''))
            lines.append(
                'def device_close_{0}(inst):'.format(i))
            lines.extend(
                '    ' + line
                for line in device.get_device_close_code('inst'))
            lines.extend((
                '',
                ''))

        lines.extend((
            '@pytest.fixture(scope="module")',
            'def _s(request):',
            '',
            '    class TestSession(object): pass',
            '    s = TestSession()',
            '    s.devices = []',
            ''))

        for i in range(len(self.devices)):
            lines.append('    s.devices.append(device_open_{0}())'.format(i))

        lines.extend((
            '',
            '    def close_all_devices():'))

        for i in range(len(self.devices)):
            lines.append('        device_close_{0}(s.devices[{1}])'
                         .format(i, i))

        lines.extend((
            '',
            '    def fin():',
            '        close_all_devices()',
            '    request.addfinalizer(fin)'
            '',
            '    return s',
            '',
            '',
            'def test_run(_s):',
            ''))

        self.file.write('\n'.join(lines))

    def finish(self):
        """Writes ending part of the script"""
        self.file.write('\n')

    def get_recorder(self, device_index=0):
        """Returns recorder function"""

        def recorder(written_text_template):
            """Creates string from given template string and record it"""
            instance_name = '_s.devices[{0}]'.format(device_index)
            text = written_text_template.format(instance=instance_name)
            self.file.write('    {0}\n'.format(text))
        return recorder
