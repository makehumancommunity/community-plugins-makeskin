#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

# layout:
#
# [preferences/common-settings]
# [create material]
# [import material]
# [write material]

import bpy
from .utils import getVersion

class MHS_PT_MakeSkinPanel(bpy.types.Panel):
    bl_label = "MakeSkin v %d.%d.%d" % getVersion()
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MakeSkin"

    def draw(self, context):
        layout = self.layout

        scn = context.scene
        obj = context.active_object

        # common settings (always displayed)
        #
        commonSettingsBox = layout.box()
        commonSettingsBox.label(text="Common settings", icon="TOOL_SETTINGS")
        col = commonSettingsBox.column()
        col.prop(scn, 'MhMsOverwrite', text="Replace object materials")
        col.prop(scn, 'MhMsNodeVis', text="Extended node visualisation")

        createBox = layout.box()
        if obj is None or obj.type != "MESH":
            createBox.label(text="- select a visible mesh object -")
        else:
            createBox.label(text="Create material", icon="MESH_DATA")
            createBox.prop(scn, 'MhMsCreateDiffuse', text="Diffuse texture")
            createBox.prop(scn, 'MhMsCreateNormal', text="Normal map")
            createBox.prop(scn, 'MhMsCreateBump', text="Bump map")
            createBox.prop(scn, 'MhMsCreateTrans', text="Transmission map")
            createBox.prop(scn, 'MhMsCreateRough', text="Roughness map")
            createBox.prop(scn, 'MhMsCreateMetallic', text="Metallic map")
            createBox.prop(scn, 'MhMsCreateDisp', text="Displacement map")
            createBox.operator("makeskin.create_material", text="Create material")

            importBox = layout.box()
            importBox.label(text="Import material", icon="MESH_DATA")
            importBox.operator("makeskin.import_material", text="Import material")

            writeBox = layout.box()
            writeBox.label(text="Write material", icon="MATERIAL_DATA")

            writeBox.prop(obj, 'MhMsName', text='Name')
            writeBox.prop(obj, 'MhMsDescription', text='Description')
            writeBox.prop(obj, 'MhMsTag', text='Tags')
            row = writeBox.row()
            row.label(text="License")
            row.prop(obj, 'MhMsMatLicense', text="")
            row = writeBox.row()
            row.label(text="Author")
            row.prop(obj, 'MhMsAuthor', text="")
            row = writeBox.row()
            row.label(text="Homepage")
            row.prop(obj, 'MhMsHomepage', text="")

            writeBox.prop(obj, 'MhMsBackfaceCull', text='Backface culling')
            writeBox.prop(obj, 'MhMsCastShadows', text='Cast shadows')
            writeBox.prop(obj, 'MhMsReceiveShadows', text='Receive shadows')
            writeBox.prop(obj, 'MhMsAlphaToCoverage', text='AlphaToCoverage')
            writeBox.prop(obj, 'MhMsShadeless', text='Shadeless')
            writeBox.prop(obj, 'MhMsWireframe', text='Wireframe')
            writeBox.prop(obj, 'MhMsTransparent', text='Transparent')
            writeBox.prop(obj, 'MhMsDepthless', text='Depthless')
            writeBox.prop(obj, 'MhMsSSSEnable', text='Enable SSS')
            writeBox.prop(obj, 'MhMsAutoBlend', text='Auto blend')
            writeBox.prop(obj, 'MhMsTextures', text='Paths')
            writeBox.prop(obj, 'MhMsUseLit', text='Use litsphere')
            writeBox.prop(obj, 'MhMsLitsphere', text='Litsphere texture')

            writeBox.prop(obj, 'MhMsWriteBlendMaterial', text='Save Blender material')

            writeBox.operator("makeskin.write_material", text="Save material")

