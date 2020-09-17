# coding=utf-8
"""
一些通用的小工具。

"""
import json

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
    start_time = 0
    end_time = 0
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


def create_three_layout_bone_ui():
    if pm.window("createThreeLayoutBoneUI", ex=True):
        pm.deleteUI("createThreeLayoutBoneUI")
    pm.window("createThreeLayoutBoneUI")
    pm.columnLayout(adj=1, rs=2)
    joint_name = pm.textFieldGrp(label="Joint name:")
    parent = pm.textFieldGrp(label=u"Parent node:")
    offset = pm.floatFieldGrp(
        numberOfFields=3,
        label='Offset:',
        value1=0,
        value2=1,
        value3=0)

    pm.button(
        label="Create and close", c=lambda *args: create_bone())

    def create_bone():
        name = pm.textFieldGrp(joint_name, q=True, text=True)
        parent_node = pm.textFieldGrp(parent, q=True, text=True)

        offset_value = pm.floatFieldGrp(offset, q=True, value=True)

        create_three_layout_bone(
            name=name,
            parent=parent_node,
            offset_value=offset_value
        )

        return

    pm.showWindow("createThreeLayoutBoneUI")


def add_node_as_parent(
        target, search_field="_BND", suffix="_LOC", node_type="locator"):
    """
    为目标节点添加一个指定节点作为它的父节点

    这个函数常用来将目标节点的通道栏参数归零
    :param suffix:
    :param search_field:
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


def add_node_to_parent_ui():
    if pm.window("addNodeToParentWnd", ex=True):
        pm.deleteUI("addNodeToParentWnd")
    pm.window("addNodeToParentWnd")
    pm.columnLayout(adj=1, rs=2)

    pm.rowColumnLayout(nr=1)
    pm.text(label=u"后缀模式：")
    collection1 = pm.radioCollection()
    rb1 = pm.radioButton(label=u'直接添加')
    rb2 = pm.radioButton(label=u'搜索替换')
    pm.setParent('..')

    search_field = pm.textFieldGrp(
        label=u"Search:", text="_BND")
    replace_field = pm.textFieldGrp(
        label=u"Replace:", text="_LOC")
    node_options_menu = pm.optionMenuGrp(label="Node options:")
    pm.menuItem(label="locator")
    pm.menuItem(label="circle")
    pm.menuItem(label="transform")
    pm.button(
        label="Create and close", c=lambda *args: add_node())
    pm.showWindow("addNodeToParentWnd")
    pm.radioCollection(collection1, edit=True, select=rb2)

    def add_node():
        suffix_mode = pm.radioCollection(collection1, q=True, select=True)
        print(suffix_mode)
        print("rb1:{}".format(rb1))
        print("rb2:{}".format(rb2))
        if suffix_mode == pm.radioButton(rb1):
            print("Test")
        elif suffix_mode == pm.radioButton(rb2):
            search_txt = pm.textFieldGrp(search_field, q=True, text=True)
            replace_txt = pm.textFieldGrp(replace_field, q=True, text=True)
            node_type = pm.optionMenuGrp(node_options_menu, q=True, value=True)

            target = None
            if len(pm.ls(sl=True)) > 0:
                target = pm.ls(sl=True)[0].name()
            else:
                pm.error(u"请至少选择一个对象")

            # print target, search_txt, replace_txt, node_type
            add_node_as_parent(
                target,
                search_field=search_txt,
                suffix=replace_txt,
                node_type=node_type
            )

        return


class PySideuicTools(Singleton):
    def __init__(self):
        super(PySideuicTools, self).__init__()

        self.ui_file = ""
        self.output_file = ""

        self.show()

    def show(self):
        if pm.window("PySideuicTools", ex=True):
            pm.deleteUI("PySideuicTools")
        pm.window("PySideuicTools", title="Ui Tool Converter")
        pm.frameLayout(mw=10, mh=10, lv=False)
        self.file_location = pm.textFieldButtonGrp(
            label="Ui File",
            cw3=[70, 100, 50],
            adj=2,
            bl="  Get  ",
            bc=lambda *args: self.set_file_location())
        self.ouput_file_control = pm.textFieldButtonGrp(
            label="Output File",
            cw3=[70, 100, 50],
            adj=2,
            bl="  Set  ",
            bc=lambda *args: self.set_output_location())
        pm.button(label="Convert!", c=lambda *args: self.convert_ui())
        pm.setParent("..")

        pm.showWindow("PySideuicTools")

    def set_file_location(self):
        ui_location = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="UI File (*.ui);;",
            fileMode=1, okc=u"选择文件")
        pm.textFieldButtonGrp(
            self.file_location, e=True, text=ui_location[0])
        self.ui_file = ui_location[0]
        return

    def convert_ui(self):
        import sys, pprint
        from pyside2uic import compileUi
        file = open(self.output_file, 'w')
        compileUi(self.ui_file, file, False, 4, False)
        file.close()
        return

    def set_output_location(self):
        ui_location = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="Python File (*.py);;",
            fileMode=0, okc=u"选择文件")
        pm.textFieldButtonGrp(
            self.ouput_file_control, e=True, text=ui_location[0])
        self.output_file = ui_location[0]
        return
