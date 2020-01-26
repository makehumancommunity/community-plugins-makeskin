# transparencymapTexture

* __Data type:__ filename
* __What is it for:__ mapping transparency of an object
* __Use when:__ you want transparency which takes IOR into account, or when the diffuse alpha channel isn't enough
* __Implemented in MakeSkin:__ yes
* __Makes visible difference in blender:__ yes
* __Makes visible difference in makehuman:__ no

Normally, you would implement transparency by using the alpha channel of the [diffuseTexture](diffuseTexture.md).
However, this only provide plain "alpha" transparency. It does not cater to, for example, IOR.

By using the transparencymapTexture, you can implement transparency that handles refraction and caustics. This is
useful for when, for example, you want to make glasses.

The transparencymapTexture is ignored in MakeHuman though, so it will only be visible in blender.

## Example

    transparencymapTexture mycharacter_transparency.png

