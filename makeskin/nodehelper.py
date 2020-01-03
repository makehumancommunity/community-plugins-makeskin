#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import bpy.types
from bpy.types import ShaderNodeBsdfPrincipled, ShaderNodeTexImage
import pprint, os

_coords = dict()
_coords["diffuseTexture"] = [-400.0, 300.0]

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
            self._nodetree.links.new(dt.outputs["Alpha"], self._principledNode.inputs["Transmission"])
        return dt

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
