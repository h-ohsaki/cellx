#!/usr/bin/env python3

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="cellx",
    version="1.1",
    author="Hiroyuki Ohsaki",
    author_email="ohsaki@lsnl.jp",
    description=
    "",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/h-ohsaki/cellx",
    packages=setuptools.find_packages(),
    install_requires=['pygame'],
    scripts=['bin/cellx'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
