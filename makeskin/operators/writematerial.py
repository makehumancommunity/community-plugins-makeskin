#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..material import MHMat
from ..utils import hasMaterial

class MHS_OT_WriteMaterialOperator(bpy.types.Operator):
    """Write material to MHMAT file"""
    bl_idname = "makeskin.write_material"
    bl_label = "Write material"
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

        if not hasMaterial(obj):
            self.report({'ERROR'}, "Object does not have a material")
            return {'FINISHED'}

        mhmat = MHMat(obj)

        if obj.MhMsName:
            mhmat.settings['name'] = obj.MhMsName

        if obj.MhMsTag:
            mhmat.settings['tag'] = obj.MhMsTag

        if obj.MhMsDescription:
            mhmat.settings['description'] = obj.MhMsDescription

        if obj.MhMsAuthor:
            mhmat.settings['author'] = obj.MhMsAuthor

        if obj.MhMsHomepage:
            mhmat.settings['homepage'] = obj.MhMsHomepage

        mhmat.settings['license'] = obj.MhMsMatLicense
        mhmat.settings['backfaceCull'] = obj.MhMsBackfaceCull
        mhmat.settings['castShadows'] = obj.MhMsCastShadows
        mhmat.settings['receiveShadows'] = obj.MhMsReceiveShadows
        mhmat.settings['alphaToCoverage'] = obj.MhMsAlphaToCoverage
        mhmat.settings['shadeless'] = obj.MhMsShadeless
        mhmat.settings['wireframe'] = obj.MhMsWireframe
        mhmat.settings['transparent'] = obj.MhMsTransparent
        mhmat.settings['depthless'] = obj.MhMsDepthless
        mhmat.settings['sssEnable'] = obj.MhMsSSSEnable

        print(mhmat)
        self.report({'INFO'}, "A material file was written")

        return {'FINISHED'}

