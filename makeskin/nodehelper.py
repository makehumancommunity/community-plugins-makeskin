#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import bpy.types
from bpy.types import ShaderNodeBsdfPrincipled, ShaderNodeTexImage, ShaderNodeNormalMap, ShaderNodeBump, ShaderNodeNormalMap, ShaderNodeDisplacement, ShaderNodeMixRGB
import pprint, os

_coords = dict()
_coords["diffuseTexture"] = [-500.0, 300.0]
_coords["diffuseIntensity"] = [-200, 400]
_coords["transmissionTexture"] = [-800.0, 200.0]
_coords["normalMapTextureSolo"] = [-600.0, -300.0]
_coords["normalMapSolo"] = [-250.0, -200.0]
_coords["bumpMapTextureSolo"] = [-600.0, 300.0]
_coords["bumpMapSolo"] = [-250.0, -200.0]
_coords["normalMapTextureDuo"] = [-800.0, -450.0]
_coords["normalMapDuo"] = [-500.0, -350.0]
_coords["bumpMapTextureDuo"] = [-600.0, -50.0]
_coords["bumpMapDuo"] = [-250.0, -150.0]
_coords["displacement"] = [-0.0, -350.0]
_coords["displacementTexture"] = [-300.0, -550.0]
_coords["roughnessTexture"] = [-1000.0, -100.0]
_coords["metallicTexture"] = [-1000.0, 450.0]

# dummy nodes

_coords["shadeless"] = [500.0, 450.0]
_coords["wireframe"] = [500.0, 350.0]
_coords["transparent"] = [500.0, 250.0]
_coords["alphaToCoverage"] = [500.0, 150.0]
_coords["backfaceCull"] = [500.0, 50.0]
_coords["depthless"] =  [500.0, -50.0]
_coords["castShadows"] = [500.0, -150.0]
_coords["receiveShadows"] = [500.0, -250.0]
_coords["litsphereTexture"] = [500.0, -350.0]


