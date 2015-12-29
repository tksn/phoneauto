"""Setup module of phoneauto"""

from setuptools import setup, find_packages

LONG_DESCRIPTION = """
Phoneauto - Phone automation tools
==================================

Phoneauto is a set of phone automation tools which are for android device automation.
Phoneauto comprises:
1. GUI application which generates automation script
2. Helper module which are intended to be used from automation scripts.

Current status
--------------

Early development stage

Documents
---------

Not yet
"""

setup(
    name='phoneauto',

    version='0.1.0.dev1',

    description='Phone automation toools',
    long_description=LONG_DESCRIPTION,

    url='https://github.com/tksn/phoneauto',

    author='tksn',
    author_email='tksnaoi+py@gmail.com',

    license = 'MIT',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Quality Assurance'
    ],

    keywords='android automation uiautomator',

    packages=find_packages(exclude=['tests', 'output']),

    setup_requires=['pytest-runner>=2.0,<3dev', 'docutils'],
    install_requires=['uiautomator', 'Pillow', 'future'],
    tests_require=['pytest>=2.8', 'mock'],

    platforms = ['Windows', 'Mac OS X'],
    zip_safe=False,
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'uiautogen=phoneauto.scriptgenerator.main:main'
        ]
    }
)

