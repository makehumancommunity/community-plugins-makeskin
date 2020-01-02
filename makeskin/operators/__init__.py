#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

from .creatematerial import MHS_OT_CreateMaterialOperator
from .importmaterial import MHS_OT_ImportMaterialOperator

OPERATOR_CLASSES = [
    MHS_OT_CreateMaterialOperator,
    MHS_OT_ImportMaterialOperator
]

__all__ = [
    "MHS_OT_CreateMaterialOperator",
    "MHS_OT_ImportMaterialOperator",
    "OPERATOR_CLASSES"
]
