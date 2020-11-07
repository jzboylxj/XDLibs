#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/10/12 23:26
# @Author  : Li XiaoJun
# @Site    :
# @File    : main.py
import os
from imp import reload
from pymel import core as pm
from animation import common
import maya.mel as mel
import maya.cmds as cmds
from pymel.util import path
from rig.names import template_dir

reload(common)


def mouth_bind_jnt_grp_translate_bc_connect(bind_jnt_grp="", old_min=0.0,
                                            old_max=0.0):
    lf_lip_sew_ctrl_follicle_shape = pm.PyNode(
        "LF_Mouth_01_LipSew_Ctrl_FollicleShape")
    rt_lip_sew_ctrl_follicle_shape = pm.PyNode(
        "RT_Mouth_01_LipSew_Ctrl_FollicleShape")

    set_range = pm.createNode("setRange",
                              name=bind_jnt_grp.replace("_Grp", "_LipSew_SR"))
    lf_lip_sew_ctrl_follicle_shape.attr("parameterU").connect(
        "{}.value.valueX".format(set_range.name())
    )
    rt_lip_sew_ctrl_follicle_shape.attr("parameterU").connect(
        "{}.value.valueY".format(set_range.name())
    )
    set_range.attr("oldMinX").set(old_min)
    set_range.attr("oldMinY").set(old_min)
    set_range.attr("oldMaxX").set(old_max)
    set_range.attr("oldMaxY").set(old_max)

    adl_node = pm.createNode("addDoubleLinear",
                             name=bind_jnt_grp.replace("_Grp", "_Jnt_ADL"))
    set_range.attr("outValueX").connect(adl_node.attr("input1"))
    set_range.attr("outValueY").connect(adl_node.attr("input2"))

    cmp_node = pm.createNode("clamp",
                             name=bind_jnt_grp.replace("_Grp", "_LipSew_CMP"))
    adl_node.attr("output").connect(cmp_node.attr("inputR"))

    pma_node = pm.createNode("plusMinusAverage",
                             name=bind_jnt_grp.replace("_Grp", "_LipSew_PMA"))
    cmp_node.attr("outputR").connect(pma_node.attr("input1D[1]"))
    pma_node.attr("input1D[0]").set(1.0)
    pma_node.attr("output1D").connect(
        "{}.blender".format(bind_jnt_grp.replace("_Grp", "_Translate_BC"))
    )
    return


def connect_targets_spec_attr(source="", source_attr="", targets=None,
                              target_attrs=None):
    if target_attrs is None:
        target_attrs = []
    if targets is None:
        targets = []

    for target in targets:
        for target_attr in target_attrs:
            pm.PyNode(source).attr(source_attr).connect(
                "{}.{}".format(target, target_attr)
            )
    return


def follicle_shape_out_for_parent(follicle_shape):
    u"""将毛囊形节点的两个属性：输出平移和输出旋转，
    连接到它的父节点（位移节点）的平移和旋转属性上

    :param follicle_shape: 毛囊形节点
    :return: None
    """
    parent = pm.PyNode(follicle_shape).getParent()
    pm.PyNode(follicle_shape).attr("outTranslate").connect(
        parent.translate)
    pm.PyNode(follicle_shape).attr("outRotate").connect(
        parent.rotate)
    return


def check_constraint(target, source):
    """检查约束状态

    :param target: 被约束目标
    :param source: 约束目标
    :return: bool True or False
    """
    target_inputs = list(set(pm.PyNode(target).inputs()))
    if target_inputs:
        for target_input in target_inputs:
            if target_input.type() in ["parentConstraint", "pointConstraint",
                                       "scaleConstraint", "aimConstraint",
                                       "orientConstraint"]:
                if (target in list(set(target_input.inputs()))
                        and source in list(set(target_input.inputs()))):
                    return True
                else:
                    return False
    else:
        return False


def make_follicle_work_on_surface(surface, follicle, param_u=0.0, param_v=0.0):
    """让毛囊在曲面上能够起作用（工作）

    :param surface: 曲面
    :param follicle: 毛囊
    :param param_u: 参数 U
    :param param_v: 参数 V
    :return: None
    """
    surface_shape = pm.PyNode(surface).getShape()
    follicle_shape = pm.PyNode(follicle).getShape()
    surface_shape.attr("local").connect(follicle_shape.attr("inputSurface"))
    surface_shape.attr("worldMatrix[0]").connect(
        follicle_shape.attr("inputWorldMatrix"))
    follicle_shape.attr("parameterU").set(param_u)
    follicle_shape.attr("parameterV").set(param_v)
    return


def get_imported_object(file_path):
    u"""返回导入到场景里面的新对象

    :return: list of new object
    """
    imported = cmds.file(
        file_path, ignoreVersion=True, i=True, type="mayaBinary", rnn=True)
    for transform_node in imported:
        if pm.PyNode(transform_node).type() == "transform":
            return transform_node


def point_on_curve_position(curve, parameter):
    u"""获取曲线上cv点的位置信息

    :param curve: 曲线的名字
    :param parameter: 曲线上的参数值
    :return: Returns the (x,y,z) position of curve at parameter.
    """
    return pm.pointOnCurve(curve, pr=parameter, p=True)


def yellow_component(name="", shape_type="", translate=(0, 0, 0),
                     parent_node=None, have_loc=False):
    u"""黄色的基础控制器组件

    黄色的控制器一般用来作为模块的细节控制器或次级控制器

    :param name: 名字
    :param shape_type: 控制器的节点类型，例如曲面，locator等
    :param translate: 位移
    :param parent_node: 父节点
    :param have_loc: 在父节点下是否创建loc
    :return:
    """
    if shape_type == "nurbsPlane":
        pm.nurbsPlane(
            name=name, p=[0, 0, 0], ax=[0, 0, 1], w=1, lr=1, d=3, u=1, v=1,
            ch=1)
    if shape_type == "locator":
        pm.spaceLocator(name=name)
    if shape_type == "joint":
        pm.select(cl=True)
        pm.joint(name=name)
    if shape_type == "sphere":
        pm.sphere(
            name=name,
            p=[0, 0, 0], ax=[0, 1, 0], ssw=0, esw=360, r=1, d=3, ut=0,
            tol=0.01, s=4, nsp=2, ch=0)
    if shape_type == "cone":
        pm.cone(
            name=name,
            p=[0, 0, 0], ax=[-1, 0, 0], ssw=0, esw=360, r=0.45, hr=2, d=1,
            ut=0,
            tol=0.01, s=4, nsp=1, ch=0)

    pm.parent(
        pm.createNode("transform", name="{}_02_Grp".format(name)),
        pm.createNode("transform", name="{}_Grp".format(name)))
    pm.parent(name, "{}_02_Grp".format(name))

    if have_loc:
        pm.parent(
            pm.spaceLocator(name="{}_Roll_Loc".format(name)),
            "{}_Grp".format(name))

    pm.PyNode("{}_Grp".format(name)).translate.set(translate)

    if parent_node is not None:
        if pm.objExists(parent_node):
            pm.parent("{}_Grp".format(name), parent_node)

    return "{}_Grp".format(name)


def cyan_control(name="", shape_type="sphere", translate=(0, 0, 0),
                 parent_node=None):
    u"""蓝色的基础控制器组件

    蓝色的控制器一般用来作为模块的主控制器

    :return:
    """
    base_ctrl = None
    if shape_type == "sphere":
        base_ctrl = pm.sphere(
            name=name,
            p=[0, 0, 0], ax=[0, 1, 0], ssw=0, esw=360, r=1, d=1, ut=0,
            tol=0.01, s=4, nsp=2, ch=0)
    pm.parent(
        base_ctrl,
        pm.createNode("transform", name="{}_Grp".format(name)))

    pm.PyNode("{}_Grp".format(name)).translate.set(translate)

    if parent_node is not None:
        if pm.objExists(parent_node):
            pm.parent("{}_Grp".format(name), parent_node)

    return "{}_Grp".format(name)


def cyan_locator_grp(name, translate=(0, 0, 0), parent_node=None):
    u"""子层级为locator的组

    :param name: locator的名字
    :param translate: 组的位移信息
    :param parent_node: 父节点
    :return: grp
    """
    loc = pm.spaceLocator(name=name)
    grp = pm.createNode("transform", name="{}_Grp".format(name))
    pm.PyNode(grp).translate.set(translate)
    pm.parent(loc, grp)

    if parent_node is not None:
        if pm.objExists(parent_node):
            pm.parent(grp, parent_node)

    return grp


def xd_follicle_node(name,
                     worldMatrixInput=None, surfaceInput=None,
                     paramUInput=None, paramVInput=None,
                     outTranslateToParent=True, outRotateToParent=True,
                     parentNode=None):
    u"""毛囊体

    :param name:
    :param worldMatrixInput:
    :param surfaceInput:
    :param paramUInput:
    :param paramVInput:
    :param outTranslateToParent:
    :param outRotateToParent:
    :param parentNode: 
    :return:
    """
    follicle = pm.rename(pm.createNode("follicle").getParent(), name)

    if worldMatrixInput is not None:
        pm.connectAttr(worldMatrixInput,
                       follicle.getShape().attr("inputWorldMatrix"))

    if surfaceInput is not None:
        pm.connectAttr(surfaceInput,
                       follicle.getShape().attr("inputSurface"))

    if paramUInput is not None:
        pm.connectAttr(paramUInput,
                       follicle.getShape().attr("parameterU"))

    if paramVInput is not None:
        pm.connectAttr(paramVInput,
                       follicle.getShape().attr("parameterV"))

    if outTranslateToParent:
        pm.PyNode(follicle).getShape().attr("outTranslate").connect(
            pm.PyNode(follicle).translate)

    if outRotateToParent:
        pm.PyNode(follicle).getShape().attr("outRotate").connect(
            pm.PyNode(follicle).rotate)

    if parentNode is not None:
        if not pm.objExists(parentNode):
            pm.createNode("transform", name=parentNode)

        pm.parent(follicle, parentNode)

    return follicle


def jnt_or_control_grp(name, object_type="joint", parent_node=None,
                       have_loc=False):
    pm.select(cl=True)

    if object_type == "joint":
        pm.parent(
            pm.joint(name=name),
            pm.createNode("transform", name="{}_Grp".format(name)))
    if object_type == "plane":
        pm.parent(
            pm.nurbsPlane(name=name, p=[0, 0, 0], ax=[0, 0, 1], w=1, lr=0.6,
                          d=1, u=1, v=1, ch=0),
            pm.createNode("transform", name="{}_Grp".format(name)))
    if have_loc:
        loc = pm.spaceLocator(name=name.replace('_Jnt', "_Loc"))
        pm.parent(loc, name)
    if parent_node is not None:
        pm.parent("{}_Grp".format(name), parent_node)
        pm.PyNode("{}_Grp".format(name)).translate.set([0, 0, 0])
        pm.PyNode("{}_Grp".format(name)).rotate.set([0, 0, 0])
    return pm.PyNode("{}_Grp".format(name))


def custom_show_channel(target, attr_list=[]):
    u"""自定义通道栏里面的属性，

    :param target:
    :param attr_list:
    :return:
    """
    attrs_in_cb = pm.listAttr(pm.PyNode(target), k=True)
    # print(attrs_in_cb)
    for attr in attrs_in_cb:
        if attr not in attr_list:
            pm.PyNode(target).attr(attr).set(lock=True, k=False, cb=False)
    return True


def ctrl_null_grp(name, parent_node=None):
    null = pm.createNode("transform", name=name)
    null_grp = pm.createNode("transform", name="{}_Grp".format(name))
    pm.parent(null, null_grp)

    if parent_node is not None:
        pm.parent(null_grp, parent_node)
        null_grp.translate.set([0, 0, 0])

    return null_grp


def chain_ctrl_null_grp(name, segment=3, parent_node=None):
    null = pm.createNode("transform", name=name)
    null_grp = pm.createNode("transform", name="{}_Grp".format(name))
    pm.parent(null, null_grp)

    for index in range(1, segment):
        null_seg = pm.createNode(
            "transform",
            name="{}_{}_Grp".format(name, "{0:02d}".format(index + 1)))
        if index == 1:
            pm.parent(null_seg, null_grp)
        else:
            pm.parent(
                null_seg,
                "{}_{}_Grp".format(name, "{0:02d}".format(index)))

    if parent_node is not None:
        pm.parent(null_grp, parent_node)
        null_grp.translate.set([0, 0, 0])

    return null_grp


class Creator(common.Singleton):

    def __init__(self):
        super(Creator, self).__init__()
        self.show()
        self.initialize()

    def show(self):
        pass

    def initialize(self):
        pass

    def build(self):
        pass


class EyeCreator(Creator):
    def __init__(self):
        super(EyeCreator, self).__init__()

        self.left_eyeball_setter = None
        self.right_eyeball_setter = None

        self.left_up_master_curve_setter = None
        self.left_low_master_curve_setter = None
        self.right_up_master_curve_setter = None
        self.right_low_master_curve_setter = None

        self.left_up_out_curve_setter = None
        self.left_low_out_curve_setter = None
        self.right_up_out_curve_setter = None
        self.right_low_out_curve_setter = None

        self.show()
        self.initialize()

    def show(self):
        if pm.window("eyeCreator", ex=True):
            pm.deleteUI("eyeCreator")
        pm.window("eyeCreator", title="Eye Creator")
        main_layout = pm.scrollLayout(cr=True)

        pm.frameLayout(p=main_layout, label=u"Pre", cll=True, cl=False, mw=5)

        pm.frameLayout(
            label=u"Step1: 基本体设置",
            mw=5,
            bgs=True,
            cll=True, cl=False)
        self.left_eyeball_setter = pm.textFieldButtonGrp(
            label=u"Left Eye:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(self.left_eyeball_setter))
        self.right_eyeball_setter = pm.textFieldButtonGrp(
            label=u"Right Eye:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(self.right_eyeball_setter))

        pm.setParent("..")

        pm.frameLayout(
            label=u"Step2: 创建Master Curve",
            ann=u"这根曲线将会约束眼皮的蒙皮骨骼",
            mw=5,
            bgs=True,
            cll=True, cl=False)
        self.left_up_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.left_up_master_curve_setter))
        self.left_low_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.left_low_master_curve_setter))

        self.right_up_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.right_up_master_curve_setter))
        self.right_low_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.right_low_master_curve_setter))
        pm.setParent("..")

        pm.frameLayout(
            label=u"Step3: 创建Out Curve",
            ann=u"这根曲线将会实现眼睛的开合功能",
            mw=5,
            bgs=True,
            cll=True, cl=False)
        self.left_up_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(self.left_up_out_curve_setter))
        self.left_low_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.left_low_out_curve_setter))

        self.right_up_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.right_up_out_curve_setter))
        self.right_low_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.right_low_out_curve_setter))
        pm.setParent("..")

        pm.setParent("..")

        pm.separator(h=20, style="none")

        pm.frameLayout(
            label=u"Builder",
            mw=5, mh=5,
            bgs=True,
            cll=True, cl=False)
        pm.button(label=u"Builder Master Ctrl",
                  c=lambda *args: self.build_master_ctrl())
        pm.setParent("..")

        pm.showWindow("eyeCreator")

    def initialize(self):
        pass

    def curve_setting(self, widget):
        select = pm.ls(sl=True)[0]
        if select:
            pm.textFieldButtonGrp(widget, e=True, text=select.name())
        else:
            pm.error(u"获取曲线失败，请确认当前是否选择一根曲线")
        return

    def build_master_ctrl(self):
        left_eyeball_geo = pm.textFieldButtonGrp(
            self.left_eyeball_setter, q=True, text=True)
        left_master_ctrl = pm.torus(
            name="LF_Eye_01_Master_Ctrl",
            p=[0, 0, 0],
            ax=[0, 0, 1],
            ssw=0,
            esw=360,
            msw=360,
            r=0.6,
            hr=0.02,
            d=3,
            ut=0,
            tol=0.01,
            s=8,
            nsp=4,
            ch=1)
        pm.delete(left_eyeball_geo, )

        return


