# coding=utf-8
"""
一些通用的小工具。

"""
import json
from functools import partial
from pymel import core as pm

__author__ = 'Li Xiao Jun'
__version__ = '0.01'


class Singleton(object):
    """
    单例模式的基类，窗口类型的类都会继承这个类

    """

    _instance = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        pass


def write_json(dict_data=None, file_path=""):
    """
    将字典类型的数据写入一个json文件中

    :param dict_data: 字典类型的数据
    :param file_path: 文件的存放路径
    :return: None
    """
    if dict_data is None:
        dict_data = {}
    with open(file_path, "w") as f:
        json.dump(dict_data, f, indent=4)

    return


def read_json(file_path=""):
    """
    从json文件中读取数据，数据以字典类型作为返回值

    :param file_path: 文件的存放路径
    :return: dict
    """
    with open(file_path, 'r') as data:
        dict_data = json.load(data)
    return dict_data


def get_anim_range_from_node(node):
    """
    获取时间范围

    :param node:
    :return:
    """
    anim_curves = pm.listConnections(
        pm.PyNode(node), s=True, t='animCurve')
    start_time = 0.0
    end_time = 0.0
    if anim_curves:
        for anim_curve in anim_curves:
            if start_time < pm.keyframe(anim_curve, q=True, index=0):
                start_time = pm.keyframe(anim_curve, q=True, index=0)[0]
            if end_time < pm.keyframe(
                    anim_curve, q=True,
                    index=len(pm.keyframe(anim_curve, q=True, iv=True)) - 1):
                end_time = pm.keyframe(
                    anim_curve, q=True,
                    index=len(pm.keyframe(anim_curve, q=True, iv=True)) - 1)[0]
    else:
        start_time = pm.playbackOptions(q=True, min=True)
        end_time = pm.playbackOptions(q=True, max=True)
    return [start_time, end_time]


def set_time_unit(unit='ntsc'):
    current_unit = pm.currentUnit(q=True, time=True)
    if current_unit == unit:
        return
    else:
        current_unit = pm.currentUnit(time=unit)
        pm.playbackOptions(min=0)
        return


def duplicate_and_parent_jnt(search="", replace=""):
    """
    复制选择的骨头，并将新骨骼成为它的子对象

    :return:
    """
    duplicate_targets = pm.ls(sl=True)
    if len(duplicate_targets) > 0:
        for duplicate_target in duplicate_targets:
            new_name = duplicate_target.name().replace(search, replace)
            target = pm.duplicate(duplicate_target, name=new_name)
            pm.parent(target, duplicate_target)

        return True
    else:
        pm.error(u"请至少选择一根骨骼")
        return False


def clean_unknown_node():
    """
    清理场景中的未知节点

    :return:
    """
    unknown_plugin_list = pm.unknownPlugin(query=True, list=True)
    if unknown_plugin_list:
        print(u"unknownPlugin个数为%s" % len(unknown_plugin_list))
        for plugin_name in unknown_plugin_list:
            try:
                pm.unknownPlugin(plugin_name, remove=True)
            except:
                # print e
                print(plugin_name, u"无法清理")
                # pass
        print(u"清理完成！")
    else:
        print(u"unknownPlugin个数为0，不需要清理")


def moving_target(target, value=None):
    """
    移动对象

    :param target:目标对象
    :param value: 目标参数
    :return: none
    """
    if value is None:
        value = [0, 0, 0, 0, 0, 0, 1, 1, 1]
    pm.PyNode(target).translateX.set(value[0])
    pm.PyNode(target).translateY.set(value[1])
    pm.PyNode(target).translateZ.set(value[2])
    pm.PyNode(target).rotateX.set(value[3])
    pm.PyNode(target).rotateY.set(value[4])
    pm.PyNode(target).rotateZ.set(value[5])
    pm.PyNode(target).scaleX.set(value[6])
    pm.PyNode(target).scaleY.set(value[7])
    pm.PyNode(target).scaleZ.set(value[8])

    return


