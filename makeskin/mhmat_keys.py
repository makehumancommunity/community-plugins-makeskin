#!/usr/bin/python
# -*- coding: utf-8 -*-

from .keytypes import *

MHMAT_KEY_GROUPS = ["Metadata", "Color", "Texture", "Intensity", "SSS", "Various"]

MHMAT_KEYS = []

### METADATA ###

MHMAT_KEYS.append(MHMATStringKey("tag", None, 'Metadata'))
MHMAT_KEYS.append(MHMATStringKey("name", None, 'Metadata'))
MHMAT_KEYS.append(MHMATStringKey("description", None, 'Metadata'))
MHMAT_KEYS.append(MHMATStringKey("uuid", None, 'Metadata'))
MHMAT_KEYS.append(MHMATStringKey("license", 'CC0', 'Metadata'))
MHMAT_KEYS.append(MHMATStringKey("homepage", None, 'Metadata'))
MHMAT_KEYS.append(MHMATStringKey("author", None, 'Metadata'))
            
### COLORS ###
        
MHMAT_KEYS.append(MHMATColorKey("diffuseColor", [0.5, 0.5, 0.5], 'Color'))
MHMAT_KEYS.append(MHMATColorKey("specularColor", [0.5, 0.5, 0.5], 'Color'))
MHMAT_KEYS.append(MHMATColorKey("emissiveColor", None, 'Color'))
MHMAT_KEYS.append(MHMATColorKey("ambientColor", None, 'Color'))
MHMAT_KEYS.append(MHMATColorKey("viewPortColor", None, 'Color'))

### TEXTURES ###

MHMAT_KEYS.append(MHMATFileKey("diffuseTexture", None, 'Texture'))
MHMAT_KEYS.append(MHMATFileKey("bumpmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MHMATFileKey("normalmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MHMATFileKey("displacementmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MHMATFileKey("specularmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MHMATFileKey("transmissionmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MHMATFileKey("transparencymapTexture", None, 'Texture'))
MHMAT_KEYS.append(MHMATFileKey("roughnessmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MHMATFileKey("metallicmapTexture", None, 'Texture'))
MHMAT_KEYS.append(MHMATFileKey("aomapTexture", None, 'Texture'))
                                 
### INTENSITIES ###

MHMAT_KEYS.append(MHMATFloatKey("diffuseIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MHMATFloatKey("bumpmapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MHMATFloatKey("normalmapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MHMATFloatKey("displacementMapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MHMATFloatKey("specularmapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MHMATFloatKey("transparencymapIntensity", None, 'Intensity'))
MHMAT_KEYS.append(MHMATFloatKey("aomapIntensity", None, 'Intensity'))

### SSS ###
        
MHMAT_KEYS.append(MHMATBooleanKey("sssEnabled", None, 'SSS'))
MHMAT_KEYS.append(MHMATFloatKey("sssRScale", None, 'SSS'))
MHMAT_KEYS.append(MHMATFloatKey("sssGScale", None, 'SSS'))
MHMAT_KEYS.append(MHMATFloatKey("sssBScale", None, 'SSS'))

### VARIOUS ###
        
MHMAT_KEYS.append(MHMATFileKey("blendMaterial", None, 'Various', blendMaterial=True))
MHMAT_KEYS.append(MHMATFloatKey("metallic", None, 'Various'))
MHMAT_KEYS.append(MHMATFloatKey("ior", None, 'Various'))
MHMAT_KEYS.append(MHMATFloatKey("roughness", 0.7, 'Various'))
MHMAT_KEYS.append(MHMATFloatKey("shininess", 0.3, 'Various'))
MHMAT_KEYS.append(MHMATFloatKey("opacity", 1.0, 'Various'))
MHMAT_KEYS.append(MHMATFloatKey("translucency", None, 'Various'))
MHMAT_KEYS.append(MHMATBooleanKey("shadeless", False, 'Various'))
MHMAT_KEYS.append(MHMATBooleanKey("wireframe", False, 'Various'))
MHMAT_KEYS.append(MHMATBooleanKey("transparent", False, 'Various'))
MHMAT_KEYS.append(MHMATBooleanKey("alphaToCoverage", True, 'Various'))
MHMAT_KEYS.append(MHMATBooleanKey("backfaceCull", True, 'Various'))
MHMAT_KEYS.append(MHMATBooleanKey("depthless", False, 'Various'))
MHMAT_KEYS.append(MHMATBooleanKey("castShadows", True, 'Various'))
MHMAT_KEYS.append(MHMATBooleanKey("receiveShadows", True, 'Various'))
MHMAT_KEYS.append(MHMATBooleanKey("autoBlendSkin", None, 'Various'))

MHMAT_NAME_TO_KEY = {}
for keyObj in MHMAT_KEYS:
    keyname = keyObj.keyNameLower
    MHMAT_NAME_TO_KEY[keyname] = keyObj

# SHADERS

MHMAT_SHADER_KEYS = []

MHMAT_SHADER_KEYS.append(MHMATStringKey("shader", None, 'Shaders'))
MHMAT_SHADER_KEYS.append(MHMATStringShaderKey("shaderParam litsphereTexture", None, 'Shaders'))
MHMAT_SHADER_KEYS.append(MHMATBooleanShaderKey("shaderConfig ambientOcclusion", True, 'Shaders'))
MHMAT_SHADER_KEYS.append(MHMATBooleanShaderKey("shaderConfig normal", False, 'Shaders'))
MHMAT_SHADER_KEYS.append(MHMATBooleanShaderKey("shaderConfig bump", False, 'Shaders'))
MHMAT_SHADER_KEYS.append(MHMATBooleanShaderKey("shaderConfig displacement", False, 'Shaders'))
MHMAT_SHADER_KEYS.append(MHMATBooleanShaderKey("shaderConfig vertexColors", False, 'Shaders'))
MHMAT_SHADER_KEYS.append(MHMATBooleanShaderKey("shaderConfig spec", True, 'Shaders'))
MHMAT_SHADER_KEYS.append(MHMATBooleanShaderKey("shaderConfig transparency", True, 'Shaders'))
MHMAT_SHADER_KEYS.append(MHMATBooleanShaderKey("shaderConfig diffuse", True, 'Shaders'))
