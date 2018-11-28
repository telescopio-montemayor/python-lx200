import os
from setuptools import find_packages, setup

from lx200 import __version__


with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='python-lx200',
    version=__version__,
    packages=find_packages(),
    namespace_packages=['lx200'],
    include_package_data=True,
    install_requires=[
        'attrs'
    ],
    license='AGPL-3.0',
    description='Utilities to generate and parse LX200 protocol messages',
    long_description=README,
    long_description_content_type='text/markdown',
    url='http://github.com/telescopio-montemayor/python-lx200',
    author='Adrián Pardini',
    author_email='github@tangopardo.com.ar',
    classifiers=[
        'Environment :: Web Environment',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Communications',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Astronomy'
    ],
    keywords='astronomy, telescope, lx200',
)
