from distutils.core import setup
from distutils.command.build_clib import build_clib

import os
import sys

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, OOBRE Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class KnockBuilder(build_clib):

    def finalize_options(self):
        # The author of build_clib built C files to temp instead of to lib.
        # This version reverses that decision.
        self.set_undefined_options('build',
                                   ('build_lib', 'build_clib'),
                                   ('build_temp', 'build_temp'),
                                   ('compiler', 'compiler'),
                                   ('debug', 'debug'),
                                   ('force', 'force'))
        self.libraries = self.distribution.libraries

        if self.libraries:
            self.check_library_list(self.libraries)

        if self.include_dirs is None:
            self.include_dirs = self.distribution.include_dirs or []
        if isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

    def build_libraries(self, libraries):
        # hack to create a shared object instead of a static archive
        if 'linux' in sys.platform:
            self.compiler.linker_so.append('-ldl')
        elif 'darwin' in sys.platform:
            self.compiler.linker_so.remove('-bundle')
            self.compiler.linker_so.extend(['-shared', '-dynamic', '-fPIC'])

        self.compiler.create_static_lib = self.compiler.link_shared_lib

        build_clib.build_libraries(self, libraries)


libknock = ('knock', {'sources': ['client/knock.c']})

setup(
    name='oobre',
    version='1.0',
    description='Out-Of-Band Reconnaissance Engine',
    packages=['oobre', 'oobre.protocols'],
    package_data={'oobre':['*.so']},
    package_dir={'': 'src'},
    libraries=[libknock],
    scripts=['client/knock'],
    requires=['twisted'],
    cmdclass={'build_clib': KnockBuilder}, requires=['twisted']
)