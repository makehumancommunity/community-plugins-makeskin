# diffuseColor

* __Data type:__ RGB floats
* __What is it for:__ controlling the color of the object
* __Use when:__ you want to set a color but don't want to use a texture
* __Implemented in MakeSkin:__ yes (it is read from "Base Color" of the principled node)
* __Makes visible difference in blender:__ yes (unless there is a diffuse texture)
* __Makes visible difference in makehuman:__ yes (unless there is a diffuse texture)

For simple materials which have no image texture, you can provide a solid color. If you 
also specify an image texture (by using the diffuseTexture key), the diffuseColor will
be ignored in both Blender and MakeHuman.

## Example

A yellow solid color:

    diffuseColor 1.0 1.0 0.5

