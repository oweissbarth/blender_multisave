# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "MultiSave",
    "author" : "Oliver Weissbarth",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 2),
    "location" : "Properties > Output",
    "warning" : "",
    "category" : "Generic"
}

import shutil
import os
import bpy
from bpy.app.handlers import persistent



class MULTISAVE_PT_Ui(bpy.types.Panel):
    bl_label = "MultiSave"
    bl_space_type = 'PROPERTIES'
    bl_region_type = "WINDOW"
    bl_context = "output"
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.template_list("MULTISAVE_UL_UiList", "", context.scene.multisave, "paths", context.scene.multisave, "active")
        col = row.column(align=True)
        col.operator("output.multisaveaddpath", icon="ADD", text="")
        col.operator("output.multisaveremovepath", icon="X", text="")


class MULTISAVE_UL_UiList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "path", text="", emboss=False, icon="FILE_FOLDER")

class MULTISAVE_PG_PathProperties(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty()

class MULTISAVE_PG_Properties(bpy.types.PropertyGroup):
    paths: bpy.props.CollectionProperty(type=MULTISAVE_PG_PathProperties)
    active: bpy.props.IntProperty()



class MULTISAVE_OT_AddPathOperator(bpy.types.Operator):
    bl_idname = "output.multisaveaddpath"
    bl_label = "MultiSaveAddPath"

    def execute(self, context):
        item = context.scene.multisave.paths.add()
        item.path = ""
        return {'FINISHED'}

class MULTISAVE_OT_RemovePathOperator(bpy.types.Operator):
    bl_idname = "output.multisaveremovepath"
    bl_label = "MultiSaveRemovePath"

    def execute(self, context):
        index = context.scene.multisave.active
        context.scene.multisave.paths.remove(index)
        return {'FINISHED'}


@persistent
def run_multisave(scene):
    if scene.render.is_movie_format:
        bpy.app.handlers.render_complete.append(multisave)
    else:
        bpy.app.handlers.render_write.append(multisave)

    bpy.app.handlers.render_complete.append(multisave_complete)


def multisave_complete(scene):
    if multisave in bpy.app.handlers.render_write:
        bpy.app.handlers.render_write.remove(multisave)
        bpy.app.handlers.render_complete.remove(multisave_complete)
    else:
        bpy.app.handlers.render_complete.remove(multisave)

    bpy.app.handlers.render_complete.remove(multisave_complete)

    print( bpy.app.handlers.render_complete)
    print(bpy.app.handlers.render_write)

def multisave(scene):
    filepath_src = scene.render.frame_path()
    filename = os.path.basename(filepath_src)
    for p in scene.multisave.paths:
        if not os.path.isdir(p.path):  
            print("%s is not a directory."%p.path)
            continue
        if not os.access(p.path, os.W_OK):
            print("%s is not writable a directory."%p.path)
            continue

        filepath_target = os.path.join(p.path, filename)
        shutil.copyfile(filepath_src, filepath_target)




classes = (
    MULTISAVE_PT_Ui,
    MULTISAVE_PG_PathProperties,
    MULTISAVE_PG_Properties,
    MULTISAVE_OT_AddPathOperator,
    MULTISAVE_OT_RemovePathOperator,
    MULTISAVE_UL_UiList
)

def register():
    import bpy
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.multisave = bpy.props.PointerProperty(type=MULTISAVE_PG_Properties)

    bpy.app.handlers.render_init.append(run_multisave)


def unregister():
    bpy.app.handlers.render_init.remove(run_multisave)
    del bpy.types.Scene.multisave
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
