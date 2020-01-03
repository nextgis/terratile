import os
import sys
import subprocess
from os import path, makedirs
from io import open

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

here = path.abspath(path.dirname(__file__))


class CMakeExtension(Extension):
    def __init__(self, name):
        Extension.__init__(self, name, sources=[])


class CMakeBuild(build_ext):

    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)

    def build_cmake(self, ext):
        if not os.path.isdir(self.build_temp):
            makedirs(self.build_temp)

        extdir = self.get_ext_fullpath(ext.name)

        config = 'Debug' if self.debug else 'Release'
        cmake_args = [
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + os.path.abspath(os.path.split(extdir)[0]),
            '-DCMAKE_BUILD_TYPE=' + config
        ]

        build_args = ['--config', config, '--', '-j2']

        env = os.environ.copy()
        subprocess.check_call(
            ['cmake', os.path.abspath(os.path.dirname(__file__))] + cmake_args,
            cwd=self.build_temp, env=env)

        if not self.dry_run:
            subprocess.check_call(
                ['cmake', '--build', '.'] + build_args,
                cwd=self.build_temp, env=env)



setup(
    name='terratile',
    description='Simple wrapper of cesium terrain builder (libctb) for terrain tiles generation.'
    version='0.1',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4',
    url='https://github.com/nextgis/terratile',
    author='NextGIS developers',
    author_email='info@nextgis.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    py_modules=['terratile'],

    ext_modules=[CMakeExtension('_terratile')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)
