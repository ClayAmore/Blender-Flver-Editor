import os
import bpy
from .importer.importer import Importer
from bpy_extras.io_utils import ImportHelper

bl_info = {
 "name": "FLVER Importer-Exporter",
 "description": "Addon for importing and exporting FLVER files.",
 "author": "ClayAmore",
 "blender": (2, 80, 0),
 "version": (1, 0, 0),
 "category": "Import-Export",
 "location": "File > Import > Flver",
}
 
class ImportFLVER(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.flver"
    bl_label = "Import FLVER File"
    bl_options = {'PRESET'}
    filepath = ""

    filename_ext = ".flver"

    def execute(self, context):
        self.report({'INFO'}, f"Importing FLVER file: {self.filepath}")

        Importer.do_import(self.filepath)
        
        return {'FINISHED'}
    
def menu_func_import(self, context):
    self.layout.operator(ImportFLVER.bl_idname, text="FLVER (.flver)")

class FLVEREditor_PT_MainPanel(bpy.types.Panel):
    bl_idname = "FLVEREditor_PT_MainPanel"
    bl_label = "FLVER Editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Test Addon"
    bl_context = "objectmode"
 
    def draw(self, context):
 
        layout = self.layout
 
        row = layout.row()
        row.label(text="How cool is this!")
        row = layout.row()
        row.label(text=os.getcwd())
 
 
def register():
    bpy.utils.register_class(ImportFLVER)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(FLVEREditor_PT_MainPanel)
 
 
def unregister():
    bpy.utils.unregister_class(ImportFLVER)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(FLVEREditor_PT_MainPanel)
 
if __name__ == "__main__":
    register()