class MouthCreator(Creator):

    def __init__(self):
        super(MouthCreator, self).__init__()

        self.mouth_module = "Mouth_01"

        self.rig_root_node = ""  # group "World"

        self.up_base_curve = ""
        self.low_base_curve = ""
        self.up_tweak_surface = ""
        self.low_tweak_surface = ""
        self.up_out_curve = ""
        self.low_out_curve = ""

        self.mouth_surface = ""
        self.mouth_lip_sew_surface = ""

    def master_control(self):
        u"""嘴巴模块的主控制器

        :return:
        """

        parameter = 0.5

        if not pm.objExists(self.up_base_curve):
            pm.error("{}丢失".format(self.up_base_curve))

        if not pm.objExists(self.low_base_curve):
            pm.error("{}丢失".format(self.low_base_curve))

        up_curve_center_position = point_on_curve_position(
            curve=self.up_base_curve, parameter=parameter)
        low_curve_center_position = point_on_curve_position(
            curve=self.low_base_curve, parameter=parameter)
        pos_x = (low_curve_center_position[0] +
                 (up_curve_center_position[0] - low_curve_center_position[
                     0]) / 2)
        pos_y = (low_curve_center_position[1] +
                 (up_curve_center_position[1] - low_curve_center_position[
                     1]) / 2)
        pos_z = (low_curve_center_position[2] +
                 (up_curve_center_position[2] - low_curve_center_position[
                     2]) / 2)
        offset = 4.0

        master_ctrl = "MD_{}_Master_Ctrl".format(self.mouth_module)
        if not pm.objExists(master_ctrl):
            cyan_control(
                name=master_ctrl,
                shape_type="sphere",
                translate=(pos_x, pos_y, pos_z + offset),
                parent_node="MD_{}_Grp".format(self.mouth_module))

        master_ctrl_loc = "MD_{}_Master_Ctrl_Loc".format(self.mouth_module)
        if not pm.objExists(master_ctrl_loc):
            cyan_locator_grp(
                name=master_ctrl_loc,
                translate=(pos_x, pos_y, pos_z + offset),
                parent_node="MD_{}_Deformer_Grp".format(self.mouth_module))

        pm.PyNode(master_ctrl).translate.connect(
            pm.PyNode(master_ctrl_loc).translate, f=True)

        return True

    def base_controls(self):
        u"""创建嘴巴的基础控件

        这个方法需要依靠 base curve 曲线为控件进行定位
        :return:
        """
        if (not pm.objExists(self.up_base_curve) or
                not pm.objExists(self.low_base_curve)):
            pm.error(u"场景中没有找到Base curve")

        base_ctrl_grp = "MD_{}_Base_Ctrl_Grp".format(self.mouth_module)
        if not pm.objExists(base_ctrl_grp):
            pm.createNode("transform", name=base_ctrl_grp)
            if pm.objExists("MD_{}_Grp".format(self.mouth_module)):
                pm.parent(base_ctrl_grp,
                          "MD_{}_Grp".format(self.mouth_module))

        base_ctrl_out_grp = "MD_{}_Base_Ctrl_Out_Grp".format(self.mouth_module)
        base_loc_grp = "MD_{}_Base_Loc_Grp".format(self.mouth_module)
        base_follicle_grp = "MD_{}_Base_Follicle_Grp".format(self.mouth_module)

        if not pm.objExists(base_ctrl_out_grp):
            pm.parent(
                pm.createNode("transform", name=base_ctrl_out_grp),
                "MD_{}_Deformer_Grp".format(self.mouth_module)
            )

            if not pm.objExists(base_loc_grp):
                pm.parent(
                    pm.createNode("transform", name=base_loc_grp),
                    base_ctrl_out_grp
                )

            if not pm.objExists(base_follicle_grp):
                pm.parent(
                    pm.createNode("transform", name=base_follicle_grp),
                    base_ctrl_out_grp
                )

        # 左右嘴角的控制
        for item in ["LF", "RT"]:
            if item == "LF":
                parameter = 0.0
            else:
                parameter = 1.0
            control_position = point_on_curve_position(
                curve=self.up_base_curve, parameter=parameter)
            control_name = "{}_{}_Ctrl".format(item, self.mouth_module)
            if not pm.objExists(control_name):
                yellow_component(name=control_name,
                                 shape_type="nurbsPlane",
                                 translate=control_position,
                                 parent_node=base_ctrl_grp)
            ctrl_loc = "{}_{}_Ctrl_Loc".format(item, self.mouth_module)
            if not pm.objExists(ctrl_loc):
                yellow_component(name=ctrl_loc,
                                 shape_type="locator",
                                 translate=control_position,
                                 parent_node=base_loc_grp)

        # 上下嘴唇的控制器
        for item in ["Up", "Low"]:
            parameter = 0.5
            if item == "Up":
                curve = self.up_base_curve
            else:
                curve = self.low_base_curve
            control_position = point_on_curve_position(
                curve=curve, parameter=parameter)
            control_name = "{}_{}_Ctrl".format(item, self.mouth_module)
            if not pm.objExists(control_name):
                yellow_component(name=control_name,
                                 shape_type="nurbsPlane",
                                 translate=control_position,
                                 parent_node=base_ctrl_grp)
        return True

    def build(self):
        # lip
        # self.follicle_on_mouth_surface()
        # self.base_follicle_grp()
        # self.rig_base_ctrl_out()
        # self.bind_jnt_follicle_on_tweak_surface()
        # self.base_curve_connect_tweak_jnt_grp()
        # self.tweak_ctrl_grp()
        # self.skin_out_curve()
        # self.use_dm_node_to_tweak_ctrl_parent_and_jnt_02_grp()
        # self.skin_tweak_surface()
        # self.__skin_lip_sew_surface_and_connect_follicle_shape()
        # self.lip_sew_ctrl_drive_follicle_shape()
        # self.make_bind_jnt_work()
        # self.make_bind_jnt_scale_work()
        self.static_corner_when_master_ctrl_move_up()
        # Jaw
        self.__connect_jaw_ctrl_and_jnt()

    def follicle_on_mouth_surface(self):
        """求出locator（为控制嘴唇整体的三根骨骼进行定位）在mouth surface上面的位置（参数U，V），
        然后将这个位置信息与控制嘴角骨骼的毛囊体的参数 U 和 V 进行连接，
        毛囊体会根据参数移动到相应的位置，
        这样控制了locator， 就控制了毛囊体，也就间接的控制了骨骼
        """
        mouth_surface_shape = pm.PyNode(self.mouth_surface).getShape()

        follicle_list = []

        for side_prefix in ["LF", "RT", "MD"]:
            if side_prefix == "MD":
                corner_locator = "{}_Mouth_01_Master_Ctrl_Loc".format(
                    side_prefix)
            else:
                corner_locator = "{}_Mouth_01_Ctrl_Loc".format(side_prefix)

            cpos_node = "{}_Mouth_01_Ctrl_CPOS".format(side_prefix)
            if not pm.objExists(cpos_node):
                cpos_node = pm.createNode(
                    "closestPointOnSurface", name=cpos_node)

            corner_locator_shape = pm.PyNode(corner_locator).getShape()

            corner_locator_shape.attr("worldPosition[0]").connect(
                cpos_node.attr("inPosition"))
            mouth_surface_shape.attr("worldSpace[0]").connect(
                cpos_node.attr("inputSurface"))

            if side_prefix == "MD":
                follicle_name = "{}_Mouth_01_Master_Ctrl_Follicle".format(
                    side_prefix)
                xd_follicle_node(
                    name=follicle_name,
                    worldMatrixInput=mouth_surface_shape.attr(
                        "worldMatrix[0]"),
                    surfaceInput=mouth_surface_shape.attr("local"),
                    paramUInput=pm.PyNode(cpos_node).attr("parameterU"),
                    paramVInput=pm.PyNode(cpos_node).attr("parameterV"),
                    outTranslateToParent=True,
                    outRotateToParent=True,
                    parentNode="MD_{}_Grp".format(self.mouth_module)
                )
                follicle_list.append(follicle_name)
            else:
                follicle_name = "{}_Mouth_01_Ctrl_Jnt_Follicle".format(
                    side_prefix)
                xd_follicle_node(
                    name=follicle_name,
                    worldMatrixInput=mouth_surface_shape.attr(
                        "worldMatrix[0]"),
                    surfaceInput=mouth_surface_shape.attr("local"),
                    paramUInput=pm.PyNode(cpos_node).attr("parameterU"),
                    paramVInput=pm.PyNode(cpos_node).attr("parameterV"),
                    outTranslateToParent=True,
                    outRotateToParent=True,
                    parentNode="MD_{}_Base_Follicle_Grp".format(
                        self.mouth_module)
                )
                follicle_list.append(follicle_name)

        return follicle_list

    def base_follicle_grp(self):
        """利用mouth surface定位毛囊，
        并利用毛囊的位移节点（父节点）对控制嘴唇的骨骼的组节点进行目标约束
        """
        for item in ["Up", "Low"]:
            aim_jnt = "{}_{}_Ctrl_Jnt".format(item, self.mouth_module)
            if not pm.objExists(aim_jnt):
                if item == "Up":
                    base_curve = self.up_base_curve
                else:
                    base_curve = self.low_base_curve
                pos = point_on_curve_position(base_curve, 0.5)
                yellow_component(name=aim_jnt,
                                 shape_type="joint",
                                 translate=pos,
                                 parent_node="MD_{}_Base_Ctrl_Out_Grp".format(
                                     self.mouth_module))

            for side in ["LF", "RT"]:
                if side == "LF":
                    flip_up = -1.0
                else:
                    flip_up = 1.0
                corner_jnt = "{}_{}_Ctrl_{}_Jnt".format(
                    side, self.mouth_module, item)
                corner_follicle = "{}_{}_Ctrl_Jnt_Follicle".format(
                    side, self.mouth_module)
                corner_jnt_grp = jnt_or_control_grp(
                    name=corner_jnt, parent_node=corner_follicle)

                pm.aimConstraint(
                    corner_follicle, corner_jnt_grp,
                    aimVector=[0, 0, -1],
                    upVector=[0, 1 * flip_up, 0],
                    worldUpType="object",
                    worldUpObject=aim_jnt)
        return

    def skin_base_curve(self):
        prefix_list = ["Up", "Low"]
        for prefix in prefix_list:
            if prefix == "Up":
                base_curve = self.up_base_curve
            else:
                base_curve = self.low_base_curve

            base_curve_skin_items = [
                "{}_Mouth_01_Ctrl_Jnt".format(prefix), base_curve]
            for ctrl_jnt_item in ["LF", "RT"]:
                base_curve_skin_items.append(
                    "{}_{}_Ctrl_{}_Jnt".format(
                        ctrl_jnt_item, self.mouth_module, prefix))
            pm.skinCluster(base_curve_skin_items,
                           name="MD_{}_{}_Base_Curve_SC".format(
                               self.mouth_module, prefix))
        return

    def corner_ctrl_connect_cpos_loc(self):
        u"""将左右嘴角控制器与cpos（嘴角位置定位loc）连接起来"""
        cpos_locs = ["LF_Mouth_01_Ctrl_Loc", "RT_Mouth_01_Ctrl_Loc"]
        for cpos_loc in cpos_locs:
            corner_ctrl = pm.PyNode(cpos_loc.replace("_Loc", ""))
            pm.PyNode(corner_ctrl).translate.connect(
                pm.PyNode(cpos_loc).translate, f=True)

        return

    def master_ctrl_null_grp(self, parent_node,
                             translate_clean=False,
                             rotate_clean=False):
        master_ctrl = pm.PyNode("MD_{}_Master_Ctrl".format(self.mouth_module))

        ctrl_null_grp = "MD_{}_Master_Ctrl_Null_Grp".format(self.mouth_module)
        if not pm.objExists(ctrl_null_grp):
            pm.createNode(
                "transform",
                name="MD_{}_Master_Ctrl_Null_Grp".format(self.mouth_module))
            pm.createNode(
                "transform",
                name="MD_{}_Master_Ctrl_Null".format(self.mouth_module))
            pm.spaceLocator(name="M_Mouth_Move_Loc")
            pm.parent(
                "MD_{}_Master_Ctrl_Null".format(self.mouth_module),
                "M_Mouth_Move_Loc",
                "MD_{}_Master_Ctrl_Null_Grp".format(self.mouth_module)
            )
        if parent_node is not None:
            pm.parent(
                "MD_{}_Master_Ctrl_Null_Grp".format(self.mouth_module),
                parent_node
            )
            pm.PyNode("MD_{}_Master_Ctrl_Null_Grp".format(
                self.mouth_module)).translate.set([0, 0, 0])

        if translate_clean:
            pm.PyNode("MD_{}_Master_Ctrl_Null_Grp".format(
                self.mouth_module)).translate.set([0, 0, 0])

        if rotate_clean:
            pm.PyNode("MD_{}_Master_Ctrl_Null_Grp".format(
                self.mouth_module)).rotate.set([0, 0, 0])

        return True

    def lip_ctrl_connect_ctrl_jnt(self):
        """连接嘴唇控制器"""

        # MD_Mouth_01_Base_Ctrl_Grp
        base_ctrl_grp = pm.PyNode(
            "MD_{}_Base_Ctrl_Grp".format(self.mouth_module))

        # 修正 MD_Mouth_01_Base_Ctrl_Grp的轴心位置
        mouth_center_follicle = "MD_{}_Master_Ctrl_Follicle".format(
            self.mouth_module)

        master_ctrl_null = "MD_{}_Master_Ctrl_Null".format(self.mouth_module)
        if not pm.objExists(master_ctrl_null):
            self.master_ctrl_null_grp(
                parent_node=mouth_center_follicle, translate_clean=True)

        pm.delete(
            pm.pointConstraint(
                mouth_center_follicle, base_ctrl_grp, mo=False))

        offset_position = base_ctrl_grp.translate.get()
        for item in base_ctrl_grp.getChildren():
            current_position = item.translate.get()
            item.translate.set([
                current_position[0] - offset_position[0],
                current_position[1] - offset_position[1],
                current_position[2] - offset_position[2]
            ])

        pm.parentConstraint(master_ctrl_null, base_ctrl_grp)

        # Up_Mouth_01_Ctrl_Jnt
        for ctrl_jnt in ["Up_{}_Ctrl_Jnt".format(self.mouth_module),
                         "Low_{}_Ctrl_Jnt".format(self.mouth_module)]:
            ctrl = pm.PyNode(ctrl_jnt.replace("_Jnt", ""))
            md_node = ctrl_jnt.replace("_Jnt", "_Scale_MD")
            if not pm.objExists(md_node):
                pm.createNode("multiplyDivide", name=md_node)
            pm.PyNode(md_node).attr("operation").set(1)
            ctrl.attr("translate").connect(pm.PyNode(md_node).attr("input1"))
            base_ctrl_grp.attr("scale").connect(
                pm.PyNode(md_node).attr("input2"))
            pm.PyNode(md_node).attr("output").connect(
                "{}.translate".format(ctrl_jnt))
            ctrl.rotate.connect("{}.rotate".format(ctrl_jnt))

        # 连接base ctrl grp， 让嘴巴的模块控制器能够工作
        mouth_master_ctrl = pm.PyNode(
            "MD_{}_Master_Ctrl".format(self.mouth_module))

        print(u"开始调整通道栏显示属性")
        custom_show_channel(
            mouth_master_ctrl,
            attr_list=["translateX", "translateY", "translateZ", "rotateZ"])

        if not pm.attributeQuery(
                "localScale", node=mouth_master_ctrl, ex=True):
            pm.addAttr(mouth_master_ctrl,
                       ln="localScale", at="double", min=0.01, dv=1)
            pm.setAttr("{}.localScale".format(mouth_master_ctrl),
                       e=True, k=True)

        mouth_master_ctrl.attr("localScale").connect(base_ctrl_grp.scaleX)
        mouth_master_ctrl.attr("localScale").connect(base_ctrl_grp.scaleY)
        mouth_master_ctrl.attr("localScale").connect(base_ctrl_grp.scaleZ)

        mouth_master_ctrl.attr("translateZ").connect(
            pm.PyNode(master_ctrl_null).translateZ)
        mouth_master_ctrl.attr("rotateZ").connect(
            pm.PyNode(master_ctrl_null).rotateZ)

        # 修正 MD_Mouth_01_Base_Ctrl_Out_Grp 的轴心位置
        base_ctrl_out_grp = pm.PyNode(
            "MD_{}_Base_Ctrl_Out_Grp".format(self.mouth_module))

        pm.delete(
            pm.pointConstraint(
                mouth_center_follicle, base_ctrl_out_grp, mo=False))

        for item in base_ctrl_out_grp.getChildren():
            current_position = item.translate.get()
            item.translate.set([
                current_position[0] - offset_position[0],
                current_position[1] - offset_position[1],
                current_position[2] - offset_position[2]
            ])

        base_ctrl_grp.translate.connect(base_ctrl_out_grp.translate)
        base_ctrl_grp.rotate.connect(base_ctrl_out_grp.rotate)

        base_loc_grp = "MD_{}_Base_Loc_Grp".format(self.mouth_module)
        pm.PyNode(base_ctrl_grp).scale.connect(
            pm.PyNode(base_loc_grp).scale, f=True)

        return

    def rig_base_ctrl_out(self):
        self.skin_base_curve()
        self.corner_ctrl_connect_cpos_loc()
        self.lip_ctrl_connect_ctrl_jnt()

    def follicle_on_tweak_surface(self):
        # 嘴唇一侧的段数，例如上嘴唇左侧为5段，右侧也为5段，加上左右嘴角，
        # 那么控制上嘴唇的骨骼数就是 5+5+2=12
        bind_jnt_follicle_grp = "MD_{}_Bind_Jnt_Follicle_Grp".format(
            self.mouth_module)
        if not pm.objExists(bind_jnt_follicle_grp):
            pm.parent(
                pm.createNode("transform", name=bind_jnt_follicle_grp),
                "MD_{}_Deformer_Grp".format(self.mouth_module)
            )

        segment = 5
        parameter_u = 0.5
        parameter_v = 0
        for location in ["Up", "Low"]:
            tweak_surface = pm.PyNode(
                "MD_Mouth_01_{}_Tweak_Surface".format(location))
            for side in ["LF", "RT"]:
                if side == "LF":
                    parameter_v = 0
                elif side == "RT":
                    parameter_v = 1

                if location == "Up":
                    corner_follicle = xd_follicle_node(
                        name="{}_{}_Lip_Jnt_Follicle".format(
                            side, self.mouth_module),
                        worldMatrixInput=tweak_surface.getShape().attr(
                            "worldMatrix[0]"),
                        surfaceInput=tweak_surface.getShape().attr("local"),
                        parentNode=bind_jnt_follicle_grp
                    )
                    pm.PyNode(corner_follicle).getShape().attr(
                        "parameterU").set(parameter_u)
                    pm.PyNode(corner_follicle).getShape().attr(
                        "parameterV").set(parameter_v)

                for index in range(1, segment + 1):
                    lip_follicle = xd_follicle_node(
                        name="{}_Mouth_01_{}Lip_{}_Jnt_Follicle".format(
                            side, location, "{0:02d}".format(index)),
                        worldMatrixInput=tweak_surface.getShape().attr(
                            "worldMatrix[0]"),
                        surfaceInput=tweak_surface.getShape().attr("local"),
                        parentNode=bind_jnt_follicle_grp
                    )
                    # 通过调整参数为定位毛囊的位置
                    lip_follicle_shape = pm.PyNode(lip_follicle).getShape()
                    lip_follicle_shape.attr("parameterU").set(parameter_u)

                    if side == "LF":
                        if index < 5:
                            parameter_v = 0.111 * (segment - index)
                        elif index == 5:
                            parameter_v = 0.037
                        lip_follicle_shape.attr("parameterV").set(parameter_v)
                    elif side == "RT":
                        parameter_v = 1 - pm.getAttr(
                            "LF_{}_{}Lip_{}_Jnt_FollicleShape"
                            ".parameterV".format(
                                self.mouth_module,
                                location,
                                "{0:02d}".format(index)))
                        lip_follicle_shape.attr("parameterV").set(parameter_v)
        return True

    def tweak_jnt_grp(self):
        segment = 3

        master_ctrl = "MD_{}_Master_Ctrl".format(self.mouth_module)
        # evenTweak
        if not pm.attributeQuery(
                "evenTweak", node=master_ctrl, ex=True):
            pm.addAttr(master_ctrl,
                       ln="evenTweak", at="double", min=0, max=1, dv=1)
            pm.setAttr("{}.evenTweak".format(master_ctrl),
                       e=True, k=True)

        tweak_jnt_grp = "MD_{}_Tweak_Jnt_Grp".format(self.mouth_module)
        if not pm.objExists(tweak_jnt_grp):
            pm.parent(
                pm.createNode("transform", name=tweak_jnt_grp),
                "MD_{}_Deformer_Grp".format(self.mouth_module)
            )

        bind_jnt_ori_null = "MD_{}_Bind_Jnt_Ori_Null".format(
            self.mouth_module)
        if not pm.objExists(bind_jnt_ori_null):
            pm.parent(
                pm.createNode('transform', name=bind_jnt_ori_null),
                "MD_{}_Grp".format(self.mouth_module)
            )
            pm.parentConstraint(
                "MD_{}_Master_Ctrl_Null".format(self.mouth_module),
                bind_jnt_ori_null,
                mo=False
            )

        for location in ["Up", "Low"]:
            base_curve = "MD_{}_{}_Base_Curve".format(
                self.mouth_module, location)
            for side in ["LF", "RT"]:
                for index in range(1, segment + 1):
                    jnt_grp = yellow_component(
                        name="{}_Mouth_01_{}Tweak_{}_Ctrl_Jnt".format(
                            side, location, "{0:02d}".format(index)),
                        shape_type="joint",
                        parent_node=tweak_jnt_grp,
                        have_loc=True
                    )

                    mp_node = jnt_grp.replace("_Grp", "_MP")
                    if not pm.objExists(mp_node):
                        pm.createNode("motionPath", name=mp_node)

                    mp_node2 = jnt_grp.replace("_Grp", "_02_MP")
                    if not pm.objExists(mp_node2):
                        pm.createNode("motionPath", name=mp_node2)
                    u_value = 0.0
                    if side == "LF":
                        if index < 3:
                            u_value = 0.2 * (segment - index)
                        elif index == 3:
                            u_value = 0.067
                        pm.PyNode(mp_node).attr("uValue").set(u_value)
                        pm.PyNode(mp_node2).attr("uValue").set(u_value)
                        pm.PyNode(mp_node2).attr("fractionMode").set(True)
                    elif side == "RT":
                        lf_mp_node2 = "LF_Mouth_01_{}Tweak_{}_Ctrl_Jnt_02_MP".format(
                            location, "{0:02d}".format(index))
                        u_value = 1 - pm.getAttr(
                            "{}.uValue".format(lf_mp_node2))
                        pm.PyNode(mp_node).attr("uValue").set(u_value)
                        pm.PyNode(mp_node2).attr("uValue").set(u_value)
                        pm.PyNode(mp_node2).attr("fractionMode").set(True)
                    pm.PyNode(base_curve).getShape().attr(
                        "worldSpace[0]").connect(
                        pm.PyNode(mp_node).attr("geometryPath"))
                    pm.PyNode(base_curve).getShape().attr(
                        "worldSpace[0]").connect(
                        pm.PyNode(mp_node2).attr("geometryPath"))

                    bc_node = jnt_grp.replace("_Grp", "_MP_BC")
                    if not pm.objExists(bc_node):
                        pm.createNode("blendColors", name=bc_node)
                    pm.PyNode(mp_node).attr("allCoordinates").connect(
                        pm.PyNode(bc_node).attr("color1"))
                    pm.PyNode(mp_node2).attr("allCoordinates").connect(
                        pm.PyNode(bc_node).attr("color2"))
                    pm.PyNode(master_ctrl).attr("evenTweak").connect(
                        pm.PyNode(bc_node).attr("blender"))
                    pm.PyNode(bc_node).attr("output").connect(
                        pm.PyNode(jnt_grp).translate)

                    pm.PyNode(bind_jnt_ori_null).rotate.connect(
                        pm.PyNode(jnt_grp).rotate)

                # 左右嘴角
                if location == "Up":
                    jnt_grp = yellow_component(
                        name="{}_{}_Tweak_Ctrl_Jnt".format(
                            side, self.mouth_module),
                        shape_type="joint",
                        parent_node=tweak_jnt_grp,
                        have_loc=True
                    )

                    mp_node = jnt_grp.replace("_Grp", "_MP")
                    if not pm.objExists(mp_node):
                        pm.createNode("motionPath", name=mp_node)
                    pm.PyNode(mp_node).attr("allCoordinates").connect(
                        pm.PyNode(jnt_grp).translate)

                    pm.PyNode(bind_jnt_ori_null).rotate.connect(
                        pm.PyNode(jnt_grp).rotate)

                    if side == "LF":
                        pm.PyNode(mp_node).attr("uValue").set(0)
                    else:
                        pm.PyNode(mp_node).attr("uValue").set(1)

                    pm.PyNode(base_curve).getShape().attr(
                        "worldSpace[0]").connect(
                        pm.PyNode(mp_node).attr("geometryPath"))

        return True

    def tweak_ctrl_grp(self):
        segment = 3

        master_ctrl_null = "MD_{}_Master_Ctrl_Null".format(self.mouth_module)
        tweak_ctrl_grp = "MD_{}_Tweak_Ctrl_Grp".format(self.mouth_module)
        module_grp = "MD_{}_Grp".format(self.mouth_module)
        deformer_grp = "MD_{}_Deformer_Grp".format(self.mouth_module)

        tweak_ori_null = "MD_{}_Tweak_Ori_Null".format(self.mouth_module)

        if not pm.objExists(tweak_ctrl_grp):
            pm.createNode("transform", name=tweak_ctrl_grp, p=module_grp)
            pm.createNode("transform", name=tweak_ori_null, p=tweak_ctrl_grp)
            pm.parentConstraint(master_ctrl_null, tweak_ori_null, mo=True)

        scale_null = "MD_{}_Scale_Null".format(self.mouth_module)
        if not pm.objExists(scale_null):
            pm.createNode("transform", name=scale_null, p=deformer_grp)

        for location in ["Up", "Low"]:
            # outer_curve = "MD_Mouth_01_{}_Out_Curve".format(location)
            if location == "Up":
                outer_curve = self.up_out_curve
            elif location == "Low":
                outer_curve = self.low_out_curve

            for side in ["LF", "RT"]:
                for index in range(1, segment + 1):
                    # ctrl_grp = "{}_Mouth_01_{}Tweak_{}_Ctrl_Grp".format(
                    #     side, location, "{0:02d}".format(
                    #         index))  # LF_Mouth_01_UpTweak_01_Ctrl_Grp
                    ctrl_grp = yellow_component(
                        name="{}_Mouth_01_{}Tweak_{}_Ctrl".format(
                            side, location, "{0:02d}".format(
                                index)),
                        shape_type="sphere",
                        parent_node=tweak_ctrl_grp,
                    )

                    mp_node = ctrl_grp.replace("_Grp", "_MP")
                    if not pm.objExists(mp_node):
                        pm.createNode("motionPath", name=mp_node)

                    u_value = 0.0
                    if side == "LF":
                        if index < 3:
                            u_value = 0.2 * (segment - index)
                        elif index == 3:
                            u_value = 0.067
                        pm.PyNode(mp_node).attr("uValue").set(u_value)
                    elif side == "RT":
                        u_value = pm.getAttr(
                            "LF_Mouth_01_{}Tweak_{}_Ctrl_MP"
                            ".uValue".format(location,
                                             "{0:02d}".format(index)))
                        pm.PyNode(mp_node).attr("uValue").set(1 - u_value)

                    pm.PyNode(outer_curve).getShape().attr(
                        "worldSpace[0]").connect(
                        pm.PyNode(mp_node).attr("geometryPath"))
                    pm.PyNode(mp_node).attr("allCoordinates").connect(
                        pm.PyNode(ctrl_grp).attr("translate"))

                    pm.PyNode(tweak_ori_null).rotate.connect(
                        pm.PyNode(ctrl_grp).rotate)
                    pm.PyNode(scale_null).scale.connect(
                        pm.PyNode(ctrl_grp).scale)

                if location == "Up":
                    # ctrl_grp = "{}_Mouth_01_Tweak_Ctrl_Grp".format(
                    #     side)
                    ctrl_grp = yellow_component(
                        name="{}_Mouth_01_Tweak_Ctrl".format(side),
                        shape_type="sphere",
                        parent_node=tweak_ctrl_grp,
                    )

                    mp_node = ctrl_grp.replace("_Grp", "_MP")
                    if not pm.objExists(mp_node):
                        pm.createNode("motionPath", name=mp_node)

                    pm.PyNode(outer_curve).getShape().attr(
                        "worldSpace[0]").connect(
                        pm.PyNode(mp_node).attr("geometryPath"))
                    pm.PyNode(mp_node).attr("allCoordinates").connect(
                        pm.PyNode(ctrl_grp).translate)

                    if side == "LF":
                        pm.PyNode(mp_node).attr("uValue").set(0)
                    else:
                        pm.PyNode(mp_node).attr("uValue").set(1)

                    pm.PyNode("MD_{}_Tweak_Ori_Null".format(
                        self.mouth_module)).rotate.connect(
                        pm.PyNode(ctrl_grp).rotate)
                    pm.PyNode("MD_{}_Scale_Null".format(
                        self.mouth_module)).scale.connect(
                        pm.PyNode(ctrl_grp).scale)

        base_ctrl_grp = "MD_{}_Base_Ctrl_Grp".format(self.mouth_module)
        if not check_constraint(scale_null, base_ctrl_grp):
            pm.scaleConstraint(base_ctrl_grp, scale_null, mo=True)
        if not check_constraint(tweak_ori_null, master_ctrl_null):
            pm.parentConstraint(master_ctrl_null, tweak_ori_null, mo=True)

        return

    def location_bind_jnt(self, jnt_grp="", jnt_type="lip", side="LF",
                          index=1):
        u"""对bind_grp进行定位

        :param jnt_grp:
        :param jnt_type:
        :return:
        """
        master_ctrl = "MD_{}_Master_Ctrl".format(self.mouth_module)

        if jnt_type == "lip":
            # 位移部分
            translate_bc_node = (jnt_grp.replace('_Grp', '_Translate_BC'))
            if not pm.objExists(translate_bc_node):
                pm.createNode("blendColors", name=translate_bc_node)
            if "UpLip" in jnt_grp:
                up_follicle_shape = (jnt_grp.replace("_Grp", "_FollicleShape"))
                low_follicle_shape = (
                    up_follicle_shape.replace("UpLip", "LowLip"))
            else:
                low_follicle_shape = (
                    jnt_grp.replace("_Grp", "_FollicleShape"))
                up_follicle_shape = (
                    low_follicle_shape.replace("LowLip", "UpLip"))

            pm.PyNode(up_follicle_shape).attr("outTranslate").connect(
                pm.PyNode(translate_bc_node).attr("color1"), f=True)
            pm.PyNode(low_follicle_shape).attr("outTranslate").connect(
                pm.PyNode(translate_bc_node).attr("color2"), f=True)
            pm.PyNode(translate_bc_node).attr("output").connect(
                pm.PyNode(jnt_grp).translate, f=True)

            lf_sew_follicle_shape = (
                "LF_{}_LipSew_Ctrl_FollicleShape".format(self.mouth_module))
            rt_sew_follicle_shape = (
                "RT_{}_LipSew_Ctrl_FollicleShape".format(self.mouth_module))

            sew_sr_node = (jnt_grp.replace("_Grp", "_LipSew_SR"))

            if not pm.objExists(sew_sr_node):
                pm.createNode("setRange", name=sew_sr_node)
                pm.PyNode(sew_sr_node).attr("minY").set(0.5)
                pm.PyNode(sew_sr_node).attr("maxX").set(0.5)
                if side == "LF":
                    pm.PyNode(sew_sr_node).attr("oldMinX").set(
                        0.5 - index * 0.1)
                    pm.PyNode(sew_sr_node).attr("oldMinY").set(
                        0.5 - index * 0.1)
                    pm.PyNode(sew_sr_node).attr("oldMaxX").set(
                        0.5 + 0.1 - index * 0.1)
                    pm.PyNode(sew_sr_node).attr("oldMaxY").set(
                        0.5 + 0.1 - index * 0.1)
                else:
                    pm.PyNode(sew_sr_node).attr("oldMinX").set(
                        0.5 - 0.1 + index * 0.1)
                    pm.PyNode(sew_sr_node).attr("oldMinY").set(
                        0.5 - 0.1 + index * 0.1)
                    pm.PyNode(sew_sr_node).attr("oldMaxX").set(
                        0.5 + index * 0.1)
                    pm.PyNode(sew_sr_node).attr("oldMaxY").set(
                        0.5 + index * 0.1)
            pm.PyNode(lf_sew_follicle_shape).attr(
                "parameterU").connect(
                pm.PyNode(sew_sr_node).attr("valueX"), f=True)
            pm.PyNode(rt_sew_follicle_shape).attr(
                "parameterU").connect(
                pm.PyNode(sew_sr_node).attr("valueY"), f=True)

            adl_node = (jnt_grp.replace("_Grp", "_ADL"))
            if not pm.objExists(adl_node):
                pm.createNode("addDoubleLinear", name=adl_node)
            pm.PyNode(sew_sr_node).attr("outValueX").connect(
                pm.PyNode(adl_node).attr("input1"), f=True)
            pm.PyNode(sew_sr_node).attr("outValueY").connect(
                pm.PyNode(adl_node).attr("input2"), f=True)

            cmp_node = (jnt_grp.replace("_Grp", "_LipSew_CMP"))
            if not pm.objExists(cmp_node):
                pm.createNode("clamp", name=cmp_node)
                pm.PyNode(cmp_node).attr("maxR").set(0.5)
            pm.PyNode(adl_node).attr("output").connect(
                pm.PyNode(cmp_node).attr("inputR"), f=True)

            if "Up" in jnt_grp:
                pma_node = (jnt_grp.replace("_Grp", "_LipSew_PMA"))
                if not pm.objExists(pma_node):
                    pm.createNode("plusMinusAverage", name=pma_node)
                    pm.PyNode(pma_node).attr("operation").set(2)
                    pm.PyNode(pma_node).attr("input1D[0]").set(1)
                pm.PyNode(cmp_node).attr("outputR").connect(
                    pm.PyNode(pma_node).attr("input1D[1]"), f=True)
                pm.PyNode(pma_node).attr("output1D").connect(
                    pm.PyNode(translate_bc_node).attr("blender"),
                    f=True)
            else:
                pm.PyNode(cmp_node).attr("outputR").connect(
                    pm.PyNode(translate_bc_node).attr("blender"),
                    f=True)

            # 旋转部分
            follicle_node = (jnt_grp.replace("_Grp", "_Follicle"))

            side_jnt_vp = (jnt_grp.replace("_Grp", "_VP"))

            if not pm.objExists(side_jnt_vp):
                pm.createNode("vectorProduct", name=side_jnt_vp)
                pm.PyNode(side_jnt_vp).attr("operation").set(3)
                pm.PyNode(side_jnt_vp).attr("input1X").set(1.0)
            pm.PyNode(follicle_node).attr("worldMatrix[0]").connect(
                pm.PyNode(side_jnt_vp).attr("matrix"), f=True)

            side_3rd_vp_node = (jnt_grp.replace("_Grp", "_3rd_VP"))
            if not pm.objExists(side_3rd_vp_node):
                pm.createNode("vectorProduct", name=side_3rd_vp_node)
                pm.PyNode(side_3rd_vp_node).attr("operation").set(2)
            pm.PyNode(side_jnt_vp).attr("output").connect(
                pm.PyNode(side_3rd_vp_node).attr("input2"), f=True)

            side_jnt_FBFM_node = (jnt_grp.replace("_Grp", "_FBFM"))
            if not pm.objExists(side_jnt_FBFM_node):
                pm.createNode("fourByFourMatrix",
                              name=side_jnt_FBFM_node)

            pm.PyNode(side_jnt_vp).attr("outputX").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in20"), f=True)
            pm.PyNode(side_jnt_vp).attr("outputY").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in21"), f=True)
            pm.PyNode(side_jnt_vp).attr("outputZ").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in22"), f=True)

            ctrl_null_vp = "MD_{}_Master_Ctrl_Null_VP".format(
                self.mouth_module)
            if not pm.objExists(ctrl_null_vp):
                pm.createNode("vectorProduct", name=ctrl_null_vp)
                pm.PyNode(ctrl_null_vp).attr("operation").set(3)
                pm.PyNode(
                    "MD_{}_Base_Ctrl_Out_Grp".format(self.mouth_module)).attr(
                    "worldMatrix[0]").connect(
                    pm.PyNode(ctrl_null_vp).attr("matrix"))
            pm.PyNode(ctrl_null_vp).attr("output").connect(
                pm.PyNode(side_3rd_vp_node).attr("input1"), f=True)
            pm.PyNode(ctrl_null_vp).attr("outputX").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in00"), f=True)
            pm.PyNode(ctrl_null_vp).attr("outputY").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in01"), f=True)
            pm.PyNode(ctrl_null_vp).attr("outputZ").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in02"), f=True)

            pm.PyNode(side_3rd_vp_node).attr("outputX").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in10"), f=True)
            pm.PyNode(side_3rd_vp_node).attr("outputY").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in11"), f=True)
            pm.PyNode(side_3rd_vp_node).attr("outputZ").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in12"), f=True)

            side_jnt_dm_node = (jnt_grp.replace("_Grp", "_DM"))
            if not pm.objExists(side_jnt_dm_node):
                pm.createNode("decomposeMatrix", name=side_jnt_dm_node)
            pm.PyNode(side_jnt_FBFM_node).attr("output").connect(
                pm.PyNode(side_jnt_dm_node).attr("inputMatrix"),
                f=True)
            pm.PyNode(side_jnt_dm_node).attr("outputRotate").connect(
                pm.PyNode(jnt_grp).rotate, f=True)

        else:
            # 位移部分
            corner_follicle = pm.PyNode(
                jnt_grp.replace("_Grp", "_Follicle"))
            corner_follicle.getShape().attr("outTranslate").connect(
                pm.PyNode(jnt_grp).translate, f=True)

            # 旋转部分
            base_ctrl_out_grp = pm.PyNode("MD_Mouth_01_Base_Ctrl_Out_Grp")

            null_vp = "MD_{}_Master_Ctrl_Null_VP".format(self.mouth_module)
            if not pm.objExists(null_vp):
                pm.createNode("vectorProduct", name=null_vp)
                pm.PyNode(null_vp).attr("operation").set(3)
                pm.PyNode(null_vp).attr("input1X").set(1.0)
            if (pm.PyNode(null_vp) not in pm.PyNode(base_ctrl_out_grp).attr(
                    "worldMatrix[0]").outputs()):
                pm.PyNode(base_ctrl_out_grp).attr("worldMatrix[0]").connect(
                    pm.PyNode(null_vp).attr("matrix"), f=True)

            jnt_vp = corner_follicle.name().replace("_Follicle", "_VP")
            if not pm.objExists(jnt_vp):
                pm.createNode("vectorProduct", name=jnt_vp)
                pm.PyNode(jnt_vp).attr("operation").set(3)
                pm.PyNode(jnt_vp).attr("input1X").set(1.0)

            corner_follicle.attr("worldMatrix[0]").connect(
                pm.PyNode(jnt_vp).attr("matrix"), f=True)

            jnt_3rd_vp = corner_follicle.name().replace("_Follicle", "_3rd_VP")
            if not pm.objExists(jnt_3rd_vp):
                pm.createNode("vectorProduct", name=jnt_3rd_vp)
                pm.PyNode(jnt_3rd_vp).attr("operation").set(2)

            pm.PyNode(null_vp).attr("output").connect(
                pm.PyNode(jnt_3rd_vp).attr("input1"), f=True)
            pm.PyNode(jnt_vp).attr("output").connect(
                pm.PyNode(jnt_3rd_vp).attr("input2"), f=True)

            jnt_FBFM_node = corner_follicle.name().replace("_Follicle",
                                                           "_FBFM")
            if not pm.objExists(jnt_FBFM_node):
                pm.createNode("fourByFourMatrix", name=jnt_FBFM_node)
            pm.PyNode(null_vp).attr("outputX").connect(
                pm.PyNode(jnt_FBFM_node).attr("in00"), f=True)
            pm.PyNode(null_vp).attr("outputY").connect(
                pm.PyNode(jnt_FBFM_node).attr("in01"), f=True)
            pm.PyNode(null_vp).attr("outputZ").connect(
                pm.PyNode(jnt_FBFM_node).attr("in02"), f=True)

            pm.PyNode(jnt_3rd_vp).attr("outputX").connect(
                pm.PyNode(jnt_FBFM_node).attr("in10"), f=True)
            pm.PyNode(jnt_3rd_vp).attr("outputY").connect(
                pm.PyNode(jnt_FBFM_node).attr("in11"), f=True)
            pm.PyNode(jnt_3rd_vp).attr("outputZ").connect(
                pm.PyNode(jnt_FBFM_node).attr("in12"), f=True)

            pm.PyNode(jnt_vp).attr("outputX").connect(
                pm.PyNode(jnt_FBFM_node).attr("in20"), f=True)
            pm.PyNode(jnt_vp).attr("outputY").connect(
                pm.PyNode(jnt_FBFM_node).attr("in21"), f=True)
            pm.PyNode(jnt_vp).attr("outputZ").connect(
                pm.PyNode(jnt_FBFM_node).attr("in22"), f=True)

            jnt_dm_node = corner_follicle.name().replace("_Follicle", "_DM")
            if not pm.objExists(jnt_dm_node):
                jnt_dm_node = pm.createNode(
                    "decomposeMatrix", name=jnt_dm_node)
            pm.PyNode(jnt_FBFM_node).attr("output").connect(
                pm.PyNode(jnt_dm_node).attr("inputMatrix"), f=True)

            pm.PyNode(jnt_dm_node).attr("outputRotate").connect(
                pm.PyNode(jnt_grp).attr("rotate"), f=True)

        # 因为 localScale 是单属性，scale是一组属性，
        # 所以必须得逐一连接属性：scaleX， scaleY， scaleZ
        pm.PyNode(master_ctrl).attr("localScale").connect(
            pm.PyNode(jnt_grp).scaleX, f=True)
        pm.PyNode(master_ctrl).attr("localScale").connect(
            pm.PyNode(jnt_grp).scaleY, f=True)
        pm.PyNode(master_ctrl).attr("localScale").connect(
            pm.PyNode(jnt_grp).scaleZ, f=True)
        return

    def xd_bind_jnt(self, name, have_loc=False, parent_node="",
                    translate=(0, 0, 0)):
        pm.select(cl=True)
        pm.joint(name=name)

        pm.parent(
            pm.createNode("transform", name="{}_RollOut_Grp".format(name)),
            pm.createNode("transform", name="{}_Grp".format(name)))
        pm.parent(name, "{}_RollOut_Grp".format(name))

        if have_loc:
            pm.parent(
                pm.spaceLocator(name="{}_RollOut_Loc".format(name)),
                "{}_Grp".format(name))

        pm.PyNode("{}_Grp".format(name)).translate.set(translate)

        if parent_node is not None:
            if pm.objExists(parent_node):
                pm.parent("{}_Grp".format(name), parent_node)

        return "{}_Grp".format(name)

    def skin_out_curve(self):
        seg = 5
        bind_jnt_grp = "MD_{}_Bind_Jnt_Grp".format(self.mouth_module)
        if not pm.objExists(bind_jnt_grp):
            pm.createNode(
                "transform",
                name=bind_jnt_grp,
                p="MD_{}_Deformer_Grp".format(self.mouth_module))
        skin_items = []
        for prefix in ["Up", "Low"]:
            if prefix == "Up":
                out_curve = self.up_base_curve
            else:
                out_curve = self.low_out_curve
            # out_curve = pm.PyNode(
            #     "MD_Mouth_01_{}_Out_Curve".format(prefix))
            skin_items.append(out_curve)
            for side in ["LF", "RT"]:
                for index in range(1, seg + 1):
                    jnt_name = "{}_Mouth_01_{}Lip_{}_Jnt".format(
                        side, prefix, "{0:02d}".format(index))
                    bind_jnt = self.xd_bind_jnt(
                        name=jnt_name,
                        parent_node=bind_jnt_grp,
                        have_loc=True)
                    self.location_bind_jnt(
                        jnt_grp=bind_jnt,
                        jnt_type='lip',
                        side=side,
                        index=index)
                    skin_items.append(jnt_name)  # LF_Mouth_01_UpLip_01_Jnt
                if prefix == "Up":
                    jnt_name = "{}_{}_Lip_Jnt".format(side, self.mouth_module)
                    bind_jnt = self.xd_bind_jnt(
                        name=jnt_name,
                        parent_node=bind_jnt_grp,
                        have_loc=True
                    )
                    self.location_bind_jnt(
                        jnt_grp=bind_jnt,
                        jnt_type='corner',
                        side=side)
                    skin_items.append(jnt_name)
            pm.skinCluster(skin_items, name="{}_SC".format(out_curve))
        return

    def use_dm_node_to_tweak_ctrl_parent_and_jnt_02_grp(self):
        # todo 考虑在tweak ctrl或者jnt创建初就调用，执行这个方法
        seg = 3
        for side in ["LF", "RT"]:
            tweak_ctrl = "{}_Mouth_01_Tweak_Ctrl".format(side)

            custom_show_channel(
                tweak_ctrl,
                attr_list=["translateX", "translateY", "translateZ"])

            pm.addAttr(tweak_ctrl, ln="roll", at="double", dv=0)
            pm.setAttr("{}.roll".format(tweak_ctrl), e=True, k=True)

            tweak_ctrl_parent = pm.PyNode(tweak_ctrl).getParent()
            dm_node = pm.createNode(
                "decomposeMatrix",
                name="{}_Inverse_DM".format(tweak_ctrl))
            pm.PyNode(tweak_ctrl).attr("inverseMatrix").connect(
                dm_node.attr("inputMatrix")
            )
            dm_node.attr("outputTranslate").connect(
                tweak_ctrl_parent.translate)
            dm_node.attr("outputRotate").connect(
                tweak_ctrl_parent.rotate)

            jnt_02_grp = "{}_Mouth_01_Tweak_Ctrl_Jnt_02_Grp".format(side)
            pm.PyNode(tweak_ctrl).translate.connect(
                pm.PyNode(jnt_02_grp).translate)
            pm.PyNode(tweak_ctrl).attr("roll").connect(
                pm.PyNode(jnt_02_grp).rotateX)

            for location in ["Up", "Low"]:
                for index in range(1, seg + 1):
                    tweak_ctrl = "{}_Mouth_01_{}Tweak_{}_Ctrl".format(
                        side, location, "{0:02d}".format(index))

                    custom_show_channel(
                        tweak_ctrl,
                        attr_list=["translateX", "translateY", "translateZ"])

                    pm.addAttr(tweak_ctrl, ln="roll", at="double", dv=0)
                    pm.setAttr("{}.roll".format(tweak_ctrl), e=True, k=True)

                    tweak_ctrl_parent = pm.PyNode(tweak_ctrl).getParent()
                    dm_node = pm.createNode(
                        "decomposeMatrix",
                        name="{}_Inverse_DM".format(tweak_ctrl))
                    pm.PyNode(tweak_ctrl).attr("inverseMatrix").connect(
                        dm_node.attr("inputMatrix")
                    )
                    dm_node.attr("outputTranslate").connect(
                        tweak_ctrl_parent.translate)
                    dm_node.attr("outputRotate").connect(
                        tweak_ctrl_parent.rotate)

                    jnt_02_grp = (
                        "{}_Mouth_01_{}Tweak_{}_Ctrl_Jnt_02_Grp".format(
                            side, location, "{0:02d}".format(index)))
                    pm.PyNode(tweak_ctrl).translate.connect(
                        pm.PyNode(jnt_02_grp).translate)
                    pm.PyNode(tweak_ctrl).attr("roll").connect(
                        pm.PyNode(jnt_02_grp).rotateX)

        return

    def skin_tweak_surface(self):
        seg = 3
        for prefix in ["Up", "Low"]:
            skin_items = []
            if prefix == "Up":
                tweak_surface = self.up_tweak_surface
            else:
                tweak_surface = self.low_tweak_surface
            skin_items.append(tweak_surface)
            print("skin_items: {}".format(skin_items))
            for side in ["LF", "RT"]:
                for index in range(1, seg + 1):
                    skin_items.append("{}_Mouth_01_{}Tweak_{}_Ctrl_Jnt".format(
                        side, prefix, "{0:02d}".format(index)))
                skin_items.append("{}_Mouth_01_Tweak_Ctrl_Jnt".format(side))
            print("skin_items: {}".format(skin_items))
            pm.skinCluster(
                skin_items,
                name="{}_SC".format(tweak_surface))
        return

    def __skin_lip_sew_surface_and_connect_follicle_shape(self):
        sew_surface = "MD_Mouth_01_LipSew_Surface"
        skin_items = ["MD_Mouth_01_Master_Ctrl_Jnt", "LF_Mouth_01_Ctrl_Jnt",
                      "RT_Mouth_01_Ctrl_Jnt", sew_surface]
        pm.skinCluster(skin_items,
                       name="{}_SC".format(sew_surface))
        for side in ["LF", "RT"]:
            follicle = "{}_Mouth_01_LipSew_Ctrl_Follicle".format(side)
            if side == "LF":
                param_u = 0.0
            else:
                param_u = 1.0
            param_v = 0.5
            make_follicle_work_on_surface(
                surface=sew_surface,
                follicle=follicle,
                param_u=param_u,
                param_v=param_v)
            follicle_shape_out_for_parent(pm.PyNode(follicle).getShape())
            mouth_scale_null_node = "MD_Mouth_01_Scale_Null"
            pm.PyNode(mouth_scale_null_node).scale.connect(
                pm.PyNode(follicle).scale, f=True)
        return

    def lip_sew_ctrl_drive_follicle_shape(self):
        for side in ["LF", "RT"]:
            follicle = "{}_Mouth_01_LipSew_Ctrl_Follicle".format(side)
            follicle_shape = pm.PyNode(follicle).getShape()

            lip_sew_ctrl = "{}_Mouth_01_LipSew_Ctrl".format(side)
            lip_sew_ctrl_grp = "{}_Grp".format(lip_sew_ctrl)
            if not pm.objExists(lip_sew_ctrl):
                lip_sew_ctrl_grp = yellow_component(
                    name=lip_sew_ctrl,
                    shape_type="cone",
                    parent_node=follicle,
                )
            pm.PyNode(lip_sew_ctrl_grp).translate.set([0, 0, 0])
            if side == "LF":
                pm.PyNode(lip_sew_ctrl_grp).rotate.set([0, 180, 0])
            else:
                pm.PyNode(lip_sew_ctrl_grp).rotate.set([0, 0, 0])
                pm.PyNode(lip_sew_ctrl_grp).scale.set([1, 1, -1])

            custom_show_channel(lip_sew_ctrl, attr_list=["translateX"])

            pm.transformLimits(lip_sew_ctrl, tx=[-0.81, 0], etx=[1, 1])

            if side == "LF":
                driver_value = [-0.814, 0]
                value = [1, 0]
            else:
                driver_value = [-0.814, 0]
                value = [0, 1]

            pm.setDrivenKeyframe(
                follicle_shape,
                at="parameterU",
                cd="{}.{}".format(lip_sew_ctrl, "translateX"),
                dv=driver_value[0],
                value=value[0],
                itt="linear",
                ott="linear",
            )

            pm.setDrivenKeyframe(
                follicle_shape,
                at="parameterU",
                cd="{}.{}".format(lip_sew_ctrl, "translateX"),
                dv=driver_value[1],
                value=value[1],
                itt="linear",
                ott="linear",
            )
        return True

    def make_bind_jnt_work(self):
        """让蒙皮骨骼能够工作

        :return:
        """
        seg = 5
        master_ctrl = "MD_{}_Master_Ctrl".format(self.mouth_module)
        for side in ["LF", "RT"]:
            corner_bind_jnt_root = "{}_{}_Lip_Jnt_Grp".format(
                side, self.mouth_module)
            # 因为 localScale 是单属性，scale是一组属性，
            # 所以必须得逐一连接属性：scaleX， scaleY， scaleZ
            pm.PyNode(master_ctrl).attr("localScale").connect(
                pm.PyNode(corner_bind_jnt_root).scaleX, f=True)
            pm.PyNode(master_ctrl).attr("localScale").connect(
                pm.PyNode(corner_bind_jnt_root).scaleY, f=True)
            pm.PyNode(master_ctrl).attr("localScale").connect(
                pm.PyNode(corner_bind_jnt_root).scaleZ, f=True)

            # 位移部分
            corner_follicle = pm.PyNode(
                corner_bind_jnt_root.replace("_Grp", "_Follicle"))
            corner_follicle.getShape().attr("outTranslate").connect(
                pm.PyNode(corner_bind_jnt_root).translate, f=True)

            # 旋转部分
            base_ctrl_out_grp = pm.PyNode("MD_Mouth_01_Base_Ctrl_Out_Grp")

            null_vp = "MD_Mouth_01_Master_Ctrl_Null_VP"
            if not pm.objExists(null_vp):
                pm.createNode("vectorProduct", name=null_vp)
                pm.PyNode(null_vp).attr("operation").set(3)
                pm.PyNode(null_vp).attr("input1X").set(1.0)

            if (pm.PyNode(null_vp) not in pm.PyNode(base_ctrl_out_grp).attr(
                    "worldMatrix[0]").outputs()):
                pm.PyNode(base_ctrl_out_grp).attr("worldMatrix[0]").connect(
                    pm.PyNode(null_vp).attr("matrix"), f=True)

            jnt_vp = corner_follicle.name().replace("_Follicle", "_VP")
            if not pm.objExists(jnt_vp):
                pm.createNode("vectorProduct", name=jnt_vp)
                pm.PyNode(jnt_vp).attr("operation").set(3)
                pm.PyNode(jnt_vp).attr("input1X").set(1.0)

            corner_follicle.attr("worldMatrix[0]").connect(
                pm.PyNode(jnt_vp).attr("matrix"), f=True)

            jnt_3rd_vp = corner_follicle.name().replace("_Follicle", "_3rd_VP")
            if not pm.objExists(jnt_3rd_vp):
                pm.createNode("vectorProduct", name=jnt_3rd_vp)
                pm.PyNode(jnt_3rd_vp).attr("operation").set(2)

            pm.PyNode(null_vp).attr("output").connect(
                pm.PyNode(jnt_3rd_vp).attr("input1"), f=True)
            pm.PyNode(jnt_vp).attr("output").connect(
                pm.PyNode(jnt_3rd_vp).attr("input2"), f=True)

            jnt_FBFM_node = corner_follicle.name().replace("_Follicle",
                                                           "_FBFM")
            if not pm.objExists(jnt_FBFM_node):
                pm.createNode("fourByFourMatrix", name=jnt_FBFM_node)
            pm.PyNode(null_vp).attr("outputX").connect(
                pm.PyNode(jnt_FBFM_node).attr("in00"), f=True)
            pm.PyNode(null_vp).attr("outputY").connect(
                pm.PyNode(jnt_FBFM_node).attr("in01"), f=True)
            pm.PyNode(null_vp).attr("outputZ").connect(
                pm.PyNode(jnt_FBFM_node).attr("in02"), f=True)

            pm.PyNode(jnt_3rd_vp).attr("outputX").connect(
                pm.PyNode(jnt_FBFM_node).attr("in10"), f=True)
            pm.PyNode(jnt_3rd_vp).attr("outputY").connect(
                pm.PyNode(jnt_FBFM_node).attr("in11"), f=True)
            pm.PyNode(jnt_3rd_vp).attr("outputZ").connect(
                pm.PyNode(jnt_FBFM_node).attr("in12"), f=True)

            pm.PyNode(jnt_vp).attr("outputX").connect(
                pm.PyNode(jnt_FBFM_node).attr("in20"), f=True)
            pm.PyNode(jnt_vp).attr("outputY").connect(
                pm.PyNode(jnt_FBFM_node).attr("in21"), f=True)
            pm.PyNode(jnt_vp).attr("outputZ").connect(
                pm.PyNode(jnt_FBFM_node).attr("in22"), f=True)

            jnt_dm_node = corner_follicle.name().replace("_Follicle", "_DM")
            if not pm.objExists(jnt_dm_node):
                jnt_dm_node = pm.createNode(
                    "decomposeMatrix", name=jnt_dm_node)
            pm.PyNode(jnt_FBFM_node).attr("output").connect(
                pm.PyNode(jnt_dm_node).attr("inputMatrix"), f=True)

            pm.PyNode(jnt_dm_node).attr("outputRotate").connect(
                pm.PyNode(corner_bind_jnt_root).attr("rotate"), f=True)

            for location in ["Up", "Low"]:
                for index in range(1, seg + 1):
                    # 缩放部分
                    bind_jnt_root = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_Grp".format(
                            side, location, "{0:02d}".format(index)))
                    pm.PyNode(master_ctrl).attr("localScale").connect(
                        pm.PyNode(bind_jnt_root).scaleX, f=True)
                    pm.PyNode(master_ctrl).attr("localScale").connect(
                        pm.PyNode(bind_jnt_root).scaleY, f=True)
                    pm.PyNode(master_ctrl).attr("localScale").connect(
                        pm.PyNode(bind_jnt_root).scaleZ, f=True)

                    # 位移部分
                    translate_bc_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_Translate_BC".format(
                            side, location, "{0:02d}".format(index)))
                    if not pm.objExists(translate_bc_node):
                        pm.createNode("blendColors", name=translate_bc_node)
                    low_follicle_shape = (
                        "{}_Mouth_01_LowLip_{}_Jnt_FollicleShape".format(
                            side, "{0:02d}".format(index)))
                    up_follicle_shape = (
                        "{}_Mouth_01_UpLip_{}_Jnt_FollicleShape".format(
                            side, "{0:02d}".format(index)))
                    pm.PyNode(up_follicle_shape).attr("outTranslate").connect(
                        pm.PyNode(translate_bc_node).attr("color1"), f=True)
                    pm.PyNode(low_follicle_shape).attr("outTranslate").connect(
                        pm.PyNode(translate_bc_node).attr("color2"), f=True)
                    pm.PyNode(translate_bc_node).attr("output").connect(
                        pm.PyNode(bind_jnt_root).translate, f=True)

                    lf_sew_follicle_shape = (
                        "LF_Mouth_01_LipSew_Ctrl_FollicleShape")
                    rt_sew_follicle_shape = (
                        "RT_Mouth_01_LipSew_Ctrl_FollicleShape")

                    sew_sr_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_LipSew_SR".format(
                            side, location, "{0:02d}".format(index)))
                    if not pm.objExists(sew_sr_node):
                        pm.createNode("setRange", name=sew_sr_node)
                        pm.PyNode(sew_sr_node).attr("minY").set(0.5)
                        pm.PyNode(sew_sr_node).attr("maxX").set(0.5)
                        if side == "LF":
                            pm.PyNode(sew_sr_node).attr("oldMinX").set(
                                0.5 - index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMinY").set(
                                0.5 - index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMaxX").set(
                                0.5 + 0.1 - index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMaxY").set(
                                0.5 + 0.1 - index * 0.1)
                        elif side == "RT":
                            pm.PyNode(sew_sr_node).attr("oldMinX").set(
                                0.5 - 0.1 + index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMinY").set(
                                0.5 - 0.1 + index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMaxX").set(
                                0.5 + index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMaxY").set(
                                0.5 + index * 0.1)
                    pm.PyNode(lf_sew_follicle_shape).attr(
                        "parameterU").connect(
                        pm.PyNode(sew_sr_node).attr("valueX"), f=True)
                    pm.PyNode(rt_sew_follicle_shape).attr(
                        "parameterU").connect(
                        pm.PyNode(sew_sr_node).attr("valueY"), f=True)

                    adl_node = ("{}_Mouth_01_{}Lip_{}_Jnt_ADL".format(
                        side, location, "{0:02d}".format(index)))
                    if not pm.objExists(adl_node):
                        pm.createNode("addDoubleLinear", name=adl_node)
                    pm.PyNode(sew_sr_node).attr("outValueX").connect(
                        pm.PyNode(adl_node).attr("input1"), f=True)
                    pm.PyNode(sew_sr_node).attr("outValueY").connect(
                        pm.PyNode(adl_node).attr("input2"), f=True)

                    cmp_node = ("{}_Mouth_01_{}Lip_{}_Jnt_LipSew_CMP".format(
                        side, location, "{0:02d}".format(index)))
                    if not pm.objExists(cmp_node):
                        pm.createNode("clamp", name=cmp_node)
                        pm.PyNode(cmp_node).attr("maxR").set(0.5)
                    pm.PyNode(adl_node).attr("output").connect(
                        pm.PyNode(cmp_node).attr("inputR"), f=True)

                    if location == "Up":
                        pma_node = (
                            "{}_Mouth_01_{}Lip_{}_Jnt_LipSew_PMA".format(
                                side, location, "{0:02d}".format(index)))
                        if not pm.objExists(pma_node):
                            pm.createNode("plusMinusAverage", name=pma_node)
                            pm.PyNode(pma_node).attr("operation").set(2)
                            pm.PyNode(pma_node).attr("input1D[0]").set(1)
                        pm.PyNode(cmp_node).attr("outputR").connect(
                            pm.PyNode(pma_node).attr("input1D[1]"), f=True)
                        pm.PyNode(pma_node).attr("output1D").connect(
                            pm.PyNode(translate_bc_node).attr("blender"),
                            f=True)
                    else:
                        pm.PyNode(cmp_node).attr("outputR").connect(
                            pm.PyNode(translate_bc_node).attr("blender"),
                            f=True)

                    # 旋转部分
                    follicle_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_Follicle".format(
                            side, location, "{0:02d}".format(index)))

                    side_jnt_vp = ("{}_Mouth_01_{}Lip_{}_Jnt_VP".format(
                        side, location, "{0:02d}".format(index)))
                    if not pm.objExists(side_jnt_vp):
                        pm.createNode("vectorProduct", name=side_jnt_vp)
                        pm.PyNode(side_jnt_vp).attr("operation").set(3)
                        pm.PyNode(side_jnt_vp).attr("input1X").set(1.0)
                    pm.PyNode(follicle_node).attr("worldMatrix[0]").connect(
                        pm.PyNode(side_jnt_vp).attr("matrix"), f=True)

                    side_3rd_vp_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_3rd_VP".format(
                            side, location, "{0:02d}".format(index)))
                    if not pm.objExists(side_3rd_vp_node):
                        pm.createNode("vectorProduct", name=side_3rd_vp_node)
                        pm.PyNode(side_3rd_vp_node).attr("operation").set(2)
                    pm.PyNode(side_jnt_vp).attr("output").connect(
                        pm.PyNode(side_3rd_vp_node).attr("input2"), f=True)

                    side_jnt_FBFM_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_FBFM".format(
                            side, location, "{0:02d}".format(index)))
                    if not pm.objExists(side_jnt_FBFM_node):
                        pm.createNode("fourByFourMatrix",
                                      name=side_jnt_FBFM_node)

                    pm.PyNode(side_jnt_vp).attr("outputX").connect(
                        pm.PyNode(side_jnt_FBFM_node).attr("in20"), f=True)
                    pm.PyNode(side_jnt_vp).attr("outputY").connect(
                        pm.PyNode(side_jnt_FBFM_node).attr("in21"), f=True)
                    pm.PyNode(side_jnt_vp).attr("outputZ").connect(
                        pm.PyNode(side_jnt_FBFM_node).attr("in22"), f=True)

                    ctrl_null_vp = "MD_Mouth_01_Master_Ctrl_Null_VP"
                    # if not pm.objExists(ctrl_null_vp):
                    #     pm.createNode("vectorProduct", name=ctrl_null_vp)
                    #     pm.PyNode(ctrl_null_vp).attr("operation").set(3)
                    pm.PyNode(ctrl_null_vp).attr("output").connect(
                        pm.PyNode(side_3rd_vp_node).attr("input1"), f=True)
                    pm.PyNode(ctrl_null_vp).attr("outputX").connect(
                        pm.PyNode(side_jnt_FBFM_node).attr("in00"), f=True)
                    pm.PyNode(ctrl_null_vp).attr("outputY").connect(
                        pm.PyNode(side_jnt_FBFM_node).attr("in01"), f=True)
                    pm.PyNode(ctrl_null_vp).attr("outputZ").connect(
                        pm.PyNode(side_jnt_FBFM_node).attr("in02"), f=True)

                    pm.PyNode(side_3rd_vp_node).attr("outputX").connect(
                        pm.PyNode(side_jnt_FBFM_node).attr("in10"), f=True)
                    pm.PyNode(side_3rd_vp_node).attr("outputY").connect(
                        pm.PyNode(side_jnt_FBFM_node).attr("in11"), f=True)
                    pm.PyNode(side_3rd_vp_node).attr("outputZ").connect(
                        pm.PyNode(side_jnt_FBFM_node).attr("in12"), f=True)

                    side_jnt_dm_node = ("{}_Mouth_01_{}Lip_{}_Jnt_DM".format(
                        side, location, "{0:02d}".format(index)))
                    if not pm.objExists(side_jnt_dm_node):
                        pm.createNode("decomposeMatrix", name=side_jnt_dm_node)
                    pm.PyNode(side_jnt_FBFM_node).attr("output").connect(
                        pm.PyNode(side_jnt_dm_node).attr("inputMatrix"),
                        f=True)
                    pm.PyNode(side_jnt_dm_node).attr("outputRotate").connect(
                        pm.PyNode(bind_jnt_root).rotate, f=True)

        return

    def make_bind_jnt_scale_work(self):
        """ 让 bind jnt 的 scale 能够正确工作

        bind jnt的缩放是由 master ctrl 的 localScale 和 lipSqueeze 两个属性，
        以及 base curve 的弧长所影响控制

        :return: None
        """
        seg = 5
        master_ctrl = "MD_{}_Master_Ctrl".format(
            self.mouth_module)  # MD_Mouth_01_Master_Ctrl

        if not pm.attributeQuery(
                "lipSqueeze", node=master_ctrl, ex=True):
            pm.addAttr(master_ctrl,
                       ln="lipSqueeze", at="double", min=0, dv=0.5)
            pm.setAttr("{}.lipSqueeze".format(master_ctrl),
                       e=True, k=True)

        for side in ["LF", "RT"]:
            for location in ["Up", "Low"]:
                base_curve = ("MD_Mouth_01_{}_Base_Curve".format(location))

                base_curve_ci = ("MD_Mouth_01_{}_Base_Curve_CI".format(
                    location))
                if not pm.objExists(base_curve_ci):
                    pm.createNode("curveInfo", name=base_curve_ci)
                    pm.PyNode(base_curve).getShape().attr(
                        "worldSpace[0]").connect(
                        pm.PyNode(base_curve_ci).attr("inputCurve"), f=True)

                base_curve_arc_length = (
                    pm.PyNode(base_curve_ci).attr("arcLength").get())

                base_scale_mdl_node = (
                    "MD_Mouth_01_{}_Base_Curve_Scale_MDL".format(location))
                if not pm.objExists(base_scale_mdl_node):
                    pm.createNode("multDoubleLinear", name=base_scale_mdl_node)
                    pm.PyNode(base_scale_mdl_node).attr("input2").set(
                        base_curve_arc_length)
                    pm.PyNode(master_ctrl).attr("localScale").connect(
                        pm.PyNode(base_scale_mdl_node).attr("input1"), f=True)

                # MD_Mouth_01_Up_Base_Curve_Scale_MD
                base_scale_md_node = (
                    "MD_Mouth_01_{}_Base_Curve_Scale_MD".format(location))
                if not pm.objExists(base_scale_md_node):
                    pm.createNode("multiplyDivide", name=base_scale_md_node)
                    pm.PyNode(base_scale_md_node).attr("operation").set(2)
                    pm.PyNode(base_scale_mdl_node).attr("output").connect(
                        pm.PyNode(base_scale_md_node).attr("input1X"), f=True)
                    pm.PyNode(base_curve_ci).attr("arcLength").connect(
                        pm.PyNode(base_scale_md_node).attr("input2X"), f=True)

                for index in range(1, seg + 1):
                    jnt_scale_cond_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_Scale_Cond".format(
                            side, location, "{0:02d}".format(index)))
                    if not pm.objExists(jnt_scale_cond_node):
                        pm.createNode("condition", name=jnt_scale_cond_node)
                        pm.PyNode(jnt_scale_cond_node).attr("secondTerm").set(
                            base_curve_arc_length)
                        pm.PyNode(jnt_scale_cond_node).attr("operation").set(2)
                        pm.PyNode(base_curve_ci).attr("arcLength").connect(
                            pm.PyNode(jnt_scale_cond_node).attr("firstTerm"),
                            f=True)

                    # LF_Mouth_01_UpLip_01_Jnt_Scale_MDL
                    jnt_scale_mdl_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_Scale_MDL".format(
                            side, location, "{0:02d}".format(index)))
                    if not pm.objExists(jnt_scale_mdl_node):
                        pm.createNode("multDoubleLinear",
                                      name=jnt_scale_mdl_node)
                        pm.PyNode(master_ctrl).attr("lipSqueeze").connect(
                            pm.PyNode(jnt_scale_mdl_node).attr("input1"),
                            f=True)
                        pm.PyNode(jnt_scale_cond_node).attr(
                            "outColorR").connect(
                            pm.PyNode(jnt_scale_mdl_node).attr("input2"),
                            f=True)

                    # LF_Mouth_01_UpLip_01_Jnt_Scale_MD
                    jnt_scale_md_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_Scale_MD".format(
                            side, location, "{0:02d}".format(index)))
                    if not pm.objExists(jnt_scale_md_node):
                        pm.createNode("multiplyDivide",
                                      name=jnt_scale_md_node)
                        pm.PyNode(jnt_scale_md_node).attr("operation").set(3)
                        pm.PyNode(base_scale_md_node).attr("outputX").connect(
                            pm.PyNode(jnt_scale_md_node).attr("input1X"),
                            f=True)
                        pm.PyNode(jnt_scale_mdl_node).attr("output").connect(
                            pm.PyNode(jnt_scale_md_node).attr("input2X"),
                            f=True)

                    # LF_Mouth_01_UpLip_01_Jnt
                    bind_jnt = (
                        "{}_Mouth_01_{}Lip_{}_Jnt".format(
                            side, location, "{0:02d}".format(index)))
                    pm.PyNode(jnt_scale_md_node).attr("outputX").connect(
                        pm.PyNode(bind_jnt).attr("scaleX"), f=True)
                    pm.PyNode(jnt_scale_md_node).attr("outputX").connect(
                        pm.PyNode(bind_jnt).attr("scaleY"), f=True)
                    pm.PyNode(jnt_scale_md_node).attr("outputX").connect(
                        pm.PyNode(bind_jnt).attr("scaleZ"), f=True)

        # print("Done!")
        return True

    def static_corner_when_master_ctrl_move_up(self):
        master_ctrl = "MD_{}_Master_Ctrl".format(self.mouth_module)
        jaw_ctrl = "MD_{}_Jaw_Ctrl".format(self.mouth_module)
        for side in ['LF', 'RT']:
            side_null_03_grp = ("{}_Mouth_01_Ctrl_Null_03_Grp".format(
                side))  # LF_Mouth_01_Ctrl_Null_03_Grp
            print(side_null_03_grp)

            driver_value = [-0.2, 0, 0.2]
            value = [0.12, 0, -0.1]

            for index in range(0, len(driver_value)):
                pm.setDrivenKeyframe(
                    side_null_03_grp,
                    at="translateY",
                    cd="{}.{}".format(master_ctrl, "translateY"),
                    dv=driver_value[index],
                    value=value[index],
                    itt="linear",
                    ott="linear",
                )

            driver_value = [-10, 0, 25]
            value = [0.0814, 0, -0.10175]

            for index in range(0, len(driver_value)):
                pm.setDrivenKeyframe(
                    side_null_03_grp,
                    at="translateX",
                    cd="{}.{}".format(jaw_ctrl, "rotateX"),
                    dv=driver_value[index],
                    value=value[index],
                    itt="linear",
                    ott="linear",
                )

            if side == "LF":
                driver_value = [-0.4, 0, 0.4]
                value = [0, 0, -0.2]
            else:
                driver_value = [-0.4, 0, 0.4]
                value = [-0.2, 0, 0]

            for index in range(0, len(driver_value)):
                pm.setDrivenKeyframe(
                    side_null_03_grp,
                    at="translateX",
                    cd="{}.{}".format(master_ctrl, "translateX"),
                    dv=driver_value[index],
                    value=value[index],
                    itt="linear",
                    ott="linear",
                )

            side_ctrl_null = ("{}_Mouth_01_Ctrl_Null".format(side))
            pm.parentConstraint(side_null_03_grp, side_ctrl_null, mo=True)

            ctrl_loc_02_grp = ("{}_Mouth_01_Ctrl_Loc_02_Grp".format(side))
            ctrl_02_grp = ("{}_Mouth_01_Ctrl_02_Grp".format(side))
            pm.PyNode(side_ctrl_null).attr("translate").connect(
                pm.PyNode(ctrl_loc_02_grp).translate)
            pm.PyNode(side_ctrl_null).attr("translate").connect(
                pm.PyNode(ctrl_02_grp).translate)

        return

    def __connect_jaw_ctrl_and_jnt(self):
        ctrl = "MD_Mouth_01_Jaw_Tweak_Ctrl"
        jnt = "MD_Mouth_01_Jaw_Tweak_Ctrl_Jnt"
        pm.PyNode(ctrl).translate.connect(pm.PyNode(jnt).translate)
        pm.PyNode(ctrl).rotate.connect(pm.PyNode(jnt).rotate)
        pm.PyNode(ctrl).scale.connect(pm.PyNode(jnt).scale)
        return True

    def make_jaw_ctrl_translate(self):
        # 将下巴控制器的位移和旋转属性连接到下巴的下半部分的组上面
        # 下巴组分为上下两个部分，上半部分包含上半部分的牙齿
        # 下部分包含下半部分的牙齿，下巴和下颚骨
        jaw_ctrl = "MD_Mouth_01_Jaw_Ctrl"
        low_jaw_jnt_grp = "MD_Mouth_01_LowJaw_Jnt_Grp"

        if not pm.PyNode(jaw_ctrl).translate.isConnectedTo(
                pm.PyNode(low_jaw_jnt_grp).translate):
            pm.PyNode(jaw_ctrl).translate.connect(
                pm.PyNode(low_jaw_jnt_grp).translate, f=True)

        if not pm.PyNode(jaw_ctrl).rotate.isConnectedTo(
                pm.PyNode(low_jaw_jnt_grp).rotate):
            pm.PyNode(jaw_ctrl).rotate.connect(
                pm.PyNode(low_jaw_jnt_grp).rotate, f=True)

        master_ctrl_grp = "MD_Mouth_01_Master_Ctrl_Grp"
        if not check_constraint(master_ctrl_grp, jaw_ctrl):
            constraint = pm.parentConstraint(
                jaw_ctrl,
                pm.PyNode(jaw_ctrl).getParent(),
                master_ctrl_grp,
                mo=True)

            driver_value = [-1, 0]
            value = [0, 1]

            for index in range(0, len(driver_value)):
                pm.setDrivenKeyframe(
                    constraint,
                    at="{}W1".format(pm.PyNode(jaw_ctrl).getParent().name()),
                    cd="{}.rotateX".format(jaw_ctrl),
                    dv=driver_value[index],
                    value=value[index],
                    itt="linear",
                    ott="linear",
                )

        # todo 缺少对脸颊 cheek 的支持

        return True

    def low_jaw_jnt_connect_low_mouth_ctrl(self):
        low_jaw_jnt = "MD_Mouth_01_LowJaw_Jnt"
        ctrl_null = "Low_Mouth_01_Ctrl_Null"
        pm.parentConstraint(low_jaw_jnt, ctrl_null, mo=True)

        ctrl_jnt_02_grp = "Low_Mouth_01_Ctrl_Jnt_02_Grp"
        ctrl_02_grp = "Low_Mouth_01_Ctrl_02_Grp"

        if not pm.PyNode(ctrl_null).translate.isConnectedTo(
                pm.PyNode(ctrl_jnt_02_grp).translate):
            pm.PyNode(ctrl_null).translate.connect(
                pm.PyNode(ctrl_jnt_02_grp).translate)
        if not pm.PyNode(ctrl_null).rotate.isConnectedTo(
                pm.PyNode(ctrl_jnt_02_grp).rotate):
            pm.PyNode(ctrl_null).rotate.connect(
                pm.PyNode(ctrl_jnt_02_grp).rotate)

        if not pm.PyNode(ctrl_null).translate.isConnectedTo(
                pm.PyNode(ctrl_02_grp).translate):
            pm.PyNode(ctrl_null).translate.connect(
                pm.PyNode(ctrl_02_grp).translate)

        # todo 缺少对 cheek 的支持

        return True

    def lip_sew_and_follicle(self):
        lip_sew_surface = self.mouth_lip_sew_surface
        skin_items = [lip_sew_surface]
        for control in ["LF_{}_Ctrl".format(self.mouth_module),
                        "RT_{}_Ctrl".format(self.mouth_module),
                        "MD_{}_Master_Ctrl".format(self.mouth_module)]:
            jnt_name = "{}_Jnt".format(control)
            skin_items.append(jnt_name)
            if not pm.objExists(jnt_name):
                pm.select(cl=True)
                jnt = pm.joint(name=jnt_name)
                pm.parent(jnt, control)
                jnt.translate.set([0, 0, 0])
        pm.skinCluster(
            skin_items, name="{}_SC".format(self.mouth_lip_sew_surface))

        sew_ctrl_grp = "MD_{}_LipSew_Ctrl_Grp".format(self.mouth_module)
        if not pm.objExists(sew_ctrl_grp):
            pm.createNode(
                "transform",
                name=sew_ctrl_grp,
                p="MD_{}_Grp".format(self.mouth_module))

        for side in ["LF", "RT"]:
            follicle_name = "{}_Mouth_01_LipSew_Ctrl_Follicle".format(side)
            surface_shape = pm.PyNode(lip_sew_surface).getShape()
            follicle = xd_follicle_node(
                name=follicle_name,
                worldMatrixInput=surface_shape.attr("worldMatrix[0]"),
                surfaceInput=surface_shape.attr("local"),
                outTranslateToParent=True,
                outRotateToParent=True,
                parentNode=sew_ctrl_grp
            )
            pm.PyNode(
                "MD_{}_Scale_Null".format(self.mouth_module)).scale.connect(
                pm.PyNode(follicle).scale)
            pm.PyNode(follicle).getShape().attr("parameterV").set(0.5)

            if side == "LF":
                pm.PyNode(follicle).getShape().attr("parameterU").set(0)
            elif side == "RT":
                pm.PyNode(follicle).getShape().attr("parameterU").set(1.0)

        return True

    def proxy_jaw(self, have_teeth=True):
        jaw_deform_grp = "MD_{}_Jaw_Out_Grp".format(self.mouth_module)
        if not pm.objExists(jaw_deform_grp):
            pm.createNode("transform",
                          name=jaw_deform_grp,
                          p="MD_{}_Deformer_Grp".format(self.mouth_module))
        jaw_root = pm.spaceLocator(name="proxyJawRoot")
        jaw_low = pm.spaceLocator(name="proxyJawLow")
        jaw_up = pm.spaceLocator(name="proxyJawUp")
        jaw_teak = pm.spaceLocator(name="proxyJawTeak")
        jaw_up_loc = pm.spaceLocator(name="proxyJawUpLoc")

        pm.parent(jaw_up, jaw_low, jaw_root)
        pm.parent(jaw_teak, jaw_low)
        pm.parent(jaw_up_loc, jaw_root)

        jaw_up.translateY.set(1.0)

        jaw_teak.translateZ.set(2.0)
        jaw_up_loc.translate.set(0, 1.0, 2.0)

        if have_teeth:
            teeth_up = pm.spaceLocator(name="proxyTeethUp")
            teeth_low = pm.spaceLocator(name="proxyTeethLow")
            pm.parent(teeth_low, jaw_low)
            pm.parent(teeth_up, jaw_up)

            teeth_low.translateZ.set(2.5)
            teeth_up.translateZ.set(2.5)

        return True

    def jaw_deformer_and_control(self):
        """创建jaw的骨骼和控制器"""
        proxy_jaw_root = pm.spaceLocator(name="proxyJawRoot")
        if not pm.objExists(proxy_jaw_root):
            pm.error(u"缺少jaw的代理骨骼")

        self.jaw_deformer_grp()
        self.jaw_control_grp()

        return True

    def jaw_deformer_grp(self):
        jaw_out_grp = "MD_{}_Jaw_Out_Grp".format(self.mouth_module)
        if not pm.objExists(jaw_out_grp):
            pm.createNode(
                "transform",
                name=jaw_out_grp,
                p="MD_{}_Deformer_Grp".format(self.mouth_module))

        low_jnt = "MD_Mouth_01_LowJaw_Jnt"
        low_jnt_grp = jnt_or_control_grp(
            name=low_jnt,
            parent_node=jaw_out_grp,
            have_loc=True
        )
        tweak_jnt_grp = jnt_or_control_grp(
            name="MD_Mouth_01_Jaw_Tweak_Ctrl_Jnt",
            parent_node="MD_Mouth_01_LowJaw_Jnt"
        )
        low_teeth_jnt_grp = jnt_or_control_grp(
            name="MD_Mouth_01_Low_Teeth_Ctrl_Jnt",
            parent_node="MD_Mouth_01_LowJaw_Jnt"
        )

        up_jnt_grp = jnt_or_control_grp(
            name="MD_Mouth_01_UpJaw_Jnt", parent_node=jaw_out_grp)
        up_teeth_jnt_grp = jnt_or_control_grp(
            name="MD_Mouth_01_Up_Teeth_Ctrl_Jnt",
            parent_node="MD_Mouth_01_UpJaw_Jnt"
        )
        up_jaw_loc = pm.spaceLocator(name="MD_Mouth_01_UpJaw_Loc")
        pm.parent(up_jaw_loc, up_jnt_grp)

        # 开始对各个组进行定位
        pm.delete(pm.parentConstraint("proxyJawRoot", jaw_out_grp, mo=False))
        pm.delete(pm.parentConstraint("proxyJawLow", low_jnt_grp, mo=False))
        offset_rotate = pm.PyNode(low_jnt_grp).rotateX.get()
        pm.PyNode(low_jnt).rotateX.set(offset_rotate)
        pm.delete(pm.parentConstraint("proxyJawTeak", tweak_jnt_grp, mo=False))
        pm.delete(
            pm.parentConstraint("proxyTeethLow", low_teeth_jnt_grp, mo=False))
        pm.delete(pm.parentConstraint("proxyJawUp", up_jnt_grp, mo=False))
        pm.delete(
            pm.parentConstraint("proxyTeethUp", up_teeth_jnt_grp, mo=False))
        pm.delete(
            pm.parentConstraint("proxyJawUpLoc", up_jaw_loc, mo=False))

        # 创建null组
        up_null_grp = ctrl_null_grp(
            name="Up_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(
            pm.parentConstraint(
                "Up_{}_Ctrl".format(self.mouth_module), up_null_grp, mo=False))
        low_null_grp = ctrl_null_grp(
            name="Low_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(
            pm.parentConstraint(
                "Low_{}_Ctrl".format(self.mouth_module), low_null_grp,
                mo=False))
        lf_null_grp = chain_ctrl_null_grp(
            name="LF_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(
            pm.parentConstraint(
                "LF_{}_Ctrl".format(self.mouth_module), lf_null_grp, mo=False))
        rt_null_grp = chain_ctrl_null_grp(
            name="RT_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(
            pm.parentConstraint(
                "RT_{}_Ctrl".format(self.mouth_module), rt_null_grp, mo=False))

        return True

    def jaw_control_grp(self):
        jaw_ctrl = "MD_{}_Jaw_Ctrl".format(self.mouth_module)
        if not pm.objExists(jaw_ctrl):
            pm.delete(
                pm.parentConstraint(
                    "proxyJawRoot",
                    jnt_or_control_grp(
                        name=jaw_ctrl,
                        object_type="plane",
                        parent_node="MD_{}_Grp".format(self.mouth_module)),
                    mo=False))

        tweak_ctrl = "MD_{}_Jaw_Tweak_Ctrl".format(self.mouth_module)
        pm.delete(
            pm.parentConstraint(
                "proxyJawTeak",
                jnt_or_control_grp(
                    name=tweak_ctrl,
                    object_type="plane",
                    parent_node=jaw_ctrl),
                mo=False))

        low_teeth_ctrl = "MD_{}_Low_Teeth_Ctrl".format(self.mouth_module)
        pm.delete(
            pm.parentConstraint(
                "proxyTeethLow",
                jnt_or_control_grp(
                    name=low_teeth_ctrl,
                    object_type="plane",
                    parent_node=jaw_ctrl),
                mo=False))

        jaw_move_loc = "M_Jaw_Move_Loc"
        pm.spaceLocator(name=jaw_move_loc)
        pm.parent(jaw_move_loc, jaw_ctrl)
        pm.PyNode(jaw_move_loc).translate.set([0, 0, 5])

        up_teeth_ctrl = "MD_{}_Up_Teeth_Ctrl".format(self.mouth_module)
        pm.delete(
            pm.parentConstraint(
                "proxyTeethUp",
                jnt_or_control_grp(
                    name=up_teeth_ctrl,
                    object_type="plane",
                    parent_node=pm.PyNode(jaw_ctrl).getParent()),
                mo=False))

        jaw_base_loc = "M_Jaw_Base_Loc"
        pm.spaceLocator(name=jaw_base_loc)
        pm.parent(jaw_base_loc, pm.PyNode(jaw_ctrl).getParent())
        pm.PyNode(jaw_base_loc).translate.set([0, 0, 0])

        return True

    def make_jaw_work(self):
        up_jaw_loc = "MD_Mouth_01_UpJaw_Loc"
        low_jaw_loc = "MD_Mouth_01_LowJaw_Loc"
        up_jaw_jnt = "MD_Mouth_01_UpJaw_Jnt"

        jaw_db = "MD_Mouth_01_Jaw_DB"
        if not pm.objExists(jaw_db):
            pm.createNode("distanceBetween", name=jaw_db)

        pm.PyNode(up_jaw_loc).getShape().attr("worldPosition[0]").connect(
            pm.PyNode(jaw_db).attr("point1"))
        pm.PyNode(low_jaw_loc).getShape().attr("worldPosition[0]").connect(
            pm.PyNode(jaw_db).attr("point2"))

        condition_node = "MD_Mouth_01_Jaw_Cond"
        if not pm.objExists(condition_node):
            pm.createNode("condition", name=condition_node)
        pm.PyNode(condition_node).attr("operation").set(2)

        pm.PyNode(jaw_db).attr("distance").connect(
            pm.PyNode(condition_node).attr("firstTerm"))
        pm.PyNode(jaw_db).attr("distance").connect(
            pm.PyNode(condition_node).attr("colorIfFalseR"))
        pm.PyNode(condition_node).attr("secondTerm").set(
            pm.PyNode(jaw_db).attr("distance").get())
        pm.PyNode(condition_node).attr("colorIfTrueR").set(
            pm.PyNode(jaw_db).attr("distance").get())

        jaw_pma = "MD_Mouth_01_Jaw_PMA"
        if not pm.objExists(jaw_pma):
            pm.createNode("plusMinusAverage", name=jaw_pma)
        pm.PyNode(jaw_pma).attr("operation").set(2)
        pm.PyNode(jaw_pma).attr("input1D[0]").set(
            pm.PyNode(jaw_db).attr("distance").get())
        pm.PyNode(condition_node).attr("outColorR").connect(
            pm.PyNode(jaw_pma).attr("input1D[1]"))

        pm.PyNode(jaw_pma).attr("output1D").connect(
            pm.PyNode(up_jaw_jnt).translateY)

        up_teeth_ctrl = "MD_Mouth_01_Up_Teeth_Ctrl"
        up_teeth_jnt = "MD_Mouth_01_Up_Teeth_Ctrl_Jnt"
        pm.PyNode(up_teeth_ctrl).translate.connect(
            pm.PyNode(up_teeth_jnt).translate)
        pm.PyNode(up_teeth_ctrl).rotate.connect(pm.PyNode(up_teeth_jnt).rotate)
        pm.PyNode(up_teeth_ctrl).scale.connect(pm.PyNode(up_teeth_jnt).scale)

        jaw_ctrl = "MD_Mouth_01_Jaw_Ctrl"
        low_jaw_grp = "MD_Mouth_01_LowJaw_Jnt_Grp"
        pm.PyNode(jaw_ctrl).translate.connect(
            pm.PyNode(low_jaw_grp).translate)
        pm.PyNode(jaw_ctrl).rotate.connect(pm.PyNode(low_jaw_grp).rotate)

        tweak_ctrl_jnt = "MD_Mouth_01_Jaw_Tweak_Ctrl_Jnt"
        tweak_ctrl = "MD_Mouth_01_Jaw_Tweak_Ctrl"
        pm.PyNode(tweak_ctrl).translate.connect(
            pm.PyNode(tweak_ctrl_jnt).translate)
        pm.PyNode(tweak_ctrl).rotate.connect(pm.PyNode(tweak_ctrl_jnt).rotate)
        pm.PyNode(tweak_ctrl).scale.connect(pm.PyNode(tweak_ctrl_jnt).scale)

        low_teeth_ctrl_jnt = "MD_Mouth_01_Low_Teeth_Ctrl_Jnt"
        low_teeth_ctrl = "MD_Mouth_01_Low_Teeth_Ctrl"
        pm.PyNode(low_teeth_ctrl).translate.connect(
            pm.PyNode(low_teeth_ctrl_jnt).translate)
        pm.PyNode(low_teeth_ctrl).rotate.connect(
            pm.PyNode(low_teeth_ctrl_jnt).rotate)
        pm.PyNode(low_teeth_ctrl).scale.connect(
            pm.PyNode(low_teeth_ctrl_jnt).scale)

        pm.parentConstraint(up_jaw_jnt, "Up_Mouth_01_Ctrl_Null", mo=False)
        pm.parentConstraint("MD_Mouth_01_LowJaw_Jnt",
                            "Low_Mouth_01_Ctrl_Null", mo=False)

        return True


