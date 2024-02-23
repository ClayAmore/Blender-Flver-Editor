import bpy
import bmesh
from math import radians
from mathutils import Vector
from ..util.util import Util
from ..formats.flver2.flver2 import FLVER2

class Importer:
    @staticmethod
    def do_import(path):
        flver = FLVER2()
        flver.read_path(path)

        for i, mesh in enumerate(flver.meshes):
            
            # Data from FLVER
            vertices = [vertice.position for vertice in mesh.vertices]
            uvs = [vertice.uvs[0] for vertice in mesh.vertices]
            indices = mesh.face_sets[0].triangluate(len(mesh.vertices) < Util.UShort.MAX_VALUE)
            faces = []
            for j in range(0, len(indices) - 2, 3):
                vi1 = indices[j]
                vi2 = indices[j + 1]
                vi3 = indices[j + 2]
                faces.append((vi1, vi2, vi3))

            # Add Meshes
            name = flver.materials[i].name
            bpy_mesh = bpy.data.meshes.new(name)
            bpy_obj = bpy.data.objects.new(name,bpy_mesh)
            bpy.context.collection.objects.link(bpy_obj)
            bpy.context.view_layer.objects.active = bpy_obj
            bpy_obj.select_set(True)
            bpy_obj.rotation_euler.x += radians(90)
            bpy_mesh.from_pydata(vertices, [], faces)

            # Add UVs
            bpy.ops.object.mode_set(mode='EDIT')
            bm = bmesh.from_edit_mesh(bpy_mesh)
            uv_layer = bm.loops.layers.uv.verify()
            for i, vert in enumerate(bm.verts):
                for loop in vert.link_loops:
                    loop_uv = loop[uv_layer]
                    loop_uv.uv = Vector((uvs[i][0], uvs[i][1]))
            bmesh.update_edit_mesh(bpy_mesh)
            bpy.ops.object.mode_set(mode='OBJECT')

            bpy_mesh.update()


            

