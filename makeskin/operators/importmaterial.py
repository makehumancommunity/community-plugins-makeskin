#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import os
from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty
from ..utils import *
from ..material import MHMat

class MHS_OT_ImportMaterialOperator(bpy.types.Operator, ImportHelper):
    """Import MHMAT"""
    bl_idname = "makeskin.import_material"
    bl_label = "Import material"
    bl_options = {'REGISTER','UNDO'}

    filter_glob: StringProperty(default='*.mhmat', options={'HIDDEN'})

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            return True
        return False

    def execute(self, context):
        obj = context.active_object
        scn = context.scene

        if hasMaterial(obj):
            print(scn.MhMsOverwrite2)
            if not scn.MhMsOverwrite2:
                self.report({'ERROR'}, "Object already has a material, and only one material at a time is supported")
                return {'FINISHED'}
            else:
                while len(obj.data.materials) > 0:
                    obj.data.materials.pop(index=0)

        mhmat = MHMat(fileName=self.filepath)
        mhmat.assignAsNodesMaterialForObj(obj)
        
        ##- Load Blend -##
        path = mhmat.settings["blendMaterial"]
        if path:
            blendMatLoad(path)

        self.report({'INFO'}, "Material imported")
        return {'FINISHED'}
