#!/usr/bin/env python

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="defectDojo_engagement_survey",
    version="1.0.1",
    description="DefectDojo Engagement Survey",
    long_description=read('README.md'),
    url="https://github.com/grendel513/defectDojo-engagement-survey",
    author="Jay Paz",
    author_email="jay.paz@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["django", "defectdojo", "risk" "survey", "security"],
    zip_safe=False,
    install_requires=[
        'django-polymorphic',
        'django-crispy-forms',
        'django-overextends',
        'django_extensions',
        ]
)
