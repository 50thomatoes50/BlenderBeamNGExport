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

# Script copyright (C) Thomas PORTASSAU (50thomatoes50)

# <pep8-80 compliant>

bl_info = {
    "name": "Export BeamNG.drive Jbeam format (.jbeam)",
    "author": "Mike Baker (rmikebaker), Thomas Portassau (50thomatoes50) & Julien Vanelian (Distrikt64/Juju)",
    "location": "File > Import-Export",
    "version": (0, 3, 0),
    "blender": (2, 80, 0),
    "wiki_url": 'http://wiki.beamng.com/Blender_Exporter_plugin',
    "tracker_url": "https://github.com/50thomatoes50/BlenderBeamNGExport/issues",
    "warning": "Under construction!",
    "description": "Export nodes, beams and collision triangles for BeamNG.drive (.jbeam)",
    # "category": "Object"
    "category": "Import-Export"
}

import sys
import io
import bpy
import imp
import os

# __version__ = PrintVer(sys.modules.get(__name__).bl_info['version'])
__version__ = ''
# http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Multi-File_packages#init_.py
"""if "bpy" in locals():
    import imp
    if "export_jbeam" in locals():
        imp.reload(export_jbeam)
else:
    import bpy"""

for filename in [f for f in os.listdir(os.path.dirname(os.path.realpath(__file__))) if f.endswith(".py")]:
    if filename == os.path.basename(__file__): continue
    mod = sys.modules.get("{}.{}".format(__name__, filename[:-3]))
    if mod: imp.reload(mod)

from bpy.props import *
from bpy.utils import *
from .tools import *
from . import export_jbeam


class BeamGen(bpy.types.Operator):
    bl_idname = 'object.beamgen'
    bl_description = 'beamGen' + ' v.' + PrintVer()
    bl_label = 'beam(edge) generator'
    bl_options = {'REGISTER', 'UNDO'}

    # execute() is called by blender when running the operator.
    def execute(self, context):
        print("started")

        # Save currently active object
        # active = context.active_object
        active = context.edit_object
        if active is None:
            self.report({'ERROR'}, 'ERROR : Currently not in edit mode! Operation cancelled!')
            print('CANCELLED: Not in edit mode')
            return {'CANCELLED'}

        print("obj:" + active.name)
        nodes = []
        edge_tmp = []

        bpy.ops.object.mode_set(mode='OBJECT')

        for v in active.data.vertices:
            if v.select:
                nodes.append(v.index)

        nb_point = len(nodes)
        print("nb_point:" + str(nb_point))
        if nb_point <= 1:
            self.report({'ERROR'}, 'ERROR: Select more than 1 vertex')
            return {'CANCELLED'}

        origin = len(active.data.edges) - 1
        i = 0
        nb_edge = 0
        j = nb_point
        while j != 0:
            j -= 1
            nb_edge += (nb_point - (nb_point - j))
        active.data.edges.add(nb_edge)

        for n1 in nodes:
            for n2 in nodes:
                if n1 != n2 and n2 > n1:
                    i += 1
                    active.data.edges[origin + i].vertices[0] = n1
                    active.data.edges[origin + i].vertices[1] = n2

        bpy.ops.object.mode_set(mode='EDIT')

        # this lets blender know the operator finished successfully.
        return {'FINISHED'}


