#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import bpy.types
import re, os, random
from .utils import createEmptyMaterial, blendMatSave
from .extraproperties import _licenses, _litspheres
from .nodehelper import NodeHelper
from .mhmat_keys import MHMAT_KEYS, MHMAT_SHADER_KEYS, MHMAT_KEY_GROUPS, MHMAT_NAME_TO_KEY
from .keytypes import *
import shutil

DEBUG = False

class MHMat:

    def __init__(self, obj = None, fileName = None):

        if obj and fileName:
            raise ValueError("You cannot construct from both file and object at the same time")

        self.settings = dict()
        self.shaderConfig = dict()

        for keyObj in MHMAT_KEYS:
            self.settings[keyObj.keyName] = keyObj.defaultValue
            if DEBUG: print (keyObj.keyName)

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

    # test for all texture nodes and add an error text to be displayed on blender
    #
    def checkAllTexturesAreSaved(self):

        nh = self.nodehelper

        tn = nh.findDiffuseTextureNode()
        if tn:
            (name, err) = nh.findDiffuseTextureFilePath()
            if (err):
                return "Diffuse image: " + err

        tn = nh.findNormalMapTextureNode()
        if tn:
            (name, err) = nh.findNormalMapTextureFilePath()
            if (err):
                return "Normal map: " + err

        tn = nh.findBumpMapTextureNode()
        if tn:
            (name, err) = nh.findBumpMapTextureFilePath()
            if (err):
                return "Bump map: " + err

        tn = nh.findTransmissionTextureNode()
        if tn:
            (name, err) = nh.findTransmissionTextureFilePath()
            if (err):
                return "Transmission map: " + err

        return ""

    def _parseNodeMaterial(self):

        sett = self.settings

        # Material properties, i.e not the node setup

        dc = self._blenderMaterial.diffuse_color
        sett["viewPortColor"] = [ dc[0], dc[1], dc[2] ]

        # Everything else should be from nodes

        nh = self.nodehelper

        sett["diffuseTexture"] = None
        (dtp, err) = nh.findDiffuseTextureFilePath()
        if dtp and str(dtp).strip():
            sett["diffuseTexture"] = str(dtp).strip()

        sett["transmissionmapTexture"] = None
        (dtp, err) = nh.findTransmissionTextureFilePath()
        if dtp and str(dtp).strip():
            sett["transmissionmapTexture"] = str(dtp).strip()

        sett["roughnessmapTexture"] = None
        (dtp, err) = nh.findRoughnessTextureFilePath()
        if dtp and str(dtp).strip():
            sett["roughnessmapTexture"] = str(dtp).strip()

        sett["metallicmapTexture"] = None
        (dtp, err) = nh.findMetallicTextureFilePath()
        if dtp and str(dtp).strip():
            sett["metallicmapTexture"] = str(dtp).strip()

        sett["bumpmapTexture"] = None
        (dtp, err) = nh.findBumpMapTextureFilePath()
        if dtp and str(dtp).strip():
            sett["metallicmapTexture"] = str(dtp).strip()
            sett["bumpmapTexture"] = str(dtp).strip()
            sett["bumpmapIntensity"] = nh.findBumpMapIntensity()

        sett["normalmapTexture"] = None
        (dtp, err) = nh.findNormalMapTextureFilePath()
        if dtp and str(dtp).strip():
            sett["normalmapTexture"] = str(dtp).strip()
            sett["normalmapIntensity"] = nh.findNormalMapIntensity()

        sett["displacementmapTexture"] = None
        (dtp, err) = nh.findDisplacementTextureFilePath()
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
            if isinstance(keyObj, MHMATFileKey) and keyObj.keyName in self.settings and keyObj.keyName != "litsphereTexture":
                key = keyObj.keyName
                if DEBUG: print(key)
                origLoc = self.settings[key]
                if DEBUG: print(origLoc)
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
                        print ("copy from " + origLoc  + " to " + destLoc)
                        shutil.copyfile(origLoc, destLoc)
                    else:
                        print("Source and destination is same file, skipping texture copy for this entry")
                    if adjustSettings:
                        self.settings[key] = baseName

    #
    # create a node-setup for a new or loaded material
    # take information from scene and objects
    #
    def assignAsNodesMaterialForObj(self, scn, obj, mode_load=False):
        if obj is None or scn is None:
            return

        diffusePH=False
        bumpPH=False
        normalPH=False
        transpPH=False
        displacePH=False
        roughnessPH=False
        metallicPH=False
        name = None

        if mode_load is False:
            diffusePH = scn.MhMsCreateDiffuse
            normalPH = scn.MhMsCreateNormal
            bumpPH = scn.MhMsCreateBump
            transpPH = scn.MhMsCreateTrans
            roughnessPH = scn.MhMsCreateRough
            metallicPH = scn.MhMsCreateMetallic
            displacePH = scn.MhMsCreateDisp
            name = obj.name
            self.settings["litsphereTexture"] = obj.MhMsLitsphere
            self.settings["shadeless"] = obj.MhMsShadeless
            self.settings["transparent"] = obj.MhMsTransparent
            self.settings["alphaToCoverage"] = obj.MhMsAlphaToCoverage
            self.settings["backfaceCull"] = obj.MhMsBackfaceCull
            self.settings["depthless"] = obj.MhMsDepthless
            self.settings["castShadows"] = obj.MhMsCastShadows
            self.settings["receiveShadows"] = obj.MhMsReceiveShadows
            self.settings["wireframe"] = obj.MhMsWireframe
        else:
            name = self.settings["name"]
            obj.MhMsShadeless = self.settings["shadeless"]
            obj.MhMsTransparent = self.settings["transparent"]
            obj.MhMsAlphaToCoverage = self.settings["alphaToCoverage"]
            obj.MhMsBackfaceCull = self.settings["backfaceCull"]
            obj.MhMsDepthless = self.settings["depthless"]
            obj.MhMsCastShadows = self.settings["castShadows"]
            obj.MhMsReceiveShadows = self.settings["receiveShadows"]
            obj.MhMsWireframe = self.settings["wireframe"]
            for elem in _litspheres:
                if self.settings["litsphereTexture"] == elem[0]:
                    obj.MhMsLitsphere = self.settings["litsphereTexture"]
                    break

        if not name:
            # for the case that MHMAT file did not specify a name
            name = "makeSkinMaterial." + str(random.randint(10000,99999))

        mat = createEmptyMaterial(obj,name)
        self.nodehelper = NodeHelper(obj)

        # --- set the values in the menu (needed after import)
        #
        obj.MhMsName = mat.name # using mat.name instead of mat will take the real name like asset.001

        # license must fit to the values allowed
        #
        for elem in _licenses:
            if self.settings["license"] == elem[0]:
                obj.MhMsMatLicense = self.settings["license"]
                break

        if self.settings["description"]:
            obj.MhMsDescription = self.settings["description"]
        if self.settings["tag"]:
            obj.MhMsTag = self.settings["tag"]
        if self.settings["author"]:
            obj.MhMsAuthor = self.settings["author"]
        if self.settings["homepage"]:
            obj.MhMsHomepage = self.settings["homepage"]


        # --- visualization of MakeHuman internals in node-setup
        #
        # create node-frame for MakeHuman additional nodes
        #
        if scn.MhMsNodeVis:
            frame = self.nodehelper.createMHNodeFrame ("MakeHuman Internal")

            # now add all internal values to this frame
            #
            for nodename in [ "shadeless", "wireframe", "transparent", "alphaToCoverage", "backfaceCull", "depthless", "castShadows", "receiveShadows", "litsphereTexture" ]:
                self.nodehelper.createDummyNode(nodename, self.settings[nodename], frame)


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

            # TODO weird hack to be changed later, but otherwise col grows to infinity when 2nd material is added 
            if len(col) < 4:
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

    def writeMHmat(self, obj, fnAbsolute):

        errtext = None

        if obj.MhMsName:
            self.settings['name'] = obj.MhMsName

        if obj.MhMsTag:
            self.settings['tag'] = obj.MhMsTag

        if obj.MhMsDescription:
            self.settings['description'] = obj.MhMsDescription

        if obj.MhMsAuthor:
            self.settings['author'] = obj.MhMsAuthor

        if obj.MhMsHomepage:
            self.settings['homepage'] = obj.MhMsHomepage

        self.settings['license'] = obj.MhMsMatLicense
        self.settings['backfaceCull'] = obj.MhMsBackfaceCull
        self.settings['castShadows'] = obj.MhMsCastShadows
        self.settings['receiveShadows'] = obj.MhMsReceiveShadows
        self.settings['alphaToCoverage'] = obj.MhMsAlphaToCoverage
        self.settings['shadeless'] = obj.MhMsShadeless
        self.settings['wireframe'] = obj.MhMsWireframe
        self.settings['transparent'] = obj.MhMsTransparent
        self.settings['depthless'] = obj.MhMsDepthless
        self.settings['sssEnable'] = obj.MhMsSSSEnable
        self.settings['autoBlendSkin'] = obj.MhMsAutoBlend
        self.settings['writeBlendMaterial'] = obj.MhMsWriteBlendMaterial

        handling = "NORMALIZE"
        if obj.MhMsTextures:
            handling = obj.MhMsTextures
        if handling == "NORMALIZE":
            self.copyTextures(fnAbsolute)
        if handling == "COPY":
            self.copyTextures(fnAbsolute,normalize=False)
        # If handling is LINK, then paths are already correct

        if self.settings["normalmapTexture"]:
            self.shaderConfig["normal"] = True
        if self.settings["bumpmapTexture"]:
            self.shaderConfig["bump"] = True
        if obj.MhMsUseLit and obj.MhMsLitsphere:
            self.litSphere = obj.MhMsLitsphere
        if self.settings["displacementmapTexture"]:
            self.shaderConfig["displacement"] = True
        
        ##- Save blend -##
        if self.settings["writeBlendMaterial"]:
            if len(obj.material_slots) > 1:
                matName = obj.material_slots[1].name
            
                from pathlib import Path
                path = Path(fnAbsolute).with_suffix('.mat.blend')
                self.settings["blendMaterial"] = path.name+'/materials/'+matName
                blendMatSave(path)
            else:
                errtext = "Save blender material was skipped, because object does not have a second material."


        with open(fnAbsolute,'w') as f:
            f.write(str(self))

        return (errtext)


    def _parseFile(self, fileName):

        full = os.path.abspath(fileName)
        location = os.path.dirname(full)
        with open(fileName, 'r', errors='ignore') as f:
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
                            if key not in ["shader", "shaderConfig"]: print("Not a valid key: " + key)
                        #
                        # handle multiple occurences of tag (create a comma-separated entry)
                        #
                        if key == 'tag':
                            if self.settings[key]:
                                self.settings[key] += ", " + value
                            else:
                                self.settings[key] = value
                        elif key == 'shaderParam':
                            if value[0] == "litsphereTexture":
                                match = re.search(r'^litspheres\/(.*)\.png$', value[1])
                                if match:
                                    self.settings["litsphereTexture"] = match.group(1)
                                    if DEBUG: print (self.settings["litsphereTexture"])
                        else:
                            self.settings[key] = value
                    else:
                        if parsedLine.startswith("shader"):
                            # TODO: check for shaderConfig, shader 
                            pass
                        else:
                            print("no match")
                            print(parsedLine)
                line = f.readline()
        if DEBUG: print(self)

    def __str__(self):
        mat = "# This is a material file for MakeHuman, produced by MakeSkin\n"

        for keyGroup in MHMAT_KEY_GROUPS:
            mat = mat + "\n// " + keyGroup + "\n\n"
            for keyNameLower in MHMAT_NAME_TO_KEY.keys():
                keyObj = MHMAT_NAME_TO_KEY[keyNameLower]
                keyName = keyObj.keyName
                if keyObj.keyGroup == keyGroup and not self.settings[keyName] is None:
                    if keyName == "tag":
                        for elem in self.settings["tag"].split(","):
                            mat = mat + "tag " + elem.strip() + "\n"
                    else:
                        mat = mat + keyName + " " + keyObj.asString(self.settings[keyName]) + "\n"

        mat = mat + "\n"
        mat = mat + "// Shader properties (only affects how things look in MakeHuman)\n\n"

        if self.litSphere:
            mat = mat + "shader shaders/glsl/litsphere\n"
            mat = mat + "shaderParam litsphereTexture litspheres/" + str(self.litSphere) + ".png\n"
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
