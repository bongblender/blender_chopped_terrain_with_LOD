import bpy
import bmesh
from bpy.types import Context
from bpy.types import Operator


current_mode = str(bpy.context.object.mode)
selected_objects_name = str(bpy.context.view_layer.objects.active.name)
_lod_Steps = 3
_lod_name = ""
_lod_retio = 1
_primary_LOD = []
_block_ammount = 0
_ridge_lenth = 5

if _lod_name == "":
    _lod_name = "Terrain_LOD"
else:
    pass

#here i change view mode...
def change_mode(_mode):
    if _mode == "OBJECT":
        bpy.ops.object.editmode_toggle()
        print(_mode)
    elif _mode == "EDIT":
        bpy.ops.object.editmode_toggle()
        print(_mode)
    elif _mode == "SCULPT":
        bpy.ops.sculpt.sculptmode_toggle()
        print(_mode)
    elif _mode == "VERTEX_PAINT":
        bpy.ops.paint.vertex_paint_toggle()
        print(_mode)
    elif _mode == "WEIGHT_PAINT":
        bpy.ops.paint.weight_paint_toggle()
        print(_mode)
    elif _mode == "TEXTURE_PAINT":
        bpy.ops.paint.texture_paint_toggle()
        print(_mode)
    pass

#here I chopping the terrain into sections...
def chop_terrain(_lod_level):
    bpy.context.object.modifiers["Multires"].levels = _lod_level
    bpy.context.object.modifiers["Multires"].sculpt_levels = _lod_level
    bpy.context.object.modifiers["Multires"].render_levels = _lod_level

    change_mode("EDIT")
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.edge_split(type='EDGE')
    bpy.ops.mesh.separate(type='LOOSE')

#apply all modifire of every chopped sections...
def apply_modifires(_name):
    change_mode("OBJECT")
    for i in bpy.context.scene.objects:
        if _name in i.name:
            ob = bpy.context.scene.objects[str(i.name)]
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.shade_smooth(use_auto_smooth=True)
        else:
            pass

#here i am solving the terrain cracking problem...
def creating_ridge():
    bpy.ops.object.select_all(action='SELECT')
    change_mode("EDIT")
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, -_ridge_lenth)})
    bpy.ops.mesh.delete(type='FACE')
    change_mode("OBJECT")
    bpy.ops.object.select_all(action='DESELECT')
    pass

#hide or unhide selected object by name...
def hide_unhide(_name, actionAsHIDEorUNHIDE):
    ob = bpy.context.scene.objects[_name]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True) 
    if actionAsHIDEorUNHIDE == "HIDE":
        bpy.context.object.hide_render = True
        bpy.context.object.hide_select = True
        bpy.context.object.hide_set(True)
    elif actionAsHIDEorUNHIDE == "UNHIDE":
        bpy.context.object.hide_render = False
        bpy.context.object.hide_select = False
        bpy.context.object.hide_set(False)
        
#emulate shift + h and alt + h...
def hide_everything_but_selected(_object_name, _action):
    if _action == "HIDE":
        for i in _primary_LOD:
            hide_unhide(i, "HIDE")
        hide_unhide(_object_name, "UNHIDE")
    elif _action == "UNHIDE":
        for i in _primary_LOD:
            hide_unhide(i, "UNHIDE")
            
#making copy as per _lod_Steps ....
def duplicate_rename_and_arrange():
    for i in range(0, _lod_Steps):
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
            bpy.context.view_layer.objects.active.name = _lod_name + str(i)
            
    for i in bpy.context.scene.objects:
        if str(i.name).__contains__(_lod_name) == True:
            _primary_LOD.append(str(i.name))
        else:
            pass
    hide_unhide(selected_objects_name, "HIDE")

#fliped the normal...
def _reset_transform_normal_origine():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    change_mode("EDIT")
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    change_mode("OBJECT")
    bpy.ops.object.select_all(action='DESELECT')
    pass

