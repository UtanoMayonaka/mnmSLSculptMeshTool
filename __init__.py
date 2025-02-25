ADDON_NAME = "mnm_slsmt"

bl_info = {
    "name": "SL Sculpt Mesh Tool",
    "author": "Utano Mayonaka",
    "version": (1, 2, 19),
    "blender": (4, 0, 0),
    "support": "COMMUNITY",
    "location": "View3D > Toolshelf > MnMSLsmt",
    "description": "Add a mesh of SL-Sculpt, and Generate UV and Sculpt texture.",
    "warning": "",
    "wiki_url": "",
    "doc_url": "https://github.com/UtanoMayonaka/mnmSLSculptMeshTool/blob/main/README.md",
    "tracker_url": "https://github.com/UtanoMayonaka/mnmSLSculptMeshTool/issues",
    "category": "Object",
}

###===================================
### import block 
###===================================



import os
import addon_utils
import bpy
from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
)
from bpy.props import (
    EnumProperty,
    PointerProperty,
    StringProperty,
)

from . import mnm_sl_sculpt_map
from . import mnm_sl_sculpt_mesh


# Try use the latest script
if "bpy" in locals():
    import importlib
    if "mnm_sl_sculpt_mesh" in locals():
        importlib.reload(mnm_sl_sculpt_mesh)
    if "mnm_sl_sculpt_map" in locals():
        importlib.reload(mnm_sl_sculpt_map)


###===================================
### class block 
###===================================

class MNM_OT_create_object(Operator):
    bl_idname = "object.mnm_create_object"
    bl_label = "Create Mesh"
    bl_description = "Add mesh(SL sculpt mesh), with UV and sclupt texture."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        self.report(
            {'INFO'}, "Shape: {:s} Aspect: {:s}".format(
                scene.enum_prop_shape, scene.enum_prop_aspect,
            )
        )
        mnm_sl_sculpt_mesh.add_object(self, context)

        return {'FINISHED'}
    #END def
#END class


class MNM_OT_bake_sculptmap(Operator):
    bl_idname = "render.mnm_bake_sculptmap"
    bl_label = "SL Sculp Map baker"
    bl_description = "Bake sculpt-map image(SL sculptedmap texture)."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        btn_activate = False
        active_object = context.active_object
        if active_object is not None:
            scpmap_width = active_object.get('scpmap_width', None)
            btn_activate = scpmap_width != None and (bpy.context.object.mode != 'EDIT' and active_object.select_get())
        #END if
        return btn_activate

    def execute(self, context):
        mnm_sl_sculpt_map.main(self, context)

        return {'FINISHED'}
    #END def
#END class


class MNM_PT_slsmt(Panel):
    bl_idname = "MNM_PT_MnMDesignTools"
    bl_label = "MnMDesign Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    bl_order = 0
    bl_category = "MnMDesign"


    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        version = "-1"
        for addon in addon_utils.modules():
            if addon.bl_info['name'] == "SL Sculpt Mesh Tool":
                version = addon.bl_info.get('version', (-1, -1, -1))

        credit_box = layout.box()
        credit_box.label( text='MnM Sculpt mesh tool Version: '+str(version) )

        column_shape = layout.column()
        column_shape.prop( scene, 'enum_prop_shape', text="Select shape" )

        column_aspect = layout.column()
        column_aspect.prop( scene, 'enum_prop_aspect', text="Select aspect" )

        create_btn = layout.row()
        create_btn.operator( MNM_OT_create_object.bl_idname, text='Create Mesh' )
        
        bake_box = layout.box()
        bake_box.label( text='Select sculpt object, and Bake sculpt map texture' )

        bake_btn = layout.row()
        bake_btn.operator( MNM_OT_bake_sculptmap.bl_idname, text='Bake' )
    #END def
#END class


###===================================
### register block 
###===================================

shape = EnumProperty(
    name="Shape",
    description="Mesh shape",
    override={'LIBRARY_OVERRIDABLE'},
    items=[
        ( "1", "Cylinder", "Polygonal Rod shape." ),
        ( "2", "Sphere", "Sphere shape." ),
        ( "3", "Plane", "Flat mesh shape." ),
        ],
    default = "1",
    )

aspect = EnumProperty(
    name="Aspect",
    description="Mesh acpect",
    override={'LIBRARY_OVERRIDABLE'},
    items=[
        ( "1", "1:1(32x32)", "32x32" ),
        ( "2", "1:4(16x64)", "16x64" ),
        ( "4", "1:16(8x128)", "8x128" ),
        ( "8", "1:32(4x256)", "4x256" ),
        ( "16", "4:1(64x16)", "64x16" ),
        ( "32", "16:1(128x8)", "128x8" ),
        ( "64", "32:1(256x4)", "256x4" ),
        ],
    default = "1",
    )

classes = (
    MNM_OT_create_object,
    MNM_OT_bake_sculptmap,
    MNM_PT_slsmt,
)

def register():
    # Object Properties

    bpy.types.Scene.enum_prop_shape = shape
    bpy.types.Scene.enum_prop_aspect = aspect
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.enum_prop_aspect
    del bpy.types.Scene.enum_prop_shape

if __name__ == '__main__':
    register()