#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy


def hasMaterial(obj):
    if not obj.material_slots:
        return False
    return len(obj.material_slots) > 0


def createEmptyMaterial(obj, name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = 'HASHED'
    obj.data.materials.append(mat)
    return mat


def blendPath(path):
    """
    Converts a relative path to an asset in a blender library to an absolute path to the blend,
    the location of the asset in the blend and the name of the asset, ie return:

    (path, location, name)
    """
    blendPath, dirName, assetName = (part.strip() for part in path.rsplit('/', 2))
    return blendPath, dirName, assetName


def blendMatSave(path, fake_user=False):
    """
    Save the second material on the active object to a blend file.
    This writes into the file but will not overwrite it,
    although it might overwrite something already in it.
    """
    import bpy
    obj = bpy.context.active_object
    mat = obj.material_slots[1].material
    # May need to be more carfull with overwrites.
    bpy.data.libraries.write(str(path), {mat}, fake_user=fake_user)
    print('Wrote blend file into:', path)


def blendMatLoad(path, obj=None):
    """
    Load a material from a blend file determined by path, to a new material slot.
    """
    path, dirName, assetName = blendPath(path)
    print('Loading material @: ', path, dirName, assetName)
    with bpy.data.libraries.load(path) as (inBasket, outBasket):
        # Weird syntax.
        setattr(outBasket, dirName, [assetName])

    mat = getattr(outBasket, dirName)[0]
    mat.make_local()

    if obj is None:
        obj = bpy.context.active_object

    obj.data.materials.append(mat)
    return mat
