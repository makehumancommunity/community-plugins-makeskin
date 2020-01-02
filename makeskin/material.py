#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import bpy.types
import re
from bpy.types import ShaderNodeBsdfPrincipled, ShaderNodeTexImage
from .utils import createEmptyMaterial
from datetime import datetime
import pprint

class MHMat:

    def __init__(self, obj = None, fileName = None):

        if obj and fileName:
            raise ValueError("You cannot construct from both file and object at the same time")

        self.settings = dict()
        self._setupDefaultAndPlaceholders()

        # Internal variables for parsing object material
        self._nodes = None
        self._blenderMaterial = None
        self._principledNode = None

        self.diffuseTexture = None

        if not obj is None:
            if len(obj.data.materials) > 0:
                # Only take first material into account
                self._blenderMaterial = obj.data.materials[0]

                if not hasattr(self._blenderMaterial, "node_tree") or not hasattr(self._blenderMaterial.node_tree, "nodes"):
                    raise ValueError("Only cycles/eevee materials are supported")
                else:
                    # We have a cycles/eevee material, or a blender-internal material with nodes
                    self._parseNodeTree(self._blenderMaterial.node_tree)
            else:
                raise ValueError("Object does not have any material")

        if not fileName is None:
            self._parseFile(fileName)

    def assignAsNodesMaterialForObj(self, obj, diffusePH=False, bumpPH=False, normalPH=False):
        if obj is None:
            return
        now = datetime.now()
        name = "makeskin." + now.strftime("%Y%m%d%H:%M:%S")
        mat = createEmptyMaterial(obj,name)

    def _setupDefaultAndPlaceholders(self):

        self._metadataKeys = [
            "tag",
            "name",
            "description",
            "uuid",
            "license",
            "homepage",
            "author"]

        self._colorKeys = [
            "diffuseColor",
            "specularColor",
            "emissiveColor",
            "ambientColor"]

        self._textureKeys = [

            "diffuseTexture",
            "bumpmapTexture",
            "normalmapTexture",
            "displacementmapTexture",
            "specularmapTexture",
            "transparencymapTexture",
            "aomapTexture"]

        self._intensityKeys = [

            "diffuseIntensity",
            "bumpMapIntensity",
            "normalMapIntensity",
            "displacementMapIntensity",
            "specularMapIntensity",
            "transparencyMapIntensity",
            "aoMapIntensity"]

        self._sssKeys = [
            "sssEnabled",
            "sssRScale",
            "sssGScale",
            "sssBScale"]

        self._variousKeys = [
            "shininess",
            "opacity",
            "translucency",
            "shadeless",
            "wireframe",
            "transparent",
            "alphaToCoverage",
            "backfaceCull",
            "depthless",
            "castShadows",
            "receiveShadows"]

        self._boolKeys = [
            "shadeless",
            "wireframe",
            "transparent",
            "backfaceCull",
            "depthless",
            "castShadows",
            "receiveShadows",
            "sssEnable"
        ]

        self._floatKeys = [
            "shininess",
            "opacity",
            "translucency",
            "sssRScale",
            "sssGScale",
            "sssBScale"
        ]

        self._floatKeys.extend(self._intensityKeys)

        # TODO: Consider shaderConfig and shaderParam

        self._keyList = self._metadataKeys + self._colorKeys + self._textureKeys + self._intensityKeys + self._sssKeys + self._variousKeys

        for key in self._keyList:
            self.settings[key] = None

        # Sensible defaults for when not specified by object or mhmat
        self.settings["diffuseColor"] = [0.5, 0.5, 0.5]  # R, G, B
        self.settings["specularColor"] = [0.5, 0.5, 0.5]  # R, G, B
        self.settings["shininess"] = 0.5
        self.settings["opacity"] = 1.0
        self.settings["transparent"] = False
        self.settings["alphaToCoverage"] = True
        self.settings["backfaceCull"] = False
        self.settings["depthless"] = False

    def _parseFile(self, fileName):
        with open(fileName, 'r') as f:
            line = f.readline()
            while line:
                parsedLine = line.strip()
                if parsedLine and not parsedLine.startswith("#") and not parsedLine.startswith("/"):
                    match = re.search(r'^([a-zA-Z]+)\s+(.*)$', parsedLine)
                    if match:
                        key = match.group(1)
                        value = match.group(2)
                        if key in self._colorKeys:
                            self.settings[key] = []
                            for part in re.split(r'\s+',value):
                                self.settings[key].append(float(part))
                        else:
                            if key in self._metadataKeys:
                                self.settings[key] = value
                            if key in self._textureKeys:
                                self.settings[key] = value
                            if key in self._boolKeys:
                                self.settings[key] = (value.lower() == "true")
                            if key in self._floatKeys:
                                self.settings[key] = float(value)
                    else:
                        print("no match")
                        print(parsedLine)
                line = f.readline()
        print(self)

    def _parseNodeTree(self, nodes):
        self._nodes = nodes

        # Assume there is a principled node to which everything else
        # is connected. So find that first
        for node in nodes.nodes:
            if isinstance(node,ShaderNodeBsdfPrincipled):
                self._parsePrincipled(node)

        self._findDiffuseTexture()

    def _parsePrincipled(self, principled):
        self._principledNode = principled
        self.diffuseColor = principled.inputs["Base Color"].default_value
        self.shininess = 1.0 - principled.inputs["Roughness"].default_value

    def _findDiffuseTexture(self):
        if not self._principledNode:
            return
        for link in self._nodes.links:
            if link.to_node == self._principledNode:
                tsock = link.to_socket
                if tsock.name == "Base Color":
                    fnode = link.from_node
                    if isinstance(fnode, ShaderNodeTexImage):
                        if fnode.image:
                            if fnode.image.filepath or fnode.image.filepath_raw:
                                if fnode.image.filepath:
                                    self.diffuseTexture = fnode.image.filepath
                                else:
                                    self.diffuseTexture = fnode.image.filepath_raw
                            else:
                                print("Found image texture with an image property, but the image had an empty file path. Giving up on finding a diffuse texture.")
                                return
                        else:
                            print("Found an image texture, but its image property was empty. Giving up on finding a diffuse texture.")
                            return
                    else:
                        print("The principled node had a link to its Base Color input, but the source was not an image texture. Giving up on finding a diffuse texture.")
                        return
        if self.diffuseTexture:
            self.diffuseTexture = bpy.path.abspath(self.diffuseTexture)
            print("Found a diffuse texture: " + self.diffuseTexture)
        else:
            print("There was no diffuse texture to be found")
            
    def __str__(self):
        mat = "# This is a material file for MakeHuman, produced by MakeSkin\n\n"

        mat = mat + "// Metadata\n\n"
        for key in self._metadataKeys:
            if key in self.settings and not self.settings[key] is None:
                mat = mat + key + " = " + str(self.settings[key]) + "\n"

        mat = mat + "\n"
        mat = mat + "// Color shading attributes\n\n"

        for key in self._colorKeys:
            if key in self.settings and not self.settings[key] is None:
                r = self.settings[key][0]
                g = self.settings[key][1]
                b = self.settings[key][2]
                mat = mat + key + " = %.4f %.4f %.4f\n" % (r, g, b)

        mat = mat + "\n"
        mat = mat + "// Textures\n\n"

        for key in self._textureKeys:
            if key in self.settings and not self.settings[key] is None:
                mat = mat + key + " = " + str(self.settings[key]) + "\n"

        mat = mat + "\n"
        mat = mat + "// SSS\n\n"

        for key in self._sssKeys:
            if key in self.settings and not self.settings[key] is None:
                mat = mat + key + " = " + str(self.settings[key]) + "\n"

        mat = mat + "\n"
        mat = mat + "// Settings\n\n"

        for key in self._variousKeys:
            if key in self.settings and not self.settings[key] is None:
                mat = mat + key + " = " + str(self.settings[key]) + "\n"

        # TODO: Consider handling intensities, shaderConfig and shaderParam, although it's unclear how these could be represented in a node setup

        mat = mat + "\n"
        mat = mat + "// The following settings would also have been valid, but do currently not have a value\n//\n"
        for key in self._keyList:
            if key not in self.settings or self.settings[key] is None:
                mat = mat + "// " + key + "\n"

        return mat
