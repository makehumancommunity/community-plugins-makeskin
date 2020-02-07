# diffuseIntensity

* __Data type:__ float in range 0.0 to 1.0
* __What is it for:__ Controling the influence of the diffuseTexture
* __Use when:__ You want to mix the object's diffuse color and the diffuse texture in MakeHuman
* __Implemented in MakeSkin:__ no
* __Makes visible difference in blender:__ no
* __Makes visible difference in makehuman:__ yes

In MakeHuman, you can opt to not apply the diffuseTexture at 100% (1.0). If you, for example, want
the diffuseColor to have a 50% influence on the resulting diffuse color, you can set diffuseIntensity
to 0.5. This is ignored in Blender, where you either have a diffuseColor *or* a diffuseTexture. 

## Example

Mix diffuseColor and diffuseTexture equally:

    diffuseIntensity 0.5

