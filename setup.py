#!/usr/bin/env python

from distutils.core import setup

setup(
    name='rowan',
    version="0.1",
    description="Rowan Hierarchical Web Framework",
    packages=[
        'rowan',
        'rowan.admin', 'rowan.auth',
        'rowan.controllers', 'rowan.utils'
        ]
    )
