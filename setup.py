from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    entry_points = {
        'console_scripts': [
            'uiautogen=phoneauto.scriptgenerator.main'
        ]
    },
    name='phoneauto',
    version='0.0.1',
    author='tksn',
    author_email='tksnaoi+py@gmail.com',
    packages=find_packages(exclude=['tests*']),
    install_requires=['uiautomator', 'Pillow', 'future'],
    tests_require=['pytest', 'mock'],
    cmdclass= {'test': PyTest},
    description='Tools for Phone automation/testing',
    long_description='Tools for Phone automation/testing',
    url='https://github.com/tksn/phoneauto',
    license = 'MIT',
    platforms = ['Windows', 'Mac OS X'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Quality Assurance'
    ]
)
