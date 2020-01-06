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

    # Metadata keys
    bpy.types.Object.MhMsName = StringProperty(name="Name", description="The name of this material. This will have little practical effect apart from being written to the mhmat file.", default="material")
    bpy.types.Object.MhMsTag = StringProperty(name="Tag", description="A category the material fits into, for example \"blond\" or \"female\". This will influence sorting and filtering in MH.", default="")
    bpy.types.Object.MhMsDescription = StringProperty(name="Description", description="A description of the material. It will have little practical effect apart from being written to the mhmat file.", default="")
    bpy.types.Object.MhMsMatLicense = bpy.props.EnumProperty(items=_licenses, name="License", description=_licenseDescription, default="CC0")
    bpy.types.Object.MhMsAuthor = StringProperty(name="Author", description="The author of this material. This will have little practical effect apart from being written to the mhmat file.", default="")
    bpy.types.Object.MhMsHomepage = StringProperty(name="Home page", description="The home page of the material, if any. This will have little practical effect apart from being written to the mhmat file.", default="")

    # Boolean keys
    bpy.types.Object.MhMsBackfaceCull = BoolProperty(name="Backface culling", description="If the back side of faces with the material should be invisible. This has no effect in exports, but may be important in MH", default=True)
    bpy.types.Object.MhMsCastShadows = BoolProperty(name="Cast shadows", description="If the material casts shadows. This has no effect in exports.", default=True)
    bpy.types.Object.MhMsReceiveShadows = BoolProperty(name="Receive shadows", description="If the material receives shadows. This has no effect in exports.", default=True)
    bpy.types.Object.MhMsAlphaToCoverage = BoolProperty(name="AlphaToCoverage", description="I have no idea what this does, but it might be important", default=True)
    bpy.types.Object.MhMsShadeless = BoolProperty(name="Shadeless", description="If the material is shadeless. It is unlikely you want this.", default=False)
    bpy.types.Object.MhMsWireframe = BoolProperty(name="Wireframe", description="If the material is to be rendered as a wireframe. It is unlikely you want this.", default=False)
    bpy.types.Object.MhMsTransparent = BoolProperty(name="Transparent", description="If the material is to be rendered as a transparent. It is unlikely you want this, as the normal approach is using the alpha channel in the diffuse texture.", default=False)
    bpy.types.Object.MhMsDepthless = BoolProperty(name="Depthless", description="If the material is to be rendered as having no depth. It is unlikely you want this.", default=False)
    bpy.types.Object.MhMsSSSEnable = BoolProperty(name="SSS Enable", description="If the material is to be rendered with sub surface scattering.", default=False)
