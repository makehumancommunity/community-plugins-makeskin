#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import bpy.types
import re, os
from .utils import createEmptyMaterial
from .nodehelper import NodeHelper
from datetime import datetime
import shutil

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
        self.nodehelper = None

        if not obj is None:
            if len(obj.data.materials) > 0:
                # Only take first material into account
                self._blenderMaterial = obj.data.materials[0]

                if not hasattr(self._blenderMaterial, "node_tree") or not hasattr(self._blenderMaterial.node_tree, "nodes"):
                    raise ValueError("Only cycles/eevee materials are supported")
                else:
                    self.nodehelper = NodeHelper(obj)
                    self._parseNodeMaterial()
            else:
                raise ValueError("Object does not have any material")

        if not fileName is None:
            self._parseFile(fileName)

    def _parseNodeMaterial(self):
        nh = self.nodehelper
        sett = self.settings

        sett["diffuseTexture"] = None
        dtp = nh.findDiffuseTextureFilePath()
        if dtp and str(dtp).strip():
            sett["diffuseTexture"] = str(dtp).strip()

        sett["bumpmapTexture"] = None
        dtp = nh.findBumpMapTextureFilePath()
        if dtp and str(dtp).strip():
            sett["bumpmapTexture"] = str(dtp).strip()

        sett["normalmapTexture"] = None
        dtp = nh.findNormalMapTextureFilePath()
        if dtp and str(dtp).strip():
            sett["normalmapTexture"] = str(dtp).strip()

    def copyTextures(self, mhmatFilenameAbsolute, normalize=True, adjustSettings=True):
        matBaseName = os.path.basename(mhmatFilenameAbsolute)
        matLoc = os.path.dirname(mhmatFilenameAbsolute)
        (matBase, matExt) = os.path.splitext(matBaseName)
        for key in self._textureKeys:
            print(key)
            origLoc = self.settings[key]
            print(origLoc)
            if origLoc:
                (dummy, texExt) = os.path.splitext(origLoc)
                if not normalize:
                    baseName = os.path.basename(origLoc)
                else:
                    suffix = re.sub(r'Texture','',key)
                    suffix = re.sub(r'map','',suffix)
                    baseName = matBase + '_' + suffix + texExt
                destLoc = os.path.join(matLoc, baseName)
                shutil.copyfile(origLoc, destLoc)
                if adjustSettings:
                    self.settings[key] = baseName

    def assignAsNodesMaterialForObj(self, obj, diffusePH=False, bumpPH=False, normalPH=False):
        if obj is None:
            return
        now = datetime.now()
        name = "makeskin." + now.strftime("%Y%m%d%H:%M:%S")
        mat = createEmptyMaterial(obj,name)
        self.nodehelper = NodeHelper(obj)
        if self.settings["diffuseTexture"] or diffusePH:
            self.nodehelper.createDiffuseTextureNode(self.settings["diffuseTexture"])

        if self.settings["diffuseColor"] is not None:
            col = self.settings["diffuseColor"]
            col.append(1.0)
            self.nodehelper.setPrincipledSocketDefaultValue("Base Color", self.settings["diffuseColor"])
            mat.diffuse_color = col

        if self.settings["shininess"] is not None:
            self.nodehelper.setPrincipledSocketDefaultValue("Roughness", 1.0 - self.settings["shininess"])

        bump = bumpPH
        if self.settings["bumpmapTexture"]:
            bump = True

        normal = normalPH
        if self.settings["normalmapTexture"]:
            normal = True

        if bump and normal:
            self.nodehelper.createBumpAndNormal(bumpImagePathAbsolute=self.settings["bumpmapTexture"], normalImagePathAbsolute=self.settings["normalmapTexture"])
        else:
            if bump:
                self.nodehelper.createOnlyBump(bumpImagePathAbsolute=self.settings["bumpmapTexture"])
            if normal:
                self.nodehelper.createOnlyNormal(normalImagePathAbsolute=self.settings["normalmapTexture"])
        return mat

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
            "bumpmapIntensity",
            "normalmapIntensity",
            "displacementMapIntensity",
            "specularmapIntensity",
            "transparencymapIntensity",
            "aomapIntensity"]

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
        self.settings["specularColor"] = [0.3, 0.3, 0.3]  # R, G, B
        self.settings["shininess"] = 0.3
        self.settings["opacity"] = 1.0
        self.settings["transparent"] = False
        self.settings["alphaToCoverage"] = True
        self.settings["backfaceCull"] = False
        self.settings["depthless"] = False

    def _parseFile(self, fileName):
        full = os.path.abspath(fileName)
        location = os.path.dirname(full)
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
                                self.settings[key] = os.path.join(location, value)
                            if key in self._boolKeys:
                                self.settings[key] = (value.lower() == "true")
                            if key in self._floatKeys:
                                self.settings[key] = float(value)
                    else:
                        print("no match")
                        print(parsedLine)
                line = f.readline()
        print(self)
            
    def __str__(self):
        mat = "# This is a material file for MakeHuman, produced by MakeSkin\n\n"

        mat = mat + "// Metadata\n\n"
        for key in self._metadataKeys:
            if key in self.settings and not self.settings[key] is None:
                mat = mat + key + " " + str(self.settings[key]) + "\n"

        mat = mat + "\n"
        mat = mat + "// Color shading attributes\n\n"

        for key in self._colorKeys:
            if key in self.settings and not self.settings[key] is None:
                r = self.settings[key][0]
                g = self.settings[key][1]
                b = self.settings[key][2]
                mat = mat + key + " %.4f %.4f %.4f\n" % (r, g, b)

        mat = mat + "\n"
        mat = mat + "// Textures\n\n"

        for key in self._textureKeys:
            if key in self.settings and not self.settings[key] is None:
                mat = mat + key + " " + str(self.settings[key]) + "\n"

        mat = mat + "\n"
        mat = mat + "// SSS\n\n"

        for key in self._sssKeys:
            if key in self.settings and not self.settings[key] is None:
                mat = mat + key + " " + str(self.settings[key]) + "\n"

        mat = mat + "\n"
        mat = mat + "// Settings\n\n"

        for key in self._variousKeys:
            if key in self.settings and not self.settings[key] is None:
                mat = mat + key + " " + str(self.settings[key]) + "\n"

        # TODO: Consider handling intensities, shaderConfig and shaderParam, although it's unclear how these could be represented in a node setup

        mat = mat + "\n"
        mat = mat + "// The following settings would also have been valid, but do currently not have a value\n//\n"
        for key in self._keyList:
            if key not in self.settings or self.settings[key] is None:
                mat = mat + "// " + key + "\n"

        return mat
