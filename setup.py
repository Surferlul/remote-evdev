from setuptools import setup

setup(
    name='remote-evdev',
    version='1.0',
    packages=['remote_evdev', 'remote_evdev.config', 'remote_evdev.stream'],
    url='https://github.com/Surferlul/remote-evdev',
    license='GNU General Public License v2.0',
    author='lu',
    author_email='lukasabaumann@gmail.com',
    description='Share evdev devices (unix input devices) over network'
)
