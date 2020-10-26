#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/10/12 23:26
# @Author  : Li XiaoJun
# @Site    :
# @File    : main.py
from imp import reload

from pymel import core as pm
from animation import common

reload(common)


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
    """将毛囊形节点的两个属性：输出平移和输出旋转，
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


class MouthCreator(Creator):

    def __init__(self):
        super(MouthCreator, self).__init__()

    def build(self):
        self.__mouth_surface_location()
        self.__rig_base_ctrl_out()
        self.__add_bind_jnt_follicle_on_tweak_surface()
        self.__motion_path_on_base_curve_to_tweak_jnt_grp()
        self.__motion_path_on_out_curve_to_tweak_ctrl_grp()
        self.__skin_out_curve()
        self.__use_dm_node_to_tweak_ctrl_parent_and_jnt_02_grp()
        self.__skin_tweak_surface()
        self.__skin_lip_sew_surface_and_connect_follicle_shape()
        # self.__lip_sew_ctrl_drive_follicle_shape()

    def __mouth_surface_location(self):
        """利用mouth surface定位毛囊，
        并利用毛囊的位移节点（父节点）对控制嘴唇的骨骼的组节点进行目标约束
        """
        self.__location_on_mouth_surface_to_follicle()

        self.__follicle_output_translate_rotate_to_parent(
            ["MD_Mouth_01_Master_Ctrl_FollicleShape",
             "LF_Mouth_01_Ctrl_Jnt_FollicleShape",
             "RT_Mouth_01_Ctrl_Jnt_FollicleShape"])

        for side in ["LF", "RT"]:
            for pos in ["Up", "Low"]:
                if side == "LF":
                    flip_up = -1.0
                elif side == "RT":
                    flip_up = 1.0
                pm.aimConstraint(
                    "{}_Mouth_01_Ctrl_Jnt_Follicle".format(side),
                    "{}_Mouth_01_Ctrl_{}_Jnt_Grp".format(side, pos),
                    aimVector=[0, 0, -1],
                    upVector=[0, 1 * flip_up, 0],
                    worldUpType="object",
                    worldUpObject="{}_Mouth_01_Ctrl_Jnt".format(pos))
        return

    def __skin_base_curve(self):
        prefix_list = ["Up", "Low"]
        for prefix in prefix_list:
            base_curve = pm.PyNode(
                "MD_Mouth_01_{}_Base_Curve".format(prefix))
            base_curve_skin_items = [
                "{}_Mouth_01_Ctrl_Jnt".format(prefix),
                base_curve.getShape()]
            for ctrl_jnt_item in ["LF", "RT"]:
                base_curve_skin_items.append(
                    "{}_Mouth_01_Ctrl_{}_Jnt".format(ctrl_jnt_item, prefix))
            pm.skinCluster(base_curve_skin_items,
                           name="MD_Mouth_01_{}_Base_Curve_SC".format(prefix))
        return

    def __corner_ctrl_connect_cpos_loc(self):
        """将左右嘴角控制器与cpos（嘴角位置定位loc）连接起来"""
        cpos_locs = ["LF_Mouth_01_Ctrl_Loc", "RT_Mouth_01_Ctrl_Loc"]
        for cpos_name in cpos_locs:
            ctrl = pm.PyNode(cpos_name.replace("_Loc", ""))
            ctrl.translate.connect("{}.translate".format(cpos_name))

        pm.PyNode("MD_Mouth_01_Master_Ctrl").translate.connect(
            "MD_Mouth_01_Master_Ctrl_Loc.translate")
        return

    def __lip_ctrl_connect_ctrl_jnt(self):
        """连接嘴唇控制器"""
        base_ctrl_grp = pm.PyNode("MD_Mouth_01_Base_Ctrl_Grp")
        ctrl_jnts = ["Up_Mouth_01_Ctrl_Jnt", "Low_Mouth_01_Ctrl_Jnt"]
        for ctrl_jnt in ctrl_jnts:
            ctrl = pm.PyNode(ctrl_jnt.replace("_Jnt", ""))
            md_node = pm.createNode("multiplyDivide",
                                    name=ctrl_jnt.replace("_Jnt", "_Scale_MD"))
            md_node.attr("operation").set(1)
            ctrl.attr("translate").connect(md_node.attr("input1"))
            base_ctrl_grp.attr("scale").connect(md_node.attr("input2"))
            md_node.attr("output").connect("{}.translate".format(ctrl_jnt))
            ctrl.rotate.connect("{}.rotate".format(ctrl_jnt))

        # 　连接base ctrl grp， 让嘴巴的模块控制器能够工作
        mouth_master_ctrl = pm.PyNode("MD_Mouth_01_Master_Ctrl")
        mouth_master_ctrl.attr("localScale").connect(
            base_ctrl_grp.attr("scaleX"))
        mouth_master_ctrl.attr("localScale").connect(
            base_ctrl_grp.attr("scaleY"))
        mouth_master_ctrl.attr("localScale").connect(
            base_ctrl_grp.attr("scaleZ"))
        pm.parentConstraint("MD_Mouth_01_Master_Ctrl_Null", base_ctrl_grp)

        mouth_master_ctrl.attr("translateZ").connect(
            "MD_Mouth_01_Master_Ctrl_Null.translateZ")
        mouth_master_ctrl.attr("rotateZ").connect(
            "MD_Mouth_01_Master_Ctrl_Null.rotateZ")

        base_ctrl_grp.translate.connect(
            "MD_Mouth_01_Base_Ctrl_Out_Grp.translate")
        base_ctrl_grp.rotate.connect("MD_Mouth_01_Base_Ctrl_Out_Grp.rotate")

        return

    def __rig_base_ctrl_out(self):
        self.__skin_base_curve()
        self.__corner_ctrl_connect_cpos_loc()
        self.__lip_ctrl_connect_ctrl_jnt()

    def __add_bind_jnt_follicle_on_tweak_surface(self):
        # 嘴唇一侧的段数，例如上嘴唇左侧为5段，右侧也为5段，加上左右嘴角，
        # 那么控制上嘴唇的骨骼数就是 5+5+2=12
        segment = 5
        for location in ["Up", "Low"]:
            tweak_surface = pm.PyNode(
                "MD_Mouth_01_{}_Tweak_Surface".format(location))
            for side in ["LF", "RT"]:
                if location == "Up":
                    follicle_shape = pm.PyNode(
                        "{}_Mouth_01_Lip_Jnt_FollicleShape".format(side))
                    tweak_surface.getShape().attr("local").connect(
                        follicle_shape.attr("inputSurface"))
                    tweak_surface.getShape().attr("worldMatrix[0]").connect(
                        follicle_shape.attr("inputWorldMatrix"))
                    follicle = follicle_shape.getParent()
                    follicle_shape.attr("outTranslate").connect(
                        follicle.translate)
                    follicle_shape.attr("outRotate").connect(
                        follicle.rotate)

                    if side == "LF":
                        follicle_shape.attr("parameterU").set(0.5)
                        follicle_shape.attr("parameterV").set(0.0)
                    elif side == "RT":
                        follicle_shape.attr("parameterU").set(0.5)
                        follicle_shape.attr("parameterV").set(1.0)

                for index in range(1, segment + 1):
                    # Todo: 模块化绑定模式时，改为创建节点
                    follicle_shape = pm.PyNode(
                        "{}_Mouth_01_{}Lip_{}_Jnt_FollicleShape".format(
                            side, location, "{0:02d}".format(index)))
                    # 通过调整参数为定位毛囊的位置
                    follicle_shape.attr("parameterU").set(0.5)
                    parameter_value = 0.0
                    if side == "LF":
                        if index < 5:
                            parameter_value = 0.111 * (segment - index)
                        elif index == 5:
                            parameter_value = 0.037
                        follicle_shape.attr("parameterV").set(parameter_value)
                    elif side == "RT":
                        parameter_value = pm.getAttr(
                            "LF_Mouth_01_{}Lip_{}_Jnt_FollicleShape"
                            ".parameterV".format(location,
                                                 "{0:02d}".format(index)))
                        follicle_shape.attr("parameterV").set(
                            1 - parameter_value)

                    tweak_surface.getShape().attr("local").connect(
                        follicle_shape.attr("inputSurface"))
                    tweak_surface.getShape().attr("worldMatrix[0]").connect(
                        follicle_shape.attr("inputWorldMatrix"))
                    follicle = follicle_shape.getParent()
                    follicle_shape.attr("outTranslate").connect(
                        follicle.translate)
                    follicle_shape.attr("outRotate").connect(
                        follicle.rotate)
        return

    def __location_on_mouth_surface_to_follicle(self):
        """求出locator（为控制嘴唇整体的三根骨骼进行定位）在mouth surface上面的位置（参数U，V），
        然后将这个位置信息与控制嘴角骨骼的毛囊体的参数 U 和 V 进行连接，
        毛囊体会根据参数移动到相应的位置，
        这样控制了locator， 就控制了毛囊体，也就间接的控制了骨骼
        """
        mouth_surface = "MD_Mouth_01_Surface"
        for side_prefix in ["LF", "RT", "MD"]:
            if side_prefix == "MD":
                corner_locator = "{}_Mouth_01_Master_Ctrl_Loc".format(
                    side_prefix)
            else:
                corner_locator = "{}_Mouth_01_Ctrl_Loc".format(side_prefix)

            cpos_node = pm.createNode(
                "closestPointOnSurface",
                name="{}_Mouth_01_Ctrl_CPOS".format(side_prefix))
            corner_locator_shape = pm.PyNode(corner_locator).getShape()
            corner_locator_shape.attr("worldPosition[0]").connect(

                cpos_node.attr("inPosition"))

            mouth_surface_shape = pm.PyNode(mouth_surface).getShape()
            mouth_surface_shape.attr("worldSpace[0]").connect(
                cpos_node.attr("inputSurface"))

            if side_prefix == "MD":
                follicle = "{}_Mouth_01_Master_Ctrl_Follicle".format(
                    side_prefix)
            else:
                follicle = "{}_Mouth_01_Ctrl_Jnt_Follicle".format(side_prefix)

            follicle_shape = pm.PyNode(follicle).getShape()
            mouth_surface_shape.attr("local").connect(
                follicle_shape.attr("inputSurface"))
            mouth_surface_shape.attr("worldMatrix[0]").connect(
                follicle_shape.attr("inputWorldMatrix"))
            cpos_node.attr("parameterU").connect(
                follicle_shape.attr("parameterU"))
            cpos_node.attr("parameterV").connect(
                follicle_shape.attr("parameterV"))

        return

    def __follicle_output_translate_rotate_to_parent(self, follicle_shapes=[]):
        for follicle_shape in follicle_shapes:
            follicle_shape_out_for_parent(follicle_shape)
        return

    def __motion_path_on_base_curve_to_tweak_jnt_grp(self):
        segment = 3
        master_ctrl = "MD_Mouth_01_Master_Ctrl"
        for location in ["Up", "Low"]:
            base_curve = "MD_Mouth_01_{}_Base_Curve".format(location)
            for side in ["LF", "RT"]:
                for index in range(1, segment + 1):
                    jnt_grp = "{}_Mouth_01_{}Tweak_{}_Ctrl_Jnt_Grp".format(
                        side, location, "{0:02d}".format(index))
                    mp_node = pm.createNode(
                        "motionPath",
                        name=jnt_grp.replace("_Grp", "_MP"))
                    mp_node2 = pm.createNode(
                        "motionPath",
                        name=jnt_grp.replace("_Grp", "_02_MP"))

                    u_value = 0.0
                    if side == "LF":
                        if index < 3:
                            u_value = 0.2 * (segment - index)
                        elif index == 3:
                            u_value = 0.067
                        mp_node.attr("uValue").set(u_value)
                        mp_node2.attr("uValue").set(u_value)
                        mp_node2.attr("fractionMode").set(True)
                    elif side == "RT":
                        u_value = pm.getAttr(
                            "LF_Mouth_01_{}Tweak_{}_Ctrl_Jnt_02_MP"
                            ".uValue".format(location,
                                             "{0:02d}".format(index)))
                        mp_node.attr("uValue").set(
                            1 - u_value)
                        mp_node2.attr("uValue").set(1 - u_value)
                        mp_node2.attr("fractionMode").set(True)

                    pm.PyNode(base_curve).getShape().attr(
                        "worldSpace[0]").connect(mp_node.attr("geometryPath"))
                    pm.PyNode(base_curve).getShape().attr(
                        "worldSpace[0]").connect(mp_node2.attr("geometryPath"))
                    bc_node = pm.createNode(
                        "blendColors",
                        name=jnt_grp.replace("_Grp", "_MP_BC"))
                    mp_node.attr("allCoordinates").connect(
                        bc_node.attr("color1"))
                    mp_node2.attr("allCoordinates").connect(
                        bc_node.attr("color2"))
                    pm.PyNode(master_ctrl).attr("evenTweak").connect(
                        bc_node.attr("blender"))
                    bc_node.attr("output").connect(
                        pm.PyNode(jnt_grp).translate)

                    pm.PyNode("MD_Mouth_01_Bind_Jnt_Ori_Null").rotate.connect(
                        pm.PyNode(jnt_grp).rotate)

                if location == "Up":
                    jnt_grp = "{}_Mouth_01_Tweak_Ctrl_Jnt_Grp".format(
                        side)
                    mp_node = pm.createNode(
                        "motionPath",
                        name=jnt_grp.replace("_Grp", "_MP"))
                    mp_node.attr("allCoordinates").connect(
                        pm.PyNode(jnt_grp).translate)
                    pm.PyNode("MD_Mouth_01_Bind_Jnt_Ori_Null").rotate.connect(
                        pm.PyNode(jnt_grp).rotate)

                    if side == "LF":
                        mp_node.attr("uValue").set(0)
                    else:
                        mp_node.attr("uValue").set(1)

        if not check_constraint("MD_Mouth_01_Bind_Jnt_Ori_Null",
                                "MD_Mouth_01_Master_Ctrl_Null"):
            pm.parentConstraint(
                "MD_Mouth_01_Master_Ctrl_Null",
                "MD_Mouth_01_Bind_Jnt_Ori_Null",
                mo=True)
        return

    def __motion_path_on_out_curve_to_tweak_ctrl_grp(self):
        segment = 3
        for location in ["Up", "Low"]:
            outer_curve = "MD_Mouth_01_{}_Out_Curve".format(location)
            for side in ["LF", "RT"]:
                for index in range(1, segment + 1):
                    ctrl_grp = "{}_Mouth_01_{}Tweak_{}_Ctrl_Grp".format(
                        side, location, "{0:02d}".format(index))
                    mp_node = pm.createNode(
                        "motionPath",
                        name=ctrl_grp.replace("_Grp", "_MP"))

                    u_value = 0.0
                    if side == "LF":
                        if index < 3:
                            u_value = 0.2 * (segment - index)
                        elif index == 3:
                            u_value = 0.067
                        mp_node.attr("uValue").set(u_value)
                    elif side == "RT":
                        u_value = pm.getAttr(
                            "LF_Mouth_01_{}Tweak_{}_Ctrl_MP"
                            ".uValue".format(location,
                                             "{0:02d}".format(index)))
                        mp_node.attr("uValue").set(1 - u_value)

                    pm.PyNode(outer_curve).getShape().attr(
                        "worldSpace[0]").connect(mp_node.attr("geometryPath"))
                    mp_node.attr("allCoordinates").connect(
                        pm.PyNode(ctrl_grp).attr("translate"))

                    pm.PyNode("MD_Mouth_01_Tweak_Ori_Null").rotate.connect(
                        pm.PyNode(ctrl_grp).rotate)
                    pm.PyNode("MD_Mouth_01_Scale_Null").scale.connect(
                        pm.PyNode(ctrl_grp).scale)

                if location == "Up":
                    ctrl_grp = "{}_Mouth_01_Tweak_Ctrl_Grp".format(
                        side)
                    mp_node = pm.createNode(
                        "motionPath",
                        name=ctrl_grp.replace("_Grp", "_MP"))
                    pm.PyNode(outer_curve).getShape().attr(
                        "worldSpace[0]").connect(mp_node.attr("geometryPath"))
                    mp_node.attr("allCoordinates").connect(
                        pm.PyNode(ctrl_grp).translate)

                    if side == "LF":
                        mp_node.attr("uValue").set(0)
                    else:
                        mp_node.attr("uValue").set(1)

                    pm.PyNode("MD_Mouth_01_Tweak_Ori_Null").rotate.connect(
                        pm.PyNode(ctrl_grp).rotate)
                    pm.PyNode("MD_Mouth_01_Scale_Null").scale.connect(
                        pm.PyNode(ctrl_grp).scale)

        if not check_constraint("MD_Mouth_01_Scale_Null",
                                "MD_Mouth_01_Base_Ctrl_Grp"):
            pm.scaleConstraint("MD_Mouth_01_Base_Ctrl_Grp",
                               "MD_Mouth_01_Scale_Null", mo=True)
        if not check_constraint("MD_Mouth_01_Tweak_Ori_Null",
                                "MD_Mouth_01_Master_Ctrl_Null"):
            pm.parentConstraint("MD_Mouth_01_Master_Ctrl_Null",
                                "MD_Mouth_01_Tweak_Ori_Null", mo=True)

        return

    def __skin_out_curve(self):
        prefix_list = ["Up", "Low"]
        seg = 5
        for prefix in prefix_list:
            skin_items = []
            out_curve = pm.PyNode(
                "MD_Mouth_01_{}_Out_Curve".format(prefix))
            skin_items.append(out_curve)
            for side in ["LF", "RT"]:
                for index in range(1, seg + 1):
                    skin_items.append("{}_Mouth_01_{}Lip_{}_Jnt".format(
                        side, prefix, "{0:02d}".format(index)))
                skin_items.append("{}_Mouth_01_Lip_Jnt".format(side))
            pm.skinCluster(skin_items,
                           name="MD_Mouth_01_{}_Out_Curve_SC".format(prefix))
        return

    def __use_dm_node_to_tweak_ctrl_parent_and_jnt_02_grp(self):
        seg = 3
        for side in ["LF", "RT"]:
            tweak_ctrl = "{}_Mouth_01_Tweak_Ctrl".format(side)
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

    def __skin_tweak_surface(self):
        prefix_list = ["Up", "Low"]
        seg = 3
        for prefix in prefix_list:
            skin_items = []
            tweak_surface = "MD_Mouth_01_{}_Tweak_Surface".format(prefix)
            skin_items.append(tweak_surface)
            for side in ["LF", "RT"]:
                for index in range(1, seg + 1):
                    skin_items.append("{}_Mouth_01_{}Tweak_{}_Ctrl_Jnt".format(
                        side, prefix, "{0:02d}".format(index)))
                skin_items.append("{}_Mouth_01_Tweak_Ctrl_Jnt".format(side))
            pm.skinCluster(
                skin_items,
                name="MD_Mouth_01_{}_Tweak_Surface_SC".format(prefix))
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
        return

    def lip_sew_ctrl_drive_follicle_shape(self):
        for side in ["LF", "RT"]:
            lip_sew_ctrl = "{}_Mouth_01_LipSew_Ctrl".format(side)
            follicle_shape = "{}_Mouth_01_LipSew_Ctrl_FollicleShape".format(
                side)

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

    def make_bind_jnt_work(self):
        """让蒙皮骨骼能够工作

        :return:
        """
        seg = 5
        master_ctrl = "MD_Mouth_01_Master_Ctrl"
        for side in ["LF", "RT"]:
            bind_jnt_root = "{}_Mouth_01_Lip_Jnt_Grp".format(side)
            # 因为 localScale 是单属性，scale是一组属性，
            # 所以必须得逐一连接属性：scaleX， scaleY， scaleZ
            pm.PyNode(master_ctrl).attr("localScale").connect(
                pm.PyNode(bind_jnt_root).scaleX, f=True)
            pm.PyNode(master_ctrl).attr("localScale").connect(
                pm.PyNode(bind_jnt_root).scaleY, f=True)
            pm.PyNode(master_ctrl).attr("localScale").connect(
                pm.PyNode(bind_jnt_root).scaleZ, f=True)

            # 位移部分
            follicle = pm.PyNode(bind_jnt_root.replace("_Grp", "_Follicle"))
            follicle.getShape().attr("outTranslate").connect(
                pm.PyNode(bind_jnt_root).translate, f=True)

            # 旋转部分
            base_ctrl_out_grp = pm.PyNode("MD_Mouth_01_Base_Ctrl_Out_Grp")

            null_vp = "MD_Mouth_01_Master_Ctrl_Null_VP"
            if not pm.objExists(null_vp):
                pm.createNode("vectorProduct", name=null_vp)

            if (pm.PyNode(null_vp) not in pm.PyNode(base_ctrl_out_grp).attr(
                    "worldMatrix[0]").outputs()):
                pm.PyNode(base_ctrl_out_grp).attr("worldMatrix[0]").connect(
                    pm.PyNode(null_vp).attr("matrix"), f=True)

            jnt_vp = follicle.name().replace("_Follicle", "_VP")
            if not pm.objExists(jnt_vp):
                pm.createNode("vectorProduct", name=jnt_vp)
            follicle.attr("worldMatrix[0]").connect(
                pm.PyNode(jnt_vp).attr("matrix"), f=True)

            jnt_3rd_vp = follicle.name().replace("_Follicle", "_3rd_VP")
            if not pm.objExists(jnt_3rd_vp):
                pm.createNode("vectorProduct", name=jnt_3rd_vp)

            pm.PyNode(null_vp).attr("output").connect(
                pm.PyNode(jnt_3rd_vp).attr("input1"), f=True)
            pm.PyNode(jnt_vp).attr("output").connect(
                pm.PyNode(jnt_3rd_vp).attr("input2"), f=True)

            jnt_FBFM_node = follicle.name().replace("_Follicle", "_FBFM")
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

            jnt_dm_node = follicle.name().replace("_Follicle", "_DM")
            if not pm.objExists(jnt_dm_node):
                jnt_dm_node = pm.createNode(
                    "decomposeMatrix", name=jnt_dm_node)
            pm.PyNode(jnt_FBFM_node).attr("output").connect(
                pm.PyNode(jnt_dm_node).attr("inputMatrix"))

            pm.PyNode(jnt_dm_node).attr("outputRotate").connect(
                pm.PyNode(bind_jnt_root).attr("rotate"))

            for location in ["Up", "Low"]:
                for index in range(1, seg + 1):
                    bind_jnt_root = ("{}_Mouth_01_{}Lip_{}_Jnt_Grp".format(
                        side, location, "{0:02d}".format(index)))
                    pm.PyNode(master_ctrl).attr("localScale").connect(
                        pm.PyNode(bind_jnt_root).scaleX)
                    pm.PyNode(master_ctrl).attr("localScale").connect(
                        pm.PyNode(bind_jnt_root).scaleY)
                    pm.PyNode(master_ctrl).attr("localScale").connect(
                        pm.PyNode(bind_jnt_root).scaleZ)

        return
