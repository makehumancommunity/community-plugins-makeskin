#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..material import MHMat
from ..utils import hasMaterial
from datetime import datetime

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
            print(scn.MhMsOverwrite1)
            if not scn.MhMsOverwrite1:
                self.report({'ERROR'}, "Object already has a material, and only one material at a time is supported")
                return {'FINISHED'}
            else:
                while len(obj.data.materials) > 0:
                    obj.data.materials.pop(index=0)

        dPH = scn.MhMsCreateDiffuse
        nPH = scn.MhMsCreateNormal
        bPH = scn.MhMsCreateBump
        tPH = scn.MhMsCreateTrans
        rPH = scn.MhMsCreateRough
        mPH = scn.MhMsCreateMetallic
        disPH = scn.MhMsCreateDisp

        mhmat = MHMat()

        now = datetime.now()
        name = "makeskin." + now.strftime("%Y%m%d%H:%M:%S")
        mhmat.assignAsNodesMaterialForObj(obj, name, diffusePH=dPH, normalPH=nPH, bumpPH=bPH, transpPH=tPH, displacePH=disPH, roughnessPH=rPH, metallicPH=mPH)

        self.report({'INFO'}, "A template material was created")
        return {'FINISHED'}

