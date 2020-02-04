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
        self.shaderConfig = dict()
        self._setupDefaultAndPlaceholders()

        # Internal variables for parsing object material
        self._nodes = None
        self._blenderMaterial = None
        self._principledNode = None

        self.diffuseTexture = None
        self.nodehelper = None
        self.litSphere = None

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

    def checkAllTexturesAreSaved(self):

        nh = self.nodehelper

        pre = "There is "
        post = " texture node, but it doesn't point at a physical file. You will need to save the image to a file before trying to save the material."

        tn = nh.findDiffuseTextureNode()
        if tn and not nh.findDiffuseTextureFilePath():
            return pre + "a diffuse image " + post

        tn = nh.findNormalMapTextureNode()
        if tn and not nh.findNormalMapTextureFilePath():
            return pre + "a normal map " + post

        tn = nh.findBumpMapTextureNode()
        if tn and not nh.findBumpMapTextureFilePath():
            return pre + "a bump map " + post

        tn = nh.findTransparencyTextureNode()
        if tn and not nh.findTransparencyTextureFilePath():
            return pre + "a transparency map " + post

        return ""

    def _parseNodeMaterial(self):

        sett = self.settings

        # Material properties, i.e not the node setup

        dc = self._blenderMaterial.diffuse_color
        sett["viewPortColor"] = [ dc[0], dc[1], dc[2] ]

        # Everything else should be from nodes

        nh = self.nodehelper

        sett["diffuseTexture"] = None
        dtp = nh.findDiffuseTextureFilePath()
        if dtp and str(dtp).strip():
            sett["diffuseTexture"] = str(dtp).strip()

        sett["transparencymapTexture"] = None
        dtp = nh.findTransparencyTextureFilePath()
        if dtp and str(dtp).strip():
            sett["transparencymapTexture"] = str(dtp).strip()

        sett["bumpmapTexture"] = None
        dtp = nh.findBumpMapTextureFilePath()
        if dtp and str(dtp).strip():
            sett["bumpmapTexture"] = str(dtp).strip()
            sett["bumpmapIntensity"] = nh.findBumpMapIntensity()

        sett["normalmapTexture"] = None
        dtp = nh.findNormalMapTextureFilePath()
        if dtp and str(dtp).strip():
            sett["normalmapTexture"] = str(dtp).strip()
            sett["normalmapIntensity"] = nh.findNormalMapIntensity()

        sett["displacementmapTexture"] = None
        dtp = nh.findDisplacementTextureFilePath()
        if dtp and str(dtp).strip():
            sett["displacementmapTexture"] = str(dtp).strip()
            sett["displacementmapIntensity"] = nh.findDisplacementMapIntensity()

        sett["emissiveColor"] = None
        col = nh.getPrincipledSocketDefaultValue("Emission")
        if col:
            if col[0] < 0.01 and col[1] < 0.01 and col[2] < 0.01:
                pass # emission is black
            else:
                sett["emissiveColor"] = [col[0], col[1], col[2]]

        r = 1.0 - nh.getPrincipledSocketDefaultValue('Roughness')
        sett["shininess"] = r
        sett["specularColor"] = [r, r, r]

        d = nh.getPrincipledSocketDefaultValue('Base Color')
        sett["diffuseColor"] = [d[0], d[1], d[2]]

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
                origLoc = os.path.abspath(origLoc)
                destLoc = os.path.abspath(destLoc)
                if origLoc != destLoc:
                    shutil.copyfile(origLoc, destLoc)
                else:
                    print("Source and destination is same file, skipping texture copy for this entry")
                if adjustSettings:
                    self.settings[key] = baseName

    def assignAsNodesMaterialForObj(self, obj, diffusePH=False, bumpPH=False, normalPH=False, transpPH=False, displacePH=False):
        if obj is None:
            return
        now = datetime.now()
        name = "makeskin." + now.strftime("%Y%m%d%H:%M:%S")
        mat = createEmptyMaterial(obj,name)
        self.nodehelper = NodeHelper(obj)
        if self.settings["diffuseTexture"] or diffusePH:
            self.nodehelper.createDiffuseTextureNode(self.settings["diffuseTexture"])

        if self.settings["transparencymapTexture"] or transpPH:
            self.nodehelper.createTransparencyTextureNode(self.settings["transparencymapTexture"])

        if self.settings["displacementmapTexture"] or displacePH:
            self.nodehelper.createDisplacementTextureNode(self.settings["displacementmapTexture"])

        if self.settings["diffuseColor"] is not None:
            col = self.settings["diffuseColor"]
            col.append(1.0)
            self.nodehelper.setPrincipledSocketDefaultValue("Base Color", col)

        if self.settings["viewPortColor"] is not None:
            col = self.settings["viewPortColor"]
            col.append(1.0)
            mat.diffuse_color = col

        if self.settings["emissiveColor"] is not None:
            col = self.settings["emissiveColor"]
            col.append(1.0)
            self.nodehelper.setPrincipledSocketDefaultValue("Emission", col)

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
            "ambientColor",
            "viewPortColor"]

        self._textureKeys = [

            "diffuseTexture",
            "bumpmapTexture",
            "normalmapTexture",
            "displacementmapTexture",
            "specularmapTexture",
            "transparencymapTexture",
            "aomapTexture",
            "blendMaterial"]

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
            "receiveShadows",
            "autoBlendSkin"]

        self._boolKeys = [
            "shadeless",
            "wireframe",
            "transparent",
            "backfaceCull",
            "depthless",
            "castShadows",
            "receiveShadows",
            "sssEnable",
            "autoBlendSkin"
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

        self.shaderConfig["ambientOcclusion"] = True
        self.shaderConfig["normal"] = False
        self.shaderConfig["bump"] = False
        self.shaderConfig["displacement"] = False
        self.shaderConfig["vertexColors"] = False
        self.shaderConfig["spec"] = True
        self.shaderConfig["transparency"] = True
        self.shaderConfig["diffuse"] = True

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
                        if parsedLine.startswith("shader"):
                            pass
                            # TODO: check for shaderConfig, shader and shaderParam
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
        mat = mat + "// Intensities\n\n"

        for key in self._intensityKeys:
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

        mat = mat + "\n"
        mat = mat + "// Shader properties (only affects how things look in MakeHuman)\n\n"

        if self.litSphere:
            mat = mat + "shader shaders/glsl/litsphere\n"
            mat = mat + "shaderParam litsphereTexture litspheres/lit_" + str(self.litSphere) + ".png\n"
        for key in self.shaderConfig.keys():
            mat = mat + "shaderConfig " + key + " " + str(self.shaderConfig[key]) + "\n"

        mat = mat + "\n"
        mat = mat + "// The following settings would also have been valid, but do currently not have a value\n//\n"
        for key in self._keyList:
            if key not in self.settings or self.settings[key] is None:
                mat = mat + "// " + key + "\n"

        return mat
