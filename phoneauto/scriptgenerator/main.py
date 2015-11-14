# -*- coding: utf-8 -*-
"""scriptgenerator application entry point

:copyright: (c) 2015 by tksn
:license: MIT
"""
# pylint: disable=invalid-name

from __future__ import unicode_literals
import codecs
import io
import os
import sys

from phoneauto.scriptgenerator.pytest_script_writer import PytestScriptWriter
from phoneauto.scriptgenerator.scriptgenerator import ScriptGenerator
from phoneauto.scriptgenerator.scriptgenerator_ui import ScriptGeneratorUI
from phoneauto.scriptgenerator.uiautomator_device import UiautomatorDevice


def scriptgenerator_main(result_out=None, scale=0.3, platform=None):
    """Launches scriptgenerator GUI application

    Args:
        result_out (file):
            A file object to which automation script is written.
            Defaults to sys.stdout if result_out is None.
        scale (float):
            Resizing scale which is used when the screenshot aquired from
            the device is displayed in GUI window. 1.0 means no scaling,
            scale > 1.0 makes it larger, scale < 1.0 makes it smaller.
    """
    if result_out is None:
        if sys.version_info[0] >= 3:
            outfile = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        else:
            outfile = codecs.getwriter('utf-8')(sys.stdout)
    else:
        outfile = codecs.getwriter('utf-8')(result_out)

    ui = ScriptGeneratorUI(scale=scale, platform_sys=platform)
    device = UiautomatorDevice()
    writer = PytestScriptWriter(outfile, [device])

    writer.start()
    controller = ScriptGenerator([device], writer)
    ui.run(controller)
    writer.finish()

    device.close()


if __name__ == '__main__':
    kwargs = {}
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(script_dir, '../../output')
        output_path = os.path.join(output_dir, filename)
        kwargs['result_out'] = io.open(output_path, 'wb')
    scriptgenerator_main(**kwargs)
