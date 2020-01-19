#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty
from ..material import MHMat
from ..utils import hasMaterial, blendMatSave

class MHS_OT_WriteMaterialOperator(bpy.types.Operator, ExportHelper):
    """Write material to MHMAT file"""
    bl_idname = "makeskin.write_material"
    bl_label = "Write material"
    bl_options = {'REGISTER'}

    filename_ext = '.mhmat'

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

        fnAbsolute = bpy.path.abspath(self.filepath)

        if not hasMaterial(obj):
            self.report({'ERROR'}, "Object does not have a material")
            return {'FINISHED'}

        mhmat = MHMat(obj)

        checkImg = mhmat.checkAllTexturesAreSaved()
        if checkImg:
            self.report({'ERROR'}, checkImg)
            return {'FINISHED'}

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
        mhmat.settings['autoBlendSkin'] = obj.MhMsAutoBlend
        mhmat.settings['writeBlendMaterial'] = obj.MhMsWriteBlendMaterial

        handling = "NORMALIZE"
        if obj.MhMsTextures:
            handling = obj.MhMsTextures
        if handling == "NORMALIZE":
            mhmat.copyTextures(fnAbsolute)
        if handling == "COPY":
            mhmat.copyTextures(fnAbsolute,normalize=False)
        # If handling is LINK, then paths are already correct

        if mhmat.settings["normalmapTexture"]:
            mhmat.shaderConfig["normal"] = True
        if mhmat.settings["bumpmapTexture"]:
            mhmat.shaderConfig["bump"] = True
        if obj.MhMsUseLit and obj.MhMsLitsphere:
            mhmat.litSphere = obj.MhMsLitsphere
        
        ##- Save blend -##
        if mhmat.settings["writeBlendMaterial"]:
            try:  matName = obj.material_slots[1].name
            except IndexError:
              msg = "Object dose not have a second material."
              self.report({'ERROR'}, msg)
              raise IndexError(msg)
            
            from pathlib import Path
            path = Path(fnAbsolute).with_suffix('.mat.blend')
            mhmat.settings["blendMaterial"] = path.name+'/materials/'+matName
            blendMatSave(path)


        with open(fnAbsolute,'w') as f:
            f.write(str(mhmat))
        print(mhmat)
        self.report({'INFO'}, "A material file was written")

        return {'FINISHED'}

