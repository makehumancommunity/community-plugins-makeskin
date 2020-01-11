#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import bpy.types
from bpy.types import ShaderNodeBsdfPrincipled, ShaderNodeTexImage, ShaderNodeNormalMap, ShaderNodeBump
import pprint, os

_coords = dict()
_coords["diffuseTexture"] = [-400.0, 300.0]
_coords["normalMapTextureSolo"] = [-600.0, -300.0]
_coords["normalMapSolo"] = [-250.0, -200.0]
_coords["bumpMapTextureSolo"] = [-600.0, -300.0]
_coords["bumpMapSolo"] = [-250.0, -200.0]

class NodeHelper:

    def __init__(self, obj):
        self.obj = obj
        self._material = obj.data.materials[0]
        self._nodetree = self._material.node_tree

        self._principledNode = None
        self._diffuseTextureNode = None
        self._normalmapTextureNode = None
        self._bumpmapTextureNode = None

        for node in self._nodetree.nodes:
            if isinstance(node, ShaderNodeBsdfPrincipled):
                self._principledNode = node

    def getPrincipledSocketDefaultValue(self, socketName):
        if not self._principledNode:
            return None
        return self._principledNode.inputs[socketName].default_value

    def setPrincipledSocketDefaultValue(self, socketName, socketValue):
        if not self._principledNode:
            return
        self._principledNode.inputs[socketName].default_value = socketValue

    def _findNodeLinkedToPrincipled(self, principledSocketName):
        if not self._principledNode:
            return None
        for link in self._nodetree.links:
            if link.to_node == self._principledNode:
                tsock = link.to_socket
                if tsock.name == principledSocketName:
                    return link.from_node

    def createDiffuseTextureNode(self, imagePathAbsolute=None, linkToPrincipled=True):
        global _coords
        dt = self._nodetree.nodes.new("ShaderNodeTexImage")
        dt.location = _coords["diffuseTexture"]

        if imagePathAbsolute:
            fn = os.path.basename(imagePathAbsolute)
            if fn in bpy.data.images:
                print("image existed: " + imagePathAbsolute)
                image = bpy.data.images[fn]
            else:
                image = bpy.data.images.load(imagePathAbsolute)
            image.colorspace_settings.name = "sRGB"
            dt.image = image

        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(dt.outputs["Color"], self._principledNode.inputs["Base Color"])
            self._nodetree.links.new(dt.outputs["Alpha"], self._principledNode.inputs["Alpha"])
        return dt

    def createBumpAndNormal(self, bumpImagePathAbsolute=None, normalImagePathAbsolute=None, linkToPrincipled=True):
        # TODO: support bump maps
        self.createOnlyNormal(normalImagePathAbsolute=normalImagePathAbsolute, linkToPrincipled=linkToPrincipled)

    def createOnlyBump(self, bumpImagePathAbsolute=None, linkToPrincipled=True):
        global _coords
        bmt = self._nodetree.nodes.new("ShaderNodeTexImage")
        bmt.location = _coords["bumpMapTextureSolo"]

        if bumpImagePathAbsolute:
            fn = os.path.basename(bumpImagePathAbsolute)
            if fn in bpy.data.images:
                print("image existed: " + bumpImagePathAbsolute)
                image = bpy.data.images[fn]
            else:
                image = bpy.data.images.load(bumpImagePathAbsolute)
            image.colorspace_settings.name = "Non-Color"
            bmt.image = image

        bm = self._nodetree.nodes.new("ShaderNodeBump")
        bm.location = _coords["bumpMapSolo"]

        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(bm.outputs["Normal"], self._principledNode.inputs["Normal"])
            self._nodetree.links.new(bmt.outputs["Color"], bm.inputs["Height"])
        return bmt

    def createOnlyNormal(self, normalImagePathAbsolute=None, linkToPrincipled=True):
        global _coords
        nmt = self._nodetree.nodes.new("ShaderNodeTexImage")
        nmt.location = _coords["normalMapTextureSolo"]

        if normalImagePathAbsolute:
            fn = os.path.basename(normalImagePathAbsolute)
            if fn in bpy.data.images:
                print("image existed: " + normalImagePathAbsolute)
                image = bpy.data.images[fn]
            else:
                image = bpy.data.images.load(normalImagePathAbsolute)
            image.colorspace_settings.name = "Non-Color"
            nmt.image = image

        nm = self._nodetree.nodes.new("ShaderNodeNormalMap")
        nm.location = _coords["normalMapSolo"]

        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(nm.outputs["Normal"], self._principledNode.inputs["Normal"])
            self._nodetree.links.new(nmt.outputs["Color"], nm.inputs["Color"])
        return nmt

    def findDiffuseTextureNode(self):
        if not self._principledNode:
            return None
        dtn = self._findNodeLinkedToPrincipled("Base Color")
        if not dtn:
            print("The principled node did not have anything linked to its Base color input, so there is no diffuse texture node")
            return None
        if not isinstance(dtn, ShaderNodeTexImage):
            print("The principled node had a link to its Base Color input, but the source was not an image texture. Giving up on finding a diffuse texture node.")
            return None
        return dtn

    def findDiffuseTextureFilePath(self):
        if not self._principledNode:
            return None
        fnode = self.findDiffuseTextureFilePath()
        if fnode:
            if fnode.image:
                if fnode.image.filepath or fnode.image.filepath_raw:
                    if fnode.image.filepath:
                        return fnode.image.filepath
                    else:
                        return fnode.image.filepath_raw
                else:
                    print("Found image texture with an image property, but the image had an empty file path. Giving up on finding a diffuse texture.")
                    return None
            else:
                print("Found an image texture, but its image property was empty. Giving up on finding a diffuse texture.")
                return None
        print("There was no diffuse texture to be found")
        return None