#here i create collection to arrange...
def creat_collection(_collection_name):
    collection = bpy.data.collections.new(_collection_name)
    bpy.context.scene.collection.children.link(collection)

#lower the lod retio...
_get_multires_level = int(bpy.context.object.modifiers["Multires"].levels)
def _lod_retio_set():
    global _get_multires_level
    _level = 0
    if _lod_retio != 0:
        _level = _get_multires_level - _lod_retio
        _get_multires_level = _level
    else:
        _level = _get_multires_level - 1
        _get_multires_level = _level
    print(_level + 1)
    return int(_level + 1)
    pass

#here i parent the objects...
def _parenting():
    global _block_ammount
    _parent_object_name = ""
    _child_object_name = ""
    for i in bpy.context.scene.objects:
        if _lod_name + "0" in i.name:
            _locaation_for_emty = bpy.data.objects[i.name].location
            print(_locaation_for_emty)
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=_locaation_for_emty, scale=(1, 1, 1))
            empty_object = bpy.context.object
            empty_object.name = str(i.name).replace(_lod_name + "0", "LOD_Holder")
            _block_ammount += 1
        else:
            pass
    for i in range(0, _block_ammount):
        _parent_object_name = ""
        _child_object_name = ""
        if i == 0:
            for j in range(0, _lod_Steps):
                if j == 0:
                    _parent_object_name = "LOD_Holder"
                    _child_object_name = _lod_name + str(j)
                    bpy.ops.object.select_all(action='DESELECT')
                    _parent_object = bpy.data.objects[_parent_object_name]
                    _child_object = bpy.data.objects[_child_object_name]
                    _parent_object.select_set(True)
                    _child_object.select_set(True)
                    bpy.context.view_layer.objects.active = _parent_object
                    bpy.ops.object.parent_set(type='OBJECT')
                else:
                    _child_object_name = _lod_name + str(j)
                    bpy.ops.object.select_all(action='DESELECT')
                    _parent_object = bpy.data.objects[_parent_object_name]
                    _child_object = bpy.data.objects[_child_object_name]
                    _parent_object.select_set(True)
                    _child_object.select_set(True)
                    bpy.context.view_layer.objects.active = _parent_object
                    bpy.ops.object.parent_set(type='OBJECT')
        else:
            for j in range(0, _lod_Steps):
                if j == 0:
                    _parent_object_name = "LOD_Holder" + "." + str('{:03d}'.format(i))
                    _child_object_name = _lod_name + str(j) + "." + str('{:03d}'.format(i))
                    bpy.ops.object.select_all(action='DESELECT')
                    _parent_object = bpy.data.objects[_parent_object_name]
                    _child_object = bpy.data.objects[_child_object_name]
                    _parent_object.select_set(True)
                    _child_object.select_set(True)
                    bpy.context.view_layer.objects.active = _parent_object
                    bpy.ops.object.parent_set(type='OBJECT')
                else:
                    _child_object_name = _lod_name + str(j) + "." + str('{:03d}'.format(i))
                    bpy.ops.object.select_all(action='DESELECT')
                    _parent_object = bpy.data.objects[_parent_object_name]
                    _child_object = bpy.data.objects[_child_object_name]
                    _parent_object.select_set(True)
                    _child_object.select_set(True)
                    bpy.context.view_layer.objects.active = _parent_object
                    bpy.ops.object.parent_set(type='OBJECT')

#main function.... 
def _main_driver():
    duplicate_rename_and_arrange()
    for i in range(0, len(_primary_LOD)):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[_primary_LOD[i]].select_set(True)
        hide_everything_but_selected(_primary_LOD[i], "HIDE")
        chop_terrain(_lod_retio_set())
        apply_modifires(_primary_LOD[i])
    hide_everything_but_selected(_primary_LOD[i], "UNHIDE")
    creating_ridge()
    _reset_transform_normal_origine()
    _parenting()

_main_driver()
