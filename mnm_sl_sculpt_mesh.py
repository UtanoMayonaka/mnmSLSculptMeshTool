# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#    "author": "Utano Mayonaka",
#    "version": (2, 8, 3),

###===================================
### import block 
###===================================

import bpy
import bmesh
import math

from addon_utils import *
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


###===================================
### function block 
###===================================

def mesh_plane(verts, faces, width, height, center_x, center_y):
    ### create vertices       
    for y in range(height):
        for x in range(width):
            verts.append(Vector(((x-center_x)/10, (y-center_y)/10, 0)))
        #END for
    #END for

    ### create faces       
    for y in range(height-1):
        for x in range(width-1):
            faces.append([y*width+x, y*width+x+1, (y+1)*width+x+1, (y+1)*width+x])
        #END for
    #END for
#END def


def mesh_cylinder(verts, faces, width, height, center_x, center_y):
    ### create vertices       
    for y in range(height):
        for x in range(width-1):
            theta = (math.pi * 2 / (width-1)) * ((width-1) - x)
            verts.append(Vector((math.sin(theta), math.cos(theta), (y-center_y)/10)))
        #END for
    #END for

    ### create faces       
    for y in range(height-1):
        for x in range(width-2):
            faces.append([y   *(width-1)+x,
                          y   *(width-1)+x+1,
                         (y+1)*(width-1)+x+1,
                         (y+1)*(width-1)+x])
        #END for
        faces.append([y   *(width-1)+(width-2),
                      y   *(width-1),
                     (y+1)*(width-1),
                     (y+1)*(width-1)+(width-2)])
    #END for
#END def


def mesh_sphere(verts, faces, width, height, center_x, center_y):
    ### create vertices       
    for y in range(height):
        theta = (math.pi / (height-1)) * y
        h = math.cos(theta)
        r = math.sin(theta)
        for x in range(width-1):
            theta = (math.pi * 2 / (width-1)) * x
            verts.append(Vector((math.cos(theta)*r, math.sin(theta)*r, -h)))
        #END for
    #END for

    ### create faces       
    for y in range(height-1):
        for x in range(width-2):
            faces.append([y   *(width-1)+x,
                          y   *(width-1)+x+1,
                         (y+1)*(width-1)+x+1,
                         (y+1)*(width-1)+x])
        #END for
        faces.append([y   *(width-1)+(width-2),
                      y   *(width-1),
                     (y+1)*(width-1),
                     (y+1)*(width-1)+(width-2)])
    #END for
#END def


def create_sculptmap_image(mesh, width, height):
    ### create uv map image
    w = (width-1) * 2
    h = (height-1) * 2
    imgSculptMap = bpy.data.images.new(name = mesh.name, width = w, height = h, alpha = True)

    uvmap = mesh.uv_layers.active
    uvco = []
    for y in range(height-1):
        for x in range(width-1):
            uvco.append([ x/(width-1),    y/(height-1),
                         (x+1)/(width-1), y/(height-1),
                         (x+1)/(width-1),(y+1)/(height-1),
                          x/(width-1),   (y+1)/(height-1)])
        #END for
    #END for

    for i, coord in enumerate(uvco):
        uvmap.data[i*4  ].uv = Vector((coord[0], coord[1]))
        uvmap.data[i*4+1].uv = Vector((coord[2], coord[3]))
        uvmap.data[i*4+2].uv = Vector((coord[4], coord[5]))
        uvmap.data[i*4+3].uv = Vector((coord[6], coord[7]))


def add_object(self, context):
    scene = context.scene
    aspect = scene.enum_prop_aspect
    shape = scene.enum_prop_shape

    width = 32
    height = 32
    center_x = 16
    center_y = 16
    type = "Cylinder"

    if aspect == '2':
        width = 17
        height = 65
        center_x = 8
        center_y = 32
    elif aspect == '4':
        width = 9
        height = 129
        center_x = 4
        center_y = 64        
    elif aspect == '8':
        width = 5
        height = 257
        center_x = 2
        center_y = 128        
    elif aspect == '16':
        width = 65
        height = 17
        center_x = 32
        center_y = 8        
    elif aspect == '32':
        width = 129
        height = 9
        center_x = 64
        center_y = 4        
    elif aspect == '64':
        width = 257
        height = 5
        center_x = 128
        center_y = 2        
    else:
        width = 33
        height = 33
        center_x = 16
        center_y = 16


    ### create mesh data ###
    verts = []
    edges = []
    faces = []
    mesh_name = "SL Mesh"
    if shape == '2':
        mesh_sphere( verts, faces, width, height, center_x, center_y )
        mesh_name += ' Sphere'
    elif shape == '3':
        mesh_plane( verts, faces, width, height, center_x, center_y )
        mesh_name += ' Plane'
    else:
        mesh_cylinder( verts, faces, width, height, center_x, center_y )
        mesh_name += ' Cylinder'

    mesh = bpy.data.meshes.new(name=mesh_name)
    mesh.from_pydata(verts, edges, faces)

    obj = bpy.data.objects.new(mesh.name, mesh)
    obj.location = scene.cursor.location
    obj['scpmap_height'] = height-1
    obj['scpmap_width'] = width-1
    
    current_col = bpy.context.view_layer.active_layer_collection.collection

    current_col.objects.link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


    ### add uv_texture
    bpy.ops.mesh.uv_texture_add()
    uvmap = bpy.context.object.data.uv_layers[0]
    uvmap.name = "UVMap"

    ### create uv map image
    create_sculptmap_image(mesh, width, height)
    
    ### setting material
    if "MaterialSculptMap" in bpy.data.materials.keys():
        mat = bpy.data.materials.get("MaterialSculptMap")
    else:
        mat = bpy.data.materials.new("MaterialSculptMap")
        mat.use_nodes = True
#        nodes = mat.node_tree.nodes
#        node = nodes.new('ShaderNodeBsdfDiffuse')
    #END if    

    obj.active_material = mat
#END def

# Unit Testing
if __name__ == '__main__':
    add_object(bpy.data, bpy.context)
    