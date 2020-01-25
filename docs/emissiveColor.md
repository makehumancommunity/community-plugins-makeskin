# emissiveColor

* __Data type:__ RGB floats
* __What is it for:__ controlling the color of emitted light
* __Use when:__ you want the material to shine 
* __Implemented in MakeSkin:__ no (but this is planned)
* __Makes visible difference in blender:__  no (but this is planned)
* __Makes visible difference in makehuman:__ no

The purpose of emissiveColor is to allow materials to emit light. Unfortunately it is not implemented
anywhere, not even in MakeHuman. Currently, setting this will have no visible effect anywhere.

The default is 0, 0, 0 (black), which means emit no light.

## Example

This will emit bright white light (or would if it was implemented):

    emissiveColor 1.0 1.0 1.0

