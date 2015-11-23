# -*- coding: utf-8 -*-
"""scriptgenerator application entry point

:copyright: (c) 2015 by tksn
:license: MIT
"""
# pylint: disable=invalid-name

from __future__ import unicode_literals
import argparse
import codecs
import io
import os
import sys

from phoneauto.scriptgenerator.pytest_script_writer import PytestScriptWriter
from phoneauto.scriptgenerator.scriptgenerator import ScriptGenerator
from phoneauto.scriptgenerator.scriptgenerator_ui import ScriptGeneratorUI
from phoneauto.scriptgenerator.uiautomator_device import UiautomatorDevice


def scriptgenerator_main(options):
    """Launches scriptgenerator GUI application

    Args:
        options['result_out'] (file):
            A file object to which automation script is written.
            Defaults to sys.stdout if result_out is None.
        options['scale'] (float):
            Resizing scale which is used when the screenshot aquired from
            the device is displayed in GUI window. 1.0 means no scaling,
            scale > 1.0 makes it larger, scale < 1.0 makes it smaller.
        options['platform'] (text):
            A string which specifies platform such as 'Darwin' etc.
            see sys.platform
    """
    result_out = options.get('result_out', None)
    if result_out is None:
        if sys.version_info[0] >= 3:
            outfile = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        else:
            outfile = codecs.getwriter('utf-8')(sys.stdout)
    else:
        outfile = codecs.getwriter('utf-8')(result_out)

    ui = ScriptGeneratorUI(scale=options.get('scale', 0.5),
                           platform_sys=options.get('platform', None))
    timeouts = options.get('timeouts')
    if timeouts:
        ui.set_timeouts(timeouts)

    device = UiautomatorDevice()
    writer = PytestScriptWriter(outfile, [device])

    writer.start()
    controller = ScriptGenerator([device], writer)
    ui.run(controller)
    writer.finish()

    device.close()


def parse_options():
    """Parse options"""
    parser = argparse.ArgumentParser(
        description='Phone automation script generator')
    parser.add_argument(
        '-s', '--scale', default=0.5, type=float,
        help='scale factor for screenshot when it is displayed')
    parser.add_argument(
        '-o', '--output', default='',
        help='Output file path. Stdout if omitted')
    parser.add_argument(
        '--wait_idle_timeout', default=5000, type=int,
        help='default timeout for wait.idle in milliseconds')
    parser.add_argument(
        '--wait_update_timeout', default=1000, type=int,
        help='default timeout for wait.update in milliseconds')
    parser.add_argument(
        '--wait_exists_timeout', default=5000, type=int,
        help='default timeout for wait.exists in milliseconds')
    parser.add_argument(
        '--wait_gone_timeout', default=5000, type=int,
        help='default timeout for wait.gone in milliseconds')
    return parser.parse_args()


def main():
    """Entry point"""
    cmd_options = parse_options()

    options = {}
    if cmd_options.output:
        outpath = os.path.abspath(cmd_options.output)
        options['result_out'] = io.open(outpath, 'wb')
    options['scale'] = cmd_options.scale
    options['timeout'] = {
        'idle': cmd_options.wait_idle_timeout,
        'update': cmd_options.wait_update_timeout,
        'exists': cmd_options.wait_exists_timeout,
        'gone': cmd_options.wait_gone_timeout
    }
    scriptgenerator_main(options)


if __name__ == '__main__':
    main()
