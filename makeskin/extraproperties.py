#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

import bpy
import json
import os
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

_licenses = []
_licenses.append(("CC0",   "CC0", "Creative Commons Zero",                                                  1))
_licenses.append(("CC-BY", "CC-BY", "Creative Commons Attribution",                                           2))
_licenses.append(("AGPL",  "AGPL", "Affero Gnu Public License (don't use unless absolutely necessary)",     3))
_licenseDescription = "Set an output license for the material. This will have no practical effect apart from being included in the written MHMAT file."

def extraProperties():
    #
    # properties used by materials are added to the scene
    #
    bpy.types.Scene.MhMsMatLicense = bpy.props.EnumProperty(items=_licenses, name="material_license", description=_licenseDescription, default="CC0")
    bpy.types.Scene.MhMsMatAuthor  = StringProperty(name="Author name", description="", default="unknown")

    # Object properties, normally set by MPFB
    if not hasattr(bpy.types.Object, "MhObjectType"):
        bpy.types.Object.MhObjectType = StringProperty(name="Object type", description="This is what type of MakeHuman object is (such as Clothes, Eyes...)", default="")
    if not hasattr(bpy.types.Object, "MhHuman"):
        bpy.types.Object.MhHuman = BoolProperty(name="Is MH Human", description="Old makeclothes property for deciding object type", default=False)

    bpy.types.Scene.MhMsCreateDiffuse = BoolProperty(name="Create diffuse placeholder", description="Create a placeholder for a diffuse texture", default=True)
    bpy.types.Scene.MhMsCreateNormal = BoolProperty(name="Create normal map placeholder", description="Create a placeholder for a normal map", default=False)
    bpy.types.Scene.MhMsCreateBump = BoolProperty(name="Create bump map placeholder", description="Create a placeholder for a bump map", default=False)

    bpy.types.Scene.MhMsOverwrite1 = BoolProperty(name="Overwrite existing (create)", description="Overwrite existing material(s) on object", default=False)
    bpy.types.Scene.MhMsOverwrite2 = BoolProperty(name="Overwrite existing (import)", description="Overwrite existing material(s) on object", default=False)


