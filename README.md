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
difference in MakeHuman, under the right conditions (not all shaders in MH support all material features). 

It should be especially noted that the MHMAT model is wider than what is actually implemented in MakeHuman, so there are 
several keys that are supported by MHMAT, but which makes no visible difference at all in MakeHuman.

| MHMAT key                   | Implemented in MakeSkin | Visible in Blender | Visible in MH  | Description |  
| :-------------------------- | :---------------------: | :----------------: | :------------: | ----------: |
| tag                         | PARTIAL                 | -                  | YES            | Tags are used for filtering in MakeHuman. Materials support multiple tags, but MakeSkin currently only has support for one   |
| name                        | YES                     | -                  | -              | Name is a simple metadata string in MHMAT files. It isn't used for anything in practice.             |
| description                 | YES                     | -                  | -              | Description is a simple metadata string in MHMAT files. It isn't used for anything in practice.             |
| uuid                        | YES                     | -                  | ?              | UUID is used for telling materials apart. It is unclear if this is ever used though.            |
| license                     | YES                     | -                  | -              | License is a simple metadata string in MHMAT files. It isn't used for anything in practice.             |
| homepage                    | YES                     | -                  | -              | Homepage is a simple metadata string in MHMAT files. It isn't used for anything in practice.             |
| author                      | YES                     | -                  | -              | Author is a simple metadata string in MHMAT files. It isn't used for anything in practice.             |
| diffuseColor                | YES                     | YES                | YES            | This is the color of the material. It is usually overwritten by the diffuseTexture.            |
| specularColor               | PARTIAL                 | -                  | YES            | The color of specular highlights. This is not supported by nodes materials.            |
| emissiveColor               | -                       | YES                | ?              | What light (if any) is emitted by the material.            |
| ambientColor                | -                       | -                  | ?              | Color used for simulating ambient light. This is not supported by nodes materials            |
| diffuseTexture              | YES                     | YES                | YES            | The image file used for diffuse color texturing            |
| bumpmapTexture              | YES                     | YES                | -              | The image file used for bump mapping. No shaders in MH are able to represent this visually.            |
| normalmapTexture            | YES                     | YES                | YES            | The image file used for normal mapping.            |
| displacementmapTexture      | -                       | YES                | ?              | The image file used for displacement mapping.             |
| specularmapTexture          | -                       | -                  | ?              | (It'll have to be further investigated what this does, if anything)            |
| transparencymapTexture      | -                       | YES                | ?              | (It'll have to be further investigated what this does, if anything... We already have an alpha channel in the diffuse texture)            |
| aomapTexture                | -                       | -                  | ?              | The image file used for ambient occlusion mapping. This is not supported by node materials.            |
| blendMaterial *             | YES                     | YES                | -              | A file name pointing at a .blend file with a complete blender material. This is supported by MakeSkin, but not actually a part of the MHMAT spec.            |
| diffuseIntensity            | -                       | -                  | YES            | How much weight should be assigned to the diffuse texture (vs the diffuseColor key). Default is 1.0.            |
| bumpmapIntensity            | YES                     | YES                | -              | How strong is the bump map? Default is 1.0           |
| normalmapIntensity          | YES                     | YES                | YES            | How strong is the normal map? Default is 1.0            |
| displacementMapIntensity    | -                       | YES                | -              | How strong is the displacement map? Default is 1.0            |
| specularmapIntensity        | -                       | -                  | ?              | How strong is the specular map? Default is 1.0            |
| transparencymapIntensity    | -                       | YES                | ?              | How strong is the transparency map? Default is 1.0            |
| aomapIntensity              | -                       | -                  | ?              | How strong is the ao map? Default is 1.0            |
| sssEnabled                  | -                       | YES                | ?              | Should we use SSS at all?            |
| sssRScale                   | -                       | YES                | ?              | Scale of red SSS channel            |
| sssGScale                   | -                       | YES                | ?              | Scale of green SSS channel            |
| sssBScale                   | -                       | YES                | ?              | Scale of blue SSS channel            |
| shininess                   | PARTIAL                 | YES                | YES            | How shiny is the material. This has been implemented in reverse as roughness in blender.            |
| opacity                     | -                       | -                  | ?              | (It'll have to be further investigated what this does, if anything)            |
| translucency                | -                       | -                  | ?              | (It'll have to be further investigated what this does, if anything)            |
| shadeless                   | YES                     | -                  | ?              | (It'll have to be further investigated what this does, if anything)            |
| wireframe                   | YES                     | -                  | YES            | Whether to render the material as a wireframe in MH. Doesn't have any correspondence in blender.            |
| transparent                 | YES                     | -                  | ?              | Should we use transparency at all? (It'll have to be investigated what this actually does)            |
| alphaToCoverage             | YES                     | -                  | ?              | ?            |
| backfaceCull                | YES                     | -                  | YES            | Should we render both sides of a face or remove ("cull") the back side when rendering? This is not a material property in blender.           |
| depthless                   | YES                     | -                  | ?              | ?            |
| castShadows                 | YES                     | -                  | ?              | (It'll have to be further investigated what this does, if anything)            |
| receiveShadows              | YES                     | -                  | ?              | (It'll have to be further investigated what this does, if anything)            |
| litsphere (shader)          | YES                     | -                  | YES            | Use the "litsphere" shader when rendering in MakeHuman            |
| litsphere texture (param)   | YES                     | -                  | YES            | When using litsphere, use this texture to emulate reflections            |
| normalmap (shader)          | -                       | -                  | YES            | Use the "normalmap" shader when rendering in MakeHuman            |
| phong (shader)              | -                       | -                  | YES            | Use the "phong" shader when rendering in MakeHuman            |
| skin (shader)               | -                       | -                  | YES            | Use the "skin" shader when rendering in MakeHuman            |
| toon (shader)               | -                       | -                  | YES            | Use the "toon" shader when rendering in MakeHuman            |
| xray (shader)               | -                       | -                  | YES            | Use the "xray" shader when rendering in MakeHuman            |

There are also a bunch of other shaderParam settings which are not listed here. They are usually consequences of the above, such as "normal" 
for saying whether we should take the normal map into account. MakeSkin will infer this from whether the texture is set or not.
