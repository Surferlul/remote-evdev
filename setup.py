from setuptools import setup

setup(
    name='remote-evdev',
    version='1.0.0.dev1',
    packages=['remote_evdev', 'remote_evdev.config', 'remote_evdev.stream'],
    url='https://github.com/Surferlul/remote-evdev',
    license='GNU General Public License v2.0',
    author='Surferlul',
    author_email='lukasabaumann@gmail.com',
    description='Share evdev devices (unix input devices) over network',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Topic :: System',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.10'
    ],
    python_requires='>=3.10'
)
