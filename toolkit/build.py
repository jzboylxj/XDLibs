#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/12/3 18:49
# @Author  : Li XiaoJun
# @Site    : 
# @File    : build.py

from pymel import core as pm

from rig import main as main_kit

def multiple_bone_on_curve(curve="", spans=7, prefix=None):
    u"""利用motion path节点为对象进行定位

    :param curve: 定位曲线
    :param spans: 线段上对象的数量
    :return:
    """

    shape = pm.PyNode(curve).getShape()
    if not shape.type() == "nurbsCurve":
        pm.error(u"输入的{}不是nurbs曲线".format(curve))

    for index in range(0, spans):
        bone_grp = main_kit.yellow_component(name=prefix, shape_type="joint")

        main_kit.mp_node(node_name="{}_MP".format(prefix),
                         geometry_path_input="{}.worldSpace[0]".format(shape),
                         all_coordinates_output="{}.translate".format(bone_grp))


    return