class FaceCreatorUI(common.Singleton):
    def __init__(self):
        super(FaceCreatorUI, self).__init__()

        self.mouth_module = "Mouth_01"
        self.mouth_creator = MouthCreator()

        self.rig_root_node = ""  # group "World"

        self.up_base_curve = ""
        self.low_base_curve = ""
        self.up_tweak_surface = ""
        self.low_tweak_surface = ""
        self.up_out_curve = ""
        self.low_out_curve = ""

        self.mouth_surface = ""
        self.mouth_lip_sew_surface = ""

        self.show_window()

    def show_window(self):
        self.initialize()

        if pm.window("xdFaceCreatorWnd", exists=True):
            pm.deleteUI("xdFaceCreatorWnd")

        pm.window("xdFaceCreatorWnd",
                  title="Biped Creator",
                  mb=True,
                  cc=lambda *args: self._closed_window_cmd())

        self.menu_bar()

        root_layout = pm.scrollLayout(hst=16, vst=16, cr=True)

        tab_layout = pm.tabLayout(p=root_layout)

        pre_tab = pm.columnLayout(adj=1, p=tab_layout)
        self.rig_pre_frame(pre_tab)
        pm.setParent(pre_tab)

        eye_ear_tab = pm.columnLayout(adj=1, p=tab_layout)
        pm.setParent(eye_ear_tab)

        brow_tab = pm.columnLayout(adj=1, p=tab_layout)
        pm.setParent(brow_tab)

        nose_tab = pm.columnLayout(adj=1, p=tab_layout)
        pm.setParent(brow_tab)

        mouth_tab = pm.columnLayout(adj=1, p=tab_layout)
        self.mouth_module_frame(mouth_tab)
        pm.setParent(mouth_tab)

        face_tab = pm.columnLayout(adj=1, p=tab_layout)
        pm.setParent(brow_tab)

        cmds.tabLayout(
            tab_layout, edit=True,
            tabLabel=(
                (pre_tab, 'Pre'),
                (eye_ear_tab, 'Eye&Nose'),
                (brow_tab, 'Brow'),
                (nose_tab, 'Nose'),
                (mouth_tab, 'Mouth'),
                (face_tab, 'Face'),
            )
        )
        pm.setParent(tab_layout)
        pm.showWindow("xdFaceCreatorWnd")

    def _closed_window_cmd(self):
        pm.optionVar(
            sv=('mouth_01_Up_Base_Curve',
                pm.textFieldButtonGrp(
                    "xdMouthCreatorUpBaseCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Low_Base_Curve',
                pm.textFieldButtonGrp(
                    "xdMouthCreatorLowBaseCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Up_Tweak_Surface',
                pm.textFieldButtonGrp(
                    "xdMouthCreatorUpTweakSurfaceField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Low_Tweak_Surface',
                pm.textFieldButtonGrp(
                    "xdMouthCreatorLowTweakSurfaceField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Up_Out_Curve',
                pm.textFieldButtonGrp(
                    "xdMouthCreatorUpOutCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Low_Out_Curve',
                pm.textFieldButtonGrp(
                    "xdMouthCreatorLowOutCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_mouth_surface',
                pm.textFieldButtonGrp(
                    "xdMouthCreatorMouthSurfaceField", q=True, text=True)))

        pm.optionVar(
            sv=('mouth_01_lip_sew_surface',
                pm.textFieldButtonGrp(
                    "xdMouthCreatorMouthLipSewSurfaceField",
                    q=True, text=True)))

    def initialize(self):
        u"""初始化数据

        从MAYA的保存的属性数据里面获取一些值

        :return:
        """
        if pm.optionVar(q='mouth_01_Up_Base_Curve'):
            self.up_base_curve = pm.optionVar(q='mouth_01_Up_Base_Curve')
        if pm.optionVar(q='mouth_01_Low_Base_Curve'):
            self.low_base_curve = pm.optionVar(q='mouth_01_Low_Base_Curve')
        if pm.optionVar(q='mouth_01_Up_Tweak_Surface'):
            self.up_tweak_surface = pm.optionVar(q='mouth_01_Up_Tweak_Surface')
        if pm.optionVar(q='mouth_01_Low_Tweak_Surface'):
            self.low_tweak_surface = pm.optionVar(
                q='mouth_01_Low_Tweak_Surface')
        if pm.optionVar(q='mouth_01_Up_Out_Curve'):
            self.up_out_curve = pm.optionVar(q='mouth_01_Up_Out_Curve')
        if pm.optionVar(q='mouth_01_Low_Out_Curve'):
            self.low_out_curve = pm.optionVar(q='mouth_01_Low_Out_Curve')
        if pm.optionVar(q='mouth_01_mouth_surface'):
            self.mouth_surface = pm.optionVar(q='mouth_01_mouth_surface')
        if pm.optionVar(q='mouth_01_lip_sew_surface'):
            self.mouth_lip_sew_surface = pm.optionVar(
                q='mouth_01_lip_sew_surface')
        return

    def menu_bar(self):
        u"""菜单栏"""
        menu_component = pm.menu(label=u"Component", tearOff=False)
        pm.menuItem(
            p=menu_component,
            label=u"Base loc",
            c=lambda *args: self.build_base_loc())

        menu_template = pm.menu(label="Module", tearOff=False)
        pm.menuItem(
            p=menu_template,
            label=u"Mouth surface",
            c=lambda *args: self.build_base_loc())
        pm.menuItem(
            p=menu_template,
            label=u"Mouth tweak surface",
            c=lambda *args: self.build_base_loc())
        # submenu_module_base = pm.menuItem(
        #     subMenu=True, label="Base", p=menu_module)
        # pm.menuItem(
        #     label="Root",
        #     p=submenu_module_base,
        #     c=lambda *args: self.create_module_root())
        # submenu_module_body = pm.menuItem(
        #     subMenu=True, label="Body", p=menu_module)
        # pm.menuItem(
        #     label="Head",
        #     p=submenu_module_body,
        #     c=lambda *args: self.create_module_head())

    def rig_pre_frame(self, parent):
        layout = pm.frameLayout(p=parent, lv=False, mw=10, mh=5, bgs=True)
        pm.button(
            "xdMouthCreatorNewRigBtn",
            label=u"New",
            c=lambda *args: self.new_rig_structure())
        pm.setParent(layout)

        return layout

    def mouth_module_frame(self, parent):
        frame = pm.frameLayout(
            p=parent, label=u"Preparatory Work", mh=5, mw=10)

        curve_grp_frame = pm.frameLayout(
            p=frame, label=u"Mouth Curve Grp", mh=5, mw=10, bgs=True)
        pm.textFieldButtonGrp(
            "xdMouthCreatorUpBaseCurveField",
            label=u"Up base curve",
            bl=u"Get Object",
            adj=2,
            text=self.up_base_curve,
            bc=lambda *args: self.get_object_in_field(
                "xdMouthCreatorUpBaseCurveField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLowBaseCurveField",
            label=u"Low base curve",
            bl=u"Get Object",
            adj=2,
            text=self.low_base_curve,
            bc=lambda *args: self.get_object_in_field(
                "xdMouthCreatorLowBaseCurveField"))

        pm.textFieldButtonGrp(
            "xdMouthCreatorUpTweakSurfaceField",
            label=u"Up tweak surface",
            bl=u"Get Object",
            adj=2,
            text=self.up_tweak_surface,
            bc=lambda *args: self.get_object_in_field(
                "xdMouthCreatorUpTweakSurfaceField"))

        pm.textFieldButtonGrp(
            "xdMouthCreatorLowTweakSurfaceField",
            label=u"Low tweak surface",
            bl=u"Get Object",
            adj=2,
            text=self.low_tweak_surface,
            bc=lambda *args: self.get_object_in_field(
                "xdMouthCreatorLowTweakSurfaceField"))

        pm.setParent(curve_grp_frame)

        out_curve_grp_frame = pm.frameLayout(
            p=frame, label=u"Out Curve Grp", mh=5, mw=10, bgs=True)
        pm.textFieldButtonGrp(
            "xdMouthCreatorUpOutCurveField",
            label=u"Up out curve",
            bl=u"Get Object",
            adj=2,
            text=self.up_out_curve,
            bc=lambda *args: self.get_object_in_field(
                "xdMouthCreatorUpOutCurveField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLowOutCurveField",
            label=u"Low out curve",
            bl=u"Get Object",
            adj=2,
            text=self.low_out_curve,
            bc=lambda *args: self.get_object_in_field(
                "xdMouthCreatorLowOutCurveField"))
        pm.setParent(out_curve_grp_frame)

        pm.separator(h=5, style="in")

        pm.textFieldButtonGrp(
            "xdMouthCreatorMouthSurfaceField",
            label="mouth surface",
            adj=2,
            text=self.mouth_surface,
            bl="Get Object",
            bc=lambda *args: self.import_mouth_surface(
                "mouth_surface",
                "xdMouthCreatorMouthSurfaceField"))

        pm.textFieldButtonGrp(
            "xdMouthCreatorMouthLipSewSurfaceField",
            label="lip sew surface",
            adj=2,
            text=self.mouth_lip_sew_surface,
            bl="Get Object",
            bc=lambda *args: self.import_mouth_surface(
                "mouth_lip_sew_surface",
                "xdMouthCreatorMouthLipSewSurfaceField",
                rename="Mouth_01_LipSew"))

        pm.separator(h=5, style="in")
        pm.intFieldGrp(
            "xdMouthCreatorTweakSegmentField",
            label=u"tweak segment",
            numberOfFields=1,
            value1=6)

        jaw_frame = pm.frameLayout(
            p=frame, label="Jaw Control", mh=5, mw=10, bgs=True)
        pm.checkBoxGrp(label=u"Mouth cavity",
                       numberOfCheckBoxes=1,
                       label1='Teeth',
                       value1=True)
        pm.button(
            "xdMouthCreatorAddProxyJawBtn",
            label=u"Add proxy jaw",
            c=lambda *args: self.proxy_jaw())

        pm.setParent(jaw_frame)

        control_frame = pm.frameLayout(
            p=frame, label="Location Controls", mh=5, mw=10, bgs=True)
        pm.button(
            label=u"Test Command(make_jaw_work)",
            c=lambda *args: self.test_command())
        pm.setParent(control_frame)

        pm.button(
            "xdMouthCreatorBuildMouthModuleBtn",
            label=u"Build Module",
            c=lambda *args: self.build_mouth_module())

        pm.setParent(frame)
        return frame

    @staticmethod
    def get_object_in_field(field):
        sel_object = pm.ls(sl=True)[0]
        pm.textFieldButtonGrp(field, e=True, text=sel_object)
        return

    def import_mouth_surface(self, template="", field="", rename="Mouth_01"):
        template_file = path(template_dir).joinpath("{}.mb".format(template))
        import_object = get_imported_object(template_file)
        import_object = pm.rename(
            import_object, "MD_{}_Surface".format(rename))

        # print("import_object: {}".format(pm.PyNode(import_object).name()))

        deformer_grp = "MD_{}_Deformer_Grp".format(self.mouth_module)
        if pm.objExists(deformer_grp):
            pm.parent(import_object, deformer_grp)

        # self.mouth_surface = import_object
        pm.textFieldButtonGrp(field, e=True, text=import_object)

        return True

    def import_tweak_surface(self, location, field):
        template_file = path(template_dir).joinpath("mouth_tweak_surface.mb")
        # import_object = get_imported_object(template_file)
        import_object = pm.rename(
            get_imported_object(template_file),
            "MD_{}_{}_Tweak_Surface".format(self.mouth_module, location))
        if pm.objExists("MD_Mouth_01_Curve_Grp"):
            pm.parent(import_object, "MD_Mouth_01_Curve_Grp")
        pm.textFieldButtonGrp(field, e=True, text=import_object)

        return True

    def new_rig_structure(self):
        if not pm.objExists("World"):
            self.rig_root_node = pm.createNode("transform", name="World")

            deformer_grp = pm.createNode("transform", name="Deformer_Grp")
            pm.parent(deformer_grp, self.rig_root_node)
            master_ctrl = pm.createNode("transform", name="Master_Ctrl")
            pm.parent(master_ctrl, self.rig_root_node)

            pm.button("xdMouthCreatorNewRigBtn", e=True, en=False)
        else:
            pm.confirmDialog(
                title=u'错误提示',
                icn="warning",
                message=u"场景中已存在绑定\n"
                        u"提示：开始绑定前需要检查文件，确保场景中没有存在绑定结构")
        return

    def build_mouth_module(self):
        self.before_build()

        self.mouth_creator.master_control()
        self.mouth_creator.base_controls()

        self.mouth_creator.follicle_on_mouth_surface()
        self.mouth_creator.base_follicle_grp()

        self.mouth_creator.skin_base_curve()
        self.mouth_creator.corner_ctrl_connect_cpos_loc()
        self.mouth_creator.lip_ctrl_connect_ctrl_jnt()

        self.mouth_creator.follicle_on_tweak_surface()
        self.mouth_creator.tweak_jnt_grp()
        self.mouth_creator.tweak_ctrl_grp()

        self.mouth_creator.lip_sew_and_follicle()
        self.mouth_creator.skin_out_curve()

        self.mouth_creator.use_dm_node_to_tweak_ctrl_parent_and_jnt_02_grp()
        self.mouth_creator.skin_tweak_surface()

        self.mouth_creator.lip_sew_ctrl_drive_follicle_shape()

        self.mouth_creator.make_bind_jnt_scale_work()

        return

    def build_base_loc(self):
        if pm.window("xdBaseLocCreatorWnd", ex=True):
            pm.deleteUI("xdBaseLocCreatorWnd")
        pm.window("xdBaseLocCreatorWnd", title="Base Loc Creator")
        pm.showWindow("xdBaseLocCreatorWnd")

    def before_build(self):
        u"""mouth creator执行创建命令之前，执行此方法，初始化所有的变量"""
        self.up_base_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorUpBaseCurveField", q=True, text=True)
        self.low_base_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLowBaseCurveField", q=True, text=True)
        self.mouth_creator.up_base_curve = self.up_base_curve
        self.mouth_creator.low_base_curve = self.low_base_curve

        self.up_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorUpOutCurveField", q=True, text=True)
        self.low_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLowOutCurveField", q=True, text=True)
        self.mouth_creator.up_out_curve = self.up_out_curve
        self.mouth_creator.low_out_curve = self.low_out_curve

        self.up_tweak_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorUpTweakSurfaceField", q=True, text=True)
        self.low_tweak_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorLowTweakSurfaceField", q=True, text=True)
        self.mouth_creator.up_tweak_surface = self.up_tweak_surface
        self.mouth_creator.low_tweak_surface = self.low_tweak_surface

        self.mouth_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorMouthSurfaceField", q=True, text=True)
        self.mouth_creator.mouth_surface = self.mouth_surface

        self.mouth_lip_sew_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorMouthLipSewSurfaceField", q=True, text=True)
        self.mouth_creator.mouth_lip_sew_surface = self.mouth_lip_sew_surface

        return

    def test_command(self):
        u"""创建嘴巴模块的控件

        :return:
        """

        self.before_build()

        # self.mouth_creator.jaw_deformer_and_control()
        self.mouth_creator.make_jaw_work()
        # self.mouth_creator.static_corner_when_master_ctrl_move_up()
        return True

    def proxy_jaw(self):
        self.before_build()
        if pm.objExists("proxyJawRoot"):
            pm.error(u"代理Jaw已经创建了")
        if self.mouth_creator.proxy_jaw():
            pm.button("xdMouthCreatorAddProxyJawBtn", e=True, en=False)


def open_creator_ui():
    FaceCreatorUI()
