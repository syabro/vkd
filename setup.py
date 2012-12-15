from distutils.command.install import INSTALL_SCHEMES
from distutils.command.install_data import install_data
from setuptools import setup
import os
import sys


class osx_install_data(install_data):
    # On MacOS, the platform-specific lib dir is /System/Library/Framework/Python/.../
    # which is wrong. Python 2.5 supplied with MacOS 10.5 has an Apple-specific fix
    # for this in distutils.command.install_data#306. It fixes install_lib but not
    # install_data, which is why we roll our own install_data class.

    def finalize_options(self):
        # By the time finalize_options is called, install.install_lib is set to the
        # fixed directory, so we set the installdir to install_lib. The
        # install_data class uses ('install_data', 'install_dir') instead.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)

if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}

core_dir = 'vkd'
packages = []
data_files = []

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

for dirpath, dirnames, filenames in os.walk(core_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

setup(
    name='vkd',
    version='1.0.0.8',
    packages = packages,
    cmdclass = cmdclasses,
    data_files = data_files,
    url='https://github.com/syabro/vkontakte-post-downloader',
    install_requires = [
        'html5lib',
        'requests',
        'hurry.filesize',
        'mutagen',
        'configobj',
        'beautifulsoup4'
    ],
    scripts = ['vkd/bin/vkd', 'vkd/bin/vk_download_album'],
    license='',
    author='Max Syabro',
    author_email='syabro@gmail.com',
    description=''
)
