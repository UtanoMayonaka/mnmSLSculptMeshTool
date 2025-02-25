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
#    "version": (1, 4, 0),

###===================================
### import block 
###===================================

import bpy
import bmesh
import os

from mathutils import Vector
from bpy.props import *


###===================================
### function block 
###===================================

def getRGB(x, y, z, xmin, ymin, zmin, xbase, ybase, zbase):
    r = 0.0
    g = 0.0
    b = 0.0
	
    if xbase > 0:
        r = (float(x) - xmin) / xbase
    #END if
    if ybase > 0:
        g = (float(y) - ymin) / ybase
    #END if
    if zbase > 0:
        b = (float(z) - zmin) / zbase
    #END if

    if r > 255:
        r = 255.0
    #END if
    if g > 255:
        g = 255.0
    #END if
    if b > 255:
        b = 255.0
    #END if

    result = [r/255.0, g/255.0, b/255.0]
    return result
#END def

def getRGBls(x, y, z, xmin, ymin, zmin, xbase, ybase, zbase):
    r = 0
    g = 0
    b = 0

    if float(x) < 0.005:
        r = int(round((float(x) + 1.28) * 100))
    else:
        r = int(round((float(x) + 1.27) * 100))
    #END if

    if float(y) < 0.005:
        g = int(round((float(y) + 1.28) * 100))
    else:
        g = int(round((float(y) + 1.27) * 100))
    #END if

    if float(z) < 0.005:
        b = int(round((float(z) + 1.28) * 100))
    else:
        b = int(round((float(z) + 1.27) * 100))
    #END if
		 
    if r > 255:
        r = 255.0
    #END if
    if g > 255:
        g = 255.0
    #END if
    if b > 255:
        b = 255.0
    #END if

    result = [r/255.0, g/255.0, b/255.0]
    return result
#END def

def PrintInformation(obj, bb):
    mesh = bpy.context.blend_data.meshes[obj.data.name]

    print ("\n")
    print ("Sculpt map for SL >>")
    print ("Object Name: " + obj.data.name)
#    print ("Faces Count: %i" % len(mesh.faces))
    print ("Object Size: X %f" % bb[0],"Y %f" % bb[1], "Z %f" % bb[2])
#END def

def create_sculptmap_image(mesh, width, height):
    ### create uv map image
    w = width * 2
    h = height * 2
    imgSculptMap = bpy.data.images.new(name = mesh.name, width = w, height = h, alpha = True)


def main(self, context):
    obj = context.active_object
    mesh = obj.data

    bbox = obj.bound_box
    bb_x = []
    bb_y = []
    bb_z = []
    for v in bbox:
        bb_x.append(v[0])
        bb_y.append(v[1])
        bb_z.append(v[2])
    #END for
    bb_x.sort()
    bb_y.sort()
    bb_z.sort()

    bb_x_min = bb_x[0]
    bb_x_max = bb_x[7]
    bb_y_min = bb_y[0]
    bb_y_max = bb_y[7]
    bb_z_min = bb_z[0]
    bb_z_max = bb_z[7]

    bb = obj.dimensions #object bound-box size
    # display information...
    PrintInformation(obj, bb)

    f_base_x = bb[0] / 256
    f_base_y = bb[1] / 256
    f_base_z = bb[2] / 256

    sculp_map = bpy.data.images.get(obj.name, None)
    if sculp_map == None:
        create_sculptmap_image(mesh, obj['scpmap_width'], obj['scpmap_height'])
        sculp_map = bpy.data.images[obj.name]
    #END if
    
    maskimg = None
    for tex in bpy.data.textures:
        tname = tex.name.lower()
        print(tname)
        if tname == "mask":
            maskimg = tex.image
        #END if
    #END for
    if maskimg == None:
        maskimg = sculp_map
    #END if

    uv_xbase = 1.0 / sculp_map.size[0]
    uv_ybase = 1.0 / sculp_map.size[1]

    for polygon in mesh.polygons:
        v1  = polygon.vertices[0]
        v2  = polygon.vertices[1]
        v3  = polygon.vertices[2]
        v4  = polygon.vertices[3]
        idx = polygon.index*4

        uv  = mesh.uv_layers[0].data[idx].uv

        px = round(uv.x / uv_xbase)
        py = round(uv.y / uv_ybase)
        v = mesh.vertices[v1].co
        rgb = getRGB("%f" %v.x, "%f" %v.y, "%f" %v.z, bb_x_min,bb_y_min,bb_z_min, f_base_x,f_base_y,f_base_z)

        pixidx = (px*4) + (py*4*sculp_map.size[0]);
        sculp_map.pixels[pixidx+0] = rgb[0]
        sculp_map.pixels[pixidx+1] = rgb[1]
        sculp_map.pixels[pixidx+2] = rgb[2]
        sculp_map.pixels[pixidx+3] = maskimg.pixels[pixidx+3]


        uv  = mesh.uv_layers[0].data[idx+1].uv

        px = round(uv.x / uv_xbase)-1
        py = round(uv.y / uv_ybase)
        v = mesh.vertices[v2].co
        rgb = getRGB("%f" %v.x, "%f" %v.y, "%f" %v.z, bb_x_min,bb_y_min,bb_z_min, f_base_x,f_base_y,f_base_z)

        pixidx = (px*4) + (py*4*sculp_map.size[0]);
        sculp_map.pixels[pixidx+0] = rgb[0]
        sculp_map.pixels[pixidx+1] = rgb[1]
        sculp_map.pixels[pixidx+2] = rgb[2]
        sculp_map.pixels[pixidx+3] = maskimg.pixels[pixidx+3]

        uv  = mesh.uv_layers[0].data[idx+2].uv

        px = round(uv.x / uv_xbase)-1
        py = round(uv.y / uv_ybase)-1
        v = mesh.vertices[v3].co
        rgb = getRGB("%f" %v.x, "%f" %v.y, "%f" %v.z, bb_x_min,bb_y_min,bb_z_min, f_base_x,f_base_y,f_base_z)

        pixidx = (px*4) + (py*4*sculp_map.size[0]);
        sculp_map.pixels[pixidx+0] = rgb[0]
        sculp_map.pixels[pixidx+1] = rgb[1]
        sculp_map.pixels[pixidx+2] = rgb[2]
        sculp_map.pixels[pixidx+3] = maskimg.pixels[pixidx+3]

        uv  = mesh.uv_layers[0].data[idx+3].uv

        px = round(uv.x / uv_xbase)
        py = round(uv.y / uv_ybase)-1
        v = mesh.vertices[v4].co
        rgb = getRGB("%f" %v.x, "%f" %v.y, "%f" %v.z, bb_x_min,bb_y_min,bb_z_min, f_base_x,f_base_y,f_base_z)

        pixidx = (px*4) + (py*4*sculp_map.size[0]);
        sculp_map.pixels[pixidx+0] = rgb[0]
        sculp_map.pixels[pixidx+1] = rgb[1]
        sculp_map.pixels[pixidx+2] = rgb[2]
        sculp_map.pixels[pixidx+3] = maskimg.pixels[pixidx+3]
    #END for    
#END def

# Unit Testing
if __name__ == '__main__':
    main(bpy.data, bpy.context)
    