class IO_mesh_jbeam_ExporterChoice(bpy.types.Menu):
    bl_label = 'Export Jbeam' + ' v.' + PrintVer()

    def draw(self, context):

        l = self.layout
        l.operator_context = 'EXEC_DEFAULT'

        exportables = context.selected_objects
        if len(exportables):
            single_obs = []
            # print(exportables)
            for s in exportables:
                if s.type == 'MESH':
                    single_obs.append(s)
            '''groups = list([ex for ex in exportables if ex.ob_type == 'GROUP'])
            groups.sort(key=lambda g: g.name.lower())

            group_layout = l
            for i,group in enumerate(groups):
                if type(self) == SMD_PT_Scene:
                    if i == 0: group_col = l.column(align=True)
                    if i % 2 == 0: group_layout = group_col.row(align=True)
                group_layout.operator(SmdExporter.bl_idname, text=group.name, icon='GROUP').group = group.get_id().name'''
            group_col = l.column(align=True)
            group_layout = group_col.row(align=True)
            # group_layout.operator(ExportJbeam.bl_idname, text="group.name", icon='GROUP')
            num_obs = len(single_obs)
            # print(single_obs)
            # print(num_obs)
            if num_obs > 1:
                group_layout.operator(export_jbeam.ExportJbeam.bl_idname,
                                      text="Export selected objects (" + str(num_obs) + ")", icon='OBJECT_DATA')
            elif num_obs:
                group_layout.operator(export_jbeam.ExportJbeam.bl_idname, text=single_obs[0].name, icon='MESH_DATA')
        elif len(bpy.context.selected_objects):
            row = l.row()
            row.operator(export_jbeam.ExportJbeam.bl_idname, text="invalid selection", icon='ERROR')
            row.enabled = False

        row = l.row()
        num_scene_exports = getscene()

        row.operator(export_jbeam.ExportJbeam.bl_idname,
                     text="Scene(selectable): all mesh like *.jbeam (" + str(num_scene_exports) + ")",
                     icon='SCENE_DATA').export_scene = True
        row.enabled = num_scene_exports > 0


def getscene():
    num = 0
    for obj in bpy.context.selectable_objects:
        if obj.type == 'MESH':
            if '.jbeam' in obj.name:
                num += 1
    return num


def menu_func_export(self, context):
    # self.layout.operator(ExportJbeam.bl_idname, text='Export Jbeam v.' + __version__ + ' (.jbeam)')
    self.layout.menu("IO_mesh_jbeam_ExporterChoice", text='Export Jbeam v.' + PrintVer() + ' (.jbeam)')


updater_supported = True
try:
    import urllib.request, urllib.error, zipfile
except:
    updater_supported = False


class JbeamUpdated(bpy.types.Menu):
    bl_label = "Jbeam updated"

    def draw(self, context):
        self.layout.operator("wm.url_open", text="Change log available at Github",
                             icon='TEXT').url = "https://github.com/50thomatoes50/BlenderBeamNGExport/blob/master/changelod.md"


