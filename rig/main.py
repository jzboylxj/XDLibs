#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/10/12 23:26
# @Author  : Li XiaoJun
# @Site    :
# @File    : main.py
from imp import reload
from pymel import core as pm
from animation import common
import maya.cmds as cmds
from pymel.util import path
from rig.names import template_dir

reload(common)


def mouth_bind_jnt_grp_translate_bc_connect(bind_jnt_grp="", old_min=0.0, old_max=0.0):
    lf_lip_sew_ctrl_follicle_shape = pm.PyNode(
        "LF_Mouth_01_LipSew_Ctrl_FollicleShape")
    rt_lip_sew_ctrl_follicle_shape = pm.PyNode(
        "RT_Mouth_01_LipSew_Ctrl_FollicleShape")

    set_range = pm.createNode(
        "setRange", name=bind_jnt_grp.replace("_Grp", "_LipSew_SR"))
    lf_lip_sew_ctrl_follicle_shape.attr("parameterU").connect(
        "{}.value.valueX".format(set_range.name()))
    rt_lip_sew_ctrl_follicle_shape.attr("parameterU").connect(
        "{}.value.valueY".format(set_range.name()))
    set_range.attr("oldMinX").set(old_min)
    set_range.attr("oldMinY").set(old_min)
    set_range.attr("oldMaxX").set(old_max)
    set_range.attr("oldMaxY").set(old_max)

    adl_node = pm.createNode(
        "addDoubleLinear", name=bind_jnt_grp.replace("_Grp", "_Jnt_ADL"))
    set_range.attr("outValueX").connect(adl_node.attr("input1"))
    set_range.attr("outValueY").connect(adl_node.attr("input2"))

    cmp_node = pm.createNode(
        "clamp", name=bind_jnt_grp.replace("_Grp", "_LipSew_CMP"))
    adl_node.attr("output").connect(cmp_node.attr("inputR"))

    pma_node = pm.createNode(
        "plusMinusAverage", name=bind_jnt_grp.replace("_Grp", "_LipSew_PMA"))
    cmp_node.attr("outputR").connect(pma_node.attr("input1D[1]"))
    pma_node.attr("input1D[0]").set(1.0)
    pma_node.attr("output1D").connect("{}.blender".format(
        bind_jnt_grp.replace("_Grp", "_Translate_BC")))
    return


def connect_targets_spec_attr(source="", source_attr="", targets=None, target_attrs=None):
    if target_attrs is None:
        target_attrs = []
    if targets is None:
        targets = []

    for target in targets:
        for target_attr in target_attrs:
            pm.PyNode(source).attr(source_attr).connect("{}.{}".format(target, target_attr))
    return


def follicle_shape_out_for_parent(follicle_shape):
    u"""将毛囊形节点的两个属性：输出平移和输出旋转，
    连接到它的父节点（位移节点）的平移和旋转属性上

    :param follicle_shape: 毛囊形节点
    :return: None
    """
    parent = pm.PyNode(follicle_shape).getParent()
    pm.PyNode(follicle_shape).attr("outTranslate").connect(parent.translate)
    pm.PyNode(follicle_shape).attr("outRotate").connect(parent.rotate)
    return


def check_constraint(target, source):
    u"""检查约束状态

    :param target: 被约束目标
    :param source: 约束目标
    :return: bool True or False
    """
    target_inputs = list(set(pm.PyNode(target).inputs()))
    if target_inputs:
        for target_input in target_inputs:
            if target_input.type() in ["parentConstraint", "pointConstraint", "scaleConstraint", "aimConstraint",
                                       "orientConstraint"]:
                if target in list(set(target_input.inputs())) and source in list(set(target_input.inputs())):
                    return True
                else:
                    return False
    else:
        return False


def make_follicle_work_on_surface(surface, follicle, param_u=0.0, param_v=0.0):
    u"""让毛囊在曲面上能够起作用（工作）

    :param surface: 曲面
    :param follicle: 毛囊
    :param param_u: 参数 U
    :param param_v: 参数 V
    :return: None
    """
    surface_shape = pm.PyNode(surface).getShape()
    follicle_shape = pm.PyNode(follicle).getShape()
    surface_shape.attr("local").connect(follicle_shape.attr("inputSurface"))
    surface_shape.attr("worldMatrix[0]").connect(follicle_shape.attr("inputWorldMatrix"))
    follicle_shape.attr("parameterU").set(param_u)
    follicle_shape.attr("parameterV").set(param_v)
    return


def imported_object(file_path):
    u"""返回导入到场景里面的新对象

    :return: list of new object
    """
    imported = cmds.file(file_path, ignoreVersion=True, i=True, type="mayaBinary", rnn=True)
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


def yellow_component(name="", shape_type="", translate=(0, 0, 0), parent_node=None, have_loc=False, have_jnt=False):
    u"""黄色的基础控制器组件

    黄色的控制器一般用来作为模块的细节控制器或次级控制器

    :param name: 名字
    :param shape_type: 控制器的节点类型，例如曲面，locator等
    :param translate: 位移
    :param parent_node: 父节点
    :param have_loc: 在父节点下是否创建loc
    :return: grp
    """
    if shape_type == "nurbsPlane":
        pm.nurbsPlane(name=name, p=[0, 0, 0], ax=[0, 0, 1], w=1, lr=1, d=3, u=1, v=1, ch=1)
    if shape_type == "locator":
        pm.spaceLocator(name=name)
    if shape_type == "joint":
        pm.select(cl=True)
        pm.joint(name=name)
    if shape_type == "sphere":
        pm.sphere(name=name, p=[0, 0, 0], ax=[0, 1, 0], ssw=0, esw=360, r=0.3, d=3, ut=0, tol=0.01, s=4, nsp=2, ch=1)
    if shape_type == "cone":
        pm.cone(name=name, p=[0, 0, 0], ax=[-1, 0, 0], ssw=0, esw=360, r=0.45, hr=2, d=1, ut=0, tol=0.01, s=4, nsp=1,
                ch=0)

    pm.parent(
        pm.createNode("transform", name="{}_02_Grp".format(name)),
        pm.createNode("transform", name="{}_Grp".format(name))
    )

    pm.parent(name, "{}_02_Grp".format(name))

    if have_loc:
        pm.parent(pm.spaceLocator(name="{}_Roll_Loc".format(name)), "{}_Grp".format(name))

    if have_jnt:
        pm.select(cl=True)
        jnt = pm.joint(name="{}_Jnt".format(name))
        pm.parent(jnt, name)

    pm.PyNode("{}_Grp".format(name)).translate.set(translate)

    if parent_node is not None:
        if pm.objExists(parent_node):
            pm.parent("{}_Grp".format(name), parent_node)

    return "{}_Grp".format(name)


def cyan_control(name="", shape_type="sphere", translate=(0, 0, 0), parent_node=None):
    u"""蓝色的基础控制器组件

    蓝色的控制器一般用来作为模块的主控制器

    :return:
    """
    base_ctrl = None
    if shape_type == "sphere":
        base_ctrl = pm.sphere(name=name, p=[0, 0, 0], ax=[0, 1, 0], ssw=0, esw=360, r=1, d=1, ut=0, tol=0.01, s=4,
                              nsp=2, ch=0)
    pm.parent(base_ctrl, pm.createNode("transform", name="{}_Grp".format(name)))

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


def xd_follicle_node(name, worldMatrixInput=None, surfaceInput=None, paramUInput=None, paramVInput=None,
                     outTranslateToParent=True, outRotateToParent=True, parentNode=None):
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
        pm.connectAttr(worldMatrixInput, follicle.getShape().attr("inputWorldMatrix"))

    if surfaceInput is not None:
        pm.connectAttr(surfaceInput, follicle.getShape().attr("inputSurface"))

    if paramUInput is not None:
        pm.connectAttr(paramUInput, follicle.getShape().attr("parameterU"))

    if paramVInput is not None:
        pm.connectAttr(paramVInput, follicle.getShape().attr("parameterV"))

    if outTranslateToParent:
        pm.PyNode(follicle).getShape().attr("outTranslate").connect(pm.PyNode(follicle).translate)

    if outRotateToParent:
        pm.PyNode(follicle).getShape().attr("outRotate").connect(pm.PyNode(follicle).rotate)

    if parentNode is not None:
        if not pm.objExists(parentNode):
            pm.createNode("transform", name=parentNode)

        pm.parent(follicle, parentNode)

    return follicle


def jnt_or_control_grp(name, object_type="joint", parent_node=None, have_loc=False, have_jnt=False):
    u"""骨骼组或控制器组

    :param name:
    :param object_type: 可选项：joint,plane,tours,locator,sphere,cylinder
    :param parent_node:
    :param have_loc:
    :return: grp
    """
    pm.select(cl=True)

    if object_type == "joint":
        pm.joint(name=name),
    if object_type == "plane":
        pm.nurbsPlane(name=name, p=[0, 0, 0], ax=[0, 0, 1], w=1, lr=0.6, d=1, u=1, v=1, ch=0),
    if object_type == "tours":
        pm.torus(name=name, p=[0, 0, 0], ax=[0, 0, 1],
                 ssw=0, esw=360, msw=360, r=1, hr=0.5, d=3, ut=0, tol=0.01, s=8, nsp=4, ch=1),
    if object_type == "locator":
        pm.spaceLocator(name=name)
    if object_type == "sphere":
        pm.sphere(name=name, p=[0, 0, 0], ax=[0, 1, 0], ssw=0, esw=360, r=1, d=3, ut=0, tol=0.01, s=4, nsp=2, ch=1)
    if object_type == "cylinder":
        pm.cylinder(name=name, p=[0, 0, 0], ax=[0, 0, 1], ssw=0, esw=360, r=1, hr=2, d=3, ut=0, tol=0.01, s=8, nsp=1,
                    ch=1)

    pm.parent(name, pm.createNode("transform", name="{}_Grp".format(name)))

    if have_loc:
        loc = pm.spaceLocator(name=name.replace('_Jnt', "_Loc"))
        pm.parent(loc, name)

    if have_jnt:
        pm.select(cl=True)
        pm.joint(name="{}_Jnt".format(name))
        pm.parent("{}_Jnt".format(name), name)

    if parent_node is not None:
        pm.parent("{}_Grp".format(name), parent_node)
        pm.PyNode("{}_Grp".format(name)).translate.set([0, 0, 0])
        pm.PyNode("{}_Grp".format(name)).rotate.set([0, 0, 0])
    return pm.PyNode("{}_Grp".format(name))


def control_grp_have_joint(name, object_type="plane", parent_node=None):
    u"""包含子骨骼的控制器组

    :param name: 控制器名
    :param object_type: 控制器的样式
    :param parent_node: 父节点
    :return: 控制器组
    """
    grp = pm.createNode("transform", name="{}_Grp".format(name))
    if object_type == "plane":
        pm.parent(pm.nurbsPlane(name=name, p=[0, 0, 0], ax=[0, 0, 1], w=1, lr=1, d=1, u=1, v=1, ch=0), grp)
    pm.select(cl=True)
    jnt = pm.joint(name="{}_Jnt".format(name))
    pm.parent(jnt, name)
    if parent_node is not None:
        pm.parent(grp, parent_node)
        grp.translate.set([0, 0, 0])
        grp.rotate.set([0, 0, 0])
        grp.scale.set([1, 1, 1])
    return grp


def custom_show_channel(target, attr_list=None):
    u"""自定义通道栏里面的属性，

    :param target:
    :param attr_list:
    :return:
    """
    if attr_list is None:
        attr_list = []
    attrs_in_cb = pm.listAttr(pm.PyNode(target), k=True)
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
    u"""子节点包含3个空节点的组

    :param name:
    :param segment:
    :param parent_node:
    :return: null grp
    """
    null = pm.createNode("transform", name=name)
    null_grp = pm.createNode("transform", name="{}_Grp".format(name))
    pm.parent(null, null_grp)

    for index in range(1, segment):
        null_seg = pm.createNode("transform", name="{}_{}_Grp".format(name, "{0:02d}".format(index + 1)))
        if index == 1:
            pm.parent(null_seg, null_grp)
        else:
            pm.parent(null_seg, "{}_{}_Grp".format(name, "{0:02d}".format(index)))

    if parent_node is not None:
        pm.parent(null_grp, parent_node)
        null_grp.translate.set([0, 0, 0])

    return null_grp


def symmetry_surface(source, target):
    u"""对称surface

    :param source:
    :param target:
    :return:
    """
    num_u = pm.PyNode(source).getShape().attr("degreeU").get() + pm.PyNode(source).getShape().attr("spansU").get()
    num_v = pm.PyNode(source).getShape().attr("degreeV").get() + pm.PyNode(source).getShape().attr("spansV").get()

    for index_u in range(0, num_u):
        for index_v in range(0, num_v):
            source_position = pm.pointPosition('{}.cv[{}][{}]'.format(source, index_u, index_v), w=True)
            pm.move(source_position[0] * -1, source_position[1], source_position[2],
                    pm.PyNode("{}.cv[{}][{}]".format(target, index_u, index_v)))
    return True


def drag_to_group_and_field(target, field="", group=None):
    pm.textFieldButtonGrp(field, e=True, text=target)
    if group is not None:
        pm.parent(target, group)
    return


def dm_node(node_name, matrix_input="", translate_output="", rotate_output=""):
    u"""decomposeMatrix节点

    :param node_name: 节点名字
    :param matrix_input: 输入矩阵的属性
    :param translate_output: output_translate输出的属性
    :param rotate_output: out_rotate输出的属性
    :return: dm_node
    """
    dm_node = pm.createNode("decomposeMatrix", name=node_name)
    pm.Attribute(matrix_input).connect(dm_node.attr("inputMatrix"), f=True)
    dm_node.attr("outputTranslate").connect(translate_output)
    dm_node.attr("outputRotate").connect(rotate_output)
    return dm_node


def mp_node(node_name, geometry_path_input="", all_coordinates_output=""):
    u"""motion path节点

    :param node_name: 节点名字
    :param geometry_path_input: 连接geometryPath属性的外部属性
    :param all_coordinates_output: allCoordinates属性输出的外部属性
    :return: mp_node
    """
    mp_node = pm.createNode("motionPath", name=node_name)
    mp_node.attr("uValue").set(0)

    pm.Attribute(geometry_path_input).connect(mp_node.attr('geometryPath'))
    pm.PyNode(mp_node).attr("allCoordinates").connect(all_coordinates_output)
    return mp_node


class Creator(common.Singleton):

    def __init__(self):
        super(Creator, self).__init__()

        self.module_name = ""

    def proxy(self):
        pass

    def build_module(self):
        pass


class NeckEarCreator(Creator):
    def __init__(self):
        super(NeckEarCreator, self).__init__()

        self.module_name = "Neck_01"

    def proxy(self):
        if not pm.objExists("Proxy_Grp"):
            pm.createNode("transform", name="Proxy_Grp")

        if pm.objExists("Proxy_neck_head_Grp"):
            pm.error(u"场景中已经存在代理对象")

        pm.createNode("transform", name="Proxy_neck_head_Grp", p="Proxy_Grp")

        pm.parent(pm.spaceLocator(name="proxyHeadLoc"), "Proxy_neck_head_Grp")

        for side in ["LF", "RT"]:
            pm.parent(pm.spaceLocator(name="proxy{}EarLoc".format(side)), "proxyHeadLoc")
            if side == "LF":
                pm.PyNode("proxy{}EarLoc".format(side)).translate.set([5, 2, 0])
            else:
                pm.PyNode("proxy{}EarLoc".format(side)).translate.set([-5, 2, 0])

        return True

    def build_module(self):
        neck_ctrl_group = "MD_{}_Grp".format(self.module_name)
        if not pm.objExists(neck_ctrl_group):
            pm.createNode("transform", name=neck_ctrl_group, p="Master_Ctrl")

        head_ctrl = "MD_{}_Head_Ctrl".format(self.module_name)
        head_ctrl_grp = jnt_or_control_grp(
            name=head_ctrl, object_type="tours", parent_node=neck_ctrl_group, have_jnt=True)
        if not pm.objExists("proxyHeadLoc"):
            pm.error(u"缺少代理物体")
        pm.delete(pm.pointConstraint("proxyHeadLoc", head_ctrl_grp, mo=False))

        for side in ["LF", "RT"]:
            ear_fk_ctrl = "{}_Ear_01_01_FK_Ctrl".format(side)
            ear_fk_ctrl_grp = jnt_or_control_grp(
                name=ear_fk_ctrl, object_type="cylinder", parent_node=head_ctrl, have_jnt=True)
            pm.delete(pm.parentConstraint("proxy{}EarLoc".format(side), ear_fk_ctrl_grp, mo=False))

        return