def lock_and_hide_attr(target, translate=True, rotate=True, scale=True,
                       vis=False):
    """
    锁定并隐藏目标的通道栏属性

    :param target: 目标对象
    :param translate: 位移属性
    :param rotate: 旋转属性
    :param scale: 缩放属性
    :param vis: 可见性
    :return: none
    """
    pm.setAttr("%s.tx" % target, lock=translate, k=(not translate),
               cb=(not translate))
    pm.setAttr("%s.ty" % target, lock=translate, k=(not translate),
               cb=(not translate))
    pm.setAttr("%s.tz" % target, lock=translate, k=(not translate),
               cb=(not translate))

    pm.setAttr("%s.rx" % target, lock=rotate, k=(not rotate), cb=(not rotate))
    pm.setAttr("%s.ry" % target, lock=rotate, k=(not rotate), cb=(not rotate))
    pm.setAttr("%s.rz" % target, lock=rotate, k=(not rotate), cb=(not rotate))

    pm.setAttr("%s.sx" % target, lock=scale, k=(not scale), cb=(not scale))
    pm.setAttr("%s.sy" % target, lock=scale, k=(not scale), cb=(not scale))
    pm.setAttr("%s.sz" % target, lock=scale, k=(not scale), cb=(not scale))

    pm.setAttr("%s.visibility" % target, lock=vis, k=(not vis), cb=(not vis))

    return


def null_node(name, parent="", node_type="transform"):
    null_node = pm.createNode(node_type, name=name).name()
    lock_and_hide_attr(null_node, vis=True)
    pm.parent(null_node, parent)
    return null_node


def quick_add_attr(node="", attr="", value=""):
    pm.addAttr(node, ln=attr, dt="string")
    pm.setAttr("%s.%s" % (node, attr), e=True, keyable=True)
    pm.setAttr("%s.%s" % (node, attr), value)
    return


def create_two_layout_bone(name, parent, offset_value=None):
    pm.select(cl=True)
    if offset_value is None:
        offset_value = [0, 1, 0]
    bone = pm.joint(name=name)
    con = add_node_as_parent(
        bone.name(),
        search_field="_BND",
        suffix="_CON",
        node_type="circle")
    bnd_grp = add_node_as_parent(
        con,
        search_field="_CON",
        suffix="_GRP",
        node_type="transform")
    pm.parent(bnd_grp, parent)
    bnd_grp.translateX.set(offset_value[0])
    bnd_grp.translateY.set(offset_value[1])
    bnd_grp.translateZ.set(offset_value[2])
    return bone


def create_three_layout_bone(name="", parent="", offset_value=None):
    if offset_value is None:
        offset_value = [0, 1, 0]
    pm.select(cl=True)
    bone = pm.joint(name=name)
    con = add_node_as_parent(
        bone.name(),
        search_field="_BND",
        suffix="_CON",
        node_type="circle")
    bnd_loc = add_node_as_parent(
        con,
        search_field="_CON",
        suffix="_BND_LOC",
        node_type="locator")
    bnd_grp = add_node_as_parent(
        bnd_loc,
        search_field="_BND_LOC",
        suffix="_BND_GRP", node_type="transform")
    pm.parent(bnd_grp, parent)
    bnd_grp.translateX.set(offset_value[0])
    bnd_grp.translateY.set(offset_value[1])
    bnd_grp.translateZ.set(offset_value[2])
    return bone


def add_node_as_parent(
        target, search_field="_BND", suffix="_LOC", node_type="locator"):
    """
    为目标节点添加一个指定节点作为它的父节点

    这个函数常用来将目标节点的通道栏参数归零
    :param target: 目标节点
    :param node_type: 节点类型
    :return: 新的创建的节点
    """
    new_parent_node = None

    new_parent_name = target.replace(search_field, suffix)

    if node_type == "locator":
        new_parent_node = pm.spaceLocator(name=new_parent_name).name()
    if node_type == "circle":
        new_parent_node = pm.circle(
            c=(0, 0, 0), nr=(0, 1, 0), name=new_parent_name, ch=0)[0].name()
    if node_type == "transform":
        new_parent_node = pm.createNode(
            "transform", name=new_parent_name).name()

    pm.delete(pm.parentConstraint(target, new_parent_node, mo=False))

    current_parent = pm.PyNode(target).getParent()

    if current_parent is not None:
        pm.parent(target, new_parent_node)
        pm.parent(new_parent_node, current_parent)
    else:
        pm.parent(target, new_parent_node)
    return new_parent_node


