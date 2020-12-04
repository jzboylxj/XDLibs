#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/12/3 18:49
# @Author  : Li XiaoJun
# @Site    :
# @File    : build.py

from pymel import core as pm

from rig import main as main_kit

reload(main_kit)


def multiple_object_on_curve(curve="", spans=7, prefix=None, object_type="joint"):
    u"""利用motion path节点为对象进行定位

    :param curve: 定位曲线
    :param spans: 线段上对象的数量
    :param prefix: 前缀名，对象的实际名会在前缀的后面加上序列数字
    :param object_type: 对象的类型，目前只支持joint, control
    :return: 对象列表
    """

    shape = pm.PyNode(curve).getShape()
    if not shape.type() == "nurbsCurve":
        pm.error(u"输入的{}不是nurbs曲线".format(curve))

    objects_list = []

    for index in range(0, spans):
        object_name = "{}_{}".format(prefix, "{0:02d}".format(index+1))

        if object_type == "joint":
            object = "{}_Ctrl_Jnt".format(object_name)
            object_grp = main_kit.yellow_component(name=object, shape_type="joint")
        elif object_type == "control":
            object = "{}_Ctrl".format(object_name)
            object_grp = main_kit.yellow_component(name=object, shape_type="sphere")

        mp_name = "{}_MP".format(object_name)
        mp_node = main_kit.mp_node(node_name=mp_name,
                                   geometry_path_input="{}.worldSpace[0]".format(shape),
                                   all_coordinates_output="{}.translate".format(object_grp))

        # 曲线的起始端
        if index == 0:
            mp_node.attr("uValue").set(0)
        # 曲线中间的片段
        else:
            mp_node.attr("uValue").set(float(index)/float(spans-1))

        objects_list.append(object_grp)

    return objects_list


def build_jawline_deformer():
    jawline_tweaks = multiple_object_on_curve(
        curve="MD_Jaw_01_Master_Curve",
        prefix="JawLine_01",
        spans=7,
        object_type="control")

    for index in range(0, len(jawline_tweaks)):
        # object_name = "JawLine_01_{}".format("{0:02d}".format(index+1))
        # object_grp = main_kit.jnt_or_control_grp(
        #     name="{}_Jnt".format(object_name), object_type="joint")

        print(jawline_tweaks[index])

    return


build_jawline_deformer()
