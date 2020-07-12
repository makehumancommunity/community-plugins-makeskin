#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import bpy.types
import re, os
from .utils import createEmptyMaterial
from .nodehelper import NodeHelper
from .mhmat_keys import MHMAT_KEYS, MHMAT_SHADER_KEYS, MHMAT_KEY_GROUPS, MHMAT_NAME_TO_KEY
from .keytypes import *
import shutil

class MHMat:

    def __init__(self, obj = None, fileName = None):

        if obj and fileName:
            raise ValueError("You cannot construct from both file and object at the same time")

        self.settings = dict()
        self.shaderConfig = dict()

        for keyObj in MHMAT_KEYS:
            self.settings[keyObj.keyName] = keyObj.defaultValue

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

        tn = nh.findTransmissionTextureNode()
        if tn and not nh.findTransmissionTextureFilePath():
            return pre + "a transmission map " + post

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

        sett["transmissionmapTexture"] = None
        dtp = nh.findTransmissionTextureFilePath()
        if dtp and str(dtp).strip():
            sett["transmissionmapTexture"] = str(dtp).strip()

        sett["roughnessmapTexture"] = None
        dtp = nh.findRoughnessTextureFilePath()
        if dtp and str(dtp).strip():
            sett["roughnessmapTexture"] = str(dtp).strip()

        sett["metallicmapTexture"] = None
        dtp = nh.findMetallicTextureFilePath()
        if dtp and str(dtp).strip():
            sett["metallicmapTexture"] = str(dtp).strip()

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

        diffuseColor = nh.getPrincipledSocketDefaultValue('Base Color')

        diffuseIntensity = nh.findNodeByName('diffuseIntensity')
        if diffuseIntensity:
            sett["diffuseIntensity"] = diffuseIntensity.inputs['Fac'].default_value
            diffuseColor = diffuseIntensity.inputs['Color1'].default_value

        sett["diffuseColor"] = [diffuseColor[0], diffuseColor[1], diffuseColor[2]]

        sett["emissiveColor"] = None
        col = nh.getPrincipledSocketDefaultValue("Emission")
        if col:
            if col[0] < 0.01 and col[1] < 0.01 and col[2] < 0.01:
                pass # emission is black
            else:
                sett["emissiveColor"] = [col[0], col[1], col[2]]

        roughness = nh.getPrincipledSocketDefaultValue('Roughness')
        r = 1.0 - roughness
        sett["shininess"] = r
        sett["specularColor"] = [r, r, r]
        sett["roughness"] = roughness

        sett["metallic"] = nh.getPrincipledSocketDefaultValue('Metallic')
        sett["ior"] = nh.getPrincipledSocketDefaultValue('IOR')


    def copyTextures(self, mhmatFilenameAbsolute, normalize=True, adjustSettings=True):
        matBaseName = os.path.basename(mhmatFilenameAbsolute)
        matLoc = os.path.dirname(mhmatFilenameAbsolute)
        (matBase, matExt) = os.path.splitext(matBaseName)

        for keyObj in MHMAT_KEYS:
            if isinstance(keyObj, MHMATFileKey) and keyObj.keyName in self.settings:
                key = keyObj.keyName
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

    def assignAsNodesMaterialForObj(self, obj, name, diffusePH=False, bumpPH=False, normalPH=False, transpPH=False, displacePH=False, roughnessPH=False, metallicPH=False):
        if obj is None:
            return

        if name is None:
            name = self.settings["name"]

        mat = createEmptyMaterial(obj,name)
        self.nodehelper = NodeHelper(obj)

        # create node-frame for MakeHuman additional nodes
        #
        frame = self.nodehelper.createMHNodeFrame ("MakeHuman Internal")

        # now add all internal values to this frame
        #
        for name in [ "shadeless", "wireframe", "transparent", "alphaToCoverage", "backfaceCull", "depthless", "castShadows", "receiveShadows" ]:
            self.nodehelper.createDummyNode(name, self.settings[name], frame)

        if self.settings["diffuseTexture"] or diffusePH:
            self.nodehelper.createDiffuseTextureNode(self.settings["diffuseTexture"])

        if self.settings["transmissionmapTexture"] or transpPH:
            self.nodehelper.createTransmissionTextureNode(self.settings["transmissionmapTexture"])

        if self.settings["metallicmapTexture"] or metallicPH:
            self.nodehelper.createMetallicTextureNode(self.settings["metallicmapTexture"])

        if self.settings["roughnessmapTexture"] or roughnessPH:
            self.nodehelper.createRoughnessTextureNode(self.settings["roughnessmapTexture"])

        if self.settings["displacementmapTexture"] or displacePH:
            self.nodehelper.createDisplacementTextureNode(self.settings["displacementmapTexture"])

        if self.settings["diffuseColor"] is not None:
            col = self.settings["diffuseColor"]
            col.append(1.0)
            self.nodehelper.setPrincipledSocketDefaultValue("Base Color", col)
            diffuseIntensity = self.nodehelper.findNodeByName("diffuseIntensity")
            if diffuseIntensity:
                diffuseIntensity.inputs['Color1'].default_value = col

        if self.settings["diffuseIntensity"] is not None:
            diffuseIntensity = self.nodehelper.findNodeByName("diffuseIntensity")
            if diffuseIntensity:
                diffuseIntensity.inputs['Fac'].default_value = self.settings["diffuseIntensity"]

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

        if self.settings["roughness"] is not None:
            self.nodehelper.setPrincipledSocketDefaultValue("Roughness", self.settings["roughness"])

        if self.settings["metallic"] is not None:
            self.nodehelper.setPrincipledSocketDefaultValue("Metallic", self.settings["metallic"])

        if self.settings["ior"] is not None:
            self.nodehelper.setPrincipledSocketDefaultValue("IOR", self.settings["ior"])
        
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
                        keyLower = key.lower()
                        value = None

                        if keyLower in MHMAT_NAME_TO_KEY:
                            keyObj = MHMAT_NAME_TO_KEY[keyLower]
                            keyCorrectCase = keyObj.keyName
                            if key != keyCorrectCase:
                                print("Autofixing case: " + key + " -> " + keyCorrectCase)
                                key = keyCorrectCase
                            if isinstance(keyObj, MHMATFileKey):
                                (usedKey, value) = keyObj.parseFile(parsedLine, location)
                            else:
                                (usedKey, value) = keyObj.parse(parsedLine)
                        else:
                            print("Not a valid key: " + key)
                        self.settings[key] = value
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
        mat = "# This is a material file for MakeHuman, produced by MakeSkin\n"

        for keyGroup in MHMAT_KEY_GROUPS:
            mat = mat + "\n// " + keyGroup + "\n\n"
            for keyNameLower in MHMAT_NAME_TO_KEY.keys():
                keyObj = MHMAT_NAME_TO_KEY[keyNameLower]
                keyName = keyObj.keyName
                if keyObj.keyGroup == keyGroup and not self.settings[keyName] is None:
                    mat = mat + keyName + " " + keyObj.asString(self.settings[keyName]) + "\n"

        mat = mat + "\n"
        mat = mat + "// Shader properties (only affects how things look in MakeHuman)\n\n"

        if self.litSphere:
            mat = mat + "shader shaders/glsl/litsphere\n"
            mat = mat + "shaderParam litsphereTexture litspheres/lit_" + str(self.litSphere) + ".png\n"
        for key in self.shaderConfig.keys():
            mat = mat + "shaderConfig " + key + " " + str(self.shaderConfig[key]) + "\n"

        mat = mat + "\n"
        mat = mat + "// The following settings would also have been valid, but do currently not have a value\n//\n"
        for keyName in MHMAT_NAME_TO_KEY.keys():
            keyObj = MHMAT_NAME_TO_KEY[keyName]
            key = keyObj.keyName
            if key not in self.settings or self.settings[key] is None:
                mat = mat + "// " + key + "\n"

        return mat
