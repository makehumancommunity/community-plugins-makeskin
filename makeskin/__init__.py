#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Authors: Joel Palmius
#           black-punkduck

from .utils import blendMatLoad, setVersion

bl_info = {
    "name": "MakeSkin",
    "author": "Joel Palmius",
    "version": (0,9,0),
    "blender": (2,80,0),
    "location": "View3D > Properties > Make Skin",
    "description": "Create MakeHuman Materials",
    'wiki_url': "http://www.makehumancommunity.org/",
    "category": "MakeHuman"}

setVersion(bl_info["version"])

from bpy.utils import register_class, unregister_class
from .extraproperties import extraProperties
from .makeskin import MHS_PT_MakeSkinPanel
from .operators import *
from .material import MHMat

MAKESKIN_VERSION = bl_info["version"]

MAKESKIN_CLASSES = []
MAKESKIN_CLASSES.extend(OPERATOR_CLASSES)
MAKESKIN_CLASSES.append(MHS_PT_MakeSkinPanel)

__all__ = [
    "MAKESKIN_CLASSES",
    "MAKESKIN_VERSION",
    "MHMat",
    "blendMatLoad"
]

def register():
    extraProperties()
    for cls in MAKESKIN_CLASSES:
        register_class(cls)

def unregister():

    for cls in reversed(MAKESKIN_CLASSES):
        unregister_class(cls)

if __name__ == "__main__":
    register()
    print("MakeSkin loaded")

