#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-ios-notification",
    version = "1.0.1",
    author = "Matheus Lima",
    author_email = "matheus.se@gmail.com",
    description = ("A Django Application for contacting the Apple Push Service"
                                    " and maintaining a list of iOS devices."),
    license = "Apache License 2.0",
    keywords = "django ios notification push",
    url = "https://github.com/matheussl/django-ios-notification",
    packages=['ios_notification',],
    long_description="N/A",

    requires = [],
)