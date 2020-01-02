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