def snap_targets():
    """捕捉目标

    使用父子约束的方法捕捉选择列表，选择的第一个对象为捕捉对象，其余选择为被捕捉对象"""
    select_list = pm.ls(sl=True)
    if len(select_list) > 1:
        source = select_list[0]
        for target_index in range(1, len(select_list)):
            pm.delete(pm.parentConstraint(
                source, select_list[target_index], mo=False))
    return


def rename_targets(template_name=""):
    """批量修改名字

    :parameter template_name: 用#作为数字的占位符
    """
    select_list = pm.ls(sl=True)
    if len(select_list) > 0:
        for target_index in range(0, len(select_list)):
            pm.rename(
                select_list[target_index],
                template_name.replace("#", "{0:02d}".format(target_index + 1)))
    return


def target_parent_add_decompose_matrix_node():
    select_list = pm.ls(sl=True)
    if len(select_list) > 0:
        for target in select_list:
            target_parent = target.getParent()
            decompose_matrix_node = pm.createNode(
                "decomposeMatrix", name=target.name() + "_Inverse_DM")
            target.attr("inverseMatrix").connect(
                decompose_matrix_node.attr("inputMatrix"))
            decompose_matrix_node.attr("outputTranslate").connect(
                target_parent.attr("translate"))
            decompose_matrix_node.attr("outputRotate").connect(
                target_parent.attr("rotate"))
    return


def tweak_ctrl_connect_jnt():
    select_list = pm.ls(sl=True)
    if len(select_list) > 0:
        for target in select_list:
            target_jnt = pm.PyNode(target.name() + "_Jnt_02_Grp")
            target.translate.connect(target_jnt.translate)
    return


def compile_ui_file_to_py():
    """将 ui 文件编译为 py 文件

    :return:
    """

    def _set_output_path():
        output_path = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="Python File (*.py);;",
            fileMode=0,
            okc=u"选择目录")
        if output_path:
            pm.textFieldButtonGrp(
                py_store_path_field, e=True, text=output_path[0])
        return True

    if pm.window("compileHelperWnd", exists=True):
        pm.deleteUI("compileHelperWnd")

    def _get_ui_location():
        ui_location = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="Ui File (*.ui);;",
            fileMode=1,
            okc=u"选择文件")
        if ui_location:
            pm.textFieldButtonGrp(
                ui_file_location_field,
                e=True, text=ui_location[0])
        return True

    def _compile_ui_file(*args):
        import sys, pprint
        from pysideuic import compileUi

        py_file = pm.textFieldButtonGrp(py_store_path_field,
                                        q=True, text=True)
        ui_file = pm.textFieldButtonGrp(ui_file_location_field,
                                        q=True, text=True)
        output_file = open(py_file, 'w')
        compileUi(ui_file, output_file, False, 4, False)
        output_file.close()

        print("Compile Done!")
        return True

    pm.window("compileHelperWnd", title="ui compile helper")
    root_layout = pm.columnLayout(adj=1)
    file_frame = pm.frameLayout(
        label="Compile file", p=root_layout, mw=10, mh=10, bgs=True)
    ui_file_location_field = pm.textFieldButtonGrp(
        label=u"ui file",
        bl=u"  Get  ",
        p=file_frame, bc=partial(_get_ui_location))
    py_store_path_field = pm.textFieldButtonGrp(
        label=u"Py file store path",
        bl=u'  Set  ',
        p=file_frame, bc=partial(_set_output_path))
    pm.button(label=u'Compile!', c=partial(_compile_ui_file))
    pm.showWindow("compileHelperWnd")
