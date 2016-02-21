# -*- coding: utf-8 -*-
"""screenrecord thread

:copyright: (c) 2016 by tksn
:license: MIT
"""

from distutils.spawn import find_executable
import io
import logging
from queue import Queue
from subprocess import Popen, PIPE
from threading import Thread
from PIL import Image


def check_prerequisites():
    if not find_executable('ffmpeg'):
        raise RuntimeError('Could not find ffmpeg')


_NUM_COMPONENT = 3
_BUFSIZE = 10**7

_ADB_EXE = 'adb'
_FFMPEG_EXE = 'ffmpeg'
_FFMPEG_COMMAND = [_FFMPEG_EXE,
                   '-i', '-',
                   '-f', 'image2pipe',
                   '-pix_fmt', 'rgb24',
                   '-vcodec', 'rawvideo',
                   '-']


def get_adb_command(width, height):
    return [
        _ADB_EXE,
        'exec-out',
        'screenrecord',
        '--output-format=h264',
        '--size={0}x{1}'.format(width, height),
        '-']


class Screenrecord(Thread):

    def __init__(self, width=540, height=960):
        super(Screenrecord, self).__init__()
        self.__alive = True
        self.__queue = Queue()
        self.__size = (width, height)

    @property
    def queue(self):
        return self.__queue

    @property
    def width(self):
        return self.__size[0]

    @property
    def height(self):
        return self.__size[1]

    def capture_oneshot(self):
        command = [
            _ADB_EXE,
            'exec-out',
            'screencap',
            '-p']
        buf_size = self.width * self.height * _NUM_COMPONENT
        adb_proc = Popen(command, stdout=PIPE, bufsize=buf_size)
        png_data, _ = adb_proc.communicate()
        return Image.open(io.BytesIO(png_data)).resize(self.__size)

    def run(self):
        logger = logging.getLogger(__name__)
        logger.info('thread start')
        frame_size = self.width * self.height * _NUM_COMPONENT
        buf_size = frame_size * 4

        procs = {}

        def start_video():
            logger.info('starting video processes')
            procs['adb'] = Popen(
                get_adb_command(self.width, self.height),
                stdout=PIPE, bufsize=buf_size)
            procs['ffmpeg'] = Popen(
                _FFMPEG_COMMAND,
                stdin=procs['adb'].stdout,
                stdout=PIPE, bufsize=buf_size)
            logger.info('video processes started')

        def stop_video():
            logger.info('stopping video processes')
            procs['adb'].kill()
            procs['adb'].communicate()
            procs['ffmpeg'].kill()
            procs['ffmpeg'].communicate()
            procs.clear()
            logger.info('video processes stopped')

        start_video()
        while self.__alive:
            frame_data = procs['ffmpeg'].stdout.read(frame_size)
            if len(frame_data) == frame_size:
                frame = Image.frombytes(mode='RGB',
                                        size=self.__size,
                                        data=frame_data)
                self.__queue.put(frame)
            else:
                stop_video()
                start_video()
        stop_video()
        logger.info('thread stop')

    def join(self, timeout=None):
        self.__alive = False
        super(Screenrecord, self).join(timeout=timeout)
