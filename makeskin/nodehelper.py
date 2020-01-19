#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import bpy.types
from bpy.types import ShaderNodeBsdfPrincipled, ShaderNodeTexImage, ShaderNodeNormalMap, ShaderNodeBump, ShaderNodeNormalMap
import pprint, os

_coords = dict()
_coords["diffuseTexture"] = [-400.0, 300.0]
_coords["transparencyTexture"] = [-800.0, 100.0]
_coords["normalMapTextureSolo"] = [-600.0, -300.0]
_coords["normalMapSolo"] = [-250.0, -200.0]
_coords["bumpMapTextureSolo"] = [-600.0, 300.0]
_coords["bumpMapSolo"] = [-250.0, -200.0]
_coords["normalMapTextureDuo"] = [-800.0, -450.0]
_coords["normalMapDuo"] = [-500.0, -350.0]
_coords["bumpMapTextureDuo"] = [-600.0, -50.0]
_coords["bumpMapDuo"] = [-250.0, -150.0]

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

    def _findNodeLinkedTo(self, nodeTarget, socketTarget):
        srcNode = None
        for link in self._nodetree.links:
            if link.to_node == nodeTarget:
                tsock = link.to_socket
                if tsock.name == socketTarget:
                    srcNode = link.from_node
        return srcNode

    def _findNodeLinkedToPrincipled(self, principledSocketName):
        if not self._principledNode:
            return None
        for link in self._nodetree.links:
            if link.to_node == self._principledNode:
                tsock = link.to_socket
                if tsock.name == principledSocketName:
                    return link.from_node

    def createTransparencyTextureNode(self, imagePathAbsolute=None, linkToPrincipled=True):
        global _coords
        dt = self._nodetree.nodes.new("ShaderNodeTexImage")
        dt.location = _coords["transparencyTexture"]

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
            self._nodetree.links.new(dt.outputs["Color"], self._principledNode.inputs["Transmission"])
        return dt

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
        global _coords
        (nmt, nm) = self._createNormal(normalImagePathAbsolute=normalImagePathAbsolute, linkToPrincipled=False)
        nmt.location = _coords["normalMapTextureDuo"]
        nm.location = _coords["normalMapDuo"]

        (bmt, bm) = self._createBump(bumpImagePathAbsolute=bumpImagePathAbsolute, linkToPrincipled=False)
        bmt.location = _coords["bumpMapTextureDuo"]
        bm.location = _coords["bumpMapDuo"]

        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(bm.outputs["Normal"], self._principledNode.inputs["Normal"])
            self._nodetree.links.new(bmt.outputs["Color"], bm.inputs["Height"])
            self._nodetree.links.new(nm.outputs["Normal"], bm.inputs["Normal"])
            self._nodetree.links.new(nmt.outputs["Color"], nm.inputs["Color"])

    def _createBump(self, bumpImagePathAbsolute=None, linkToPrincipled=True):
        bmt = self._nodetree.nodes.new("ShaderNodeTexImage")

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

        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(bm.outputs["Normal"], self._principledNode.inputs["Normal"])
            self._nodetree.links.new(bmt.outputs["Color"], bm.inputs["Height"])
        return (bmt, bm)

    def createOnlyBump(self, bumpImagePathAbsolute=None, linkToPrincipled=True):
        global _coords
        (bmt, bm) = self._createBump(bumpImagePathAbsolute=bumpImagePathAbsolute, linkToPrincipled=linkToPrincipled)
        bmt.location = _coords["bumpMapTextureSolo"]
        bm.location = _coords["bumpMapSolo"]

    def _createNormal(self, normalImagePathAbsolute=None, linkToPrincipled=True):
        nmt = self._nodetree.nodes.new("ShaderNodeTexImage")

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

        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(nm.outputs["Normal"], self._principledNode.inputs["Normal"])
            self._nodetree.links.new(nmt.outputs["Color"], nm.inputs["Color"])
        return (nmt, nm)

    def createOnlyNormal(self, normalImagePathAbsolute=None, linkToPrincipled=True):
        (nmt, nm) = self._createNormal(normalImagePathAbsolute=normalImagePathAbsolute, linkToPrincipled=linkToPrincipled)
        nmt.location = _coords["normalMapTextureSolo"]
        nm.location = _coords["normalMapSolo"]
        return nmt

    def _extractImageFilePath(self, textureNode):
        if not textureNode:
            return None
        if textureNode.image:
            if textureNode.image.filepath or textureNode.image.filepath_raw:
                if textureNode.image.filepath:
                    return bpy.path.abspath(textureNode.image.filepath)
                else:
                    return bpy.path.abspath(textureNode.image.filepath_raw)
            else:
                print("Found image texture with an image property, but the image had an empty file path.")
        else:
            print("Found an image texture, but its image property was empty.")
        return None

    def findTransparencyTextureNode(self):
        if not self._principledNode:
            return None
        dtn = self._findNodeLinkedToPrincipled("Transmission")
        if not dtn:
            print("The principled node did not have anything linked to its Transmission input, so there is no transparency texture node")
            return None
        if not isinstance(dtn, ShaderNodeTexImage):
            print("The principled node had a link to its Transmission input, but the source was not an image texture. Giving up on finding a transparency texture node.")
            return None
        return dtn

    def findTransparencyTextureFilePath(self):
        if not self._principledNode:
            return None
        fnode = self.findTransparencyTextureNode()
        return self._extractImageFilePath(fnode)

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
        fnode = self.findDiffuseTextureNode()
        return self._extractImageFilePath(fnode)

    def findBumpMapNode(self):
        if not self._principledNode:
            return None
        nn = self._findNodeLinkedToPrincipled("Normal")
        if not nn:
            print("The principled node did not have anything linked to its Normal input, so there is no bumpmap texture node")
            return None
        if isinstance(nn, ShaderNodeBump):
            return nn
        return None

    def findBumpMapTextureNode(self):
        nn = self.findBumpMapNode()
        if not nn:
            return None
        return self._findNodeLinkedTo(nn, "Height")

    def findBumpMapIntensity(self):
        nn = self.findBumpMapNode()
        if not nn:
            return None
        return nn.inputs['Strength'].default_value

    def findBumpMapTextureFilePath(self):
        if not self._principledNode:
            return None
        fnode = self.findBumpMapTextureNode()
        return self._extractImageFilePath(fnode)

    def findNormalMapNode(self):
        if not self._principledNode:
            return None
        nn = self._findNodeLinkedToPrincipled("Normal")
        if not nn:
            print("The principled node did not have anything linked to its Normal input, so there is no normalmap texture node")
            return None
        if isinstance(nn, ShaderNodeBump):
            nn = self._findNodeLinkedTo(nn, "Normal")
            if not nn:
                return None
        if isinstance(nn, ShaderNodeNormalMap):
            return nn
        return None

    def findNormalMapTextureNode(self):
        nn = self.findNormalMapNode()
        if not nn:
            return None
        return self._findNodeLinkedTo(nn, "Color")

    def findNormalMapIntensity(self):
        nn = self.findNormalMapNode()
        if not nn:
            return None
        return nn.inputs['Strength'].default_value

    def findNormalMapTextureFilePath(self):
        if not self._principledNode:
            return None
        fnode = self.findNormalMapTextureNode()
        return self._extractImageFilePath(fnode)
