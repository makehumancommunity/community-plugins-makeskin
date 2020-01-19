# MakeSkin

MakeSkin is a tool for working with MakeHuman materials. It is intended for uses where more advanced settings are needed,
as opposed to (for example) the rather primitive materials written by MakeClothes. 

It is also intended to cater for production of skin materials, something which was never supported by MakeClothes. 

In the longer run, it is intended that the full MHMAT model should be supported, with both import and export to/from
blender node setups. However, at this point, there are areas which do not map. See "compatibility matrix" below.
 
## Current status

This tool is as of yet pre-alpha and is not really usable for any real-world scenario. You will only want to download 
this if you intend to participate in the development.
 
## Installation and usage

Right now there is no build available. In order to use with Blender, you'll have to clone the source and either link or 
copy the "makeskin" directory to Blender's "addons" directory.

## Compatibility matrix

The following is an overview of how the MakeSkin material model fits into MHMAT, Blender and MakeHuman.

"Visible in blender" means that the material feature can be represented in such a way that it would make a visible difference 
in Blender (even if this has not been implemented by MakeSkin yet). "Visible in MH" means that the feature will make a visible 
difference in MakeHuman, under the right conditions. Not all shaders in MH support all material features.

| MHMAT key                   | Implemented in MakeSkin | Visible in Blender | Visible in MH  | Description |  
| :-------------------------- | :---------------------: | :----------------: | :------------: | ----------: |
| tag                         | PARTIAL                 | -                  | YES (filter)   |             |
| name                        | YES                     | -                  | -              |             |
| description                 | YES                     | -                  | -              |             |
| uuid                        | YES                     | -                  | -              |             |
| license                     | YES                     | -                  | -              |             |
| homepage                    | YES                     | -                  | -              |             |
| author                      | YES                     | -                  | -              |             |
| diffuseColor                | YES                     | YES                | YES            |             |
| specularColor               | PARTIAL                 | -                  | YES            |             |
| emissiveColor               | -                       | YES                | ?              |             |
| ambientColor                | -                       | -                  | ?              |             |
| diffuseTexture              | YES                     | YES                | YES            |             |
| bumpmapTexture              | YES                     | YES                | -              |             |
| normalmapTexture            | YES                     | YES                | YES            |             |
| displacementmapTexture      | -                       | YES                | ?              |             |
| specularmapTexture          | -                       | -                  | ?              |             |
| transparencymapTexture      | -                       | YES                | ?              |             |
| aomapTexture                | -                       | -                  | ?              |             |
| blendMaterial *             | YES                     | YES                | -              |             |
| diffuseIntensity            | -                       | -                  | YES            |             |
| bumpmapIntensity            | YES                     | YES                | -              |             |
| normalmapIntensity          | YES                     | YES                | YES            |             |
| displacementMapIntensity    | -                       | YES                | -              |             |
| specularmapIntensity        | -                       | -                  | ?              |             |
| transparencymapIntensity    | -                       | YES                | ?              |             |
| aomapIntensity              | -                       | -                  | ?              |             |
| sssEnabled                  | -                       | YES                | ?              |             |
| sssRScale                   | -                       | YES                | ?              |             |
| sssGScale                   | -                       | YES                | ?              |             |
| sssBScale                   | -                       | YES                | ?              |             |
| shininess                   | PARTIAL                 | YES                | YES            |             |
| opacity                     | -                       | -                  | ?              |             |
| translucency                | -                       | -                  | ?              |             |
| shadeless                   | YES                     | -                  | ?              |             |
| wireframe                   | YES                     | -                  | YES            |             |
| transparent                 | YES                     | -                  | ?              |             |
| alphaToCoverage             | YES                     | -                  | ?              |             |
| backfaceCull                | YES                     | -                  | YES            |             |
| depthless                   | YES                     | -                  | ?              |             |
| castShadows                 | YES                     | -                  | ?              |             |
| receiveShadows              | YES                     | -                  | ?              |             |
| litSphere (shader)          | YES                     | -                  | YES            |             |
| normalmap (shader)          | -                       | -                  | YES            |             |
| phong (shader)              | -                       | -                  | YES            |             |
| skin (shader)               | -                       | -                  | YES            |             |
| toon (shader)               | -                       | -                  | YES            |             |
| xray (shader)               | -                       | -                  | YES            |             |