class EyeCreator(Creator):
    def __init__(self):
        super(EyeCreator, self).__init__()

        self.module_name = "Eye_01"

        self.left_up_master_curve = ""
        self.left_low_master_curve = ""
        self.left_up_blink_curve = ""
        self.left_low_blink_curve = ""
        self.left_up_out_curve = ""
        self.left_low_out_curve = ""
        self.left_up_tweak_curve = ""
        self.left_low_tweak_curve = ""
        self.left_up_freshy_curve = ""
        self.left_low_freshy_curve = ""
        self.left_up_shape_surface = ""
        self.left_low_shape_surface = ""

        self.right_up_master_curve = ""
        self.right_low_master_curve = ""
        self.right_up_blink_curve = ""
        self.right_low_blink_curve = ""
        self.right_up_out_curve = ""
        self.right_low_out_curve = ""
        self.right_up_tweak_curve = ""
        self.right_low_tweak_curve = ""
        self.right_up_freshy_curve = ""
        self.right_low_freshy_curve = ""
        self.right_up_shape_surface = ""
        self.right_low_shape_surface = ""

        self.left_eye_geo = ""
        self.right_eye_geo = ""
        self.left_eye_proxy = ""
        self.right_eye_proxy = ""

        self.left_master_control = ""
        self.right_master_control = ""

    def init_structure(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            deformer_group = "{}_Deformer_Grp".format(prefix)
            if not pm.objExists(deformer_group):
                pm.createNode("transform", name=deformer_group, p="Deformer_Grp")

            guid_curve_grp = "{}_Curve_Grp".format(prefix)
            if not pm.objExists(guid_curve_grp):
                pm.createNode("transform", name=guid_curve_grp, p=deformer_group)

            control_group = "{}_Grp".format(prefix)
            if not pm.objExists(control_group):
                pm.createNode("transform", name=control_group, p="Head_01_Grp")

        return True

    def build_module(self):
        self.init_structure()
        self.build_base_ctrl_group()
        self.build_base_loc_group()
        self.build_base_jnt_group()
        self.build_bind_loc_group()
        self.build_bind_jnt_group()
        self.skin_out_curve()
        self.tweak_ctrl_group()
        self.make_blink_work()
        self.skin_master_curve()
        self.make_master_ctrl_work()
        self.build_shape_ctrl_group()
        self.build_shape_jnt_group()
        self.build_eyeball_ctrl_group()
        self.build_aim_ctrl_group()

    def build_base_ctrl_group(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            master_ctrl = "{}_Master_Ctrl".format(prefix)
            if not pm.objExists(master_ctrl):
                pm.error(u"场景中缺少{}".format(master_ctrl))

            base_ctrl_group = "{}_Base_Ctrl_Grp".format(prefix)
            if not pm.objExists(base_ctrl_group):
                pm.createNode("transform", name=base_ctrl_group)
                pm.parent(base_ctrl_group, "{}_Master_Ctrl_Grp".format(prefix))

            for item in ["Up", "Low", "Inner", "Outer"]:
                if item == "Low":
                    out_curve = "{}_Low_Out_Curve".format(prefix)
                else:
                    out_curve = "{}_Up_Out_Curve".format(prefix)

                u_value = 0
                if item == "Outer":
                    u_value = 1.0
                elif item == "Inner":
                    u_value = 0.0
                elif item == "Low":
                    u_value = 0.5
                elif item == "Up":
                    u_value = 0.5

                temp_loc_name = "{}_{}_temp_Loc".format(side, item)
                temp_loc = pm.spaceLocator(name=temp_loc_name)
                temp_mp_name = "{}_{}_temp_MP".format(side, item)
                temp_mp = mp_node(node_name=temp_mp_name,
                                  geometry_path_input=pm.PyNode(out_curve).getShape().attr("worldSpace[0]"),
                                  all_coordinates_output=pm.PyNode(temp_loc).translate)
                pm.PyNode(temp_mp).rotateX.connect(pm.PyNode(temp_loc).rotateX)
                pm.PyNode(temp_mp).rotateY.connect(pm.PyNode(temp_loc).rotateY)
                pm.PyNode(temp_mp).rotateZ.connect(pm.PyNode(temp_loc).rotateZ)

                if side == "LF":
                    pm.PyNode(temp_mp).attr("uValue").set(u_value)
                    pm.disconnectAttr(
                        pm.PyNode(out_curve).getShape().attr("worldSpace[0]"),
                        pm.PyNode(temp_mp).attr("geometryPath"))
                    pm.delete(temp_mp_name)
                    if item == "Inner":
                        pm.PyNode(temp_loc).rotateX.set(0)
                        # current_rotate = pm.PyNode(temp_loc).rotateY.get()
                        # pm.PyNode(temp_loc).rotateY.set(current_rotate+90)
                        pm.PyNode(temp_loc).rotateZ.set(0)
                    elif item == "Outer":
                        pm.PyNode(temp_loc).rotateX.set(0)
                        current_rotate = pm.PyNode(temp_loc).rotateY.get()
                        pm.PyNode(temp_loc).rotateY.set(current_rotate * -1)
                        pm.PyNode(temp_loc).rotateZ.set(0)
                    else:
                        pm.PyNode(temp_loc).rotateX.set(0)
                        current_rotate = pm.PyNode(temp_loc).rotateY.get()
                        pm.PyNode(temp_loc).rotateY.set(current_rotate + 90)
                        pm.PyNode(temp_loc).rotateZ.set(0)

                else:
                    pm.PyNode(temp_mp).attr("uValue").set(u_value)
                    pm.disconnectAttr(
                        pm.PyNode(out_curve).getShape().attr("worldSpace[0]"),
                        pm.PyNode(temp_mp).attr("geometryPath"))
                    pm.delete(temp_mp_name)
                    if item == "Inner":
                        pm.PyNode(temp_loc).rotateX.set(0)
                        current_rotate = pm.PyNode(temp_loc).rotateY.get()
                        pm.PyNode(temp_loc).rotateY.set(current_rotate + 180)
                        pm.PyNode(temp_loc).rotateZ.set(0)
                    elif item == "Outer":
                        pm.PyNode(temp_loc).rotateX.set(0)
                        current_rotate = pm.PyNode(temp_loc).rotateY.get()
                        pm.PyNode(temp_loc).rotateY.set(180 - current_rotate)
                        pm.PyNode(temp_loc).rotateZ.set(0)
                    else:
                        pm.PyNode(temp_loc).rotateX.set(0)
                        current_rotate = pm.PyNode(temp_loc).rotateY.get()
                        pm.PyNode(temp_loc).rotateY.set(current_rotate + 90)
                        pm.PyNode(temp_loc).rotateZ.set(0)

                ctrl_name = "{}_{}_Ctrl".format(prefix, item)
                base_ctrl_grp = yellow_component(name=ctrl_name, shape_type="nurbsPlane", parent_node=base_ctrl_group)

                pm.delete(pm.orientConstraint(temp_loc_name, base_ctrl_grp, mo=False))

                dm_node(
                    node_name="{}_{}_Ctrl_Inverse_DM".format(prefix, item),
                    matrix_input=pm.PyNode(ctrl_name).attr("inverseMatrix"),
                    translate_output=pm.PyNode(ctrl_name).getParent().translate,
                    rotate_output=pm.PyNode(ctrl_name).getParent().rotate)

                mp_node_name = "{}_{}Master_MP".format(prefix, item)

                if not pm.objExists(mp_node_name):
                    pm.createNode("motionPath", name=mp_node_name)
                pm.PyNode(mp_node_name).attr("uValue").set(u_value)

                pm.PyNode(out_curve).getShape().attr('worldSpace[0]').connect(
                    pm.PyNode(mp_node_name).attr('geometryPath'))
                pm.PyNode(mp_node_name).attr("allCoordinates").connect(pm.PyNode(base_ctrl_grp).translate)
                pm.PyNode(master_ctrl).scale.connect(pm.PyNode(base_ctrl_grp).scale)
                pm.orientConstraint(master_ctrl, base_ctrl_grp, mo=True)

                pm.delete(temp_loc)

        return

    def build_base_loc_group(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            deformer_loc_group = "{}_Loc_Grp".format(prefix)
            if not pm.objExists(deformer_loc_group):
                pm.createNode("transform", name=deformer_loc_group)

            pm.parent(deformer_loc_group, "{}_Deformer_Grp".format(prefix))

            master_ctrl = "{}_Master_Ctrl".format(prefix)
            pm.delete(pm.parentConstraint(master_ctrl, deformer_loc_group, mo=False))

            base_loc_group = "{}_Base_Loc_Grp".format(prefix)
            pm.createNode("transform", name=base_loc_group, p=deformer_loc_group)

            for item in ["Up", "Low", "Inner", "Outer"]:
                loc_name = "{}_{}_Ctrl_Loc".format(prefix, item)
                loc_grp = jnt_or_control_grp(name=loc_name, object_type="locator")

                if item == "Low":
                    master_curve = "{}_Low_Master_Curve".format(prefix)
                else:
                    master_curve = "{}_Up_Master_Curve".format(prefix)

                ctrl = "{}_{}_Ctrl".format(prefix, item)
                ctrl_grp = "{}_Grp".format(ctrl)
                pm.delete(pm.orientConstraint(ctrl_grp, loc_grp, mo=False))

                postion = None
                if item == "Outer":
                    postion = point_on_curve_position(master_curve, 1.0)
                    pm.PyNode(ctrl).translate.connect(pm.PyNode(loc_name).translate)
                elif item == "Inner":
                    postion = point_on_curve_position(master_curve, 0)
                    pm.PyNode(ctrl).translate.connect(pm.PyNode(loc_name).translate)
                elif item == "Low" or "Up":
                    postion = point_on_curve_position(master_curve, 0.5)
                    pm.PyNode(ctrl).translateX.connect(pm.PyNode(loc_name).translateX)
                    pm.PyNode(ctrl).translateZ.connect(pm.PyNode(loc_name).translateZ)

                pm.PyNode(ctrl).rotate.connect(pm.PyNode(loc_name).rotate)

                pm.PyNode(loc_grp).translate.set(postion)
                pm.parent(loc_grp, base_loc_group)

        return

    def build_base_jnt_group(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            master_ctrl = "{}_Master_Ctrl".format(prefix)

            root_jnt_group = "{}_Jnt_Grp".format(prefix)
            if not pm.objExists(root_jnt_group):
                pm.createNode("transform", name=root_jnt_group, p="{}_Deformer_Grp".format(prefix))
            pm.delete(pm.parentConstraint(master_ctrl, root_jnt_group, mo=False))

            master_ctrl_jnt_group = "{}_Master_Ctrl_Jnt_Grp".format(prefix)
            pm.createNode("transform", name=master_ctrl_jnt_group, p=root_jnt_group)

            base_jnt_group = "{}_Base_Jnt_Grp".format(prefix)
            pm.createNode("transform", name=base_jnt_group, p=master_ctrl_jnt_group)

            side_name = "LF"
            if side == "LF":
                side_name = "Left"
            elif side == "RT":
                side_name = "Right"

            proxy_eye = pm.textFieldButtonGrp("xdMouthCreator{}EyeProxyField".format(side_name), q=True, text=True)

            temp_locs = []

            temp_root = pm.spaceLocator(name="temp_root_loc")
            pm.delete(pm.parentConstraint(proxy_eye, temp_root, mo=False))

            temp_locs.append(temp_root)

            for item in ["Up", "Low", "Inner", "Outer"]:
                base_loc = "{}_{}_Ctrl_Loc".format(prefix, item)
                temp_loc = pm.spaceLocator(name="temp_{}_loc".format(item))
                pm.delete(pm.parentConstraint(base_loc, temp_loc, mo=False))
                temp_locs.append(temp_loc)

                pm.select(cl=True)
                pm.joint(name="{}_{}_Ctrl_01_Jnt".format(prefix, item), p=pm.PyNode(temp_root).translate.get())
                pm.joint(name="{}_{}_Ctrl_02_Jnt".format(prefix, item), p=pm.PyNode(temp_loc).translate.get())
                pm.joint("{}_{}_Ctrl_01_Jnt".format(prefix, item), e=True, zso=True, oj="xyz", sao="yup")

                pm.parent("{}_{}_Ctrl_01_Jnt".format(prefix, item), base_jnt_group)

                pm.aimConstraint(
                    pm.PyNode(base_loc), "{}_{}_Ctrl_01_Jnt".format(prefix, item),
                    worldUpType="objectrotation",
                    worldUpObject=base_loc,
                    mo=True)

            pm.delete(temp_locs)

        return

    def build_bind_loc_group(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            bind_loc_group = "{}_Bind_Loc_Grp".format(prefix)
            pm.createNode("transform", name=bind_loc_group, p="{}_Loc_Grp".format(prefix))
            pm.PyNode(bind_loc_group).attr("inheritsTransform").set(0)

            seg = 10
            for vertical in ["Up", "Low"]:
                master_curve = "{}_{}_Master_Curve".format(prefix, vertical)
                for index in range(1, seg + 1):
                    loc_name = "{}_{}_{}_Loc".format(prefix, vertical, "{0:02d}".format(index))
                    bind_loc = pm.spaceLocator(name=loc_name)
                    pm.parent(bind_loc, bind_loc_group)

                    mp = mp_node(node_name=loc_name.replace("Loc", "MP"),
                                 geometry_path_input=pm.PyNode(master_curve).getShape().attr("worldSpace[0]"),
                                 all_coordinates_output=bind_loc.translate)
                    u_value = 0
                    if index == 1:
                        u_value = 0
                    elif index == seg:
                        u_value = 1
                    elif index == 2:
                        u_value = 0.048
                    elif index == seg + 1 - 2:  # 9
                        u_value = 1 - 0.048
                    elif 2 < index < seg + 1 - 2:  # 3 ~ 8
                        u_value = 0.143 * (index - 2)

                    pm.PyNode(mp).attr("uValue").set(u_value)

                    if vertical == "Low":
                        up_loc = "{}_Up_{}_Loc".format(prefix, "{0:02d}".format(index))
                        up_ctrl = "{}_Up_Ctrl".format(prefix)
                        custom_show_channel(up_ctrl,
                                            attr_list=["translateX", "translateY", "rotateX", "rotateY", "rotateZ"])
                        if not pm.attributeQuery("collideGap", node=up_ctrl, ex=True):
                            pm.addAttr(up_ctrl, ln="collideGap", at="double", dv=0)
                            pm.setAttr("{}.collideGap".format(up_ctrl), e=True, k=True)

                        adl = pm.createNode("addDoubleLinear",
                                            name="{}_Low_{}_ADL".format(prefix, "{0:02d}".format(index)))

                        pm.PyNode(up_loc).translateY.connect(adl.attr("input1"))
                        pm.PyNode(up_ctrl).attr("collideGap").connect(adl.attr("input2"))

                        clamp = pm.createNode("clamp", name="{}_Low_{}_CMP".format(prefix, "{0:02d}".format(index)))
                        clamp.attr("minR").set(-9999.0)
                        adl.attr("output").connect(clamp.attr("maxR"))
                        mp.attr("yCoordinate").connect(clamp.attr("inputR"))
                        clamp.attr("outputR").connect(bind_loc.attr("translateY"), f=True)

        return

    def build_bind_jnt_group(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            master_ctrl_jnt_group = "{}_Master_Ctrl_Jnt_Grp".format(prefix)

            bind_jnt_group = "{}_Bind_Jnt_Grp".format(prefix)
            pm.createNode("transform", name=bind_jnt_group, p=master_ctrl_jnt_group)

            side_name = "LF"
            if side == "LF":
                side_name = "Left"
            elif side == "RT":
                side_name = "Right"

            proxy_eye = pm.textFieldButtonGrp("xdMouthCreator{}EyeProxyField".format(side_name), q=True, text=True)

            temp_locs = []

            temp_root = pm.spaceLocator(name="temp_root_loc")
            pm.delete(pm.parentConstraint(proxy_eye, temp_root, mo=False))

            temp_locs.append(temp_root)

            seg = 10
            for item in ["Up", "Low"]:
                for index in range(1, seg + 1):
                    bind_loc = "{}_{}_{}_Loc".format(prefix, item, "{0:02d}".format(index))

                    pm.select(cl=True)
                    pm.joint(name="{}_{}_{}_Base_Jnt".format(prefix, item, "{0:02d}".format(index)),
                             p=pm.PyNode(temp_root).translate.get())
                    pm.joint(name="{}_{}_{}_Jnt".format(prefix, item, "{0:02d}".format(index)),
                             p=pm.PyNode(bind_loc).translate.get())
                    pm.joint("{}_{}_{}_Base_Jnt".format(prefix, item, "{0:02d}".format(index)),
                             e=True, zso=True, oj="xyz", sao="yup")

                    pm.parent("{}_{}_{}_Base_Jnt".format(
                        prefix, item, "{0:02d}".format(index)), bind_jnt_group)

                    pm.aimConstraint(
                        pm.PyNode(bind_loc), "{}_{}_{}_Base_Jnt".format(prefix, item, "{0:02d}".format(index)),
                        worldUpType="objectrotation",
                        worldUpObject=bind_jnt_group,
                        mo=True)

            pm.delete(temp_locs)

    def skin_out_curve(self):
        seg = 10
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)
            for vertical in ["Up", "Low"]:
                out_curve = "{}_{}_Out_Curve".format(prefix, vertical)
                # print(out_curve)
                skin_items = [out_curve]
                for index in range(1, seg + 1):
                    skin_items.append("{}_{}_{}_Jnt".format(prefix, vertical, "{0:02d}".format(index)))
                # print(skin_items)
                pm.skinCluster(skin_items, tsb=True, name="{}_{}_Out_Curve_SC".format(prefix, vertical))
        return

    def tweak_ctrl_group(self):
        seg = 4
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            tweak_ctrl_group = "{}_Tweak_Ctrl_Grp".format(prefix)
            pm.createNode("transform", name=tweak_ctrl_group)
            pm.parent(tweak_ctrl_group, "{}_Master_Ctrl_Grp".format(prefix))

            tweak_jnt_group = "{}_Tweak_Jnt_Grp".format(prefix)
            pm.createNode("transform", name=tweak_jnt_group)
            pm.parent(tweak_jnt_group, "{}_Jnt_Grp".format(prefix))

            master_ctrl = pm.PyNode("{}_Master_Ctrl".format(prefix))

            for vertical in ["Up", "Low"]:
                out_curve = pm.PyNode("{}_{}_Out_Curve".format(prefix, vertical))
                tweak_curve = pm.PyNode("{}_{}_Tweak_Curve".format(prefix, vertical))

                tweak_skin_items = [tweak_curve]

                for index in range(1, seg + 1):
                    tweak_ctrl = "{}_{}Tweak_{}_Ctrl".format(prefix, vertical, "{0:02d}".format(index))
                    tweak_ctrl_grp = yellow_component(name=tweak_ctrl,
                                                      shape_type="sphere",
                                                      parent_node=tweak_ctrl_group)
                    dm_node(
                        node_name="{}_Inverse_DM".format(tweak_ctrl),
                        matrix_input=pm.PyNode(tweak_ctrl).attr("inverseMatrix"),
                        translate_output=pm.PyNode(tweak_ctrl).getParent().translate,
                        rotate_output=pm.PyNode(tweak_ctrl).getParent().rotate)

                    mp = mp_node(node_name=tweak_ctrl.replace("Ctrl", "MP"),
                                 geometry_path_input=out_curve.getShape().attr("worldSpace[0]"),
                                 all_coordinates_output=pm.PyNode(tweak_ctrl_grp).translate)
                    u_value = float(index) / float(seg + 1)
                    pm.PyNode(mp).attr("uValue").set(u_value)

                    master_ctrl.scale.connect(pm.PyNode(tweak_ctrl_grp).scale)
                    pm.orientConstraint(master_ctrl, tweak_ctrl_grp)

                    ctrl_jnt = "{}_Jnt".format(tweak_ctrl)
                    ctrl_jnt_grp = jnt_or_control_grp(name=ctrl_jnt, parent_node=tweak_jnt_group)
                    pm.delete(pm.pointConstraint(tweak_ctrl_grp, ctrl_jnt_grp, mo=False))

                    pm.PyNode(tweak_ctrl).translate.connect(pm.PyNode(ctrl_jnt).translate)

                    tweak_skin_items.append(ctrl_jnt)

                if vertical == "Up":
                    for horizontal in ["Inner", "Outer"]:
                        tweak_ctrl = "{}_{}Tweak_Ctrl".format(prefix, horizontal)
                        tweak_ctrl_grp = yellow_component(name=tweak_ctrl,
                                                          shape_type="sphere",
                                                          parent_node=tweak_ctrl_group)

                        dm_node(
                            node_name="{}_Inverse_DM".format(tweak_ctrl),
                            matrix_input=pm.PyNode(tweak_ctrl).attr("inverseMatrix"),
                            translate_output=pm.PyNode(tweak_ctrl).getParent().translate,
                            rotate_output=pm.PyNode(tweak_ctrl).getParent().rotate)

                        mp = mp_node(node_name=tweak_ctrl.replace("Ctrl", "MP"),
                                     geometry_path_input=out_curve.getShape().attr("worldSpace[0]"),
                                     all_coordinates_output=pm.PyNode(tweak_ctrl_grp).translate)
                        if horizontal == "Inner":
                            pm.PyNode(mp).attr("uValue").set(0)
                        else:
                            pm.PyNode(mp).attr("uValue").set(1)

                        master_ctrl.scale.connect(pm.PyNode(tweak_ctrl_grp).scale)
                        pm.orientConstraint(master_ctrl, tweak_ctrl_grp)

                        ctrl_jnt = "{}_Jnt".format(tweak_ctrl)
                        ctrl_jnt_grp = jnt_or_control_grp(name=ctrl_jnt, parent_node=tweak_jnt_group)
                        pm.delete(pm.pointConstraint(tweak_ctrl_grp, ctrl_jnt_grp, mo=False))

                        pm.PyNode(tweak_ctrl).translate.connect(pm.PyNode(ctrl_jnt).translate)

                        tweak_skin_items.append(ctrl_jnt)

                pm.skinCluster(tweak_skin_items, tsb=True, name="{}_SC".format(tweak_curve))
        return

    def make_blink_work(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            master_ctrl = "{}_Master_Ctrl".format(prefix)  # LF_Eye_01_Master_Ctrl

            custom_show_channel(master_ctrl,
                                attr_list=["translateX", "translateY", "translateZ",
                                           "rotateX", "rotateY", "rotateZ",
                                           "scaleX", "scaleY", "scaleZ"])

            if not pm.attributeQuery("shift", node=master_ctrl, ex=True):
                pm.addAttr(master_ctrl, ln="shift", at="double", min=0.0, max=1.0, dv=0.3)
                pm.setAttr("{}.shift".format(master_ctrl), e=True, l=False, keyable=True)

            blink_rev = "{}_Blink_Rev".format(prefix)
            pm.createNode("reverse", name=blink_rev)
            pm.PyNode(master_ctrl).attr("shift").connect(pm.PyNode(blink_rev).attr("inputX"))

            blink_md = "{}_Blink_MD".format(prefix)
            pm.createNode("multiplyDivide", name=blink_md)
            pm.PyNode(blink_md).attr("operation").set(1)
            if not pm.attributeQuery("blink", node=master_ctrl, ex=True):
                pm.addAttr(master_ctrl, ln="blink", at="double", min=-0.5, max=1.0, dv=0.0)
                pm.setAttr("{}.blink".format(master_ctrl), e=True, k=True)
            pm.PyNode(master_ctrl).attr("blink").connect(pm.PyNode(blink_md).attr("input1X"))
            pm.PyNode(master_ctrl).attr("blink").connect(pm.PyNode(blink_md).attr("input1Y"))
            pm.PyNode(master_ctrl).attr("shift").connect(pm.PyNode(blink_md).attr("input2Y"))
            pm.PyNode(blink_rev).attr("outputX").connect(pm.PyNode(blink_md).attr("input2X"))

            blink_cond = "{}_Blink_Cond".format(prefix)
            pm.createNode("condition", name=blink_cond)
            pm.PyNode(blink_cond).attr("operation").set(2)
            pm.PyNode(master_ctrl).attr("blink").connect(pm.PyNode(blink_cond).attr("firstTerm"))
            pm.PyNode(master_ctrl).attr("blink").connect(pm.PyNode(blink_cond).attr("colorIfFalseR"))
            pm.PyNode(master_ctrl).attr("blink").connect(pm.PyNode(blink_cond).attr("colorIfFalseG"))
            pm.PyNode(blink_md).attr("outputX").connect(pm.PyNode(blink_cond).attr("colorIfTrueR"))
            pm.PyNode(blink_md).attr("outputY").connect(pm.PyNode(blink_cond).attr("colorIfTrueG"))

            for vertical in ["Up", "Low"]:
                up_ctrl = pm.PyNode("{}_{}_Ctrl".format(prefix, vertical))  # LF_Eye_01_Up_Ctrl

                if vertical == "Up":
                    blink_curve = "{}_Low_Blink_Curve".format(prefix)
                else:
                    blink_curve = "{}_Up_Blink_Curve".format(prefix)

                curves = [blink_curve,
                          "{}_{}_Tweak_Curve".format(prefix, vertical),
                          "{}_{}_Freshy_Curve".format(prefix, vertical),
                          "{}_{}_Master_Curve".format(prefix, vertical)]

                # LF_Eye_01_Up_Master_Curve_BS
                pm.blendShape(curves, frontOfChain=True, name="{}_{}_Master_Curve_BS".format(prefix, vertical))

                # up_ctrl
                blink_mdl = "{}_{}_Blink_MDL".format(prefix, vertical)  # LF_Eye_01_Up_Blink_MDL
                pm.createNode("multDoubleLinear", name=blink_mdl)
                up_ctrl.translateY.connect(pm.PyNode(blink_mdl).attr("input1"))

                blink_adl = "{}_{}_Blink_ADL".format(prefix, vertical)
                pm.createNode("addDoubleLinear", name=blink_adl)
                pm.PyNode(blink_mdl).attr("output").connect(pm.PyNode(blink_adl).attr("input1"))
                pm.PyNode(blink_adl).attr("output").connect(
                    pm.PyNode("{}_{}_Master_Curve_BS".format(prefix, vertical)).attr(blink_curve))

                pm.PyNode("{}_{}_Master_Curve_BS".format(prefix, vertical)).attr(
                    "{}_{}_Tweak_Curve".format(prefix, vertical)).set(1.0)

                # master_ctrl
                if vertical == "Up":
                    pm.PyNode(blink_mdl).attr("input2").set(-1.0)
                    pm.PyNode(blink_cond).attr("outColorR").connect(pm.PyNode(blink_adl).attr("input2"))
                else:
                    pm.PyNode(blink_mdl).attr("input2").set(1.0)
                    pm.PyNode(blink_cond).attr("outColorG").connect(pm.PyNode(blink_adl).attr("input2"))
        return

    def skin_master_curve(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)
            for vertical in ["Up", "Low"]:
                master_curve = "{}_{}_Master_Curve".format(prefix, vertical)
                skin_items = [
                    master_curve,
                    "{}_Outer_Ctrl_02_Jnt".format(prefix),
                    "{}_Inner_Ctrl_02_Jnt".format(prefix),
                    "{}_{}_Ctrl_02_Jnt".format(prefix, vertical)
                ]
                pm.skinCluster(skin_items, tsb=True, name="{}_SC".format(master_curve))
        return

    def make_master_ctrl_work(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            master_ctrl = pm.PyNode("{}_Master_Ctrl".format(prefix))

            base_loc_group = pm.PyNode("{}_Base_Loc_Grp".format(prefix))
            master_ctrl.translate.connect(base_loc_group.translate)
            master_ctrl.rotate.connect(base_loc_group.rotate)
            master_ctrl.scale.connect(base_loc_group.scale)

            master_ctrl_jnt_group = pm.PyNode("{}_Master_Ctrl_Jnt_Grp".format(prefix))
            master_ctrl.translate.connect(master_ctrl_jnt_group.translate)
            master_ctrl.rotate.connect(master_ctrl_jnt_group.rotate)
            master_ctrl.scale.connect(master_ctrl_jnt_group.scale)

            for vertical in ["Up", "Low"]:
                ctrl = "{}_{}_Ctrl".format(prefix, vertical)
                mp = "{}_{}Master_MP".format(prefix, vertical)

                driver_value = [-0.4, 0, 0.4]
                value = [0, 0.5, 1]

                for index in range(0, len(driver_value)):
                    pm.setDrivenKeyframe(
                        mp, at="uValue", cd="{}.{}".format(ctrl, "translateX"),
                        dv=driver_value[index], value=value[index],
                        itt="linear", ott="linear", )

        return

    def build_shape_ctrl_group(self):
        seg = 3
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            shape_ctrl_group = "{}_Shape_Ctrl_Grp".format(prefix)
            pm.createNode("transform", name=shape_ctrl_group, p="{}_Grp".format(prefix))
            pm.PyNode(shape_ctrl_group).attr("inheritsTransform").set(0)

            original_jnt = "{}_Original_Jnt".format(prefix)
            pm.select(cl=True)
            pm.joint(name=original_jnt)
            pm.parent(original_jnt, "{}_Grp".format(prefix))

            if side == "LF":
                proxy_eye = pm.textFieldButtonGrp("xdMouthCreator{}EyeProxyField".format("Left"), q=True, text=True)
            else:
                proxy_eye = pm.textFieldButtonGrp("xdMouthCreator{}EyeProxyField".format("Right"), q=True, text=True)
            pm.delete(pm.pointConstraint(proxy_eye, original_jnt, mo=False))

            for vertical in ["Up", "Low"]:
                shape_surface = pm.PyNode("{}_{}_Shape_Surface".format(prefix, vertical))

                for index in range(1, seg + 1):
                    follicle = xd_follicle_node(
                        name="{}_{}_{}_Shape_Follicle".format(prefix, vertical, "{0:02d}".format(index)),
                        worldMatrixInput=shape_surface.getShape().attr("worldMatrix[0]"),
                        surfaceInput=shape_surface.getShape().attr("local"),
                        parentNode=shape_ctrl_group)
                    pm.PyNode(follicle).getShape().attr("parameterU").set(0.5)
                    pm.PyNode(follicle).getShape().attr("parameterV").set(float(index) / float(seg + 1))

                    shape_ctrl = jnt_or_control_grp(
                        name="{}_{}_{}_Shape_Ctrl".format(prefix, vertical, "{0:02d}".format(index)),
                        object_type="sphere",
                        parent_node=follicle)

                    if side == "LF":
                        pm.PyNode(shape_ctrl).rotate.set([90, 0, 90])
                    else:
                        pm.PyNode(shape_ctrl).rotate.set([90, 0, -90])

                main_shape_ctrl = "{}_{}_Main_Shape_Ctrl".format(prefix, vertical)
                main_shape_ctrl_grp = control_grp_have_joint(name=main_shape_ctrl, parent_node="{}_Grp".format(prefix))
                pm.delete(
                    pm.parentConstraint("{}_{}_02_Shape_Follicle".format(prefix, vertical),
                                        main_shape_ctrl_grp, mo=False))

                current_rotate = pm.PyNode(main_shape_ctrl_grp).rotate.get()
                if side == "LF":
                    pm.PyNode(main_shape_ctrl_grp).rotate.set(
                        [current_rotate[0] + 90, current_rotate[1] + 90, current_rotate[2]])
                else:
                    pm.PyNode(main_shape_ctrl_grp).rotate.set(
                        [current_rotate[0] + 90, current_rotate[1] - 90, current_rotate[2]])

                skin_items = [original_jnt, "{}_Jnt".format(main_shape_ctrl), shape_surface]
                pm.skinCluster(skin_items, tsb=True, name="{}_SC".format(shape_surface))

        return

    def build_shape_jnt_group(self):
        seg = 3
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            shape_jnt_group = "{}_Shape_Jnt_Grp".format(prefix)
            pm.createNode("transform", name=shape_jnt_group)
            pm.parent(shape_jnt_group, "{}_Jnt_Grp".format(prefix))

            eye_group = pm.PyNode("{}_Grp".format(prefix))

            for vertical in ["Up", "Low"]:
                for index in range(1, seg + 1):
                    jnt = "{}_{}_{}_Shape_Ctrl_Jnt".format(prefix, vertical, "{0:02d}".format(index))
                    jnt_grp = yellow_component(
                        name=jnt,
                        shape_type="joint",
                        parent_node=shape_jnt_group)

                    shape_ctrl_jnt_mm = pm.createNode("multMatrix", name="{}_MM".format(jnt))
                    shape_follicle = pm.PyNode("{}_{}_{}_Shape_Follicle".format(
                        prefix, vertical, "{0:02d}".format(index)))
                    shape_follicle.attr("worldMatrix[0]").connect(shape_ctrl_jnt_mm.attr("matrixIn[0]"))
                    eye_group.attr("worldInverseMatrix[0]").connect(shape_ctrl_jnt_mm.attr("matrixIn[1]"))

                    jnt_dm = "{}_{}_{}_Shape_Ctrl_Jnt_DM".format(prefix, vertical, "{0:02d}".format(index))
                    dm_node(node_name=jnt_dm,
                            matrix_input=pm.PyNode(shape_ctrl_jnt_mm).attr("matrixSum"),
                            translate_output=pm.PyNode(jnt_grp).translate,
                            rotate_output=pm.PyNode(jnt_grp).rotate)

                    if side == "LF":
                        pm.PyNode(jnt).getParent().rotate.set([90, 0, 90])
                    else:
                        pm.PyNode(jnt).getParent().rotate.set([90, 0, -90])

                    shape_ctrl = pm.PyNode("{}_{}_{}_Shape_Ctrl".format(prefix, vertical, "{0:02d}".format(index)))
                    shape_ctrl.translate.connect(pm.PyNode(jnt).translate)
                    shape_ctrl.rotate.connect(pm.PyNode(jnt).rotate)
                    shape_ctrl.scale.connect(pm.PyNode(jnt).scale)
        return

    def build_eyeball_ctrl_group(self):
        for side in ["LF", "RT"]:
            if side == "LF":
                proxy_geo = self.left_eye_proxy
            else:
                proxy_geo = self.right_eye_proxy

            prefix = "{}_{}".format(side, self.module_name)

            # 眼球骨骼部分
            jnt_grp = "{}_Eyeball_Jnt_Grp".format(prefix)
            pm.createNode("transform", name=jnt_grp, p="{}_Jnt_Grp".format(prefix))
            eyeball_base_jnt = "{}_Eyeball_Base_Jnt".format(prefix)
            pm.joint(name=eyeball_base_jnt)
            pm.delete(pm.pointConstraint(proxy_geo, eyeball_base_jnt, mo=False))
            eyeball_jnt = "{}_Eyeball_Jnt".format(prefix)
            pm.joint(name=eyeball_jnt)

            master_ctrl = "{}_Master_Ctrl".format(prefix)

            aim_root_group = "{}_Ctrl_Grp".format(prefix)
            if not pm.objExists(aim_root_group):
                pm.createNode("transform", name=aim_root_group, p=master_ctrl)

            aim_grp = "{}_Aim_Grp".format(prefix)
            if not pm.objExists(aim_grp):
                pm.createNode("transform", name=aim_grp, p=aim_root_group)
                pm.delete(pm.pointConstraint(proxy_geo, aim_grp, mo=False))

            aim_ctrl = "{}_Aim_01_Ctrl".format(prefix)
            aim_ctrl_grp = jnt_or_control_grp(name=aim_ctrl, object_type="sphere", parent_node=aim_grp)
            pm.delete(pm.orientConstraint(proxy_geo, aim_ctrl_grp, mo=False))
            rotate = pm.PyNode(aim_ctrl_grp).rotate.get()
            pm.PyNode(aim_ctrl_grp).rotate.set([rotate[0] - 90, rotate[1], rotate[2]])

            aim_null = "{}_Aim_Null".format(prefix)
            pm.createNode("transform", name=aim_null, p=aim_root_group)

            pm.orientConstraint(aim_ctrl, aim_null, mo=True)

            pm.PyNode(aim_ctrl).translate.connect(pm.PyNode(eyeball_jnt).translate)
            pm.PyNode(aim_null).rotate.connect(pm.PyNode(eyeball_jnt).rotate)

        return

    def build_aim_ctrl_group(self):
        offset_Z = 15
        for side in ["LF", "RT"]:
            if side == "LF":
                proxy_geo = self.left_eye_proxy
            else:
                proxy_geo = self.right_eye_proxy

            prefix = "{}_{}".format(side, self.module_name)
            eye_aim_ctrl = "{}_Aim_02_Ctrl".format(prefix)
            eye_aim_ctrl_grp = jnt_or_control_grp(
                name=eye_aim_ctrl, object_type="sphere", parent_node="{}_Grp".format(prefix))
            pm.delete(pm.pointConstraint(proxy_geo, eye_aim_ctrl_grp, mo=False))
            translate_Z = pm.PyNode(eye_aim_ctrl_grp).translateZ.get()
            pm.PyNode(eye_aim_ctrl_grp).translateZ.set(translate_Z + offset_Z)

            pm.aimConstraint(
                eye_aim_ctrl, "{}_Aim_Grp".format(prefix),
                aimVector=[0, 0, 1],
                upVector=[0, 1, 0],
                worldUpType="objectrotation",
                worldUpVector=[0, 1, 0],
                worldUpObject=eye_aim_ctrl,
                mo=True)

        main_aim_ctrl = "MD_{}_Main_Aim_Ctrl".format(self.module_name)
        main_aim_ctrl_grp = jnt_or_control_grp(
            name=main_aim_ctrl, object_type="sphere", parent_node="{}_Grp".format(prefix))

        pm.delete(
            pm.pointConstraint(
                "LF_{}_Aim_02_Ctrl_Grp".format(self.module_name),
                "RT_{}_Aim_02_Ctrl_Grp".format(self.module_name),
                main_aim_ctrl_grp,
                mo=False))
        pm.parentConstraint(main_aim_ctrl, "LF_{}_Aim_02_Ctrl_Grp".format(self.module_name), mo=True)
        pm.parentConstraint(main_aim_ctrl, "RT_{}_Aim_02_Ctrl_Grp".format(self.module_name), mo=True)

        return


class BrowCreator(Creator):
    def __init__(self):
        super(BrowCreator, self).__init__()

        self.module_name = "Brow_01"
        self.left_brow_surface = ""
        self.right_brow_surface = ""

        self.left_brow_curve = ""
        self.right_brow_curve = ""

        self.left_master_ctrl_surface = ""
        self.right_master_ctrl_surface = ""

        self.brow_segment = 7

    def sub_control(self, side="LF", index=1, parent_node=None):
        control = "{}_{}_Sub_{}_Ctrl".format(side, self.module_name, "{0:02d}".format(index))
        control_grp = "{}_Grp".format(control)
        squeeze_grp = control.replace("Ctrl", "Jnt_Squeeze_Grp")
        local_scale_grp = control.replace("Ctrl", "Jnt_LocalScale_Grp")

        pm.createNode("transform", name=local_scale_grp)
        pm.createNode("transform", name=squeeze_grp, p=local_scale_grp)
        pm.createNode("transform", name=control_grp, p=squeeze_grp)

        pm.sphere(name=control, p=[0, 0, 0], ax=[
            0, 1, 0], ssw=0, esw=360, r=0.5, d=3, ut=0, tol=0.01, s=4, nsp=2, ch=0)

        pm.parent(control, control_grp)

        if parent_node is not None:
            if not pm.objExists(parent_node):
                pm.error(u"场景中缺少{}".format(parent_node))
            else:
                pm.parent(local_scale_grp, parent_node)
                pm.PyNode(local_scale_grp).translate.set([0, 0, 0])
                pm.PyNode(local_scale_grp).rotate.set([0, 0, 0])

        return control

    def output_follicle(self):
        for side in ["LF", "RT"]:
            if side == "LF":
                surface = self.left_brow_surface
            else:
                surface = self.right_brow_surface

            surface_shape = pm.PyNode(surface).getShape()

            for index in range(0, self.brow_segment):
                follicle_name = "{}_{}_Sub_{}_Follicle".format(
                    side, self.module_name, "{0:02d}".format(index + 1))
                # print(follicle_name)
                follicle = xd_follicle_node(
                    name=follicle_name,
                    worldMatrixInput=surface_shape.attr("worldMatrix[0]"),
                    surfaceInput=surface_shape.attr("local"),
                    outTranslateToParent=True,
                    outRotateToParent=False,
                    parentNode="{}_{}_Sub_Output_Jnt_Grp".format(
                        side, self.module_name)
                )
                follicle_shape = pm.PyNode(follicle).getShape()
                # 毛囊会根据parameterV的值，调整它在曲面上面的位置
                follicle_shape.attr("parameterU").set(0.5)
                if index == 0:
                    follicle_shape.attr("parameterV").set(0)
                elif index == self.brow_segment - 1:
                    follicle_shape.attr("parameterV").set(1)
                else:
                    follicle_shape.attr("parameterV").set(0.167 * index)

                # 添加次级控制器到毛囊的子层级
                sub_control = self.sub_control(side=side, index=index + 1, parent_node=follicle)
                if side == "RT":
                    pm.PyNode(sub_control).getParent().scaleX.set(-1)
        return True

    def init_structure(self):
        if not pm.objExists("Head_01_Grp"):
            pm.createNode("transform", name="Head_01_Grp", p="Master_Ctrl")

        for side in ["LF", "RT"]:
            side_module_grp = "{}_{}_Grp".format(side, self.module_name)
            if not pm.objExists(side_module_grp):
                pm.createNode("transform", name=side_module_grp,
                              p="Head_01_Grp")

            side_output_jnt_grp = "{}_{}_Sub_Output_Jnt_Grp".format(side, self.module_name)
            if not pm.objExists(side_output_jnt_grp):
                pm.createNode("transform", name=side_output_jnt_grp, p=side_module_grp)
                pm.PyNode(side_output_jnt_grp).attr("inheritsTransform").set(0)

        return True

    def build_master_control(self):
        for side in ["LF", "RT"]:
            master_surface = "{}_{}_Master_Ctrl_Follicle_Surface".format(
                side, self.module_name)
            master_surface_shape = pm.PyNode(master_surface).getShape()

            master_follicle_name = "{}_{}_Master_Ctrl_Follicle".format(
                side, self.module_name)
            if not pm.objExists(master_follicle_name):
                follicle = xd_follicle_node(
                    name=master_follicle_name,
                    worldMatrixInput=master_surface_shape.attr(
                        "worldMatrix[0]"),
                    surfaceInput=master_surface_shape.attr("local"),
                    parentNode="{}_{}_Grp".format(side, self.module_name),
                )
                pm.PyNode(follicle).getShape().attr("parameterU").set(0.5)
                pm.PyNode(follicle).getShape().attr("parameterV").set(0.5)

            master_ctrl = "{}_{}_Master_Ctrl".format(side, self.module_name)
            master_ctrl_grp = "{}_Grp".format(master_ctrl)
            if not pm.objExists(master_ctrl_grp):
                pm.createNode("transform", name=master_ctrl_grp)
                pm.torus(name=master_ctrl, p=[0, 0, 0], ax=[0, 0, 1], ssw=0, esw=360, msw=360, r=1, hr=0.1, d=1, ut=0,
                         tol=0.01, s=4, nsp=5, ch=1)
                pm.PyNode(master_ctrl).rotateZ.set(45)
                pm.makeIdentity(apply=True, t=1, r=1, s=1, n=0, pn=1)
                pm.parent(master_ctrl, master_ctrl_grp)
                pm.parent(master_ctrl_grp, master_follicle_name)
                pm.PyNode(master_ctrl_grp).translate.set([0, 0, 0])
                if side == "LF":
                    pm.PyNode(master_ctrl_grp).rotate.set([0, 0, 0])
                else:
                    pm.PyNode(master_ctrl_grp).rotate.set([180, 0, 0])
                    pm.PyNode(master_ctrl_grp).scale.set([1, 1, -1])

                pm.setAttr("{}.visibility".format(master_ctrl),
                           lock=True, k=False, cb=False)
                pm.select(master_ctrl)
                pm.mel.eval('DeleteHistory;')
        return

    def master_sub_control(self):
        control_num = 4
        for side in ["LF", "RT"]:
            master_ctrl = "{}_{}_Master_Ctrl".format(side, self.module_name)

            if side == "LF":
                sub_curve = self.left_brow_curve
                sub_surface = self.left_brow_surface
            else:
                sub_curve = self.right_brow_curve
                sub_surface = self.right_brow_surface

            temp_loc = pm.spaceLocator()
            temp_mp_node = pm.pathAnimation(
                temp_loc, sub_curve, fractionMode=True, follow=True,
                followAxis="x", upAxis="y", worldUpType="vector", worldUpVector=[0, 1, 0],
                inverseUp=False, inverseFront=False, bank=False)

            surface_skin_items = []
            for index in range(0, control_num):
                if index < 1:
                    pm.PyNode(temp_mp_node).attr("uValue").set(0)
                else:
                    pm.PyNode(temp_mp_node).attr("uValue").set(float(index) / (float(control_num - 1)))

                control_name = "{}_{}_Main_{}_Ctrl".format(side, self.module_name, "{0:02d}".format(index + 1))
                control_grp = control_grp_have_joint(name=control_name, parent_node=master_ctrl)
                pm.delete(pm.parentConstraint(temp_loc, control_grp, mo=False, skipRotate=["x", "z"]))
                if side == "RT":
                    rotate_angle = pm.PyNode(control_grp).rotateY.get()
                    if rotate_angle > 180:
                        pm.PyNode(control_grp).rotateY.set(rotate_angle - 180)
                    else:
                        pm.PyNode(control_grp).rotateY.set(rotate_angle * -1)

                pm.orientConstraint(
                    control_name,
                    "{}_{}_Sub_{}_Ctrl_Grp".format(side, self.module_name, "{0:02d}".format(index + 1)),
                    mo=True)

                surface_skin_items.append("{}_Jnt".format(control_name))
            pm.delete(temp_loc, temp_mp_node)
            surface_skin_items.append(sub_surface)
            skin_name = "{}_SC".format(sub_surface)
            pm.skinCluster(surface_skin_items, tsb=True, name=skin_name)
        return True

    def make_master_control_rotate(self):
        seg_of_brow = 7
        for side in ["LF", "RT"]:
            master_ctrl = "{}_{}_Master_Ctrl".format(side, self.module_name)
            sub_ori_null = "{}_{}_Sub_Ori_Null".format(side, self.module_name)
            if not pm.objExists(sub_ori_null):
                pm.createNode("transform", name=sub_ori_null,
                              p="{}_{}_Sub_Output_Jnt_Grp".format(side, self.module_name))
            pm.orientConstraint(master_ctrl, sub_ori_null, mo=False)
            for index in range(1, seg_of_brow + 1):
                pm.PyNode(sub_ori_null).rotate.connect(
                    pm.PyNode("{}_{}_Sub_{}_Follicle".format(side, self.module_name, "{0:02d}".format(index))).rotate)
        return

    def make_master_control_scale(self):
        seg_of_brow = 7
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)
            master_ctrl = "{}_Master_Ctrl".format(prefix)
            if not pm.attributeQuery("squeeze", node=master_ctrl, ex=True):
                pm.addAttr(master_ctrl, ln="squeeze", at="double", dv=0)
                pm.setAttr("{}.squeeze".format(master_ctrl), e=True, k=True)

            # LF_Brow_01_Scale_Null
            sub_scale_null = "{}_Scale_Null".format(prefix)
            if not pm.objExists(sub_scale_null):
                pm.createNode("transform", name=sub_scale_null, p="{}_Deformer_Grp".format(prefix))
                pm.PyNode(sub_scale_null).scaleZ.set(-1)
            pm.scaleConstraint(master_ctrl, sub_scale_null, mo=True)

            sub_surface = "{}_Sub_Surface".format(prefix)
            pm.PyNode(sub_scale_null).scaleX.connect(
                pm.PyNode(sub_surface).attr("globalScale"))

            for index in range(1, seg_of_brow + 1):
                pm.PyNode(sub_surface).attr("globalScale").connect(
                    pm.PyNode("{}_Sub_{}_Follicle".format(prefix, "{0:02d}".format(index))).scaleX)
                pm.PyNode(sub_surface).attr("globalScale").connect(
                    pm.PyNode("{}_Sub_{}_Follicle".format(prefix, "{0:02d}".format(index))).scaleY)
                pm.PyNode(sub_surface).attr("globalScale").connect(
                    pm.PyNode("{}_Sub_{}_Follicle".format(prefix, "{0:02d}".format(index))).scaleZ)

                sub_db_scale_md_node = "{}_Sub_DBScale_{}_MD".format(
                    prefix, "{0:02d}".format(index))
                if not pm.objExists(sub_db_scale_md_node):
                    pm.createNode("multiplyDivide", name=sub_db_scale_md_node)
                    pm.PyNode(sub_db_scale_md_node).attr("operation").set(2)
                pm.PyNode(sub_surface).attr("globalScale").connect(
                    pm.PyNode(sub_db_scale_md_node).attr("input2X"))

                sub_surface_shape = pm.PyNode(sub_surface).getShape()

                sub_index_01_posi = "{}_Sub_{}_01_POSI".format(
                    prefix, "{0:02d}".format(index))
                if not pm.objExists(sub_index_01_posi):
                    pm.createNode("pointOnSurfaceInfo", name=sub_index_01_posi)
                    pm.PyNode(sub_index_01_posi).attr("parameterU").set(0)
                    pm.PyNode(sub_index_01_posi).attr("parameterV").set(
                        float(index - 1) / float(seg_of_brow - 1))
                sub_surface_shape.attr("worldSpace[0]").connect(
                    pm.PyNode(sub_index_01_posi).attr("inputSurface"))

                sub_index_02_posi = "{}_Sub_{}_02_POSI".format(
                    prefix, "{0:02d}".format(index))
                if not pm.objExists(sub_index_02_posi):
                    pm.createNode("pointOnSurfaceInfo", name=sub_index_02_posi)
                    pm.PyNode(sub_index_02_posi).attr("parameterU").set(1)
                    pm.PyNode(sub_index_02_posi).attr("parameterV").set(
                        float(index - 1) / float(seg_of_brow - 1))
                sub_surface_shape.attr("worldSpace[0]").connect(
                    pm.PyNode(sub_index_02_posi).attr("inputSurface"))

                distance_node = "{}_Sub_{}_DB".format(
                    prefix, "{0:02d}".format(index))
                if not pm.objExists(distance_node):
                    pm.createNode("distanceBetween", name=distance_node)
                pm.PyNode(sub_index_01_posi).attr("position").connect(
                    pm.PyNode(distance_node).attr("point1"))
                pm.PyNode(sub_index_02_posi).attr("position").connect(
                    pm.PyNode(distance_node).attr("point2"))
                pm.PyNode(distance_node).attr("distance").connect(
                    pm.PyNode(sub_db_scale_md_node).attr("input1X"))

                sub_local_scale_md = "{}_Sub_LocalScale_{}_MD".format(
                    prefix, "{0:02d}".format(index))
                if not pm.objExists(sub_local_scale_md):
                    pm.createNode("multiplyDivide", name=sub_local_scale_md)
                    pm.PyNode(sub_local_scale_md).attr("operation").set(2)
                pm.PyNode(sub_db_scale_md_node).attr("outputX").connect(
                    pm.PyNode(sub_local_scale_md).attr("input1X"))
                pm.PyNode(sub_local_scale_md).attr("input2X").set(
                    pm.PyNode(sub_db_scale_md_node).attr("outputX").get())

                pm.PyNode(sub_local_scale_md).attr("outputX").connect(
                    pm.PyNode("{}_Sub_{}_Jnt_LocalScale_Grp".format(prefix, "{0:02d}".format(index))).scaleX)
                pm.PyNode(sub_local_scale_md).attr("outputX").connect(
                    pm.PyNode("{}_Sub_{}_Jnt_LocalScale_Grp".format(prefix, "{0:02d}".format(index))).scaleY)
                pm.PyNode(sub_local_scale_md).attr("outputX").connect(
                    pm.PyNode("{}_Sub_{}_Jnt_LocalScale_Grp".format(prefix, "{0:02d}".format(index))).scaleZ)

            if not pm.attributeQuery("squeeze", node=sub_surface, ex=True):
                pm.addAttr(sub_surface, ln="squeeze", at="double", dv=0)
                pm.setAttr("{}.squeeze".format(sub_surface), e=True, k=True)

            sub_curve = "{}_{}_Sub_Curve".format(side, self.module_name)
            sub_curve_shape = pm.PyNode(sub_curve).getShape()
            curve_info_node = "{}_{}_Sub_CI".format(side, self.module_name)
            if not pm.objExists(curve_info_node):
                pm.createNode("curveInfo", name=curve_info_node)
            sub_curve_shape.attr("worldSpace[0]").connect(
                pm.PyNode(curve_info_node).attr("inputCurve"))

            length_mdl_node = "{}_{}_Sub_Original_Length_MDL".format(
                side, self.module_name)
            if not pm.objExists(length_mdl_node):
                pm.createNode("multDoubleLinear", name=length_mdl_node)
            pm.PyNode(length_mdl_node).attr("input1").set(
                pm.PyNode(curve_info_node).attr("arcLength").get())
            pm.PyNode(sub_surface).attr("globalScale").connect(
                pm.PyNode(length_mdl_node).attr("input2"))

            stretch_md_node = "{}_{}_Sub_Stretch_MD".format(
                side, self.module_name)
            if not pm.objExists(stretch_md_node):
                pm.createNode("multiplyDivide", name=stretch_md_node)
                pm.PyNode(stretch_md_node).attr("operation").set(2)
            pm.PyNode(length_mdl_node).attr("output").connect(
                pm.PyNode(stretch_md_node).attr("input1X"))
            pm.PyNode(curve_info_node).attr("arcLength").connect(
                pm.PyNode(stretch_md_node).attr("input2X"))

            for index in range(1, seg_of_brow + 1):
                squeeze_md = "{}_{}_Sub_Squeeze_{}_MD".format(
                    side, self.module_name, "{0:02d}".format(index))
                if not pm.objExists(squeeze_md):
                    pm.createNode("multiplyDivide", name=squeeze_md)
                    pm.PyNode(squeeze_md).attr("operation").set(3)
                pm.PyNode(stretch_md_node).attr("outputX").connect(
                    pm.PyNode(squeeze_md).attr("input1X"))

                squeeze_mdl = "{}_{}_Sub_Squeeze_{}_MDL".format(
                    side, self.module_name, "{0:02d}".format(index))
                if not pm.objExists(squeeze_mdl):
                    pm.createNode("multDoubleLinear", name=squeeze_mdl)
                pm.PyNode(sub_surface).attr("squeeze").connect(
                    pm.PyNode(squeeze_mdl).attr("input1"))
                pm.PyNode(sub_surface).attr("squeeze{}".format("{0:02d}".format(index - 1))).connect(
                    pm.PyNode(squeeze_mdl).attr("input2"))
                pm.PyNode(squeeze_mdl).attr("output").connect(
                    pm.PyNode(squeeze_md).attr("input2X"))

                jnt_squeeze_grp = "{}_{}_Sub_{}_Jnt_Squeeze_Grp".format(
                    side, self.module_name, "{0:02d}".format(index))
                pm.PyNode(squeeze_md).attr("input1X").connect(
                    pm.PyNode(jnt_squeeze_grp).scaleY)
                pm.PyNode(squeeze_md).attr("input1X").connect(
                    pm.PyNode(jnt_squeeze_grp).scaleZ)

        return

    def master_ctrl_vis(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)
            master_ctrl = "{}_Master_Ctrl".format(prefix)
            if not pm.attributeQuery("ctrlVis", node=master_ctrl, ex=True):
                pm.addAttr(master_ctrl, ln="ctrlVis",
                           at="double", min=0, max=1, dv=0)
                pm.setAttr("{}.ctrlVis".format(master_ctrl), e=True, k=True)

            output_jnt_grp = "{}_Sub_Output_Jnt_Grp".format(prefix)
            if pm.objExists(output_jnt_grp):
                pm.PyNode(master_ctrl).attr("ctrlVis").connect(
                    pm.PyNode(output_jnt_grp).attr("visibility"))

            master_follicle = "{}_Master_Ctrl_Follicle".format(prefix)
            pm.PyNode(master_follicle).getShape().attr("visibility").set(0)

        return

    def local_rig_out(self):
        seg_of_brow = 7
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            rig_out_grp = "{}_LocalRig_Out_Grp".format(prefix)
            if not pm.objExists(rig_out_grp):
                pm.createNode("transform", name=rig_out_grp,
                              p="{}_Deformer_Grp".format(prefix))

            rig_track_grp = "{}_LocalRig_Track_Grp".format(prefix)
            if not pm.objExists(rig_track_grp):
                pm.createNode("transform", name=rig_track_grp)
                pm.parent(rig_track_grp, "{}_Master_Ctrl_Grp".format(prefix))

            for index in range(1, seg_of_brow + 1):
                sub_null = "{}_Sub_{}_Null".format(prefix, "{0:02d}".format(index))
                pm.createNode("transform", name=sub_null, p=rig_track_grp)
                pm.PyNode(sub_null).scaleX.set(-1)

                sub_ctrl = "{}_Sub_{}_Ctrl".format(prefix, "{0:02d}".format(index))
                pm.parentConstraint(sub_ctrl, sub_null, mo=False)
                pm.scaleConstraint(sub_ctrl, sub_null, mo=True)

                pm.select(cl=True)
                jnt = pm.joint(name="{}_Sub_{}_Jnt".format(
                    prefix, "{0:02d}".format(index)))
                pm.parent(jnt, rig_out_grp)

                pm.PyNode(sub_null).translate.connect(pm.PyNode(jnt).translate)
                pm.PyNode(sub_null).rotate.connect(pm.PyNode(jnt).rotate)
                pm.PyNode(sub_null).scale.connect(pm.PyNode(jnt).scale)
        return


class CheekCreator(Creator):
    def __init__(self):
        super(CheekCreator, self).__init__()

        self.module_name = "Cheek_01"

    def update_init(self):
        pass

    def proxy(self):
        if not pm.objExists("Proxy_Grp"):
            pm.createNode("transform", name="Proxy_Grp")

        if pm.objExists("Proxy_Cheek_Grp"):
            pm.error("Proxy_Cheek_Grp was exists!")
        else:
            pm.createNode("transform", name="Proxy_Cheek_Grp", p="Proxy_Grp")

        seg = 5
        for index in range(1, seg + 1):
            pm.parent(pm.spaceLocator(name="LF_proxyCheek{}Loc".format(
                "{0:02d}".format(index))), "Proxy_Cheek_Grp")

        pm.PyNode("LF_proxyCheek01Loc").translate.set([3, 1.2, -1.4])
        pm.PyNode("LF_proxyCheek02Loc").translate.set([1.9, 3.1, -0.23])
        pm.PyNode("LF_proxyCheek03Loc").translate.set([3.81, 4.0, -1.3])
        pm.PyNode("LF_proxyCheek04Loc").translate.set([1.156, 0.181, 0])
        pm.PyNode("LF_proxyCheek05Loc").translate.set([0.229, 4, -0.469])

        print("Build proxy done!")
        return

    def mirror_proxy(self):
        seg = 5
        for index in range(0, 5):
            lf_proxy_loc = "LF_proxyCheek{}Loc".format(
                "{0:02d}".format(index + 1))
            translate = pm.PyNode(lf_proxy_loc).translate.get()
            rotate = pm.PyNode(lf_proxy_loc).rotate.get()

            rt_proxy_loc = lf_proxy_loc.replace("LF", "RT")
            pm.spaceLocator(name=rt_proxy_loc)
            pm.parent(rt_proxy_loc, "Proxy_Cheek_Grp")
            pm.PyNode(rt_proxy_loc).translate.set(
                [translate[0] * -1, translate[1], translate[2]])
            pm.PyNode(rt_proxy_loc).rotate.set(
                [rotate[0], rotate[1] * -1, rotate[2] * -1])
            pm.PyNode(rt_proxy_loc).scale.set([-1, 1, 1])

            pm.textFieldButtonGrp("xdMouthCreatorRightCheek{}ProxyField".format("{0:02d}".format(index + 1)),
                                  e=True,
                                  text=rt_proxy_loc)
        return

    def build_module(self):
        self.build_deformer_grp()

        # todo 缺少微表情

        return

    def build_deformer_grp(self):
        cheeck_num = 5
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            deformer_grp = "{}_Deformer_Grp".format(prefix)
            if not pm.objExists(deformer_grp):
                pm.createNode("transform", name=deformer_grp, p="Deformer_Grp")

            cheek_jnt_group = "{}_Jnt_Grp".format(prefix)
            if not pm.objExists(cheek_jnt_group):
                pm.createNode("transform", name=cheek_jnt_group, p=deformer_grp)

            control_grp = "{}_Grp".format(prefix)
            if not pm.objExists(control_grp):
                pm.createNode("transform", name=control_grp, p="Head_02_Grp")

            control_main_grp = "{}_Main_Grp".format(prefix)
            if not pm.objExists(control_main_grp):
                pm.createNode("transform", name=control_main_grp, p=control_grp)

            for index in range(1, cheeck_num + 1):
                proxy_loc = "{}_proxyCheek{}Loc".format(side, "{0:02d}".format(index))

                cheek_ctrl = "{}_{}_Ctrl".format(prefix, "{0:02d}".format(index))
                cheek_ctrl_grp = yellow_component(name=cheek_ctrl, shape_type="sphere", parent_node=control_main_grp)
                pm.delete(pm.parentConstraint(proxy_loc, cheek_ctrl_grp, mo=False))
                pm.delete(pm.scaleConstraint(proxy_loc, cheek_ctrl_grp, mo=False))

                cheek_jnt = "{}_{}_Ctrl_Jnt".format(prefix, "{0:02d}".format(index))
                cheek_jnt_grp = yellow_component(name=cheek_jnt, shape_type="joint", parent_node=cheek_jnt_group)
                pm.delete(pm.parentConstraint(cheek_ctrl_grp, cheek_jnt_grp, mo=False))
                if side == "RT":
                    pm.PyNode(cheek_jnt_grp).scaleZ.set(-1)
                    pm.rotate(cheek_jnt_grp, 180, 0, 180, r=True, os=True, fo=True)

                pm.PyNode(cheek_ctrl).translate.connect(pm.PyNode(cheek_jnt).translate)
                pm.PyNode(cheek_ctrl).rotate.connect(pm.PyNode(cheek_jnt).rotate)
                pm.PyNode(cheek_ctrl).scale.connect(pm.PyNode(cheek_jnt).scale)

        return


class NoseCreator(Creator):
    def __init__(self):
        super(NoseCreator, self).__init__()

        self.proxy_bridge = ""
        self.proxy_master = ""
        self.proxy_tip = ""
        self.proxy_left = ""
        self.proxy_right = ""
        self.proxy_up = ""

        self.module_name = "Nose_01"

    def update_init(self):
        self.proxy_bridge = pm.textFieldButtonGrp("xdMouthCreatorNoseBridgeProxyField", q=True, text=True)
        self.proxy_master = pm.textFieldButtonGrp("xdMouthCreatorNoseMasterProxyField", q=True, text=True)
        self.proxy_tip = pm.textFieldButtonGrp("xdMouthCreatorNoseTipProxyField", q=True, text=True)
        self.proxy_left = pm.textFieldButtonGrp("xdMouthCreatorNoseLeftProxyField", q=True, text=True)
        self.proxy_right = pm.textFieldButtonGrp("xdMouthCreatorNoseRightProxyField", q=True, text=True)
        self.proxy_up = pm.textFieldButtonGrp("xdMouthCreatorNoseUpProxyField", q=True, text=True)
        return

    def proxy(self):
        if not pm.objExists("Proxy_Grp"):
            pm.createNode("transform", name="Proxy_Grp")

        if pm.objExists("Proxy_Nose_Grp"):
            pm.error(u"场景中已经存在代理对象")

        pm.createNode("transform", name="Proxy_Nose_Grp", p="Proxy_Grp")

        for item in ["Bridge", "Master", "MD", "LF", "RT", "Up"]:
            pm.parent(pm.spaceLocator(name="proxyNose{}Loc".format(item)), "Proxy_Nose_Grp")

        pm.PyNode("proxyNoseBridgeLoc").translateY.set(3)
        pm.PyNode("proxyNoseBridgeLoc").rotateX.set(-15)

        pm.parent("proxyNoseMasterLoc", "proxyNoseBridgeLoc")
        pm.PyNode("proxyNoseMasterLoc").translateY.set(-2.5)
        pm.PyNode("proxyNoseMasterLoc").rotateX.set(15)

        pm.parent("proxyNoseMDLoc", "proxyNoseLFLoc", "proxyNoseRTLoc", "proxyNoseMasterLoc")
        pm.PyNode("proxyNoseMDLoc").translateY.set(-0.5)
        pm.PyNode("proxyNoseMDLoc").translateZ.set(3)
        pm.PyNode("proxyNoseLFLoc").translate.set([1.5, -0.5, 1.5])
        pm.PyNode("proxyNoseRTLoc").translate.set([-1.5, -0.5, 1.5])

        pm.PyNode("proxyNoseUpLoc").translateY.set(4)

        return True

    def build_module(self):
        ctrl_list = self.local_rig_out_grp()
        # todo 右边鼻翼控制器scaleX应该为-1，而不是scaleZ的值为-1
        self.make_ctrl_work(ctrl_list)

    def local_rig_out_grp(self):
        self.update_init()

        mid_prefix = "MD_{}".format(self.module_name)
        lf_prefix = "LF_{}".format(self.module_name)
        rt_prefix = "RT_{}".format(self.module_name)

        ctrl_list = []

        deformer_grp = "{}_Deformer_Grp".format(mid_prefix)
        if not pm.objExists(deformer_grp):
            pm.createNode("transform", name=deformer_grp, p="Deformer_Grp")

        control_grp = "{}_Grp".format(mid_prefix)
        if not pm.objExists(control_grp):
            pm.createNode("transform", name=control_grp, p="Head_02_Grp")

        local_rig_out_grp = "{}_LocalRig_Out_Grp".format(mid_prefix)
        if not pm.objExists(local_rig_out_grp):
            pm.createNode("transform", name=local_rig_out_grp, p="{}_Deformer_Grp".format(mid_prefix))

        bridge_jnt_grp = jnt_or_control_grp(
            name="{}_Bridge_Ctrl_Jnt".format(mid_prefix), parent_node=local_rig_out_grp)
        pm.delete(pm.parentConstraint(self.proxy_bridge, bridge_jnt_grp, mo=False))
        bridge_ctrl_grp = jnt_or_control_grp(
            name="{}_Bridge_Ctrl".format(mid_prefix), object_type="plane", parent_node=control_grp)
        pm.delete(pm.parentConstraint(self.proxy_bridge, bridge_ctrl_grp, mo=False))
        ctrl_list.append("{}_Bridge_Ctrl".format(mid_prefix))

        master_jnt_grp = yellow_component(
            name="{}_Master_Ctrl_Jnt".format(mid_prefix),
            shape_type="joint",
            parent_node="{}_Bridge_Ctrl_Jnt".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_master, master_jnt_grp, mo=False))
        master_ctrl_grp = yellow_component(
            name="{}_Master_Ctrl".format(mid_prefix),
            shape_type="sphere",
            parent_node="{}_Bridge_Ctrl".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_master, master_ctrl_grp, mo=False))
        ctrl_list.append("{}_Master_Ctrl".format(mid_prefix))

        tip_jnt_grp = jnt_or_control_grp(
            name="{}_Ctrl_Jnt".format(mid_prefix),
            object_type='joint',
            parent_node="{}_Master_Ctrl_Jnt".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_tip, tip_jnt_grp, mo=False))
        tip_ctrl_grp = jnt_or_control_grp(
            name="{}_Ctrl".format(mid_prefix),
            object_type='plane',
            parent_node="{}_Master_Ctrl".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_tip, tip_ctrl_grp, mo=False))
        ctrl_list.append("{}_Ctrl".format(mid_prefix))

        left_jnt_grp = yellow_component(
            name="{}_Ctrl_Jnt".format(lf_prefix),
            shape_type="joint",
            parent_node="{}_Master_Ctrl_Jnt".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_left, left_jnt_grp, mo=False))
        left_ctrl_grp = yellow_component(
            name="{}_Ctrl".format(lf_prefix),
            shape_type="sphere",
            parent_node="{}_Master_Ctrl".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_left, left_ctrl_grp, mo=False))
        ctrl_list.append("{}_Ctrl".format(lf_prefix))

        right_jnt_grp = yellow_component(
            name="{}_Ctrl_Jnt".format(rt_prefix), shape_type="joint",
            parent_node="{}_Master_Ctrl_Jnt".format(mid_prefix))
        pm.PyNode(right_jnt_grp).scaleZ.set(-1)
        pm.delete(pm.parentConstraint(self.proxy_right, right_jnt_grp, mo=False))

        right_ctrl_grp = yellow_component(
            name="{}_Ctrl".format(rt_prefix),
            shape_type="sphere",
            parent_node="{}_Master_Ctrl".format(mid_prefix))
        pm.PyNode(right_ctrl_grp).scaleX.set(-1)
        pm.delete(pm.parentConstraint(self.proxy_right, right_ctrl_grp, mo=False))

        ctrl_list.append("{}_Ctrl".format(rt_prefix))

        up_jnt_grp = jnt_or_control_grp(
            name="{}_Up_Ctrl_Jnt".format(mid_prefix),
            object_type="joint",
            parent_node=local_rig_out_grp)
        pm.delete(pm.parentConstraint(self.proxy_up, up_jnt_grp, mo=False))
        up_ctrl_grp = jnt_or_control_grp(
            name="{}_Up_Ctrl".format(mid_prefix),
            object_type="plane",
            parent_node="Head_02_Grp")
        pm.delete(pm.parentConstraint(self.proxy_up, up_ctrl_grp, mo=False))
        ctrl_list.append("{}_Up_Ctrl".format(mid_prefix))

        return ctrl_list

    def make_ctrl_work(self, ctrl_list):
        for ctrl in ctrl_list:
            jnt = "{}_Jnt".format(ctrl)
            pm.PyNode(ctrl).translate.connect(pm.PyNode(jnt).translate)
            pm.PyNode(ctrl).getParent().translate.connect(pm.PyNode(jnt).getParent().translate)
            pm.PyNode(ctrl).rotate.connect(pm.PyNode(jnt).rotate)
            pm.PyNode(ctrl).getParent().rotate.connect(pm.PyNode(jnt).getParent().rotate)
            pm.PyNode(ctrl).scale.connect(pm.PyNode(jnt).scale)
        # todo 鼻子的微表情


