from distutils.command.install import INSTALL_SCHEMES
from pprint import pprint
from distutils.command.install_data import install_data
from setuptools import setup
import os
import re
import sys

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line): # comments
            continue
        if re.match(r'^(\s*git\+)', line): #git+
            if '#' in line: # git+https://github.com/robot-republic/python-s3#python-s3
                requirements.append(line.split('#')[-1])
            else: # git+https://github.com/robot-republic/python-s3
                requirements.append(line.split('/')[-1])
            continue
        if re.match(r'\s*-e\s+', line):
            # TODO support version numbers
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements


def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*git\+)', line):
            url = line.strip()[4:].split('#')[0].rstrip('/').replace('https://', 'http://')
            package = line.strip().split('#')[1]
            dependency_links.append('%s/tarball/master#egg=%s-dev' % (url, package))

    return dependency_links


REQS = os.path.join(os.path.dirname(__file__), 'requirements.txt')


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

core_dir = 'reincubate_core'
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
    version='1.0.0.1',
    packages = packages,
    cmdclass = cmdclasses,
    data_files = data_files,
    url='https://github.com/syabro/vkontakte-post-downloader',
    install_requires = parse_requirements(REQS),
    dependency_links = parse_dependency_links(REQS),
    scripts = ['vkd/bin/vkd.py'],
    license='',
    author='Max Syabro',
    author_email='syabro@gmail.com',
    description=''
)
