#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..material import MHMat
from ..utils import hasMaterial

class MHS_OT_CreateMaterialOperator(bpy.types.Operator):
    """Create template material"""
    bl_idname = "makeskin.create_material"
    bl_label = "Create material"
    bl_options = {'REGISTER'}

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
            if not scn.MhMsOverwrite:
                self.report({'ERROR'}, "A material for this object already exists, change 'replace' option in common settings to overwrite material")
                return {'FINISHED'}
            else:
                while len(obj.data.materials) > 0:
                    obj.data.materials.pop(index=0)

        mhmat = MHMat()

        # use object name as a first guess, if it already exists, a .001 is automatically appended by new function for material
        #
        name = obj.name
        mhmat.assignAsNodesMaterialForObj(scn, obj)

        self.report({'INFO'}, "A template material was created")
        return {'FINISHED'}