class MouthCreator(Creator):

    def __init__(self):
        super(MouthCreator, self).__init__()

        self.module_name = "Mouth_01"

        self.rig_root_node = ""  # group "World"

        self.up_base_curve = ""
        self.low_base_curve = ""
        self.up_tweak_surface = ""
        self.low_tweak_surface = ""
        self.up_out_curve = ""
        self.low_out_curve = ""

        self.mouth_surface = ""
        self.mouth_lip_sew_surface = ""

    def build_module(self):
        # self.master_control()
        # self.base_controls()
        #
        # self.follicle_on_mouth_surface()
        # self.base_follicle_jnt_grp()
        #
        # self.skin_base_curve()
        # self.corner_ctrl_connect_cpos_loc()
        # self.lip_ctrl_connect_ctrl_jnt()
        #
        # self.follicle_on_tweak_surface()
        # self.tweak_jnt_grp()
        # self.tweak_ctrl_grp()
        #
        # self.lip_sew_and_follicle()
        # self.skin_out_curve()
        #
        # self.use_dm_node_to_tweak_ctrl_parent_and_jnt_02_grp()
        # self.skin_tweak_surface()
        #
        # self.lip_sew_ctrl_drive_follicle_shape()
        #
        # self.make_bind_jnt_scale_work()
        #
        # self.jaw_deformer_and_control()
        # self.make_jaw_work()
        # self.static_corner_when_master_ctrl_move_up()
        # self.tongue_ctrl_grp()

        self.make_lip_roll()

        print(u"Build Done!")
        return

    def master_control(self):
        u"""嘴巴模块的主控制器

        创建嘴巴的主控制器，locator，还有一个毛囊

        :return: bool
        """

        prefix = "MD_{}".format(self.module_name)

        parameter = 0.5

        if not pm.objExists(self.up_base_curve):
            pm.error("{}丢失".format(self.up_base_curve))

        if not pm.objExists(self.low_base_curve):
            pm.error("{}丢失".format(self.low_base_curve))

        up_curve_center_position = point_on_curve_position(curve=self.up_base_curve, parameter=parameter)
        low_curve_center_position = point_on_curve_position(curve=self.low_base_curve, parameter=parameter)
        pos_x = (low_curve_center_position[0] + (up_curve_center_position[0] - low_curve_center_position[0]) / 2)
        pos_y = (low_curve_center_position[1] + (up_curve_center_position[1] - low_curve_center_position[1]) / 2)
        pos_z = (low_curve_center_position[2] + (up_curve_center_position[2] - low_curve_center_position[2]) / 2)
        offset = 4.0

        master_ctrl = "{}_Master_Ctrl".format(prefix)
        if not pm.objExists(master_ctrl):
            cyan_control(
                name=master_ctrl,
                shape_type="sphere",
                translate=(pos_x, pos_y, pos_z + offset),
                parent_node="MD_{}_Grp".format(self.module_name))

        master_ctrl_jnt = "{}_Jnt".format(master_ctrl)
        pm.select(cl=True)
        pm.joint(name=master_ctrl_jnt)
        pm.parent(master_ctrl_jnt, master_ctrl)
        pm.PyNode(master_ctrl_jnt).translate.set([0, 0, 0])

        custom_show_channel(master_ctrl, attr_list=["translateX", "translateY", "translateZ", "rotateZ"])

        # MD_Mouth_01_Master_Ctrl_Loc
        master_ctrl_loc = "MD_{}_Master_Ctrl_Loc".format(self.module_name)
        if not pm.objExists(master_ctrl_loc):
            cyan_locator_grp(
                name=master_ctrl_loc,
                translate=(pos_x, pos_y, pos_z + offset),
                parent_node="MD_{}_Deformer_Grp".format(self.module_name))

        if not pm.isConnected(pm.PyNode(master_ctrl).translate, pm.PyNode(master_ctrl_loc).translate):
            pm.PyNode(master_ctrl).translate.connect(pm.PyNode(master_ctrl_loc).translate, f=True)

        cpos = "MD_{}_Ctrl_CPOS".format(self.module_name)
        if not pm.objExists(cpos):
            pm.createNode("closestPointOnSurface", name=cpos)

        pm.PyNode(master_ctrl_loc).getShape().attr("worldPosition[0]").connect(pm.PyNode(cpos).attr("inPosition"))
        pm.PyNode(self.mouth_surface).getShape().attr("worldSpace[0]").connect(pm.PyNode(cpos).attr("inputSurface"))

        master_ctrl_follicle = "MD_{}_Master_Ctrl_Follicle".format(self.module_name)
        if not pm.objExists(master_ctrl_follicle):
            xd_follicle_node(name=master_ctrl_follicle,
                             worldMatrixInput=pm.PyNode(self.mouth_surface).getShape().attr("worldMatrix[0]"),
                             surfaceInput=pm.PyNode(self.mouth_surface).getShape().attr("local"),
                             paramVInput=pm.PyNode(cpos).attr("parameterV"),
                             paramUInput=pm.PyNode(cpos).attr("parameterU"),
                             parentNode="MD_{}_Grp".format(self.module_name))

        ctrl_null_grp = "{}_Master_Ctrl_Null_Grp".format(prefix)
        if not pm.objExists(ctrl_null_grp):
            pm.createNode("transform", name=ctrl_null_grp, p=master_ctrl_follicle)
        follicle_rotate = pm.PyNode(master_ctrl_follicle).rotate.get()
        pm.PyNode(ctrl_null_grp).rotate.set([follicle_rotate[1] * -1, 0, follicle_rotate[2] * -1])

        ctrl_null = "{}_Master_Ctrl_Null".format(prefix)
        if not pm.objExists(ctrl_null):
            pm.createNode("transform", name=ctrl_null, p=ctrl_null_grp)

        pm.PyNode(master_ctrl).translateZ.connect(pm.PyNode(ctrl_null).translateZ)
        pm.PyNode(master_ctrl).rotateZ.connect(pm.PyNode(ctrl_null).rotateZ)

        pm.spaceLocator(name="M_Mouth_Move_Loc")
        pm.parent("M_Mouth_Move_Loc", ctrl_null_grp)
        pm.PyNode("M_Mouth_Move_Loc").translate.set([0, 0, 0])
        pm.PyNode("M_Mouth_Move_Loc").rotate.set([0, 0, 0])

        print(u"Master ctrl创建完毕")
        return True

    def base_controls(self):
        u"""创建嘴巴的基础控件

        这个方法需要依靠 base curve 曲线为控件进行定位
        :return:
        """
        prefix = "MD_{}".format(self.module_name)

        if not pm.objExists(self.up_base_curve) or not pm.objExists(self.low_base_curve):
            pm.error(u"场景中没有找到Base curve")

        master_follicle = "{}_Master_Ctrl_Follicle".format(prefix)

        base_ctrl_grp = "{}_Base_Ctrl_Grp".format(prefix)
        if not pm.objExists(base_ctrl_grp):
            pm.createNode("transform", name=base_ctrl_grp)
            if pm.objExists("{}_Grp".format(prefix)):
                pm.parent(base_ctrl_grp, "{}_Grp".format(prefix))
        pm.delete(pm.pointConstraint(master_follicle, base_ctrl_grp))

        master_ctrl = "{}_Master_Ctrl".format(prefix)
        if not pm.attributeQuery("localScale", node=master_ctrl, ex=True):
            pm.addAttr(master_ctrl, ln="localScale", at="double", min=0.01, dv=1)
            pm.setAttr("{}.localScale".format(master_ctrl), e=True, k=True)
        pm.PyNode(master_ctrl).attr("localScale").connect(pm.PyNode(base_ctrl_grp).scaleX)
        pm.PyNode(master_ctrl).attr("localScale").connect(pm.PyNode(base_ctrl_grp).scaleY)
        pm.PyNode(master_ctrl).attr("localScale").connect(pm.PyNode(base_ctrl_grp).scaleZ)

        master_ctrl_null = "{}_Master_Ctrl_Null".format(prefix)
        pm.parentConstraint(master_ctrl_null, base_ctrl_grp, mo=True)

        # MD_Mouth_01_Base_Ctrl_Out_Grp
        base_ctrl_out_grp = "{}_Base_Ctrl_Out_Grp".format(prefix)
        base_loc_grp = "{}_Base_Loc_Grp".format(prefix)
        base_follicle_grp = "{}_Base_Follicle_Grp".format(prefix)
        if not pm.objExists(base_ctrl_out_grp):
            pm.createNode("transform", name=base_ctrl_out_grp)
            pm.parent(base_ctrl_out_grp, "{}_Deformer_Grp".format(prefix))
            pm.delete(pm.pointConstraint(master_follicle, base_ctrl_out_grp))

            # MD_Mouth_01_Base_Loc_Grp
            if not pm.objExists(base_loc_grp):
                pm.createNode("transform", name=base_loc_grp, p=base_ctrl_out_grp)
            # MD_Mouth_01_Base_Follicle_Grp
            if not pm.objExists(base_follicle_grp):
                pm.createNode("transform", name=base_follicle_grp)
                pm.parent(base_follicle_grp, base_ctrl_out_grp)
                pm.PyNode(base_follicle_grp).translate.set([0, 0, 0])
                pm.makeIdentity(base_follicle_grp, apply=True, t=1, r=1, s=1, n=0, pn=1)
                pm.PyNode(base_follicle_grp).attr("inheritsTransform").set(0)

        # 左右嘴角的控制器
        for item in ["LF", "RT"]:
            prefix = "{}_{}".format(item, self.module_name)

            temp_loc_name = "{}_temp_Loc".format(item)
            temp_loc = pm.spaceLocator(name=temp_loc_name)
            mp_name = "{}_temp_MP".format(item)
            mp = mp_node(node_name=mp_name,
                         geometry_path_input=pm.PyNode(self.up_base_curve).getShape().attr("worldSpace[0]"),
                         all_coordinates_output=temp_loc.translate)
            pm.PyNode(mp).rotateX.connect(pm.PyNode(temp_loc).rotateX)
            pm.PyNode(mp).rotateY.connect(pm.PyNode(temp_loc).rotateY)
            pm.PyNode(mp).rotateZ.connect(pm.PyNode(temp_loc).rotateZ)

            if item == "LF":
                parameter = 0.0
                pm.PyNode(mp).attr("uValue").set(parameter)
                pm.disconnectAttr(
                    pm.PyNode(self.up_base_curve).getShape().attr("worldSpace[0]"), pm.PyNode(mp).attr("geometryPath"))
                pm.delete(mp_name)
                pm.PyNode(temp_loc).rotateX.set(0)
                #     pm.PyNode(temp_loc).rotateX.set(pm.PyNode(temp_loc).rotateX.get()+90)
                pm.PyNode(temp_loc).rotateZ.set(0)
            else:
                parameter = 1.0
                pm.PyNode(mp).attr("uValue").set(parameter)
                pm.disconnectAttr(
                    pm.PyNode(self.up_base_curve).getShape().attr("worldSpace[0]"), pm.PyNode(mp).attr("geometryPath"))
                pm.delete(mp_name)
                pm.PyNode(temp_loc).scaleX.set(-1)
                pm.PyNode(temp_loc).rotateX.set(0)
                current_rotate = pm.PyNode(temp_loc).rotateY.get()
                pm.PyNode(temp_loc).rotateY.set(current_rotate + 270.0)
                pm.PyNode(temp_loc).rotateZ.set(0)

            control_name = "{}_Ctrl".format(prefix)
            if not pm.objExists(control_name):
                ctrl_grp = yellow_component(name=control_name,
                                            shape_type="nurbsPlane",
                                            parent_node=base_ctrl_grp,
                                            have_jnt=True)
                pm.delete(pm.parentConstraint(temp_loc, ctrl_grp, mo=False))
                pm.delete(pm.scaleConstraint(temp_loc, ctrl_grp, mo=False))
            ctrl_loc = "{}_Ctrl_Loc".format(prefix)
            if not pm.objExists(ctrl_loc):
                ctrl_loc_grp = yellow_component(name=ctrl_loc, shape_type="locator", parent_node=base_loc_grp)
                pm.delete(pm.parentConstraint(temp_loc, ctrl_loc_grp, mo=False))
                pm.delete(pm.scaleConstraint(temp_loc, ctrl_loc_grp, mo=False))

            pm.delete(temp_loc)

        # 上下嘴唇的控制器
        for item in ["Up", "Low"]:
            prefix = "{}_{}".format(item, self.module_name)
            parameter = 0.5
            if item == "Up":
                curve = self.up_base_curve
            else:
                curve = self.low_base_curve
            if not pm.objExists("{}_Ctrl".format(prefix)):
                yellow_component(name="{}_Ctrl".format(prefix), shape_type="nurbsPlane",
                                 translate=point_on_curve_position(curve=curve, parameter=parameter),
                                 parent_node=base_ctrl_grp)

        if not pm.isConnected(pm.PyNode(base_ctrl_grp).translate, pm.PyNode(base_ctrl_out_grp).translate):
            pm.PyNode(base_ctrl_grp).translate.connect(pm.PyNode(base_ctrl_out_grp).translate)

        if not pm.isConnected(pm.PyNode(base_ctrl_grp).rotate, pm.PyNode(base_ctrl_out_grp).rotate):
            pm.PyNode(base_ctrl_grp).rotate.connect(pm.PyNode(base_ctrl_out_grp).rotate)

        if not pm.isConnected(pm.PyNode(base_ctrl_grp).scale, pm.PyNode(base_loc_grp).scale):
            pm.PyNode(base_ctrl_grp).scale.connect(pm.PyNode(base_loc_grp).scale)

        print(u"Base controls已经被创建")
        return True

    def follicle_on_mouth_surface(self):
        u"""左右嘴角，上下嘴唇中部一共四个毛囊

        执行这个方法之前需要先创建相应locator，毛囊需要利用这些locator进行定位

        求出locator（为控制嘴唇整体的三根骨骼进行定位）在mouth surface上面的位置（参数U，V），
        然后将这个位置信息与控制嘴角骨骼的毛囊体的参数 U 和 V 进行连接，
        毛囊体会根据参数移动到相应的位置，
        这样控制了locator， 就控制了毛囊体，也就间接的控制了骨骼
        """
        mouth_surface_shape = pm.PyNode(self.mouth_surface).getShape()
        follicle_list = []
        for side in ["LF", "RT", "MD"]:
            prefix = "{}_{}".format(side, self.module_name)

            if side == "MD":
                # MD_Mouth_01_Master_Ctrl_Loc
                corner_locator = "{}_Master_Ctrl_Loc".format(prefix)
            else:
                # LF_Mouth_01_Ctrl_Loc
                corner_locator = "{}_Ctrl_Loc".format(prefix)

            cpos_node = "{}_Ctrl_CPOS".format(prefix)
            if not pm.objExists(cpos_node):
                cpos_node = pm.createNode("closestPointOnSurface", name=cpos_node)

            corner_locator_shape = pm.PyNode(corner_locator).getShape()
            if not pm.isConnected(corner_locator_shape.attr("worldPosition[0]"),
                                  pm.PyNode(cpos_node).attr("inPosition")):
                corner_locator_shape.attr("worldPosition[0]").connect(cpos_node.attr("inPosition"), f=True)
            if not pm.isConnected(mouth_surface_shape.attr("worldSpace[0]"),
                                  pm.PyNode(cpos_node).attr("inputSurface")):
                mouth_surface_shape.attr("worldSpace[0]").connect(cpos_node.attr("inputSurface"), f=True)

            if side == "MD":
                follicle_name = "{}_Master_Ctrl_Follicle".format(prefix)
                if not pm.objExists(follicle_name):
                    xd_follicle_node(
                        name=follicle_name,
                        worldMatrixInput=mouth_surface_shape.attr("worldMatrix[0]"),
                        surfaceInput=mouth_surface_shape.attr("local"),
                        paramUInput=pm.PyNode(cpos_node).attr("parameterU"),
                        paramVInput=pm.PyNode(cpos_node).attr("parameterV"),
                        outTranslateToParent=True,
                        outRotateToParent=True,
                        parentNode="MD_{}_Grp".format(self.module_name))
                follicle_list.append(follicle_name)
            else:
                follicle_name = "{}_Ctrl_Jnt_Follicle".format(prefix)
                if not pm.objExists(follicle_name):
                    xd_follicle_node(
                        name=follicle_name,
                        worldMatrixInput=mouth_surface_shape.attr("worldMatrix[0]"),
                        surfaceInput=mouth_surface_shape.attr("local"),
                        paramUInput=pm.PyNode(cpos_node).attr("parameterU"),
                        paramVInput=pm.PyNode(cpos_node).attr("parameterV"),
                        outTranslateToParent=True,
                        outRotateToParent=True,
                        parentNode="MD_{}_Base_Follicle_Grp".format(self.module_name))
                follicle_list.append(follicle_name)
        print(u"已经创建毛囊体：{}".format(follicle_list))
        return follicle_list

    def base_follicle_jnt_grp(self):
        u"""利用mouth surface定位毛囊，

        并利用毛囊的位移节点（父节点）对控制嘴唇的骨骼的组节点进行目标约束
        """

        base_ctrl_group = "MD_{}_Base_Ctrl_Grp".format(self.module_name)
        check_list = []
        for item in ["Up", "Low"]:
            # Up_Mouth_01_Ctrl_Jnt or Low_Mouth_01_Ctrl_Jnt
            aim_jnt = "{}_{}_Ctrl_Jnt".format(item, self.module_name)
            check_list.append(aim_jnt)

            if item == "Up":
                base_curve = self.up_base_curve
            else:
                base_curve = self.low_base_curve

            if not pm.objExists(aim_jnt):
                yellow_component(name=aim_jnt,
                                 shape_type="joint",
                                 translate=point_on_curve_position(base_curve, 0.5),
                                 parent_node="MD_{}_Base_Ctrl_Out_Grp".format(self.module_name))

            item_ctrl = "{}_{}_Ctrl".format(item, self.module_name)
            pm.PyNode(item_ctrl).translate.connect(pm.PyNode(aim_jnt).rotate)

            item_md_node = "{}_{}_Ctrl_Scale_MD".format(item, self.module_name)
            if not pm.objExists(item_md_node):
                pm.createNode("multiplyDivide", name=item_md_node)
            pm.PyNode(item_md_node).attr("operation").set(1)
            pm.PyNode(item_ctrl).translate.connect(pm.PyNode(item_md_node).attr("input1"))
            pm.PyNode(base_ctrl_group).scale.connect(pm.PyNode(item_md_node).attr("input2"))
            pm.PyNode(item_md_node).attr("output").connect(pm.PyNode(aim_jnt).translate)

            for side in ["LF", "RT"]:
                if side == "LF":
                    flip_up = -1.0
                else:
                    flip_up = 1.0

                # LF_Mouth_01_Ctrl_Jnt_Follicle or RT_Mouth_01_Ctrl_Jnt_Follicle
                corner_follicle = "{}_{}_Ctrl_Jnt_Follicle".format(side, self.module_name)
                # LF_Mouth_01_Up_Jnt or RT_Mouth_01_Up_Jnt
                corner_jnt = "{}_{}_Ctrl_{}_Jnt".format(side, self.module_name, item)
                corner_jnt_grp = "{}_Grp".format(corner_jnt)
                if not pm.objExists(corner_jnt):
                    corner_jnt_grp = jnt_or_control_grp(name=corner_jnt, parent_node=corner_follicle)

                check_list.append(corner_jnt)

                if not check_constraint(corner_follicle, corner_jnt_grp):
                    pm.aimConstraint(
                        corner_follicle, corner_jnt_grp,
                        aimVector=[0, 0, -1],
                        upVector=[0, 1 * flip_up, 0],
                        worldUpType="object",
                        worldUpObject=aim_jnt,
                        mo=False)
        print(u"已经创建{}".format(check_list))
        return True

    def skin_base_curve(self):
        vertical_list = ["Up", "Low"]
        for vertical in vertical_list:
            if vertical == "Up":
                base_curve = self.up_base_curve
            else:
                base_curve = self.low_base_curve

            base_curve_skin_items = ["{}_Mouth_01_Ctrl_Jnt".format(vertical), base_curve]
            for side in ["LF", "RT"]:
                base_curve_skin_items.append("{}_{}_Ctrl_{}_Jnt".format(side, self.module_name, vertical))
            skin_node = "MD_{}_{}_Base_Curve_SC".format(self.module_name, vertical)
            if not pm.objExists(skin_node):
                pm.skinCluster(base_curve_skin_items, tsb=True, name=skin_node)
        print(u"skin_base_curve已经执行完毕".format())
        return True

    def corner_ctrl_connect_cpos_loc(self):
        u"""将左右嘴角控制器与cpos（嘴角位置定位loc）连接起来"""
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)
            # cpos_locs = ["LF_Mouth_01_Ctrl_Loc", "RT_Mouth_01_Ctrl_Loc"]
            # for cpos_loc in cpos_locs:
            cpos_loc = "{}_Ctrl_Loc".format(prefix)
            corner_ctrl = pm.PyNode(cpos_loc.replace("_Loc", ""))
            if not pm.isConnected(pm.PyNode(corner_ctrl).translate, pm.PyNode(cpos_loc).translate):
                pm.PyNode(corner_ctrl).translate.connect(pm.PyNode(cpos_loc).translate, f=True)
        print("corner_ctrl_connect_cpos_loc done!")
        return True

    def master_ctrl_null_grp(self, parent_node, translate_clean=False, rotate_clean=False):
        master_ctrl = pm.PyNode("MD_{}_Master_Ctrl".format(self.module_name))

        ctrl_null_grp = "MD_{}_Master_Ctrl_Null_Grp".format(self.module_name)
        if not pm.objExists(ctrl_null_grp):
            pm.createNode(
                "transform", name="MD_{}_Master_Ctrl_Null_Grp".format(self.module_name))
            pm.createNode(
                "transform", name="MD_{}_Master_Ctrl_Null".format(self.module_name))
            pm.spaceLocator(name="M_Mouth_Move_Loc")
            pm.parent(
                "MD_{}_Master_Ctrl_Null".format(
                    self.module_name), "M_Mouth_Move_Loc",
                "MD_{}_Master_Ctrl_Null_Grp".format(self.module_name)
            )
        if parent_node is not None:
            pm.parent("MD_{}_Master_Ctrl_Null_Grp".format(
                self.module_name), parent_node)
            pm.PyNode("MD_{}_Master_Ctrl_Null_Grp".format(
                self.module_name)).translate.set([0, 0, 0])

        if translate_clean:
            pm.PyNode("MD_{}_Master_Ctrl_Null_Grp".format(
                self.module_name)).translate.set([0, 0, 0])

        if rotate_clean:
            pm.PyNode("MD_{}_Master_Ctrl_Null_Grp".format(
                self.module_name)).rotate.set([0, 0, 0])

        return True

    def lip_ctrl_connect_ctrl_jnt(self):
        u"""连接嘴唇控制器"""

        # 用于修正 MD_Mouth_01_Base_Ctrl_Grp的轴心位置
        mouth_center_follicle = "MD_{}_Master_Ctrl_Follicle".format(self.module_name)
        # MD_Mouth_01_Base_Ctrl_Grp
        base_ctrl_grp = pm.PyNode("MD_{}_Base_Ctrl_Grp".format(self.module_name))

        # MD_Mouth_01_Master_Ctrl_Null
        master_ctrl_null = "MD_{}_Master_Ctrl_Null".format(self.module_name)
        if not pm.objExists(master_ctrl_null):
            self.master_ctrl_null_grp(parent_node=mouth_center_follicle, translate_clean=True)

        if not check_constraint(master_ctrl_null, base_ctrl_grp):
            pm.parentConstraint(master_ctrl_null, base_ctrl_grp, mo=True)

        # Up_Mouth_01_Ctrl_Jnt
        for ctrl_jnt in ["Up_{}_Ctrl_Jnt".format(self.module_name), "Low_{}_Ctrl_Jnt".format(self.module_name)]:
            ctrl = pm.PyNode(ctrl_jnt.replace("_Jnt", ""))
            md_node = ctrl_jnt.replace("_Jnt", "_Scale_MD")

            if not pm.objExists(md_node):
                pm.createNode("multiplyDivide", name=md_node)
                pm.PyNode(md_node).attr("operation").set(1)
                if not pm.isConnected(ctrl.attr("translate"), pm.PyNode(md_node).attr("input1")):
                    ctrl.attr("translate").connect(pm.PyNode(md_node).attr("input1"))
                if not pm.isConnected(base_ctrl_grp.attr("scale"), pm.PyNode(md_node).attr("input2")):
                    base_ctrl_grp.attr("scale").connect(pm.PyNode(md_node).attr("input2"))
                if not pm.isConnected(pm.PyNode(md_node).attr("output"), "{}.translate".format(ctrl_jnt)):
                    pm.PyNode(md_node).attr("output").connect("{}.translate".format(ctrl_jnt))

            if not pm.isConnected(ctrl.rotate, "{}.rotate".format(ctrl_jnt)):
                ctrl.rotate.connect("{}.rotate".format(ctrl_jnt), f=True)

        # 连接base ctrl grp， 让嘴巴的模块控制器能够工作
        mouth_master_ctrl = pm.PyNode("MD_{}_Master_Ctrl".format(self.module_name))
        # print(u"开始调整通道栏显示属性")
        # custom_show_channel(mouth_master_ctrl, attr_list=["translateX", "translateY", "translateZ", "rotateZ"])

        if not pm.attributeQuery("localScale", node=mouth_master_ctrl, ex=True):
            pm.addAttr(mouth_master_ctrl, ln="localScale", at="double", min=0.01, dv=1)
            pm.setAttr("{}.localScale".format(mouth_master_ctrl), e=True, k=True)

        if not pm.isConnected(mouth_master_ctrl.attr("localScale"), base_ctrl_grp.scaleX):
            mouth_master_ctrl.attr("localScale").connect(base_ctrl_grp.scaleX, f=True)
        if not pm.isConnected(mouth_master_ctrl.attr("localScale"), base_ctrl_grp.scaleY):
            mouth_master_ctrl.attr("localScale").connect(base_ctrl_grp.scaleY, f=True)
        if not pm.isConnected(mouth_master_ctrl.attr("localScale"), base_ctrl_grp.scaleZ):
            mouth_master_ctrl.attr("localScale").connect(base_ctrl_grp.scaleZ, f=True)

        if not pm.isConnected(mouth_master_ctrl.attr("translateZ"), pm.PyNode(master_ctrl_null).translateZ):
            mouth_master_ctrl.attr("translateZ").connect(pm.PyNode(master_ctrl_null).translateZ)
        if not pm.isConnected(mouth_master_ctrl.attr("rotateZ"), pm.PyNode(master_ctrl_null).rotateZ):
            mouth_master_ctrl.attr("rotateZ").connect(pm.PyNode(master_ctrl_null).rotateZ)

        # 修正 MD_Mouth_01_Base_Ctrl_Out_Grp 的轴心位置
        base_ctrl_out_grp = pm.PyNode("MD_{}_Base_Ctrl_Out_Grp".format(self.module_name))

        if not pm.isConnected(base_ctrl_grp.translate, base_ctrl_out_grp.translate):
            base_ctrl_grp.translate.connect(base_ctrl_out_grp.translate)
        if not pm.isConnected(base_ctrl_grp.rotate, base_ctrl_out_grp.rotate):
            base_ctrl_grp.rotate.connect(base_ctrl_out_grp.rotate)

        base_loc_grp = "MD_{}_Base_Loc_Grp".format(self.module_name)
        if not pm.isConnected(pm.PyNode(base_ctrl_grp).scale, pm.PyNode(base_loc_grp).scale):
            pm.PyNode(base_ctrl_grp).scale.connect(pm.PyNode(base_loc_grp).scale, f=True)

        print("lip_ctrl_connect_ctrl_jnt done!")
        return True

    def rig_base_ctrl_out(self):
        self.skin_base_curve()
        self.corner_ctrl_connect_cpos_loc()
        self.lip_ctrl_connect_ctrl_jnt()

    def follicle_on_tweak_surface(self):
        # 嘴唇一侧的段数，例如上嘴唇左侧为5段，右侧也为5段，加上左右嘴角，
        # 那么控制上嘴唇的骨骼数就是 5+5+2=12
        bind_jnt_follicle_grp = "MD_{}_Bind_Jnt_Follicle_Grp".format(self.module_name)
        if not pm.objExists(bind_jnt_follicle_grp):
            pm.createNode("transform", name=bind_jnt_follicle_grp, p="MD_{}_Deformer_Grp".format(self.module_name))

        segment = 5
        parameter_u = 0.5
        parameter_v = 0
        for location in ["Up", "Low"]:
            tweak_surface = pm.PyNode("MD_{}_{}_Tweak_Surface".format(self.module_name, location))
            for side in ["LF", "RT"]:
                if side == "LF":
                    parameter_v = 0
                elif side == "RT":
                    parameter_v = 1

                if location == "Up":
                    corner_follicle = "{}_{}_Lip_Jnt_Follicle".format(side, self.module_name)
                    if not pm.objExists(corner_follicle):
                        corner_follicle = xd_follicle_node(
                            name="{}_{}_Lip_Jnt_Follicle".format(side, self.module_name),
                            worldMatrixInput=tweak_surface.getShape().attr("worldMatrix[0]"),
                            surfaceInput=tweak_surface.getShape().attr("local"),
                            parentNode=bind_jnt_follicle_grp)
                    pm.PyNode(corner_follicle).getShape().attr("parameterU").set(parameter_u)
                    pm.PyNode(corner_follicle).getShape().attr("parameterV").set(parameter_v)

                for index in range(1, segment + 1):
                    lip_follicle = "{}_Mouth_01_{}Lip_{}_Jnt_Follicle".format(side, location, "{0:02d}".format(index))
                    if not pm.objExists(lip_follicle):
                        lip_follicle = xd_follicle_node(
                            name="{}_Mouth_01_{}Lip_{}_Jnt_Follicle".format(side, location, "{0:02d}".format(index)),
                            worldMatrixInput=tweak_surface.getShape().attr("worldMatrix[0]"),
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
                        parameter_v = 1 - pm.getAttr("LF_{}_{}Lip_{}_Jnt_FollicleShape.parameterV".format(
                            self.module_name, location, "{0:02d}".format(index)))
                        lip_follicle_shape.attr("parameterV").set(parameter_v)
        print("follicle_on_tweak_surface Done")
        return True

    def tweak_jnt_grp(self):
        segment = 3

        master_ctrl = "MD_{}_Master_Ctrl".format(self.module_name)
        # evenTweak
        if not pm.attributeQuery("evenTweak", node=master_ctrl, ex=True):
            pm.addAttr(master_ctrl, ln="evenTweak", at="double", min=0, max=1, dv=1)
            pm.setAttr("{}.evenTweak".format(master_ctrl), e=True, k=True)

        # MD_Mouth_01_Tweak_Jnt_Grp
        tweak_jnt_grp = "MD_{}_Tweak_Jnt_Grp".format(self.module_name)
        if not pm.objExists(tweak_jnt_grp):
            pm.createNode("transform", name=tweak_jnt_grp, p="MD_{}_Deformer_Grp".format(self.module_name))

        bind_jnt_ori_null = "MD_{}_Bind_Jnt_Ori_Null".format(self.module_name)
        if not pm.objExists(bind_jnt_ori_null):
            pm.parent(pm.createNode('transform', name=bind_jnt_ori_null), "MD_{}_Grp".format(self.module_name))

        pm.parentConstraint("MD_{}_Master_Ctrl_Null".format(self.module_name), bind_jnt_ori_null, mo=False)

        for location in ["Up", "Low"]:
            base_curve = "MD_{}_{}_Base_Curve".format(self.module_name, location)
            for side in ["LF", "RT"]:
                for index in range(1, segment + 1):
                    jnt = "{}_Mouth_01_{}Tweak_{}_Ctrl_Jnt".format(side, location, "{0:02d}".format(index))
                    jnt_grp = "{}_Grp".format(jnt)
                    if not pm.objExists(jnt):
                        jnt_grp = yellow_component(
                            name="{}_Mouth_01_{}Tweak_{}_Ctrl_Jnt".format(side, location, "{0:02d}".format(index)),
                            shape_type="joint",
                            parent_node=tweak_jnt_grp,
                            have_loc=True)

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
                        lf_mp_node2 = "LF_Mouth_01_{}Tweak_{}_Ctrl_Jnt_02_MP".format(location, "{0:02d}".format(index))
                        u_value = 1 - pm.getAttr("{}.uValue".format(lf_mp_node2))
                        pm.PyNode(mp_node).attr("uValue").set(u_value)
                        pm.PyNode(mp_node2).attr("uValue").set(u_value)
                        pm.PyNode(mp_node2).attr("fractionMode").set(True)
                    pm.PyNode(base_curve).getShape().attr("worldSpace[0]").connect(
                        pm.PyNode(mp_node).attr("geometryPath"))
                    pm.PyNode(base_curve).getShape().attr("worldSpace[0]").connect(
                        pm.PyNode(mp_node2).attr("geometryPath"))

                    bc_node = jnt_grp.replace("_Grp", "_MP_BC")
                    if not pm.objExists(bc_node):
                        pm.createNode("blendColors", name=bc_node)
                    pm.PyNode(mp_node).attr("allCoordinates").connect(pm.PyNode(bc_node).attr("color1"))
                    pm.PyNode(mp_node2).attr("allCoordinates").connect(pm.PyNode(bc_node).attr("color2"))
                    pm.PyNode(master_ctrl).attr("evenTweak").connect(pm.PyNode(bc_node).attr("blender"))
                    pm.PyNode(bc_node).attr("output").connect(pm.PyNode(jnt_grp).translate)

                    pm.PyNode(bind_jnt_ori_null).rotate.connect(pm.PyNode(jnt_grp).rotate)

                # 左右嘴角
                if location == "Up":
                    jnt = "{}_{}_Tweak_Ctrl_Jnt".format(side, self.module_name)
                    jnt_grp = "{}_Grp".format(jnt)
                    if not pm.objExists(jnt):
                        jnt_grp = yellow_component(
                            name="{}_{}_Tweak_Ctrl_Jnt".format(side, self.module_name),
                            shape_type="joint",
                            parent_node=tweak_jnt_grp,
                            have_loc=True
                        )

                    mp_node = jnt_grp.replace("_Grp", "_MP")
                    if not pm.objExists(mp_node):
                        pm.createNode("motionPath", name=mp_node)
                    pm.PyNode(mp_node).attr("allCoordinates").connect(pm.PyNode(jnt_grp).translate)

                    pm.PyNode(bind_jnt_ori_null).rotate.connect(pm.PyNode(jnt_grp).rotate)

                    if side == "LF":
                        pm.PyNode(mp_node).attr("uValue").set(0)
                    else:
                        pm.PyNode(mp_node).attr("uValue").set(1)

                    pm.PyNode(base_curve).getShape().attr("worldSpace[0]").connect(
                        pm.PyNode(mp_node).attr("geometryPath"))

        return True

    def tweak_ctrl_grp(self):
        segment = 3

        master_ctrl_null = "MD_{}_Master_Ctrl_Null".format(self.module_name)
        module_grp = "MD_{}_Grp".format(self.module_name)
        deformer_grp = "MD_{}_Deformer_Grp".format(self.module_name)

        tweak_ctrl_grp = "MD_{}_Tweak_Ctrl_Grp".format(self.module_name)
        if not pm.objExists(tweak_ctrl_grp):
            pm.createNode("transform", name=tweak_ctrl_grp, p=module_grp)
        pm.PyNode(tweak_ctrl_grp).attr("inheritsTransform").set(0)

        tweak_ori_null = "MD_{}_Tweak_Ori_Null".format(self.module_name)
        if not pm.objExists(tweak_ori_null):
            pm.createNode("transform", name=tweak_ori_null, p=tweak_ctrl_grp)

        if not check_constraint(tweak_ori_null, master_ctrl_null):
            pm.parentConstraint(master_ctrl_null, tweak_ori_null, mo=True)

        scale_null = "MD_{}_Scale_Null".format(self.module_name)
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
                    # LF_Mouth_01_UpTweak_01_Ctrl_Grp
                    ctrl_name = "{}_Mouth_01_{}Tweak_{}_Ctrl".format(side, location, "{0:02d}".format(index))
                    ctrl_grp = "{}_Grp".format(ctrl_name)
                    if not pm.objExists(ctrl_name):
                        ctrl_grp = yellow_component(
                            name=ctrl_name,
                            shape_type="sphere",
                            parent_node=tweak_ctrl_grp)

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
                            "LF_Mouth_01_{}Tweak_{}_Ctrl_MP.uValue".format(location, "{0:02d}".format(index)))
                        pm.PyNode(mp_node).attr("uValue").set(1 - u_value)

                    pm.PyNode(outer_curve).getShape().attr("worldSpace[0]").connect(
                        pm.PyNode(mp_node).attr("geometryPath"))
                    pm.PyNode(mp_node).attr("allCoordinates").connect(
                        pm.PyNode(ctrl_grp).attr("translate"))

                    pm.PyNode(tweak_ori_null).rotate.connect(
                        pm.PyNode(ctrl_grp).rotate)
                    pm.PyNode(scale_null).scale.connect(
                        pm.PyNode(ctrl_grp).scale)

                if location == "Up":
                    ctrl = "{}_Mouth_01_Tweak_Ctrl".format(side)
                    ctrl_grp = "{}_Grp".format(ctrl)
                    if not pm.objExists(ctrl):
                        ctrl_grp = yellow_component(name=ctrl, shape_type="sphere", parent_node=tweak_ctrl_grp)

                    mp_node = ctrl_grp.replace("_Grp", "_MP")
                    if not pm.objExists(mp_node):
                        pm.createNode("motionPath", name=mp_node)

                    pm.PyNode(outer_curve).getShape().attr("worldSpace[0]").connect(
                        pm.PyNode(mp_node).attr("geometryPath"))
                    pm.PyNode(mp_node).attr("allCoordinates").connect(pm.PyNode(ctrl_grp).translate)

                    if side == "LF":
                        pm.PyNode(mp_node).attr("uValue").set(0)
                    else:
                        pm.PyNode(mp_node).attr("uValue").set(1)

                    pm.PyNode("MD_{}_Tweak_Ori_Null".format(self.module_name)).rotate.connect(
                        pm.PyNode(ctrl_grp).rotate)
                    pm.PyNode("MD_{}_Scale_Null".format(self.module_name)).scale.connect(pm.PyNode(ctrl_grp).scale)

        base_ctrl_grp = "MD_{}_Base_Ctrl_Grp".format(self.module_name)
        if not check_constraint(scale_null, base_ctrl_grp):
            pm.scaleConstraint(base_ctrl_grp, scale_null, mo=True)
        if not check_constraint(tweak_ori_null, master_ctrl_null):
            pm.parentConstraint(master_ctrl_null, tweak_ori_null, mo=True)

        print("tweak_ctrl_grp done")

        return True

    def location_bind_jnt(self, jnt_grp="", jnt_type="lip", side="LF", index=1):
        u"""对bind_grp进行定位

        :param jnt_grp:
        :param jnt_type:
        :return:
        """
        master_ctrl = "MD_{}_Master_Ctrl".format(self.module_name)

        if jnt_type == "lip":
            # 位移部分
            translate_bc_node = (jnt_grp.replace('_Grp', '_Translate_BC'))
            if not pm.objExists(translate_bc_node):
                pm.createNode("blendColors", name=translate_bc_node)
            if "UpLip" in jnt_grp:
                up_follicle_shape = jnt_grp.replace("_Grp", "_FollicleShape")
                low_follicle_shape = up_follicle_shape.replace(
                    "UpLip", "LowLip")
            else:
                low_follicle_shape = jnt_grp.replace("_Grp", "_FollicleShape")
                up_follicle_shape = low_follicle_shape.replace(
                    "LowLip", "UpLip")

            pm.PyNode(up_follicle_shape).attr("outTranslate").connect(
                pm.PyNode(translate_bc_node).attr("color1"), f=True)
            pm.PyNode(low_follicle_shape).attr("outTranslate").connect(
                pm.PyNode(translate_bc_node).attr("color2"), f=True)
            pm.PyNode(translate_bc_node).attr("output").connect(
                pm.PyNode(jnt_grp).translate, f=True)

            lf_sew_follicle_shape = (
                "LF_{}_LipSew_Ctrl_FollicleShape".format(self.module_name))
            rt_sew_follicle_shape = (
                "RT_{}_LipSew_Ctrl_FollicleShape".format(self.module_name))

            sew_sr_node = (jnt_grp.replace("_Grp", "_LipSew_SR"))

            if not pm.objExists(sew_sr_node):
                pm.createNode("setRange", name=sew_sr_node)
                pm.PyNode(sew_sr_node).attr("minY").set(0.5)
                pm.PyNode(sew_sr_node).attr("maxX").set(0.5)
                if side == "LF":
                    pm.PyNode(sew_sr_node).attr(
                        "oldMinX").set(0.5 - index * 0.1)
                    pm.PyNode(sew_sr_node).attr(
                        "oldMinY").set(0.5 - index * 0.1)
                    pm.PyNode(sew_sr_node).attr(
                        "oldMaxX").set(0.5 + 0.1 - index * 0.1)
                    pm.PyNode(sew_sr_node).attr(
                        "oldMaxY").set(0.5 + 0.1 - index * 0.1)
                else:
                    pm.PyNode(sew_sr_node).attr(
                        "oldMinX").set(0.5 - 0.1 + index * 0.1)
                    pm.PyNode(sew_sr_node).attr(
                        "oldMinY").set(0.5 - 0.1 + index * 0.1)
                    pm.PyNode(sew_sr_node).attr(
                        "oldMaxX").set(0.5 + index * 0.1)
                    pm.PyNode(sew_sr_node).attr(
                        "oldMaxY").set(0.5 + index * 0.1)
            pm.PyNode(lf_sew_follicle_shape).attr("parameterU").connect(
                pm.PyNode(sew_sr_node).attr("valueX"), f=True)
            pm.PyNode(rt_sew_follicle_shape).attr("parameterU").connect(
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
                    pm.PyNode(translate_bc_node).attr("blender"), f=True)
            else:
                pm.PyNode(cmp_node).attr("outputR").connect(
                    pm.PyNode(translate_bc_node).attr("blender"), f=True)

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
                pm.createNode("fourByFourMatrix", name=side_jnt_FBFM_node)

            pm.PyNode(side_jnt_vp).attr("outputX").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in20"), f=True)
            pm.PyNode(side_jnt_vp).attr("outputY").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in21"), f=True)
            pm.PyNode(side_jnt_vp).attr("outputZ").connect(
                pm.PyNode(side_jnt_FBFM_node).attr("in22"), f=True)

            ctrl_null_vp = "MD_{}_Master_Ctrl_Null_VP".format(
                self.module_name)
            if not pm.objExists(ctrl_null_vp):
                pm.createNode("vectorProduct", name=ctrl_null_vp)
                pm.PyNode(ctrl_null_vp).attr("operation").set(3)
                pm.PyNode("MD_{}_Base_Ctrl_Out_Grp".format(self.module_name)).attr("worldMatrix[0]").connect(
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
                pm.PyNode(side_jnt_dm_node).attr("inputMatrix"), f=True)
            pm.PyNode(side_jnt_dm_node).attr("outputRotate").connect(
                pm.PyNode(jnt_grp).rotate, f=True)

        else:
            # 位移部分
            corner_follicle = pm.PyNode(jnt_grp.replace("_Grp", "_Follicle"))
            corner_follicle.getShape().attr("outTranslate").connect(
                pm.PyNode(jnt_grp).translate, f=True)

            # 旋转部分
            base_ctrl_out_grp = pm.PyNode("MD_Mouth_01_Base_Ctrl_Out_Grp")

            null_vp = "MD_{}_Master_Ctrl_Null_VP".format(self.module_name)
            if not pm.objExists(null_vp):
                pm.createNode("vectorProduct", name=null_vp)
                pm.PyNode(null_vp).attr("operation").set(3)
                pm.PyNode(null_vp).attr("input1X").set(1.0)
            if (pm.PyNode(null_vp) not in pm.PyNode(base_ctrl_out_grp).attr("worldMatrix[0]").outputs()):
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

            jnt_FBFM_node = corner_follicle.name().replace("_Follicle", "_FBFM")
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

    def xd_bind_jnt(self, name, have_loc=False, parent_node="", translate=(0, 0, 0)):
        pm.select(cl=True)
        pm.joint(name=name)

        pm.parent(
            pm.createNode("transform", name="{}_RollOut_Grp".format(name)),
            pm.createNode("transform", name="{}_Grp".format(name)))
        pm.parent(name, "{}_RollOut_Grp".format(name))

        if have_loc:
            pm.parent(pm.spaceLocator(
                name="{}_RollOut_Loc".format(name)), "{}_Grp".format(name))

        pm.PyNode("{}_Grp".format(name)).translate.set(translate)

        if parent_node is not None:
            if pm.objExists(parent_node):
                pm.parent("{}_Grp".format(name), parent_node)

        return "{}_Grp".format(name)

    def skin_out_curve(self):
        seg = 5
        bind_jnt_grp = "MD_{}_Bind_Jnt_Grp".format(self.module_name)
        if not pm.objExists(bind_jnt_grp):
            pm.createNode("transform", name=bind_jnt_grp, p="MD_{}_Deformer_Grp".format(self.module_name))
        for prefix in ["Up", "Low"]:
            skin_items = []
            if prefix == "Up":
                out_curve = self.up_out_curve
            else:
                out_curve = self.low_out_curve
            # out_curve = pm.PyNode(
            #     "MD_Mouth_01_{}_Out_Curve".format(prefix))
            skin_items.append(out_curve)
            for side in ["LF", "RT"]:
                for index in range(1, seg + 1):
                    jnt_name = "{}_Mouth_01_{}Lip_{}_Jnt".format(side, prefix, "{0:02d}".format(index))
                    if not pm.objExists(jnt_name):
                        bind_jnt = self.xd_bind_jnt(name=jnt_name, parent_node=bind_jnt_grp, have_loc=True)
                        self.location_bind_jnt(jnt_grp=bind_jnt, jnt_type='lip', side=side, index=index)
                    skin_items.append(jnt_name)  # LF_Mouth_01_UpLip_01_Jnt
                if prefix == "Up":
                    jnt_name = "{}_{}_Lip_Jnt".format(side, self.module_name)
                    if not pm.objExists(jnt_name):
                        bind_jnt = self.xd_bind_jnt(name=jnt_name, parent_node=bind_jnt_grp, have_loc=True)
                        self.location_bind_jnt(jnt_grp=bind_jnt, jnt_type='corner', side=side)
                    skin_items.append(jnt_name)
            pm.skinCluster(skin_items, tsb=True, name="{}_SC".format(out_curve))
        print("skin_out_curve Done")
        return True

    def use_dm_node_to_tweak_ctrl_parent_and_jnt_02_grp(self):
        # todo 考虑在tweak ctrl或者jnt创建初就调用，执行这个方法
        seg = 3
        for side in ["LF", "RT"]:
            tweak_ctrl = "{}_Mouth_01_Tweak_Ctrl".format(side)

            custom_show_channel(tweak_ctrl, attr_list=["translateX", "translateY", "translateZ"])

            if not pm.attributeQuery("roll", node=tweak_ctrl, ex=True):
                pm.addAttr(tweak_ctrl, ln="roll", at="double", dv=0)
                pm.setAttr("{}.roll".format(tweak_ctrl), e=True, k=True)

            tweak_ctrl_parent = pm.PyNode(tweak_ctrl).getParent()

            dm_node = "{}_Inverse_DM".format(tweak_ctrl)
            if not pm.objExists(dm_node):
                dm_node = pm.createNode("decomposeMatrix", name=dm_node)
            pm.PyNode(tweak_ctrl).attr("inverseMatrix").connect(dm_node.attr("inputMatrix"))
            dm_node.attr("outputTranslate").connect(tweak_ctrl_parent.translate)
            dm_node.attr("outputRotate").connect(tweak_ctrl_parent.rotate)

            jnt_02_grp = "{}_Mouth_01_Tweak_Ctrl_Jnt_02_Grp".format(side)
            pm.PyNode(tweak_ctrl).translate.connect(pm.PyNode(jnt_02_grp).translate)
            pm.PyNode(tweak_ctrl).attr("roll").connect(pm.PyNode(jnt_02_grp).rotateX)

            for location in ["Up", "Low"]:
                for index in range(1, seg + 1):
                    tweak_ctrl = "{}_Mouth_01_{}Tweak_{}_Ctrl".format(side, location, "{0:02d}".format(index))

                    custom_show_channel(tweak_ctrl, attr_list=["translateX", "translateY", "translateZ"])
                    if not pm.attributeQuery("roll", node=tweak_ctrl, ex=True):
                        pm.addAttr(tweak_ctrl, ln="roll", at="double", dv=0)
                        pm.setAttr("{}.roll".format(tweak_ctrl), e=True, k=True)

                    tweak_ctrl_parent = pm.PyNode(tweak_ctrl).getParent()

                    dm_node = "{}_Inverse_DM".format(tweak_ctrl)
                    if not pm.objExists(dm_node):
                        dm_node = pm.createNode("decomposeMatrix", name="{}_Inverse_DM".format(tweak_ctrl))
                    pm.PyNode(tweak_ctrl).attr("inverseMatrix").connect(dm_node.attr("inputMatrix"))
                    dm_node.attr("outputTranslate").connect(tweak_ctrl_parent.translate)
                    dm_node.attr("outputRotate").connect(tweak_ctrl_parent.rotate)

                    jnt_02_grp = ("{}_{}_{}Tweak_{}_Ctrl_Jnt_02_Grp".format(
                        side, self.module_name, location, "{0:02d}".format(index)))
                    pm.PyNode(tweak_ctrl).translate.connect(pm.PyNode(jnt_02_grp).translate)
                    pm.PyNode(tweak_ctrl).attr("roll").connect(pm.PyNode(jnt_02_grp).rotateX)

        return True

    def skin_tweak_surface(self):
        seg = 3
        for prefix in ["Up", "Low"]:
            skin_items = []
            if prefix == "Up":
                tweak_surface = self.up_tweak_surface
            else:
                tweak_surface = self.low_tweak_surface
            skin_items.append(tweak_surface)
            # print("skin_items: {}".format(skin_items))
            for side in ["LF", "RT"]:
                for index in range(1, seg + 1):
                    skin_items.append("{}_Mouth_01_{}Tweak_{}_Ctrl_Jnt".format(
                        side, prefix, "{0:02d}".format(index)))
                skin_items.append("{}_Mouth_01_Tweak_Ctrl_Jnt".format(side))
            # print("skin_items: {}".format(skin_items))
            pm.skinCluster(skin_items, tsb=True, name="{}_SC".format(tweak_surface))
        return True

    def __skin_lip_sew_surface_and_connect_follicle_shape(self):
        sew_surface = "MD_Mouth_01_LipSew_Surface"
        skin_items = ["MD_Mouth_01_Master_Ctrl_Jnt",
                      "LF_Mouth_01_Ctrl_Jnt", "RT_Mouth_01_Ctrl_Jnt", sew_surface]
        pm.skinCluster(skin_items, tsb=True, name="{}_SC".format(sew_surface))
        for side in ["LF", "RT"]:
            follicle = "{}_Mouth_01_LipSew_Ctrl_Follicle".format(side)
            if side == "LF":
                param_u = 0.0
            else:
                param_u = 1.0
            param_v = 0.5
            make_follicle_work_on_surface(
                surface=sew_surface, follicle=follicle, param_u=param_u, param_v=param_v)
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
                lip_sew_ctrl_grp = yellow_component(name=lip_sew_ctrl, shape_type="cone", parent_node=follicle, )
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

            inverse_dm = "{}_Mouth_01_LipSew_Ctrl_Inverse_DM".format(side)
            if not pm.objExists(inverse_dm):
                pm.createNode("decomposeMatrix", name=inverse_dm)

            pm.PyNode(lip_sew_ctrl).attr("inverseMatrix").connect(
                pm.PyNode(inverse_dm).attr("inputMatrix"), f=True)
            pm.PyNode(inverse_dm).attr("outputTranslate").connect(
                pm.PyNode(lip_sew_ctrl_grp).translate, f=True)
            pm.PyNode(inverse_dm).attr("outputRotate").connect(
                pm.PyNode(lip_sew_ctrl_grp).rotate, f=True)

        return True

    def make_bind_jnt_work(self):
        """让蒙皮骨骼能够工作

        :return:
        """
        seg = 5
        master_ctrl = "MD_{}_Master_Ctrl".format(self.module_name)
        for side in ["LF", "RT"]:
            corner_bind_jnt_root = "{}_{}_Lip_Jnt_Grp".format(
                side, self.module_name)
            # 因为 localScale 是单属性，scale是一组属性，
            # 所以必须得逐一连接属性：scaleX， scaleY， scaleZ
            pm.PyNode(master_ctrl).attr("localScale").connect(pm.PyNode(corner_bind_jnt_root).scaleX, f=True)
            pm.PyNode(master_ctrl).attr("localScale").connect(pm.PyNode(corner_bind_jnt_root).scaleY, f=True)
            pm.PyNode(master_ctrl).attr("localScale").connect(pm.PyNode(corner_bind_jnt_root).scaleZ, f=True)

            # 位移部分
            corner_follicle = pm.PyNode(corner_bind_jnt_root.replace("_Grp", "_Follicle"))
            corner_follicle.getShape().attr("outTranslate").connect(pm.PyNode(corner_bind_jnt_root).translate, f=True)

            # 旋转部分
            base_ctrl_out_grp = pm.PyNode("MD_Mouth_01_Base_Ctrl_Out_Grp")

            null_vp = "MD_Mouth_01_Master_Ctrl_Null_VP"
            if not pm.objExists(null_vp):
                pm.createNode("vectorProduct", name=null_vp)
                pm.PyNode(null_vp).attr("operation").set(3)
                pm.PyNode(null_vp).attr("input1X").set(1.0)

            if pm.PyNode(null_vp) not in pm.PyNode(base_ctrl_out_grp).attr("worldMatrix[0]").outputs():
                pm.PyNode(base_ctrl_out_grp).attr("worldMatrix[0]").connect(pm.PyNode(null_vp).attr("matrix"), f=True)

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

            jnt_FBFM_node = corner_follicle.name().replace("_Follicle", "_FBFM")
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
                jnt_dm_node = pm.createNode("decomposeMatrix", name=jnt_dm_node)
            pm.PyNode(jnt_FBFM_node).attr("output").connect(pm.PyNode(jnt_dm_node).attr("inputMatrix"), f=True)

            pm.PyNode(jnt_dm_node).attr("outputRotate").connect(
                pm.PyNode(corner_bind_jnt_root).attr("rotate"), f=True)

            for location in ["Up", "Low"]:
                for index in range(1, seg + 1):
                    # 缩放部分
                    bind_jnt_root = ("{}_Mouth_01_{}Lip_{}_Jnt_Grp".format(
                        side, location, "{0:02d}".format(index)))
                    pm.PyNode(master_ctrl).attr("localScale").connect(pm.PyNode(bind_jnt_root).scaleX, f=True)
                    pm.PyNode(master_ctrl).attr("localScale").connect(pm.PyNode(bind_jnt_root).scaleY, f=True)
                    pm.PyNode(master_ctrl).attr("localScale").connect(pm.PyNode(bind_jnt_root).scaleZ, f=True)

                    # 位移部分
                    translate_bc_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_Translate_BC".format(side, location, "{0:02d}".format(index)))
                    if not pm.objExists(translate_bc_node):
                        pm.createNode("blendColors", name=translate_bc_node)
                    low_follicle_shape = (
                        "{}_Mouth_01_LowLip_{}_Jnt_FollicleShape".format(side, "{0:02d}".format(index)))
                    up_follicle_shape = (
                        "{}_Mouth_01_UpLip_{}_Jnt_FollicleShape".format(side, "{0:02d}".format(index)))
                    pm.PyNode(up_follicle_shape).attr("outTranslate").connect(
                        pm.PyNode(translate_bc_node).attr("color1"), f=True)
                    pm.PyNode(low_follicle_shape).attr("outTranslate").connect(
                        pm.PyNode(translate_bc_node).attr("color2"), f=True)
                    pm.PyNode(translate_bc_node).attr("output").connect(
                        pm.PyNode(bind_jnt_root).translate, f=True)

                    lf_sew_follicle_shape = "LF_Mouth_01_LipSew_Ctrl_FollicleShape"
                    rt_sew_follicle_shape = "RT_Mouth_01_LipSew_Ctrl_FollicleShape"

                    sew_sr_node = "{}_Mouth_01_{}Lip_{}_Jnt_LipSew_SR".format(
                        side, location, "{0:02d}".format(index))
                    if not pm.objExists(sew_sr_node):
                        pm.createNode("setRange", name=sew_sr_node)
                        pm.PyNode(sew_sr_node).attr("minY").set(0.5)
                        pm.PyNode(sew_sr_node).attr("maxX").set(0.5)
                        if side == "LF":
                            pm.PyNode(sew_sr_node).attr("oldMinX").set(0.5 - index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMinY").set(0.5 - index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMaxX").set(0.5 + 0.1 - index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMaxY").set(0.5 + 0.1 - index * 0.1)
                        elif side == "RT":
                            pm.PyNode(sew_sr_node).attr("oldMinX").set(0.5 - 0.1 + index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMinY").set(0.5 - 0.1 + index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMaxX").set(0.5 + index * 0.1)
                            pm.PyNode(sew_sr_node).attr("oldMaxY").set(0.5 + index * 0.1)
                    pm.PyNode(lf_sew_follicle_shape).attr("parameterU").connect(
                        pm.PyNode(sew_sr_node).attr("valueX"), f=True)
                    pm.PyNode(rt_sew_follicle_shape).attr("parameterU").connect(
                        pm.PyNode(sew_sr_node).attr("valueY"), f=True)

                    adl_node = "{}_Mouth_01_{}Lip_{}_Jnt_ADL".format(
                        side, location, "{0:02d}".format(index))
                    if not pm.objExists(adl_node):
                        pm.createNode("addDoubleLinear", name=adl_node)
                    pm.PyNode(sew_sr_node).attr("outValueX").connect(
                        pm.PyNode(adl_node).attr("input1"), f=True)
                    pm.PyNode(sew_sr_node).attr("outValueY").connect(
                        pm.PyNode(adl_node).attr("input2"), f=True)

                    cmp_node = "{}_Mouth_01_{}Lip_{}_Jnt_LipSew_CMP".format(
                        side, location, "{0:02d}".format(index))
                    if not pm.objExists(cmp_node):
                        pm.createNode("clamp", name=cmp_node)
                        pm.PyNode(cmp_node).attr("maxR").set(0.5)
                    pm.PyNode(adl_node).attr("output").connect(pm.PyNode(cmp_node).attr("inputR"), f=True)

                    if location == "Up":
                        pma_node = "{}_Mouth_01_{}Lip_{}_Jnt_LipSew_PMA".format(
                            side, location, "{0:02d}".format(index))
                        if not pm.objExists(pma_node):
                            pm.createNode("plusMinusAverage", name=pma_node)
                            pm.PyNode(pma_node).attr("operation").set(2)
                            pm.PyNode(pma_node).attr("input1D[0]").set(1)
                        pm.PyNode(cmp_node).attr("outputR").connect(
                            pm.PyNode(pma_node).attr("input1D[1]"), f=True)
                        pm.PyNode(pma_node).attr("output1D").connect(
                            pm.PyNode(translate_bc_node).attr("blender"), f=True)
                    else:
                        pm.PyNode(cmp_node).attr("outputR").connect(
                            pm.PyNode(translate_bc_node).attr("blender"), f=True)

                    # 旋转部分
                    follicle_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_Follicle".format(side, location, "{0:02d}".format(index)))

                    side_jnt_vp = ("{}_Mouth_01_{}Lip_{}_Jnt_VP".format(
                        side, location, "{0:02d}".format(index)))
                    if not pm.objExists(side_jnt_vp):
                        pm.createNode("vectorProduct", name=side_jnt_vp)
                        pm.PyNode(side_jnt_vp).attr("operation").set(3)
                        pm.PyNode(side_jnt_vp).attr("input1X").set(1.0)
                    pm.PyNode(follicle_node).attr("worldMatrix[0]").connect(pm.PyNode(side_jnt_vp).attr("matrix"),
                                                                            f=True)

                    side_3rd_vp_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_3rd_VP".format(side, location, "{0:02d}".format(index)))
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
                        pm.PyNode(side_jnt_dm_node).attr("inputMatrix"), f=True)
                    pm.PyNode(side_jnt_dm_node).attr("outputRotate").connect(
                        pm.PyNode(bind_jnt_root).rotate, f=True)

        return

    def make_bind_jnt_scale_work(self):
        u""" 让 bind jnt 的 scale 能够正确工作

        bind jnt的缩放是由 master ctrl 的 localScale 和 lipSqueeze 两个属性，
        以及 base curve 的弧长所影响控制

        :return: None
        """
        seg = 5
        master_ctrl = "MD_{}_Master_Ctrl".format(
            self.module_name)  # MD_Mouth_01_Master_Ctrl

        if not pm.attributeQuery("lipSqueeze", node=master_ctrl, ex=True):
            pm.addAttr(master_ctrl, ln="lipSqueeze",
                       at="double", min=0, dv=0.5)
            pm.setAttr("{}.lipSqueeze".format(master_ctrl), e=True, k=True)

        for side in ["LF", "RT"]:
            for location in ["Up", "Low"]:
                base_curve = ("MD_Mouth_01_{}_Base_Curve".format(location))

                base_curve_ci = (
                    "MD_Mouth_01_{}_Base_Curve_CI".format(location))
                if not pm.objExists(base_curve_ci):
                    pm.createNode("curveInfo", name=base_curve_ci)
                    pm.PyNode(base_curve).getShape().attr("worldSpace[0]").connect(
                        pm.PyNode(base_curve_ci).attr("inputCurve"), f=True)

                base_curve_arc_length = (
                    pm.PyNode(base_curve_ci).attr("arcLength").get())

                base_scale_mdl_node = (
                    "MD_Mouth_01_{}_Base_Curve_Scale_MDL".format(location))
                if not pm.objExists(base_scale_mdl_node):
                    pm.createNode("multDoubleLinear", name=base_scale_mdl_node)
                    pm.PyNode(base_scale_mdl_node).attr(
                        "input2").set(base_curve_arc_length)
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
                        "{}_Mouth_01_{}Lip_{}_Jnt_Scale_Cond".format(side, location, "{0:02d}".format(index)))
                    if not pm.objExists(jnt_scale_cond_node):
                        pm.createNode("condition", name=jnt_scale_cond_node)
                        pm.PyNode(jnt_scale_cond_node).attr(
                            "secondTerm").set(base_curve_arc_length)
                        pm.PyNode(jnt_scale_cond_node).attr("operation").set(2)
                        pm.PyNode(base_curve_ci).attr("arcLength").connect(
                            pm.PyNode(jnt_scale_cond_node).attr("firstTerm"), f=True)

                    # LF_Mouth_01_UpLip_01_Jnt_Scale_MDL
                    jnt_scale_mdl_node = (
                        "{}_Mouth_01_{}Lip_{}_Jnt_Scale_MDL".format(side, location, "{0:02d}".format(index)))
                    if not pm.objExists(jnt_scale_mdl_node):
                        pm.createNode("multDoubleLinear",
                                      name=jnt_scale_mdl_node)
                        pm.PyNode(master_ctrl).attr("lipSqueeze").connect(
                            pm.PyNode(jnt_scale_mdl_node).attr("input1"), f=True)
                        pm.PyNode(jnt_scale_cond_node).attr("outColorR").connect(
                            pm.PyNode(jnt_scale_mdl_node).attr("input2"), f=True)

                    # LF_Mouth_01_UpLip_01_Jnt_Scale_MD
                    jnt_scale_md_node = "{}_Mouth_01_{}Lip_{}_Jnt_Scale_MD".format(
                        side, location, "{0:02d}".format(index))
                    if not pm.objExists(jnt_scale_md_node):
                        pm.createNode("multiplyDivide", name=jnt_scale_md_node)
                        pm.PyNode(jnt_scale_md_node).attr("operation").set(3)
                        pm.PyNode(base_scale_md_node).attr("outputX").connect(
                            pm.PyNode(jnt_scale_md_node).attr("input1X"), f=True)
                        pm.PyNode(jnt_scale_mdl_node).attr("output").connect(
                            pm.PyNode(jnt_scale_md_node).attr("input2X"), f=True)

                    # LF_Mouth_01_UpLip_01_Jnt
                    bind_jnt = ("{}_Mouth_01_{}Lip_{}_Jnt".format(
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
        master_ctrl = "MD_{}_Master_Ctrl".format(self.module_name)
        jaw_ctrl = "MD_{}_Jaw_Ctrl".format(self.module_name)
        for side in ['LF', 'RT']:
            # LF_Mouth_01_Ctrl_Null_03_Grp
            side_null_03_grp = ("{}_Mouth_01_Ctrl_Null_03_Grp".format(side))
            # print(side_null_03_grp)

            driver_value = [-2, 0, 1.0]
            value = [1.8, 0, -0.9]

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
            if not check_constraint(side_ctrl_null, side_null_03_grp):
                pm.parentConstraint(side_null_03_grp, side_ctrl_null, mo=True)

        return True

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

        if not pm.PyNode(jaw_ctrl).translate.isConnectedTo(pm.PyNode(low_jaw_jnt_grp).translate):
            pm.PyNode(jaw_ctrl).translate.connect(
                pm.PyNode(low_jaw_jnt_grp).translate, f=True)

        if not pm.PyNode(jaw_ctrl).rotate.isConnectedTo(pm.PyNode(low_jaw_jnt_grp).rotate):
            pm.PyNode(jaw_ctrl).rotate.connect(
                pm.PyNode(low_jaw_jnt_grp).rotate, f=True)

        master_ctrl_grp = "MD_Mouth_01_Master_Ctrl_Grp"
        if not check_constraint(master_ctrl_grp, jaw_ctrl):
            constraint = pm.parentConstraint(jaw_ctrl, pm.PyNode(
                jaw_ctrl).getParent(), master_ctrl_grp, mo=True)

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

        if not pm.PyNode(ctrl_null).translate.isConnectedTo(pm.PyNode(ctrl_jnt_02_grp).translate):
            pm.PyNode(ctrl_null).translate.connect(
                pm.PyNode(ctrl_jnt_02_grp).translate)
        if not pm.PyNode(ctrl_null).rotate.isConnectedTo(pm.PyNode(ctrl_jnt_02_grp).rotate):
            pm.PyNode(ctrl_null).rotate.connect(
                pm.PyNode(ctrl_jnt_02_grp).rotate)

        if not pm.PyNode(ctrl_null).translate.isConnectedTo(pm.PyNode(ctrl_02_grp).translate):
            pm.PyNode(ctrl_null).translate.connect(
                pm.PyNode(ctrl_02_grp).translate)

        # todo 缺少对 cheek 的支持

        return True

    def lip_sew_and_follicle(self):
        lip_sew_surface = self.mouth_lip_sew_surface
        skin_items = [lip_sew_surface]
        for control in ["LF_{}_Ctrl".format(self.module_name),
                        "RT_{}_Ctrl".format(self.module_name),
                        "MD_{}_Master_Ctrl".format(self.module_name)]:
            jnt_name = "{}_Jnt".format(control)
            skin_items.append(jnt_name)
            if not pm.objExists(jnt_name):
                pm.select(cl=True)
                jnt = pm.joint(name=jnt_name)
                pm.parent(jnt, control)
                jnt.translate.set([0, 0, 0])
        pm.skinCluster(skin_items, tsb=True, name="{}_SC".format(self.mouth_lip_sew_surface))

        sew_ctrl_grp = "MD_{}_LipSew_Ctrl_Grp".format(self.module_name)
        if not pm.objExists(sew_ctrl_grp):
            pm.createNode("transform", name=sew_ctrl_grp, p="MD_{}_Grp".format(self.module_name))
            pm.PyNode(sew_ctrl_grp).attr("inheritsTransform").set(0)

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
            pm.PyNode("MD_{}_Scale_Null".format(self.module_name)).scale.connect(pm.PyNode(follicle).scale)
            pm.PyNode(follicle).getShape().attr("parameterV").set(0.5)

            if side == "LF":
                pm.PyNode(follicle).getShape().attr("parameterU").set(0)
            elif side == "RT":
                pm.PyNode(follicle).getShape().attr("parameterU").set(1.0)

        return True

    def make_lip_roll(self):
        seg = 5
        for index in range(1, seg + 1):
            for side in ["LF", "RT"]:
                prefix = "{}_{}".format(side, self.module_name)
                jnt_roll_sr = pm.createNode(
                    "setRange", name="{}_Lip_{}_Jnt_Roll_SR".format(prefix, "{0:02d}".format(index)))
                # todo setRange节点缺少“最大值”和“旧最大值”这两个参数的自动填充算法逻辑
                for vertical in ["Up", "Low"]:
                    mouth_ctrl = "{}_{}_Ctrl".format(vertical, self.module_name)
                    if vertical == "Up":
                        pm.PyNode(mouth_ctrl).attr("lipRoll").connect(pm.PyNode(jnt_roll_sr).attr("valueX"))
                        pm.PyNode(jnt_roll_sr).attr("outValueX").connect(
                            pm.PyNode("{}_{}Lip_{}_Jnt_RollOut_Grp".format(
                                prefix, vertical, "{0:02d}".format(index))).rotateX)
                    else:
                        pm.PyNode(mouth_ctrl).attr("lipRoll").connect(pm.PyNode(jnt_roll_sr).attr("valueY"))
                        pm.PyNode(jnt_roll_sr).attr("outValueY").connect(
                            pm.PyNode("{}_{}Lip_{}_Jnt_RollOut_Grp".format(
                                prefix, vertical, "{0:02d}".format(index))).rotateX)

        return

    def proxy_jaw(self, have_teeth=True):
        jaw_deform_grp = "MD_{}_Jaw_Out_Grp".format(self.module_name)
        if not pm.objExists(jaw_deform_grp):
            pm.createNode("transform", name=jaw_deform_grp, p="MD_{}_Deformer_Grp".format(self.module_name))
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
        u"""创建jaw的骨骼和控制器"""
        jaw_out_grp = "MD_{}_Jaw_Out_Grp".format(self.module_name)
        if not pm.objExists(jaw_out_grp):
            proxy_jaw_root = "proxyJawRoot"
            if not pm.objExists(proxy_jaw_root):
                pm.error(u"缺少jaw的代理骨骼")
            self.jaw_deformer_grp()
            self.jaw_control_grp()

        return True

    def jaw_deformer_grp(self):
        jaw_out_grp = "MD_{}_Jaw_Out_Grp".format(self.module_name)
        if not pm.objExists(jaw_out_grp):
            pm.createNode("transform", name=jaw_out_grp, p="MD_{}_Deformer_Grp".format(self.module_name))

        low_jnt = "MD_Mouth_01_LowJaw_Jnt"
        if not pm.objExists(low_jnt):
            low_jnt_grp = jnt_or_control_grp(name=low_jnt, parent_node=jaw_out_grp, have_loc=True)

        tweak_jnt_grp = jnt_or_control_grp(
            name="MD_Mouth_01_Jaw_Tweak_Ctrl_Jnt", parent_node="MD_Mouth_01_LowJaw_Jnt")
        low_teeth_jnt_grp = jnt_or_control_grp(
            name="MD_Mouth_01_Low_Teeth_Ctrl_Jnt", parent_node="MD_Mouth_01_LowJaw_Jnt")

        up_jnt_grp = jnt_or_control_grp(name="MD_Mouth_01_UpJaw_Jnt", parent_node=jaw_out_grp)
        up_teeth_jnt_grp = jnt_or_control_grp(
            name="MD_Mouth_01_Up_Teeth_Ctrl_Jnt", parent_node="MD_Mouth_01_UpJaw_Jnt")
        up_jaw_loc = pm.spaceLocator(name="MD_Mouth_01_UpJaw_Loc")
        pm.parent(up_jaw_loc, up_jnt_grp)

        # 开始对各个组进行定位
        pm.delete(pm.parentConstraint("proxyJawRoot", jaw_out_grp, mo=False))
        pm.delete(pm.parentConstraint("proxyJawLow", low_jnt_grp, mo=False))
        offset_rotate = pm.PyNode(low_jnt_grp).rotateX.get()
        pm.PyNode(low_jnt_grp).rotateX.set(0)
        pm.PyNode(low_jnt).rotateX.set(offset_rotate)
        pm.delete(pm.parentConstraint("proxyJawTeak", tweak_jnt_grp, mo=False))
        pm.delete(pm.parentConstraint("proxyTeethLow", low_teeth_jnt_grp, mo=False))
        pm.delete(pm.parentConstraint("proxyJawUp", up_jnt_grp, mo=False))
        pm.delete(pm.parentConstraint("proxyTeethUp", up_teeth_jnt_grp, mo=False))
        pm.delete(pm.parentConstraint("proxyJawUpLoc", up_jaw_loc, mo=False))

        # 创建null组
        up_null_grp = ctrl_null_grp(name="Up_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(pm.parentConstraint("Up_{}_Ctrl".format(self.module_name), up_null_grp, mo=False))
        low_null_grp = ctrl_null_grp(name="Low_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(pm.parentConstraint("Low_{}_Ctrl".format(self.module_name), low_null_grp, mo=False))
        lf_null_grp = chain_ctrl_null_grp(name="LF_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(pm.parentConstraint("LF_{}_Ctrl".format(self.module_name), lf_null_grp, mo=False))
        rt_null_grp = chain_ctrl_null_grp(name="RT_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(pm.parentConstraint("RT_{}_Ctrl".format(self.module_name), rt_null_grp, mo=False))
        pm.PyNode(rt_null_grp).scale.set([1, 1, -1])
        rt_rotate = pm.PyNode(rt_null_grp).rotate.get()
        pm.PyNode(rt_null_grp).rotate.set([rt_rotate[0] - 180, rt_rotate[1] + 180, rt_rotate[2]])

        return True

    def jaw_control_grp(self):
        jaw_ctrl = "MD_{}_Jaw_Ctrl".format(self.module_name)
        if not pm.objExists(jaw_ctrl):
            pm.delete(
                pm.parentConstraint(
                    "proxyJawRoot",
                    jnt_or_control_grp(name=jaw_ctrl, object_type="plane",
                                       parent_node="MD_{}_Grp".format(self.module_name)),
                    mo=False))

        tweak_ctrl = "MD_{}_Jaw_Tweak_Ctrl".format(self.module_name)
        if not pm.objExists(tweak_ctrl):
            pm.delete(
                pm.parentConstraint(
                    "proxyJawTeak",
                    jnt_or_control_grp(name=tweak_ctrl, object_type="plane", parent_node=jaw_ctrl),
                    mo=False))

        low_teeth_ctrl = "MD_{}_Low_Teeth_Ctrl".format(self.module_name)
        if not pm.objExists(low_teeth_ctrl):
            pm.delete(
                pm.parentConstraint(
                    "proxyTeethLow",
                    jnt_or_control_grp(name=low_teeth_ctrl, object_type="plane", parent_node=jaw_ctrl),
                    mo=False))

        jaw_move_loc = "M_Jaw_Move_Loc"
        pm.spaceLocator(name=jaw_move_loc)
        pm.parent(jaw_move_loc, jaw_ctrl)
        pm.PyNode(jaw_move_loc).translate.set([0, 0, 5])

        up_teeth_ctrl = "MD_{}_Up_Teeth_Ctrl".format(self.module_name)
        pm.delete(
            pm.parentConstraint(
                "proxyTeethUp",
                jnt_or_control_grp(
                    name=up_teeth_ctrl, object_type="plane",
                    parent_node=pm.PyNode(jaw_ctrl).getParent()),
                mo=False))

        jaw_base_loc = "M_Jaw_Base_Loc"
        pm.spaceLocator(name=jaw_base_loc)
        pm.parent(jaw_base_loc, pm.PyNode(jaw_ctrl).getParent())
        pm.PyNode(jaw_base_loc).translate.set([0, 0, 0])

        return True

    def make_jaw_work(self):
        up_jaw_loc = "MD_Mouth_01_UpJaw_Loc"
        up_jaw_jnt = "MD_Mouth_01_UpJaw_Jnt"

        low_jaw_loc = "MD_Mouth_01_LowJaw_Loc"
        low_jaw_jnt = "MD_Mouth_01_LowJaw_Jnt"

        jaw_db = "MD_Mouth_01_Jaw_DB"
        if not pm.objExists(jaw_db):
            pm.createNode("distanceBetween", name=jaw_db)

        pm.PyNode(up_jaw_loc).getShape().attr("worldPosition[0]").connect(pm.PyNode(jaw_db).attr("point1"), f=True)
        pm.PyNode(low_jaw_loc).getShape().attr("worldPosition[0]").connect(pm.PyNode(jaw_db).attr("point2"), f=True)

        condition_node = "MD_Mouth_01_Jaw_Cond"
        if not pm.objExists(condition_node):
            pm.createNode("condition", name=condition_node)
        pm.PyNode(condition_node).attr("operation").set(2)

        pm.PyNode(jaw_db).attr("distance").connect(pm.PyNode(condition_node).attr("firstTerm"), f=True)
        pm.PyNode(jaw_db).attr("distance").connect(pm.PyNode(condition_node).attr("colorIfFalseR"), f=True)
        pm.PyNode(condition_node).attr("secondTerm").set(pm.PyNode(jaw_db).attr("distance").get())
        pm.PyNode(condition_node).attr("colorIfTrueR").set(pm.PyNode(jaw_db).attr("distance").get())

        jaw_pma = "MD_Mouth_01_Jaw_PMA"
        if not pm.objExists(jaw_pma):
            pm.createNode("plusMinusAverage", name=jaw_pma)
        pm.PyNode(jaw_pma).attr("operation").set(2)
        pm.PyNode(jaw_pma).attr("input1D[0]").set(pm.PyNode(jaw_db).attr("distance").get())
        pm.PyNode(condition_node).attr("outColorR").connect(pm.PyNode(jaw_pma).attr("input1D[1]"), f=True)

        pm.PyNode(jaw_pma).attr("output1D").connect(pm.PyNode(up_jaw_jnt).translateY, f=True)

        up_teeth_ctrl = "MD_Mouth_01_Up_Teeth_Ctrl"
        up_teeth_jnt = "MD_Mouth_01_Up_Teeth_Ctrl_Jnt"
        pm.PyNode(up_teeth_ctrl).translate.connect(pm.PyNode(up_teeth_jnt).translate, f=True)
        pm.PyNode(up_teeth_ctrl).rotate.connect(pm.PyNode(up_teeth_jnt).rotate, f=True)
        pm.PyNode(up_teeth_ctrl).scale.connect(pm.PyNode(up_teeth_jnt).scale, f=True)

        jaw_ctrl = "MD_Mouth_01_Jaw_Ctrl"
        low_jaw_grp = "MD_Mouth_01_LowJaw_Jnt_Grp"
        pm.PyNode(jaw_ctrl).translate.connect(pm.PyNode(low_jaw_grp).translate, f=True)
        pm.PyNode(jaw_ctrl).rotate.connect(pm.PyNode(low_jaw_grp).rotate, f=True)

        tweak_ctrl_jnt = "MD_Mouth_01_Jaw_Tweak_Ctrl_Jnt"
        tweak_ctrl = "MD_Mouth_01_Jaw_Tweak_Ctrl"
        pm.PyNode(tweak_ctrl).translate.connect(pm.PyNode(tweak_ctrl_jnt).translate, f=True)
        pm.PyNode(tweak_ctrl).rotate.connect(pm.PyNode(tweak_ctrl_jnt).rotate, f=True)
        pm.PyNode(tweak_ctrl).scale.connect(pm.PyNode(tweak_ctrl_jnt).scale, f=True)

        low_teeth_ctrl_jnt = "MD_Mouth_01_Low_Teeth_Ctrl_Jnt"
        low_teeth_ctrl = "MD_Mouth_01_Low_Teeth_Ctrl"
        pm.PyNode(low_teeth_ctrl).translate.connect(pm.PyNode(low_teeth_ctrl_jnt).translate, f=True)
        pm.PyNode(low_teeth_ctrl).rotate.connect(pm.PyNode(low_teeth_ctrl_jnt).rotate, f=True)
        pm.PyNode(low_teeth_ctrl).scale.connect(pm.PyNode(low_teeth_ctrl_jnt).scale, f=True)

        pm.parentConstraint(up_jaw_jnt, "Up_Mouth_01_Ctrl_Null", mo=True)
        pm.PyNode("Up_Mouth_01_Ctrl_Null").translate.connect(pm.PyNode("Up_Mouth_01_Ctrl_Jnt_02_Grp").translate, f=True)
        pm.PyNode("Up_Mouth_01_Ctrl_Null").rotate.connect(pm.PyNode("Up_Mouth_01_Ctrl_Jnt_02_Grp").rotate, f=True)
        pm.PyNode("Up_Mouth_01_Ctrl_Null").translate.connect(pm.PyNode("Up_Mouth_01_Ctrl_02_Grp").translate, f=True)

        pm.parentConstraint(low_jaw_jnt, "Low_Mouth_01_Ctrl_Null", mo=True)
        pm.PyNode("Low_Mouth_01_Ctrl_Null").translate.connect(pm.PyNode("Low_Mouth_01_Ctrl_Jnt_02_Grp").translate,
                                                              f=True)
        pm.PyNode("Low_Mouth_01_Ctrl_Null").rotate.connect(pm.PyNode("Low_Mouth_01_Ctrl_Jnt_02_Grp").rotate, f=True)
        pm.PyNode("Low_Mouth_01_Ctrl_Null").translate.connect(pm.PyNode("Low_Mouth_01_Ctrl_02_Grp").translate, f=True)

        master_ctrl = "MD_Mouth_01_Master_Ctrl"
        master_constraint = pm.parentConstraint(
            "MD_Mouth_01_Jaw_Ctrl",
            "MD_Mouth_01_Jaw_Ctrl_Grp",
            pm.PyNode(master_ctrl).getParent(),
            mo=True
        )
        master_constraint.attr("MD_Mouth_01_Jaw_CtrlW0").set(1.0)

        driver_value = [-1, 0]
        value = [0, 1]

        for index in range(0, len(driver_value)):
            pm.setDrivenKeyframe(
                master_constraint,
                at="{}W1".format("MD_Mouth_01_Jaw_Ctrl_Grp"),
                cd="{}.{}".format("MD_Mouth_01_Jaw_Ctrl", "rotateX"),
                dv=driver_value[index],
                value=value[index],
                itt="linear",
                ott="linear",
            )

        for side in ["LF", "RT"]:
            if not pm.attributeQuery("{}Corner".format(side), node=master_ctrl, ex=True):
                pm.addAttr(master_ctrl, ln="{}Corner".format(side), at="double", min=0, max=1.0, dv=0.5)
                pm.setAttr("{}.{}".format(master_ctrl, "{}Corner".format(side)), e=True, k=True)

            ctrl_null_02_grp_constraint = pm.parentConstraint(
                up_jaw_loc,
                low_jaw_loc,
                "{}_Mouth_01_Ctrl_Null_02_Grp".format(side), mo=True)

            pm.PyNode(master_ctrl).attr("{}Corner".format(side)).connect(
                "{}.{}W0".format(ctrl_null_02_grp_constraint, up_jaw_loc), f=True)

            ctrl_rev = "{}_Mouth_01_Ctrl_Rev".format(side)
            if not pm.objExists(ctrl_rev):
                pm.createNode("reverse", name=ctrl_rev)
            pm.PyNode(master_ctrl).attr("{}Corner".format(side)).connect(
                "{}.inputX".format(ctrl_rev), f=True)
            pm.PyNode(ctrl_rev).attr("outputX").connect(
                "{}.{}W1".format(ctrl_null_02_grp_constraint, low_jaw_loc), f=True)

            pm.parentConstraint(
                "{}_Mouth_01_Ctrl_Null_03_Grp".format(side),
                "{}_Mouth_01_Ctrl_Null".format(side), mo=True)
            pm.PyNode("{}_Mouth_01_Ctrl_Null".format(side)).translate.connect(
                pm.PyNode("{}_Mouth_01_Ctrl_02_Grp".format(side)).translate, f=True)
            pm.PyNode("{}_Mouth_01_Ctrl_Null".format(side)).translate.connect(
                pm.PyNode("{}_Mouth_01_Ctrl_Loc_02_Grp".format(side)).translate, f=True)

            driver_value = [-0.2, 0, 0.2]
            value = [0.12, 0, -0.1]

            for index in range(0, len(driver_value)):
                pm.setDrivenKeyframe(
                    "{}_Mouth_01_Ctrl_Null_03_Grp".format(side),
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
                    "{}_Mouth_01_Ctrl_Null_03_Grp".format(side),
                    at="translateX",
                    cd="{}.translateX".format("MD_Mouth_01_Jaw_Ctrl"),
                    dv=driver_value[index],
                    value=value[index],
                    itt="linear",
                    ott="linear",
                )

            driver_value = [-0.4, 0, 0.4]
            if side == "LF":
                value = [0, 0, -0.2]
            else:
                value = [-0.2, 0, 0]

            for index in range(0, len(driver_value)):
                pm.setDrivenKeyframe(
                    "{}_Mouth_01_Ctrl_Null_03_Grp".format(side),
                    at="translateX",
                    cd="{}.{}".format(master_ctrl, "translateX"),
                    dv=driver_value[index],
                    value=value[index],
                    itt="linear",
                    ott="linear",
                )

            side_ctrl_jnt = "{}_Mouth_01_Ctrl_Jnt".format(side)
            # 修正为目标约束
            pm.aimConstraint(
                master_ctrl, side_ctrl_jnt,
                aimVector=[-1, 0, 0],
                upVector=[0, 0, 1],
                worldUpType="objectrotation",
                worldUpVector=[0, 0, 1],
                worldUpObject="{}_Mouth_01_Ctrl".format(side),
                mo=True)

        return True

    def proxy_tongue(self):
        if not pm.objExists("Proxy_Grp"):
            pm.createNode("transform", name="Proxy_Grp")
        if pm.objExists("Proxy_tongue_Grp"):
            pm.error(u"场景中已经存在代理对象")
        pm.createNode("transform", name="Proxy_tongue_Grp", p="Proxy_Grp")

        jnt_num = 4

        for index in range(1, jnt_num + 1):
            pm.spaceLocator(name="proxyTongue{}Loc".format("{0:02d}".format(index)))
            if index == 1:
                pm.parent("proxyTongue{}Loc".format("{0:02d}".format(index)), "Proxy_tongue_Grp")
            if index > 1:
                pm.parent("proxyTongue{}Loc".format("{0:02d}".format(index)),
                          "proxyTongue{}Loc".format("{0:02d}".format(index - 1)))
            pm.PyNode("proxyTongue{}Loc".format("{0:02d}".format(index))).translateZ.set(2)

        return True

    def tongue_ctrl_grp(self):
        tongue_ctrl_root_group = "MD_Tongue_01_Grp"
        pm.createNode("transform", name=tongue_ctrl_root_group, p="Master_Ctrl")

        tongue_main_group = "MD_Tongue_01_Main_Grp"
        pm.createNode("transform", name=tongue_main_group, p=tongue_ctrl_root_group)
        pm.delete(pm.parentConstraint("proxyTongue01Loc", tongue_main_group, mo=False))

        jnt_num = 4

        for index in range(1, jnt_num + 1):
            tongue_ctrl = "MD_Tongue_01_{}_FK_Ctrl".format("{0:02d}".format(index))
            tongue_ctrl_grp = "MD_Tongue_01_{}_FK_Ctrl_Grp".format("{0:02d}".format(index))
            if index == 1:
                tongue_ctrl_grp = jnt_or_control_grp(
                    name=tongue_ctrl, object_type="cylinder", parent_node=tongue_main_group, have_jnt=True)
            if index > 1:
                tongue_ctrl_grp = jnt_or_control_grp(
                    name=tongue_ctrl, object_type="cylinder",
                    parent_node="MD_Tongue_01_{}_FK_Ctrl".format("{0:02d}".format(index - 1)), have_jnt=True)

            proxy_loc = "proxyTongue{}Loc".format("{0:02d}".format(index))
            print("{} -> {}".format(proxy_loc, tongue_ctrl_grp))
            pm.delete(pm.parentConstraint(proxy_loc, tongue_ctrl_grp, mo=False))

        return


creator_version = 0.21


class FaceCreatorUI(common.Singleton):
    def __init__(self):
        super(FaceCreatorUI, self).__init__()

        self.rig_root_node = ""  # group "World"

        # neck and ear module
        self.neck_ear_creator = NeckEarCreator()

        # eye module
        self.eye_module = "Eye_01"
        self.eye_creator = EyeCreator()

        # brow module
        self.brow_creator = BrowCreator()
        self.left_brow_surface = ""
        self.right_brow_surface = ""
        self.left_brow_curve = ""
        self.right_brow_curve = ""

        self.left_master_ctrl_surface = ""
        self.right_master_ctrl_surface = ""

        # nose module
        self.nose_creator = NoseCreator()

        # mouth module
        self.mouth_module = "Mouth_01"
        self.mouth_creator = MouthCreator()

        self.up_base_curve = ""
        self.low_base_curve = ""
        self.up_tweak_surface = ""
        self.low_tweak_surface = ""
        self.up_out_curve = ""
        self.low_out_curve = ""

        self.mouth_surface = ""
        self.mouth_lip_sew_surface = ""

        # cheek module
        self.cheek_module = "Cheek_01"
        self.cheek_creator = CheekCreator()

        self.show_window()

    def show_window(self):
        self.initialize()

        if pm.window("xdFaceCreatorWnd", exists=True):
            pm.deleteUI("xdFaceCreatorWnd")

        pm.window("xdFaceCreatorWnd",
                  title="Biped Creator dev {}".format(creator_version),
                  mb=True,
                  cc=lambda *args: self._closed_window_cmd())

        self.menu_bar()

        root_layout = pm.scrollLayout(hst=16, vst=16, cr=True)

        tab_layout = pm.tabLayout(p=root_layout)

        pre_tab = pm.columnLayout(adj=1, p=tab_layout)
        self.rig_pre_frame(pre_tab)
        pm.setParent(pre_tab)

        neck_ear_tab = pm.columnLayout(adj=1, p=tab_layout)
        self.neck_ear_module_frame(neck_ear_tab)
        pm.setParent(neck_ear_tab)

        eye_tab = pm.columnLayout(adj=1, p=tab_layout)
        self.eye_module_frame(eye_tab)
        pm.setParent(eye_tab)

        brow_tab = pm.columnLayout(adj=1, p=tab_layout)
        self.brow_module_frame(brow_tab)
        pm.setParent(brow_tab)

        nose_tab = pm.columnLayout(adj=1, p=tab_layout)
        self.nose_module_frame(nose_tab)
        pm.setParent(nose_tab)

        mouth_tab = pm.columnLayout(adj=1, p=tab_layout)
        self.mouth_module_frame(mouth_tab)
        pm.setParent(mouth_tab)

        face_tab = pm.columnLayout(adj=1, p=tab_layout)
        self.cheek_module_frame(face_tab)
        pm.setParent(face_tab)

        linkage_tab = pm.columnLayout(adj=1, p=tab_layout)
        self.linkage_frame(linkage_tab)
        pm.setParent(linkage_tab)

        cmds.tabLayout(
            tab_layout, edit=True,
            tabLabel=(
                (pre_tab, 'Pre'),
                (neck_ear_tab, 'NeckAndNeck'),
                (eye_tab, 'Eye'),
                (brow_tab, 'Brow'),
                (nose_tab, 'Nose'),
                (mouth_tab, 'Mouth'),
                (face_tab, 'Cheek'),
                (linkage_tab, 'Linkage'),
            ),
            sti=8,
        )
        pm.setParent(tab_layout)
        pm.showWindow("xdFaceCreatorWnd")

        self.eye_control_location_frame_init()
        self.nose_proxy_frame_init()
        self.cheek_proxy_frame_init()

        return

    def _closed_window_cmd(self):
        # brow module
        pm.optionVar(
            sv=('brow_01_left_sub_surface',
                pm.textFieldButtonGrp("xdMouthCreatorLeftBrowSurfaceField", q=True, text=True)))
        pm.optionVar(
            sv=('brow_01_right_sub_surface',
                pm.textFieldButtonGrp("xdMouthCreatorRightBrowSurfaceField", q=True, text=True)))

        pm.optionVar(
            sv=('brow_01_left_sub_curve',
                pm.textFieldButtonGrp("xdMouthCreatorLeftBrowCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('brow_01_right_sub_curve',
                pm.textFieldButtonGrp("xdMouthCreatorRightBrowCurveField", q=True, text=True)))

        pm.optionVar(
            sv=('brow_01_left_master_surface',
                pm.textFieldButtonGrp("xdMouthCreatorLeftMasterSurfaceField", q=True, text=True)))
        pm.optionVar(
            sv=('brow_01_right_master_surface',
                pm.textFieldButtonGrp("xdMouthCreatorRightMasterSurfaceField", q=True, text=True)))

        # mouth module
        pm.optionVar(
            sv=('mouth_01_Up_Base_Curve', pm.textFieldButtonGrp("xdMouthCreatorUpBaseCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Low_Base_Curve', pm.textFieldButtonGrp("xdMouthCreatorLowBaseCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Up_Tweak_Surface',
                pm.textFieldButtonGrp("xdMouthCreatorUpTweakSurfaceField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Low_Tweak_Surface',
                pm.textFieldButtonGrp("xdMouthCreatorLowTweakSurfaceField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Up_Out_Curve',
                pm.textFieldButtonGrp("xdMouthCreatorUpOutCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Low_Out_Curve',
                pm.textFieldButtonGrp("xdMouthCreatorLowOutCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_mouth_surface',
                pm.textFieldButtonGrp("xdMouthCreatorMouthSurfaceField", q=True, text=True)))

        pm.optionVar(
            sv=('mouth_01_lip_sew_surface',
                pm.textFieldButtonGrp("xdMouthCreatorMouthLipSewSurfaceField", q=True, text=True)))
        return

    def initialize(self):
        u"""初始化数据

        从MAYA的保存的属性数据里面获取一些值

        :return:
        """
        # brow module
        if pm.optionVar(q='brow_01_left_sub_surface'):
            self.left_brow_surface = pm.optionVar(q='brow_01_left_sub_surface')
        if pm.optionVar(q='brow_01_right_sub_surface'):
            self.right_brow_surface = pm.optionVar(
                q='brow_01_right_sub_surface')
        if pm.optionVar(q='brow_01_left_sub_curve'):
            self.left_brow_curve = pm.optionVar(q='brow_01_left_sub_curve')
        if pm.optionVar(q='brow_01_right_sub_curve'):
            self.right_brow_curve = pm.optionVar(q='brow_01_right_sub_curve')
        if pm.optionVar(q='brow_01_left_master_surface'):
            self.left_master_ctrl_surface = pm.optionVar(
                q='brow_01_left_master_surface')
        if pm.optionVar(q='brow_01_right_master_surface'):
            self.right_master_ctrl_surface = pm.optionVar(
                q='brow_01_right_master_surface')

        # mouth module
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
        pm.menuItem(p=menu_component, label=u"Base loc",
                    c=lambda *args: self.build_base_loc())

        menu_template = pm.menu(label="Module", tearOff=False)
        pm.menuItem(p=menu_template, label=u"Mouth surface",
                    c=lambda *args: self.build_base_loc())
        pm.menuItem(p=menu_template, label=u"Mouth tweak surface",
                    c=lambda *args: self.build_base_loc())

        menu_tools = pm.menu(label="Tools", tearOff=False)
        pm.menuItem(p=menu_tools, label=u"Symmetry surface",
                    c=lambda *args: self.symmetry_surface())

    def rig_pre_frame(self, parent):
        layout = pm.frameLayout(p=parent, lv=False, mw=10, mh=5, bgs=True)
        pm.button("xdMouthCreatorNewRigBtn", label=u"New",
                  c=lambda *args: self.new_rig_structure())
        pm.setParent(layout)

        return layout

    def neck_ear_module_frame(self, parent):
        frame = pm.frameLayout(p=parent, label="Preparatory Work", mh=5, mw=10)
        proxy_grp_frame = pm.frameLayout(p=frame, label=u"Proxy", mh=10, mw=10, bgs=True)
        pm.button(label=u"Build Proxy", c=lambda *args: self.proxy_neck_ear())
        pm.setParent(proxy_grp_frame)

        pm.button(label=u"Build Module", c=lambda *args: self.build_neck_head_module())

        pm.setParent(frame)
        return frame

    def eye_module_frame(self, parent):
        frame = pm.frameLayout(p=parent, label="Preparatory Work", mh=5, mw=10)

        pm.frameLayout(label=u"Eye Guid Curve", ann=u"这些曲线将会约束眼皮的蒙皮骨骼", mh=10, mw=10, bgs=True, cll=True, cl=True)
        pm.text(label="Left side:", al="left")

        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpMasterCurveField",
            label=u"Left Up Master Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftUpMasterCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowMasterCurveField",
            label=u"Left Low Master Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftLowMasterCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpBlinkCurveField",
            label=u"Left Up Blink Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftUpBlinkCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowBlinkCurveField",
            label=u"Left Low Blink Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftLowBlinkCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpOutCurveField",
            label=u"Left Up Out Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftUpOutCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowOutCurveField",
            label=u"Left Low Out Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftLowOutCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpTweakCurveField",
            label=u"Left Up Tweak Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftUpTweakCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowTweakCurveField",
            label=u"Left Low Tweak Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftLowTweakCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpFreshyCurveField",
            label=u"Left Up Freshy Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftUpFreshyCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowFreshyCurveField",
            label=u"Left Low Freshy Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftLowFreshyCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpShapeSurfaceField",
            label=u"Left Up Shape Surface", bl=u"Get Object", adj=2,
            bc=lambda *args: self.import_eye_up_shape_surface(vertical="Up", side="LF",
                                                              field="xdMouthCreatorLeftUpShapeSurfaceField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowShapeSurfaceField",
            label=u"Left Low Shape Surface", bl=u"Get Object", adj=2,
            bc=lambda *args: self.import_eye_up_shape_surface(vertical="Low", side="LF",
                                                              field="xdMouthCreatorLeftLowShapeSurfaceField"))

        pm.separator(style="in", h=5)

        pm.text(label="Right side:", al="left")

        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpMasterCurveField",
            label=u"Right Up Master Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpMasterCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowMasterCurveField",
            label=u"Right Low Master Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightLowMasterCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpBlinkCurveField",
            label=u"Right Up Blink Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpBlinkCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowBlinkCurveField",
            label=u"Right Low Blink Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightLowBlinkCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpOutCurveField",
            label=u"Right Up Out Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpOutCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowOutCurveField",
            label=u"Right Low Out Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpOutCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpTweakCurveField",
            label=u"Right Up Tweak Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpTweakCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowTweakCurveField",
            label=u"Right Low Tweak Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightLowTweakCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpFreshyCurveField",
            label=u"Right Up Freshy Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpFreshyCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowFreshyCurveField",
            label=u"Right Low Freshy Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightLowFreshyCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpShapeSurfaceField",
            label=u"Right Up Shape Surface", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpShapeSurfaceField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowShapeSurfaceField",
            label=u"Right Low Shape Surface", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightLowShapeSurfaceField",
                                                         group="RT_Eye_01_Curve_Grp"))

        pm.setParent("..")

        pm.frameLayout(label=u"Eye Control location", mh=10, mw=10, bgs=True, cll=True, cl=False)
        pm.text(label=u"* is optional", al='left')
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftEyeGeoField",
            label=u"Left eye geo", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftEyeGeoField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightEyeGeoField",
            label=u"Right eye geo", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightEyeGeoField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftEyeProxyField",
            label=u"Left eye proxy(*)", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftEyeProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightEyeProxyField",
            label=u"Right eye proxy(*)", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightEyeProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftMasterCtrlField",
            label=u"Left master control", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_master_ctrl_field(side="LF", field="xdMouthCreatorLeftMasterCtrlField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightMasterCtrlField",
            label=u"Right master control", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_master_ctrl_field(side="RT", field="xdMouthCreatorRightMasterCtrlField"))
        pm.setParent("..")

        pm.button(label=u"Build Module", c=lambda *args: self.build_eye_module())

        pm.setParent(frame)
        return frame

    def brow_module_frame(self, parent):
        frame = pm.frameLayout(p=parent, label="Preparatory Work", mh=5, mw=10)

        pm.button(label="Add module", p=frame, vis=False)

        pre_frame = pm.frameLayout(p=frame, label=u"Components", mh=10, mw=10, bgs=True)
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftBrowSurfaceField",
            label="Left brow surface", adj=2, text=self.left_brow_surface, bl="Get Object",
            bc=lambda *args: self.brow_follicle_field(
                template_name="lf_brow_sub_surface",
                field="xdMouthCreatorLeftBrowSurfaceField",
                side="LF",
                module="Brow_01"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightBrowSurfaceField",
            label="Right brow surface", adj=2, text=self.right_brow_surface, bl="Get Object",
            bc=lambda *args: self.brow_follicle_field(
                template_name="rt_brow_sub_surface",
                field="xdMouthCreatorRightBrowSurfaceField",
                side="RT",
                module="Brow_01"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftBrowCurveField",
            label="Left brow curve", adj=2, text=self.left_brow_curve, bl="Get Object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftBrowCurveField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightBrowCurveField",
            label="Right brow curve", adj=2, text=self.right_brow_curve, bl="Get Object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightBrowCurveField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftMasterSurfaceField",
            label="Left master surface", adj=2, text=self.left_master_ctrl_surface, bl="Get Object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftMasterSurfaceField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightMasterSurfaceField",
            label="Right master surface", adj=2, text=self.right_master_ctrl_surface, bl="Get Object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightMasterSurfaceField"))
        pm.setParent(pre_frame)

        parameter_frame = pm.frameLayout(p=frame, label=u"Parameters", mh=5, mw=10, bgs=True)
        pm.intFieldGrp("xdMouthCreatorBrowSubSegmentField", label=u"Segment", numberOfFields=1, value1=7)
        pm.setParent(parameter_frame)

        pm.button(label="Build module", p=frame, c=lambda *args: self.build_brow_module())
        pm.setParent(frame)

        return frame

    def nose_module_frame(self, parent):
        frame = pm.frameLayout(p=parent, label=u"Preparatory Work", mh=5, mw=10)
        proxy_grp_frame = pm.frameLayout(p=frame, label=u"Proxy", mh=10, mw=10, bgs=True)
        pm.button(label=u"Build Proxy", c=lambda *args: self.proxy_nose())

        pm.frameLayout(p=proxy_grp_frame, label=u"component detail", cl=True, cll=True, mh=10, mw=10)
        pm.textFieldButtonGrp(
            "xdMouthCreatorNoseBridgeProxyField",
            label=u"Nose bridge",
            adj=2,
            bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorNoseBridgeProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorNoseMasterProxyField",
            label=u"Nose master",
            adj=2,
            bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorNoseMasterProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorNoseTipProxyField",
            label=u"Nose tip",
            adj=2,
            bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorNoseTipProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorNoseLeftProxyField",
            label=u"Nose left",
            adj=2,
            bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorNoseLeftProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorNoseRightProxyField",
            label=u"Nose right",
            adj=2,
            bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorNoseRightProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorNoseUpProxyField",
            label=u"Nose up",
            adj=2,
            bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorNoseUpProxyField"))
        pm.setParent("..")
        pm.setParent(proxy_grp_frame)

        pm.button(label=u"Build Module", p=frame, c=lambda *args: self.build_nose_module())

        pm.setParent(frame)
        return frame

    def cheek_module_frame(self, parent):
        frame = pm.frameLayout(p=parent, label=u"Preparatory Work", mh=5, mw=10)

        proxy_grp_frame = pm.frameLayout(p=frame, label=u"Proxy", mh=10, mw=10, bgs=True)
        pm.button(label=u"Build Proxy", c=lambda *args: self.proxy_cheek())
        pm.frameLayout(p=proxy_grp_frame, label=u"component detail", cl=True, cll=True, mh=10, mw=10)

        pm.text(label="Left side:", al="left")

        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftCheek01ProxyField",
            label=u"Left cheek 01", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftCheek01ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftCheek02ProxyField",
            label=u"Left cheek 02", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftCheek02ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftCheek03ProxyField",
            label=u"Left cheek 03", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftCheek03ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftCheek04ProxyField",
            label=u"Left cheek 04", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftCheek04ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftCheek05ProxyField",
            label=u"Left cheek 05", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftCheek05ProxyField"))

        pm.separator(style="in", h=5)

        pm.rowColumnLayout(numberOfColumns=2, adj=1)
        pm.text(label="Right side:", al="left")
        pm.button(label=u"Mirror Proxy", c=lambda *args: self.mirror_cheek_proxy())
        pm.setParent("..")

        pm.textFieldButtonGrp(
            "xdMouthCreatorRightCheek01ProxyField",
            label=u"Right cheek 01", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightCheek01ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightCheek02ProxyField",
            label=u"Right cheek 02", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightCheek02ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightCheek03ProxyField",
            label=u"Right cheek 03", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightCheek03ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightCheek04ProxyField",
            label=u"Right cheek 04", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightCheek04ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightCheek05ProxyField",
            label=u"Right cheek 05", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightCheek05ProxyField"))

        pm.setParent("..")
        pm.setParent(proxy_grp_frame)

        pm.button(label=u"Build Module", p=frame, c=lambda *args: self.build_cheek_module())
        pm.setParent(frame)
        return frame

    def linkage_frame(self, parent):
        frame = pm.frameLayout(p=parent, label=u"Preparatory Work", mh=5, mw=10)
        pm.button(label=u"Build", p=frame, c=lambda *args: self.build_linkage())
        pm.setParent(frame)
        return frame

    def eye_control_location_frame_init(self):
        for side in ["LF", "RT"]:
            if side == "LF":
                side_alias = "Left"
            else:
                side_alias = "Right"

            for vertical in ["Up", "Low"]:
                prefix = "{}_{}_{}".format(side, self.eye_module, vertical)
                for item in ["Master", "Blink", "Out", "Tweak", "Freshy"]:
                    curve = "{}_{}_Curve".format(prefix, item)
                    if pm.objExists(curve):
                        pm.textFieldButtonGrp(
                            "xdMouthCreator{}{}{}CurveField".format(side_alias, vertical, item), e=True, text=curve)
                surface = "{}_Shape_Surface".format(prefix)
                # print("surface:{}".format(surface))
                if pm.objExists(surface):
                    pm.textFieldButtonGrp(
                        "xdMouthCreator{}{}ShapeSurfaceField".format(side_alias, vertical), e=True, text=surface)
            # control location frame上面的字段
            eye_geo = "{}_Eye_Geo".format(side)
            if pm.objExists(eye_geo):
                pm.textFieldButtonGrp("xdMouthCreator{}EyeGeoField".format(side_alias), e=True, text=eye_geo)

            eye_proxy = "{}_proxy_eye".format(side)
            if pm.objExists(eye_proxy):
                pm.textFieldButtonGrp("xdMouthCreator{}EyeProxyField".format(side_alias), e=True, text=eye_proxy)

            master_ctrl = "{}_{}_Master_Ctrl".format(side, self.eye_module)
            if pm.objExists(master_ctrl):
                pm.textFieldButtonGrp("xdMouthCreator{}MasterCtrlField".format(side_alias), e=True, text=master_ctrl)

        return

    @staticmethod
    def nose_proxy_frame_init():
        for item in ["Bridge", "Master", "MD", "LF", "RT", "Up"]:
            proxy_loc = "proxyNose{}Loc".format(item)

            if item == "MD":
                item = "Tip"
            elif item == "LF":
                item = "Left"
            elif item == "RT":
                item = "Right"

            if pm.objExists(proxy_loc):
                pm.textFieldButtonGrp("xdMouthCreatorNose{}ProxyField".format(item), e=True, text=proxy_loc)
        return

    def cheek_proxy_frame_init(self):
        for side in ["LF", "RT"]:
            for index in range(0, 5):
                proxy_loc = "{}_proxyCheek{}Loc".format(side, "{0:02d}".format(index + 1))

                if side == "LF":
                    sider = "Left"
                else:
                    sider = "Right"

                if pm.objExists(proxy_loc):
                    pm.textFieldButtonGrp(
                        "xdMouthCreator{}Cheek{}ProxyField".format(sider, "{0:02d}".format(index + 1)),
                        e=True, text=proxy_loc)
        return

    def mouth_module_frame(self, parent):
        frame = pm.frameLayout(p=parent, label=u"Preparatory Work", mh=5, mw=10)

        curve_grp_frame = pm.frameLayout(p=frame, label=u"Mouth Curve Grp", cll=True, cl=True, mh=10, mw=10, bgs=True)
        pm.textFieldButtonGrp(
            "xdMouthCreatorUpBaseCurveField",
            label=u"Up base curve",
            bl=u"Get Object",
            adj=2,
            text=self.up_base_curve,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorUpBaseCurveField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLowBaseCurveField",
            label=u"Low base curve",
            bl=u"Get Object",
            adj=2,
            text=self.low_base_curve,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLowBaseCurveField"))

        pm.textFieldButtonGrp(
            "xdMouthCreatorUpTweakSurfaceField",
            label=u"Up tweak surface",
            bl=u"Get Object",
            adj=2,
            text=self.up_tweak_surface,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorUpTweakSurfaceField"))

        pm.textFieldButtonGrp(
            "xdMouthCreatorLowTweakSurfaceField",
            label=u"Low tweak surface",
            bl=u"Get Object",
            adj=2,
            text=self.low_tweak_surface,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLowTweakSurfaceField"))

        pm.setParent(curve_grp_frame)

        out_curve_grp_frame = pm.frameLayout(p=frame, label=u"Out Curve Grp", cll=True, cl=True, mh=10, mw=10,
                                             bgs=True)
        pm.textFieldButtonGrp(
            "xdMouthCreatorUpOutCurveField",
            label=u"Up out curve",
            bl=u"Get Object",
            adj=2,
            text=self.up_out_curve,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorUpOutCurveField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLowOutCurveField",
            label=u"Low out curve",
            bl=u"Get Object",
            adj=2,
            text=self.low_out_curve,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLowOutCurveField"))
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
                module="Mouth_01_LipSew"))

        pm.separator(h=5, style="in")
        pm.intFieldGrp("xdMouthCreatorTweakSegmentField", label=u"tweak segment", numberOfFields=1, value1=6)

        jaw_frame = pm.frameLayout(p=frame, label="Jaw Control", cll=True, cl=True, mh=10, mw=10, bgs=True)
        pm.checkBoxGrp(label=u"Mouth cavity", numberOfCheckBoxes=1, label1='Teeth', value1=True)
        pm.button("xdMouthCreatorAddProxyJawBtn", label=u"Add proxy jaw", c=lambda *args: self.proxy_jaw())

        pm.setParent(jaw_frame)

        proxy_tongue_frame = pm.frameLayout(p=frame, label=u"Tongue Proxy", cll=True, cl=False, mh=10, mw=10, bgs=True)
        pm.button(label=u"Build Proxy", c=lambda *args: self.proxy_tongue())
        pm.setParent(proxy_tongue_frame)

        pm.button("xdMouthCreatorBuildMouthModuleBtn", p=frame, label=u"Build Module",
                  c=lambda *args: self.build_mouth_module())

        pm.setParent(frame)
        return frame

    @staticmethod
    def get_object_in_field(field):
        sel_object = pm.ls(sl=True)[0]
        pm.textFieldButtonGrp(field, e=True, text=sel_object)
        return

    def brow_follicle_field(self, template_name="lf_brow_sub_surface",
                            field="xdMouthCreatorLeftBrowSurfaceField", side="LF", module="Brow_01"):
        u"""导入眉毛的surface模板

        :param template_name: 模板文件的名字
        :param field:
        :param side:
        :param module:
        :return:
        """
        template_file = path(template_dir).joinpath(
            "{}.mb".format(template_name))

        scence_name = "{}_{}_Sub_Surface".format(side, module)
        import_object = pm.rename(imported_object(template_file), scence_name)

        deformer_grp = "{}_{}_Deformer_Grp".format(side, module)
        if not pm.objExists(deformer_grp):
            pm.createNode("transform", name=deformer_grp, p="Deformer_Grp")

        sub_deformer_grp = "{}_{}_Sub_Deformer_Grp".format(side, module)
        if not pm.objExists(sub_deformer_grp):
            pm.createNode("transform", name=sub_deformer_grp,
                          p="{}_{}_Deformer_Grp".format(side, module))
            pm.parent(scence_name, sub_deformer_grp)

        pm.textFieldButtonGrp(field, e=True, text=scence_name)

        return True

    def import_mouth_surface(self, template="", field="", module="Mouth_01"):
        template_file = path(template_dir).joinpath("{}.mb".format(template))
        import_object = pm.rename(imported_object(
            template_file), "MD_{}_Surface".format(module))
        deformer_grp = "MD_{}_Deformer_Grp".format(self.mouth_module)
        if pm.objExists(deformer_grp):
            pm.parent(import_object, deformer_grp)
        pm.textFieldButtonGrp(field, e=True, text=import_object)

        return True

    def import_tweak_surface(self, location, field):
        template_file = path(template_dir).joinpath("mouth_tweak_surface.mb")
        import_object = pm.rename(imported_object(template_file),
                                  "MD_{}_{}_Tweak_Surface".format(self.mouth_module, location))
        if pm.objExists("MD_Mouth_01_Curve_Grp"):
            pm.parent(import_object, "MD_Mouth_01_Curve_Grp")
        pm.textFieldButtonGrp(field, e=True, text=import_object)

        return True

    def import_eye_up_shape_surface(self, vertical="Up", side="LF", field=""):
        if vertical == "Up":
            template_file = path(template_dir).joinpath(
                "lf_eye_up_shape_surface.mb")
        else:
            template_file = path(template_dir).joinpath(
                "lf_eye_low_shape_surface.mb")

        import_object = pm.rename(imported_object(template_file),
                                  "{}_{}_{}_Shape_Surface".format(side, self.eye_module, vertical))
        if pm.objExists("{}_{}_Curve_Grp".format(side, self.eye_module)):
            pm.parent(import_object, "{}_{}_Curve_Grp".format(
                side, self.eye_module))

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
            pm.confirmDialog(title=u'错误提示', icn="warning",
                             message=u"场景中已存在绑定\n"
                                     u"提示：开始绑定前需要检查文件，确保场景中没有存在绑定结构")
        return

    def build_mouth_module(self):
        self.before_build_mouth()

        self.mouth_creator.build_module()
        return

    def build_base_loc(self):
        if pm.window("xdBaseLocCreatorWnd", ex=True):
            pm.deleteUI("xdBaseLocCreatorWnd")
        pm.window("xdBaseLocCreatorWnd", title="Base Loc Creator")
        pm.showWindow("xdBaseLocCreatorWnd")

    def before_build_mouth(self):
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

    def proxy_jaw(self):
        self.before_build_mouth()

        if pm.objExists("proxyJawRoot"):
            pm.error(u"代理Jaw已经创建了")
        if self.mouth_creator.proxy_jaw():
            pm.button("xdMouthCreatorAddProxyJawBtn", e=True, en=False)

    def before_build_brow(self):
        self.left_brow_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftBrowSurfaceField", q=True, text=True)
        self.right_brow_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorRightBrowSurfaceField", q=True, text=True)
        self.brow_creator.left_brow_surface = self.left_brow_surface
        self.brow_creator.right_brow_surface = self.right_brow_surface

        self.left_brow_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftBrowCurveField", q=True, text=True)
        self.right_brow_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightBrowCurveField", q=True, text=True)
        self.brow_creator.left_brow_curve = self.left_brow_curve
        self.brow_creator.right_brow_curve = self.right_brow_curve

    def build_brow_module(self):
        self.before_build_brow()
        self.brow_creator.init_structure()
        self.brow_creator.output_follicle()
        self.brow_creator.build_master_control()
        self.brow_creator.master_sub_control()
        self.brow_creator.make_master_control_rotate()
        self.brow_creator.make_master_control_scale()
        self.brow_creator.master_ctrl_vis()
        self.brow_creator.local_rig_out()

        return True

    def proxy_nose(self):
        self.nose_creator.proxy()

    def proxy_neck_ear(self):
        self.neck_ear_creator.proxy()

    def proxy_tongue(self):
        self.mouth_creator.proxy_tongue()

    def proxy_cheek(self):
        self.cheek_creator.proxy()

    def mirror_cheek_proxy(self):
        self.cheek_creator.mirror_proxy()

    @staticmethod
    def symmetry_surface():
        u"""对称surface"""
        sel_list = pm.ls(sl=True)
        if len(sel_list) > 1:
            source = sel_list[0]
            for index in range(1, len(sel_list)):
                symmetry_surface(source, sel_list[index])
        else:
            pm.error(u"请选择两个或两个以上的对象")

    def build_neck_head_module(self):
        self.neck_ear_creator.build_module()

    def build_nose_module(self):
        self.nose_creator.build_module()

    def build_cheek_module(self):
        self.cheek_creator.build_module()

    def build_eye_module(self):
        self.eye_module_init()
        self.eye_creator.init_structure()
        self.eye_creator.build_module()
        return

    def eye_module_init(self):
        self.eye_creator.left_up_master_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpMasterCurveField", q=True, text=True)
        self.eye_creator.left_low_master_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowMasterCurveField", q=True, text=True)
        self.eye_creator.left_up_blink_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpBlinkCurveField", q=True, text=True)
        self.eye_creator.left_low_blink_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowBlinkCurveField", q=True, text=True)
        self.eye_creator.left_up_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpOutCurveField", q=True, text=True)
        self.eye_creator.left_low_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowOutCurveField", q=True, text=True)
        self.eye_creator.left_up_tweak_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpTweakCurveField", q=True, text=True)
        self.eye_creator.left_low_tweak_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowTweakCurveField", q=True, text=True)
        self.eye_creator.left_up_freshy_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpFreshyCurveField", q=True, text=True)
        self.eye_creator.left_low_freshy_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowFreshyCurveField", q=True, text=True)
        self.eye_creator.left_up_shape_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpShapeSurfaceField", q=True, text=True)
        self.eye_creator.left_low_shape_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowShapeSurfaceField", q=True, text=True)

        self.eye_creator.right_up_master_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpMasterCurveField", q=True, text=True)
        self.eye_creator.right_low_master_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowMasterCurveField", q=True, text=True)
        self.eye_creator.right_up_blink_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpBlinkCurveField", q=True, text=True)
        self.eye_creator.right_low_blink_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowBlinkCurveField", q=True, text=True)
        self.eye_creator.right_up_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpOutCurveField", q=True, text=True)
        self.eye_creator.right_low_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowOutCurveField", q=True, text=True)
        self.eye_creator.right_up_tweak_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpTweakCurveField", q=True, text=True)
        self.eye_creator.right_low_tweak_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowTweakCurveField", q=True, text=True)
        self.eye_creator.right_up_freshy_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpFreshyCurveField", q=True, text=True)
        self.eye_creator.right_low_freshy_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowFreshyCurveField", q=True, text=True)
        self.eye_creator.right_up_shape_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpShapeSurfaceField", q=True, text=True)
        self.eye_creator.right_low_shape_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowShapeSurfaceField", q=True, text=True)

        self.eye_creator.left_eye_geo = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftEyeGeoField", q=True, text=True)
        self.eye_creator.right_eye_geo = pm.textFieldButtonGrp(
            "xdMouthCreatorRightEyeGeoField", q=True, text=True)
        self.eye_creator.left_eye_proxy = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftEyeProxyField", q=True, text=True)
        self.eye_creator.right_eye_proxy = pm.textFieldButtonGrp(
            "xdMouthCreatorRightEyeProxyField", q=True, text=True)

        return

    def eye_component_in_field(self, field, group=None):
        target = pm.ls(sl=True)[0]
        self.eye_creator.init_structure()
        drag_to_group_and_field(target, field=field, group=group)
        return

    def eye_master_ctrl_field(self, side, field):
        self.eye_creator.init_structure()

        prefix = "{}_{}".format(side, self.eye_module)
        master_ctrl = "{}_Master_Ctrl".format(prefix)
        jnt_or_control_grp(name=master_ctrl, object_type="tours", parent_node="{}_Grp".format(prefix))
        pm.textFieldButtonGrp(field, e=True, text=master_ctrl)

    def build_linkage(self):
        jaw_ctrl = "MD_Mouth_01_Jaw_Ctrl"
        jaw_ctrl_grp = pm.PyNode(jaw_ctrl).getParent()

        pm.parentConstraint(jaw_ctrl, "MD_Tongue_01_Main_Grp", mo=True)
        pm.scaleConstraint(jaw_ctrl, "MD_Tongue_01_Main_Grp", mo=True)

        mouth_master_ctrl_grp = "MD_Mouth_01_Master_Ctrl_Grp"
        constraint = pm.parentConstraint(jaw_ctrl, jaw_ctrl_grp, mouth_master_ctrl_grp, mo=True)

        driver_value = [-1, 0]
        value = [0, 1]
        for index in range(0, len(driver_value)):
            pm.setDrivenKeyframe(
                constraint,
                at="{}W1".format(jaw_ctrl_grp),
                cd="{}.{}".format(jaw_ctrl, "rotateX"),
                dv=driver_value[index],
                value=value[index],
                itt="linear",
                ott="linear",
            )

        for side in ["LF", "RT"]:
            pm.parentConstraint(jaw_ctrl, "{}_Cheek_01_04_Ctrl_Grp".format(side), mo=True)
            pm.PyNode("{}_Cheek_01_04_Ctrl_02_Grp".format(side)).translate.connect(
                pm.PyNode("{}_Cheek_01_04_Ctrl_Jnt_02_Grp".format(side)).translate)
        print "Done!"
        return


def open_creator_ui():
    FaceCreatorUI()