class JbeamUpdater(bpy.types.Operator):
    bl_idname = "script.update_jbeam"
    bl_label = "Jbeam updater"
    bl_description = "updater for Jbeam addon."

    @classmethod
    def poll(self, context):
        return updater_supported

    def execute(self, context):
        print("Jbeam update...")

        import sys
        cur_version = sys.modules.get(__name__.split(".")[0]).bl_info['version']

        try:
            data = urllib.request.urlopen(
                "https://raw.githubusercontent.com/50thomatoes50/BlenderBeamNGExport/master/io_mesh_jbeam/version.json").read().decode(
                'ASCII').split("\n")
            remote_ver = data[0].strip().split(".")
            remote_bpy = data[1].strip().split(".")
            download_url = data[2].strip()

            for i in range(min(len(remote_bpy), len(bpy.app.version))):
                if int(remote_bpy[i]) > bpy.app.version[i]:
                    self.report({'ERROR'}, "Blender is outdated. min ver:" + PrintVer(remote_bpy))
                    return {'FINISHED'}

            for i in range(min(len(remote_ver), len(cur_version))):
                try:
                    diff = int(remote_ver[i]) - int(cur_version[i])
                except ValueError:
                    continue
                if diff > 0:
                    print("Found new version {}, downloading from {}...".format(PrintVer(remote_ver), download_url))

                    zip = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(download_url).read()))
                    zip.extractall(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

                    self.report({'INFO'}, "update done " + PrintVer(remote_ver))
                    bpy.ops.wm.call_menu(name="JbeamUpdated")
                    return {'FINISHED'}

            self.report({'INFO'}, "update already latest " + PrintVer(cur_version))
            return {'FINISHED'}

        except urllib.error.URLError as err:
            self.report({'ERROR'}, " ".join(["update err download failed : " + str(err)]))
            return {'CANCELLED'}
        except zipfile.BadZipfile:
            self.report({'ERROR'}, "update err corruption")
            return {'CANCELLED'}
        except IOError as err:
            self.report({'ERROR'}, " ".join(["update err unknown : ", str(err)]))
            return {'CANCELLED'}


class JBEAM_Scene(bpy.types.Panel):
    bl_label = "JBeam Exporter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_default_closed = True

    def draw(self, context):
        l = self.layout
        scene = context.scene
        num_to_export = 0

        l.operator(export_jbeam.ExportJbeam.bl_idname, text="Export")

        row = l.row()
        row.alignment = 'CENTER'

        row = l.row()
        row.alert = len(scene.jbeam.export_path) == 0
        row.prop(scene.jbeam, "export_path")

        # row = l.row().split(0.33)
        # row.label(text="Export format")
        # row.row().prop(scene.jbeam,"export_format",expand=True)

        row = l.row()
        row.prop(scene.jbeam, "listbn")
        row.prop(scene.jbeam, "exp_ef")

        row = l.row()
        row.prop(scene.jbeam, "exp_tricol")
        row.prop(scene.jbeam, "exp_diag")


class Jbeam_SceneProps(bpy.types.PropertyGroup):
    export_path: bpy.props.StringProperty(name="Export Path", description="Where all the .jbeam files will be saved",
                                          subtype='DIR_PATH')
    export_format: bpy.props.EnumProperty(name="Export Format", items=(
        ('sel', "Selected", "Every selected object"), ('.jbeam', "*.jbeam", "All meshes with the name *.jbeam")),
                                          default='.jbeam')
    listbn: bpy.props.BoolProperty(name="List",
                                   description="Export has a list of nodes and beams\nElse export as a jbean file(json)",
                                   default=False)
    exp_ef: bpy.props.BoolProperty(name="Edges From Faces", description="Export edges from faces", default=True)
    exp_tricol: bpy.props.BoolProperty(name="Collision Triangles", description="Export faces to collision triangles",
                                       default=True)
    exp_diag: bpy.props.BoolProperty(name="Diagonal Quad Faces", description="Edge on quad face (automatic diagonals)",
                                     default=True)
    incompatible: bpy.props.BoolProperty(name="Incompatible type",
                                         description="This type of object is not compatible with the exporter. Use mesh type please.",
                                         default=True)


class Jbeam_ObjProps(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", description="", default="")
    slot: bpy.props.StringProperty(name="Slot of this jbeam", description="", default="main")
    nodename: bpy.props.StringProperty(name="Prefix of nodes", description="", default="n")


class JBEAM_Obj(bpy.types.Panel):
    bl_label = "JBeam parameter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_default_closed = True

    def draw(self, context):
        l = self.layout
        if not context.active_object.type == "MESH":
            # print("Object not mesh")
            row = l.row()
            row.prop(context.scene.jbeam, "incompatible")
        else:
            obj = context.active_object.data

            row = l.row()
            row.prop(obj.jbeam, "name")

            row = l.row()
            row.prop(obj.jbeam, "slot")

            row = l.row()
            row.prop(obj.jbeam, "nodename")


classes = (
    BeamGen,
    IO_mesh_jbeam_ExporterChoice,
    JbeamUpdated,
    JbeamUpdater,
    JBEAM_Scene,
    Jbeam_SceneProps,
    Jbeam_ObjProps,
    JBEAM_Obj,
    export_jbeam.ExportJbeam,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    def make_pointer(prop_type):
        return bpy.props.PointerProperty(name="Jbeam settings", type=prop_type)

    bpy.types.Scene.jbeam = make_pointer(Jbeam_SceneProps)
    bpy.types.Mesh.jbeam = make_pointer(Jbeam_ObjProps)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    del bpy.types.Scene.jbeam
    del bpy.types.Mesh.jbeam


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()
