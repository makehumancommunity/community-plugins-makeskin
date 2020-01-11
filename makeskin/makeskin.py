#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

import bpy

class MHS_PT_MakeSkinPanel(bpy.types.Panel):
    bl_label = "MakeSkin"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MakeSkin"

    def draw(self, context):
        layout = self.layout

        scn = context.scene
        obj = context.active_object

        if obj:
            createBox = layout.box()
            createBox.label(text="Create material", icon="MESH_DATA")
            createBox.prop(scn, 'MhMsCreateDiffuse', text="Diffuse texture")
            createBox.prop(scn, 'MhMsCreateNormal', text="Normal map")
            createBox.prop(scn, 'MhMsCreateBump', text="Bump map")
            createBox.prop(scn, 'MhMsOverwrite1', text="Overwrite existing")
            createBox.operator("makeskin.create_material", text="Create material")

            importBox = layout.box()
            importBox.label(text="Import material", icon="MESH_DATA")
            importBox.prop(scn, 'MhMsOverwrite2', text="Overwrite existing")
            importBox.operator("makeskin.import_material", text="Import material")

            writeBox = layout.box()
            writeBox.label(text="Write material", icon="MESH_DATA")

            writeBox.prop(obj, 'MhMsName', text='Name')
            writeBox.prop(obj, 'MhMsDescription', text='Description')
            writeBox.prop(obj, 'MhMsTag', text='Tag')
            writeBox.prop(obj, 'MhMsHomepage', text='Homepage')
            writeBox.prop(obj, 'MhMsAuthor', text='Author')
            writeBox.prop(obj, 'MhMsMatLicense', text='License')

            writeBox.prop(obj, 'MhMsBackfaceCull', text='Backface culling')
            writeBox.prop(obj, 'MhMsCastShadows', text='Cast shadows')
            writeBox.prop(obj, 'MhMsReceiveShadows', text='Receive shadows')
            writeBox.prop(obj, 'MhMsAlphaToCoverage', text='AlphaToCoverage')
            writeBox.prop(obj, 'MhMsShadeless', text='Shadeless')
            writeBox.prop(obj, 'MhMsWireframe', text='Wireframe')
            writeBox.prop(obj, 'MhMsTransparent', text='Transparent')
            writeBox.prop(obj, 'MhMsDepthless', text='Depthless')
            writeBox.prop(obj, 'MhMsSSSEnable', text='Enable SSS')
            writeBox.prop(obj, 'MhMsTextures', text='Paths:')

            writeBox.operator("makeskin.write_material", text="Save material")

