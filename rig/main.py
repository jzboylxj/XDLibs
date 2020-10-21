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


class MouthCreator(Creator):

    def __init__(self):
        super(MouthCreator, self).__init__()

    def build(self):
        self.__mouth_surface_location()
        self.__rig_base_ctrl_out()
        self.__add_bind_jnt_follicle_on_tweak_surface()

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

    def __rig_base_curve(self):
        curve_prefix_list = ["Up", "Low"]
        for prefix in curve_prefix_list:
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
        self.__rig_base_curve()
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
            follicle_shape_parent = pm.PyNode(follicle_shape).getParent()
            pm.PyNode(follicle_shape).attr("outTranslate").connect(
                follicle_shape_parent.attr("translate")
            )
            pm.PyNode(follicle_shape).attr("outRotate").connect(
                follicle_shape_parent.attr("rotate")
            )
        return
