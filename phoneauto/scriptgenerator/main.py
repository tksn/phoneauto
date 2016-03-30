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
import logging
import os
import sys

from phoneauto.scriptgenerator import pytest_script_writer
from phoneauto.scriptgenerator import scriptgenerator_ui
from phoneauto.scriptgenerator import scriptgenerator
from phoneauto.scriptgenerator import uiautomator_device
from phoneauto.scriptgenerator import uiautomator_coder
from phoneauto.scriptgenerator import screenrecord


def scriptgenerator_main(options):
    """Launches scriptgenerator GUI application

    Args:
        options['result_out'] (file):
            A file object to which automation script is written.
            Defaults to sys.stdout if result_out is None.
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

    ui = scriptgenerator_ui.ScriptGeneratorUI(
        screen_size=options.get('screen_size', (480, 800)),
        platform_sys=options.get('platform', None),
        timeouts=options.get('timeouts'))

    device = uiautomator_device.UiautomatorDevice()
    coder = uiautomator_coder.UiautomatorCoder()
    writer = pytest_script_writer.PytestScriptWriter(outfile, [coder])

    writer.start()
    conf = {
        'devices': [device],
        'coder': uiautomator_coder.UiautomatorCoder(),
        'writer': writer
    }
    controller = scriptgenerator.ScriptGenerator(conf)
    ui.run(controller)
    writer.finish()

    device.close()


def parse_options():
    """Parse options"""
    parser = argparse.ArgumentParser(
        description='Phone automation script generator')
    parser.add_argument(
        '-o', '--output', default='',
        help='Output file path. Stdout if omitted')
    parser.add_argument(
        '-s', '--screen_size', default='480x800',
        help='screen size (WxH)')
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
    logging.basicConfig(level=logging.INFO)
    cmd_options = parse_options()

    options = {}
    if cmd_options.output:
        outpath = os.path.abspath(cmd_options.output)
        options['result_out'] = io.open(outpath, 'wb')
    options['screen_size'] = tuple(
        int(s) for s in cmd_options.screen_size.split('x'))
    options['timeout'] = {
        'idle': cmd_options.wait_idle_timeout,
        'update': cmd_options.wait_update_timeout,
        'exists': cmd_options.wait_exists_timeout,
        'gone': cmd_options.wait_gone_timeout
    }

    screenrecord.check_prerequisites()

    scriptgenerator_main(options)


if __name__ == '__main__':
    main()