class NodeHelper:

    def __init__(self, obj):
        self.obj = obj
        self._material = obj.data.materials[0]
        self._nodetree = self._material.node_tree

        self._principledNode = self.findFirstNodeByClass(ShaderNodeBsdfPrincipled)
        self._diffuseTextureNode = None
        self._normalmapTextureNode = None
        self._bumpmapTextureNode = None
        self._outputNode = self.findFirstNodeByType('OUTPUT_MATERIAL')

    def findNodeByName(self, nodeName):
        for node in self._nodetree.nodes:
            if node.name == nodeName:
                return node
        return None

    def findFirstNodeByType(self, typeName):
        for node in self._nodetree.nodes:
            if node.type == typeName:
                return node
        return None

    def findFirstNodeByClass(self, typeClass):
        for node in self._nodetree.nodes:
            if isinstance(node, typeClass):
                return node
        return None

    def findNodeSocketDefaultValue(self, nodeName, socketName):
        node = self.findNodeByName(nodeName)
        if not node:
            return None
        if not node.inputs:
            print("Node of type " + str(type(node)) + " didn't have any inputs!?")
            return None
        if not socketName in node.inputs:
            print("Node of type " + str(type(node)) + " didn't have any input called " + socketName)
            return None
        return node.inputs[socketName].default_value

    def getPrincipledSocketDefaultValue(self, socketName):
        if not self._principledNode:
            return None
        return self._principledNode.inputs[socketName].default_value

    def setPrincipledSocketDefaultValue(self, socketName, socketValue):
        if not self._principledNode:
            return
        self._principledNode.inputs[socketName].default_value = socketValue

    def findNodeLinkedToSocket(self, nodeLinkedTo, nameOfSocket):
        if not nodeLinkedTo:
            return None
        sourceSideOfLink = None
        for link in self._nodetree.links:
            if link.to_node == nodeLinkedTo:
                socketLinkedTo = link.to_socket
                if socketLinkedTo.name == nameOfSocket:
                    sourceSideOfLink = link.from_node
        return sourceSideOfLink

    def findNodeLinkedToPrincipled(self, principledSocketName):
        return self.findNodeLinkedToSocket(self._principledNode, principledSocketName)

    def _createImageTextureNode(self, imagePathAbsolute=None, coordinatesName=None, colorspace="sRGB"):
        global _coords
        newTextureNode = self._nodetree.nodes.new("ShaderNodeTexImage")
        if coordinatesName:
            newTextureNode.location = _coords[coordinatesName]
        if imagePathAbsolute:
            imageFileName = os.path.basename(imagePathAbsolute)
            if imageFileName in bpy.data.images:
                print("image existed: " + imagePathAbsolute)
                image = bpy.data.images[imageFileName]
            else:
                image = bpy.data.images.load(imagePathAbsolute)
            image.colorspace_settings.name = colorspace
            newTextureNode.image = image
        return newTextureNode

    # create MakeHuman Nodeframe
    def createMHNodeFrame(self, name):
        frame_node = self._nodetree.nodes.new("NodeFrame")
        frame_node.label = name
        frame_node.name = name
        return frame_node

    # create unlinked value nodes
    #
    def createDummyNode(self, name, value, parent):
        # print ("Dummynode " + name + " " + str(value))
        node = None
        if type(value) is bool:
            node = self._nodetree.nodes.new("ShaderNodeValue")
            node.outputs["Value"].default_value = float(value)

        if type(value) is str:
            node = self._nodetree.nodes.new("ShaderNodeAttribute")
            node.attribute_name = value

        if node:
            node.location = _coords[name]
            node.parent = parent
            node.name = name
            node.label = name

        return node

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

    def createOnlyBump(self, bumpImagePathAbsolute=None, linkToPrincipled=True):
        global _coords
        (bmt, bm) = self._createBump(bumpImagePathAbsolute=bumpImagePathAbsolute, linkToPrincipled=linkToPrincipled)
        bmt.location = _coords["bumpMapTextureSolo"]
        bm.location = _coords["bumpMapSolo"]

    def _createBump(self, bumpImagePathAbsolute=None, linkToPrincipled=True):
        bumpmapTextureNode = self._createImageTextureNode(bumpImagePathAbsolute)
        if bumpImagePathAbsolute:
            bumpmapTextureNode.image.colorspace_settings.name = "Non-Color"
        bumpmapNode = self._nodetree.nodes.new("ShaderNodeBump")
        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(bumpmapNode.outputs["Normal"], self._principledNode.inputs["Normal"])
            self._nodetree.links.new(bumpmapTextureNode.outputs["Color"], bumpmapNode.inputs["Height"])
        bumpmapTextureNode.name = "bumpmapTexture"
        bumpmapTextureNode.label = "Bumpmap Texture"
        bumpmapNode.name = "bumpmap"
        bumpmapNode.label = "Bumpmap"
        return (bumpmapTextureNode, bumpmapNode)

    def _createNormal(self, normalImagePathAbsolute=None, linkToPrincipled=True):
        normalmapTextureNode = self._createImageTextureNode(normalImagePathAbsolute)
        if normalImagePathAbsolute:
            normalmapTextureNode.image.colorspace_settings.name = "Non-Color"
        normalmapNode = self._nodetree.nodes.new("ShaderNodeNormalMap")
        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(normalmapNode.outputs["Normal"], self._principledNode.inputs["Normal"])
            self._nodetree.links.new(normalmapTextureNode.outputs["Color"], normalmapNode.inputs["Color"])
        normalmapTextureNode.name = "normalmapTexture"
        normalmapTextureNode.label = "Normalmap Texture"
        normalmapNode.name = "normalmap"
        normalmapNode.label = "Normalmap"
        return (normalmapTextureNode, normalmapNode)

    def createOnlyNormal(self, normalImagePathAbsolute=None, linkToPrincipled=True):
        (nmt, nm) = self._createNormal(normalImagePathAbsolute=normalImagePathAbsolute, linkToPrincipled=linkToPrincipled)
        nmt.location = _coords["normalMapTextureSolo"]
        nm.location = _coords["normalMapSolo"]
        return nmt

    # test if a textureNode is well-defined, in case of error, return reason
    #
    def _extractImageFilePath(self, textureNode):
        if not textureNode:
            return (None, "WARNING: to test a None node for filename")
        if textureNode.image:
            if textureNode.image.filepath or textureNode.image.filepath_raw:
                if textureNode.image.filepath:
                    path = bpy.path.abspath(textureNode.image.filepath)
                    if os.path.isfile(path):
                        return (path, None)
                    return (None, path + " is not a file")
                else:
                    return (bpy.path.abspath(textureNode.image.filepath_raw), None) #  file test?!
            else:
                return (None, "Found image texture with an image property, but the image had an empty file path.")
        else:
            return (None, "Found an image texture, but its image property is empty.")

    def _findTextureFileName(self, nodeName):
        node = self.findNodeByName(nodeName)
        if not node:
            return (None, None)
        return self._extractImageFilePath(node)

    ##### DIFFUSE #####

    def createDiffuseTextureNode(self, imagePathAbsolute=None, linkToPrincipled=True):
        global _coords
        diffuseTextureNode = self._createImageTextureNode(imagePathAbsolute, "diffuseTexture")
        diffuseTextureNode.name = "diffuseTexture"
        diffuseTextureNode.label = "Diffuse Texture"

        diffuseIntensityNode = self._nodetree.nodes.new("ShaderNodeMixRGB")
        diffuseIntensityNode.name = "diffuseIntensity"
        diffuseIntensityNode.label = "diffuse intensity"
        diffuseIntensityNode.location = _coords["diffuseIntensity"]
        diffuseIntensityNode.inputs['Fac'].default_value = 1.0
        diffuseIntensityNode.inputs['Color1'].default_value = [1.0, 1.0, 1.0, 1.0]

        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(diffuseTextureNode.outputs["Color"], diffuseIntensityNode.inputs['Color2'])
            self._nodetree.links.new(diffuseIntensityNode.outputs["Color"], self._principledNode.inputs['Base Color'])
            self._nodetree.links.new(diffuseTextureNode.outputs["Alpha"], self._principledNode.inputs["Alpha"])

        return diffuseTextureNode

    def findDiffuseTextureNode(self):
        return self.findNodeByName("diffuseTexture")

    def findDiffuseTextureFilePath(self):
        return self._findTextureFileName("diffuseTexture")

    ##### TRANSMISSION #####

    def createTransmissionTextureNode(self, imagePathAbsolute=None, linkToPrincipled=True):
        transmissionTextureNode = self._createImageTextureNode(imagePathAbsolute, "transmissionTexture", colorspace="Non-Color")
        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(transmissionTextureNode.outputs["Color"], self._principledNode.inputs["Transmission"])
        transmissionTextureNode.name = "transmissionmapTexture"
        transmissionTextureNode.label = "Transmissionmap Texture"
        return transmissionTextureNode

    def findTransmissionTextureNode(self):
        return self.findNodeByName("transmissionmapTexture")

    def findTransmissionTextureFilePath(self):
        return self._findTextureFileName("transmissionmapTexture")

    ##### ROUGHNESS #####

    def createRoughnessTextureNode(self, imagePathAbsolute=None, linkToPrincipled=True):
        roughnessTextureNode = self._createImageTextureNode(imagePathAbsolute, "roughnessTexture", colorspace="Non-Color")
        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(roughnessTextureNode.outputs["Color"], self._principledNode.inputs["Roughness"])
        roughnessTextureNode.name = "roughnessmapTexture"
        roughnessTextureNode.label = "Roughnessmap Texture"
        return roughnessTextureNode

    def findRoughnessTextureNode(self):
        return self.findNodeByName("roughnessmapTexture")

    def findRoughnessTextureFilePath(self):
        return self._findTextureFileName("roughnessmapTexture")

    ##### METALLIC #####

    def createMetallicTextureNode(self, imagePathAbsolute=None, linkToPrincipled=True):
        metallicTextureNode = self._createImageTextureNode(imagePathAbsolute, "metallicTexture", colorspace="Non-Color")
        if linkToPrincipled and self._principledNode:
            self._nodetree.links.new(metallicTextureNode.outputs["Color"], self._principledNode.inputs["Metallic"])
        metallicTextureNode.name = "metallicmapTexture"
        metallicTextureNode.label = "Metallicmap Texture"
        return metallicTextureNode

    def findMetallicTextureNode(self):
        return self.findNodeByName("metallicmapTexture")

    def findMetallicTextureFilePath(self):
        return self._findTextureFileName("metallicmapTexture")

    ##### BUMP #####

    def findBumpMapNode(self):
        return self.findNodeByName("bumpmap")

    def findBumpMapTextureNode(self):
        return self.findNodeByName("bumpmapTexture")

    def findBumpMapIntensity(self):
        return self.findNodeSocketDefaultValue("bumpmap", "Strength")

    def findBumpMapTextureFilePath(self):
        return self._findTextureFileName("bumpmapTexture")

    ##### NORMAL #####

    def findNormalMapNode(self):
        return self.findNodeByName("normalmap")

    def findNormalMapTextureNode(self):
        return self.findNodeByName("normalmapTexture")

    def findNormalMapIntensity(self):
        return self.findNodeSocketDefaultValue("normalmap", "Strength")

    def findNormalMapTextureFilePath(self):
        return self._findTextureFileName("normalmapTexture")

    ##### DISPLACEMENT #####

    def createDisplacementTextureNode(self, imagePathAbsolute=None):
        global _coords
        displacementNode = self._nodetree.nodes.new("ShaderNodeDisplacement")
        displacementNode.location = _coords["displacement"]
        displacementTextureNode = self._createImageTextureNode(imagePathAbsolute, "displacementTexture")
        displacementTextureNode.location = _coords["displacementTexture"]
        self._nodetree.links.new(displacementNode.outputs["Displacement"], self._outputNode.inputs["Displacement"])
        self._nodetree.links.new(displacementTextureNode.outputs["Color"], displacementNode.inputs["Height"])
        displacementTextureNode.name = "displacementmapTexture"
        displacementTextureNode.label = "Displacementmap Texture"
        displacementNode.name = "displacementmap"
        displacementNode.label = "Displacementmap"
        return displacementTextureNode
    
    def findDisplacementNode(self):
        return self.findNodeByName("displacementmap")

    def findDisplacementTextureNode(self):
        return self.findNodeByName("displacementmapTexture")

    def findDisplacementTextureFilePath(self):
        return self._findTextureFileName("displacementmapTexture")

    def findDisplacementMapIntensity(self):
        return self.findNodeSocketDefaultValue("displacementmap", "Scale")




