# coding: utf-8


from imp import reload
from pymel import core as pm
from animation import common
# import maya.cmds as cmds
# from pymel.util import path
# from rig.names import template_dir
from rig import main

reload(common)
reload(main)


class MouthCreator:

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

        up_curve_center_position = main.point_on_curve_position(curve=self.up_base_curve, parameter=parameter)
        low_curve_center_position = main.point_on_curve_position(curve=self.low_base_curve, parameter=parameter)
        pos_x = (low_curve_center_position[0] + (up_curve_center_position[0] - low_curve_center_position[0]) / 2)
        pos_y = (low_curve_center_position[1] + (up_curve_center_position[1] - low_curve_center_position[1]) / 2)
        pos_z = (low_curve_center_position[2] + (up_curve_center_position[2] - low_curve_center_position[2]) / 2)
        offset = 4.0

        master_ctrl = "{}_Master_Ctrl".format(prefix)
        if not pm.objExists(master_ctrl):
            main.cyan_control(
                name=master_ctrl,
                shape_type="sphere",
                translate=(pos_x, pos_y, pos_z + offset),
                parent_node="MD_{}_Grp".format(self.module_name))

        master_ctrl_jnt = "{}_Jnt".format(master_ctrl)
        pm.select(cl=True)
        pm.joint(name=master_ctrl_jnt)
        pm.parent(master_ctrl_jnt, master_ctrl)
        pm.PyNode(master_ctrl_jnt).translate.set([0, 0, 0])

        main.custom_show_channel(master_ctrl, attr_list=["translateX", "translateY", "translateZ", "rotateZ"])

        # MD_Mouth_01_Master_Ctrl_Loc
        master_ctrl_loc = "MD_{}_Master_Ctrl_Loc".format(self.module_name)
        if not pm.objExists(master_ctrl_loc):
            main.cyan_locator_grp(
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
            main.xd_follicle_node(name=master_ctrl_follicle,
                                  worldMatrixInput=pm.PyNode(self.mouth_surface).getShape().attr(
                                      "worldMatrix[0]"),
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
            mp = main.mp_node(node_name=mp_name,
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
                ctrl_grp = main.yellow_component(name=control_name,
                                                 shape_type="nurbsPlane",
                                                 parent_node=base_ctrl_grp,
                                                 have_jnt=True)
                pm.delete(pm.parentConstraint(temp_loc, ctrl_grp, mo=False))
                pm.delete(pm.scaleConstraint(temp_loc, ctrl_grp, mo=False))
            ctrl_loc = "{}_Ctrl_Loc".format(prefix)
            if not pm.objExists(ctrl_loc):
                ctrl_loc_grp = main.yellow_component(
                    name=ctrl_loc, shape_type="locator", parent_node=base_loc_grp)
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
                main.yellow_component(name="{}_Ctrl".format(prefix), shape_type="nurbsPlane",
                                      translate=main.point_on_curve_position(
                                          curve=curve, parameter=parameter),
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
                    main.xd_follicle_node(
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
                    main.xd_follicle_node(
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
                main.yellow_component(name=aim_jnt,
                                      shape_type="joint",
                                      translate=main.point_on_curve_position(base_curve, 0.5),
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
                    corner_jnt_grp = main.jnt_or_control_grp(name=corner_jnt, parent_node=corner_follicle)

                check_list.append(corner_jnt)

                if not main.check_constraint(corner_follicle, corner_jnt_grp):
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

        if not main.check_constraint(master_ctrl_null, base_ctrl_grp):
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
                        corner_follicle = main.xd_follicle_node(
                            name="{}_{}_Lip_Jnt_Follicle".format(side, self.module_name),
                            worldMatrixInput=tweak_surface.getShape().attr("worldMatrix[0]"),
                            surfaceInput=tweak_surface.getShape().attr("local"),
                            parentNode=bind_jnt_follicle_grp)
                    pm.PyNode(corner_follicle).getShape().attr("parameterU").set(parameter_u)
                    pm.PyNode(corner_follicle).getShape().attr("parameterV").set(parameter_v)

                for index in range(1, segment + 1):
                    lip_follicle = "{}_Mouth_01_{}Lip_{}_Jnt_Follicle".format(side, location, "{0:02d}".format(index))
                    if not pm.objExists(lip_follicle):
                        lip_follicle = main.xd_follicle_node(
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
                        jnt_grp = main.yellow_component(
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
                        jnt_grp = main.yellow_component(
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

        if not main.check_constraint(tweak_ori_null, master_ctrl_null):
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
                        ctrl_grp = main.yellow_component(
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
                        ctrl_grp = main.yellow_component(name=ctrl, shape_type="sphere", parent_node=tweak_ctrl_grp)

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
        if not main.check_constraint(scale_null, base_ctrl_grp):
            pm.scaleConstraint(base_ctrl_grp, scale_null, mo=True)
        if not main.check_constraint(tweak_ori_null, master_ctrl_null):
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

            main.custom_show_channel(tweak_ctrl, attr_list=["translateX", "translateY", "translateZ"])

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

                    main.custom_show_channel(tweak_ctrl, attr_list=["translateX", "translateY", "translateZ"])
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
            main.make_follicle_work_on_surface(
                surface=sew_surface, follicle=follicle, param_u=param_u, param_v=param_v)
            main.follicle_shape_out_for_parent(pm.PyNode(follicle).getShape())
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
                lip_sew_ctrl_grp = main.yellow_component(name=lip_sew_ctrl, shape_type="cone", parent_node=follicle, )
            pm.PyNode(lip_sew_ctrl_grp).translate.set([0, 0, 0])
            if side == "LF":
                pm.PyNode(lip_sew_ctrl_grp).rotate.set([0, 180, 0])
            else:
                pm.PyNode(lip_sew_ctrl_grp).rotate.set([0, 0, 0])
                pm.PyNode(lip_sew_ctrl_grp).scale.set([1, 1, -1])

            main.custom_show_channel(lip_sew_ctrl, attr_list=["translateX"])

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
            if not main.check_constraint(side_ctrl_null, side_null_03_grp):
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
        if not main.check_constraint(master_ctrl_grp, jaw_ctrl):
            constraint = pm.parentConstraint(jaw_ctrl, pm.PyNode(
                jaw_ctrl).getParent(), master_ctrl_grp, mo=True)

            driver_value = [-1, 0]
            value = [0, 1]

            for index in range(0, len(driver_value)):
                pm.setDrivenKeyframe(
                    constraint,
                    at="{}W1".format(pm.PyNode(jaw_ctrl).getParent().controller_name()),
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
            follicle = main.xd_follicle_node(
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
            low_jnt_grp = main.jnt_or_control_grp(name=low_jnt, parent_node=jaw_out_grp, have_loc=True)

        tweak_jnt_grp = main.jnt_or_control_grp(
            name="MD_Mouth_01_Jaw_Tweak_Ctrl_Jnt", parent_node="MD_Mouth_01_LowJaw_Jnt")
        low_teeth_jnt_grp = main.jnt_or_control_grp(
            name="MD_Mouth_01_Low_Teeth_Ctrl_Jnt", parent_node="MD_Mouth_01_LowJaw_Jnt")

        up_jnt_grp = main.jnt_or_control_grp(name="MD_Mouth_01_UpJaw_Jnt", parent_node=jaw_out_grp)
        up_teeth_jnt_grp = main.jnt_or_control_grp(
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
        up_null_grp = main.ctrl_null_grp(name="Up_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(pm.parentConstraint("Up_{}_Ctrl".format(self.module_name), up_null_grp, mo=False))
        low_null_grp = main.ctrl_null_grp(name="Low_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(pm.parentConstraint("Low_{}_Ctrl".format(self.module_name), low_null_grp, mo=False))
        lf_null_grp = main.chain_ctrl_null_grp(name="LF_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
        pm.delete(pm.parentConstraint("LF_{}_Ctrl".format(self.module_name), lf_null_grp, mo=False))
        rt_null_grp = main.chain_ctrl_null_grp(name="RT_Mouth_01_Ctrl_Null", parent_node=jaw_out_grp)
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
                    main.jnt_or_control_grp(name=jaw_ctrl, object_type="plane",
                                            parent_node="MD_{}_Grp".format(self.module_name)),
                    mo=False))

        tweak_ctrl = "MD_{}_Jaw_Tweak_Ctrl".format(self.module_name)
        if not pm.objExists(tweak_ctrl):
            pm.delete(
                pm.parentConstraint(
                    "proxyJawTeak",
                    main.jnt_or_control_grp(name=tweak_ctrl, object_type="plane", parent_node=jaw_ctrl),
                    mo=False))

        low_teeth_ctrl = "MD_{}_Low_Teeth_Ctrl".format(self.module_name)
        if not pm.objExists(low_teeth_ctrl):
            pm.delete(
                pm.parentConstraint(
                    "proxyTeethLow",
                    main.jnt_or_control_grp(name=low_teeth_ctrl, object_type="plane", parent_node=jaw_ctrl),
                    mo=False))

        jaw_move_loc = "M_Jaw_Move_Loc"
        pm.spaceLocator(name=jaw_move_loc)
        pm.parent(jaw_move_loc, jaw_ctrl)
        pm.PyNode(jaw_move_loc).translate.set([0, 0, 5])

        up_teeth_ctrl = "MD_{}_Up_Teeth_Ctrl".format(self.module_name)
        pm.delete(
            pm.parentConstraint(
                "proxyTeethUp",
                main.jnt_or_control_grp(
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
                tongue_ctrl_grp = main.jnt_or_control_grp(
                    name=tongue_ctrl, object_type="cylinder", parent_node=tongue_main_group, have_jnt=True)
            if index > 1:
                tongue_ctrl_grp = main.jnt_or_control_grp(
                    name=tongue_ctrl, object_type="cylinder",
                    parent_node="MD_Tongue_01_{}_FK_Ctrl".format("{0:02d}".format(index - 1)), have_jnt=True)

            proxy_loc = "proxyTongue{}Loc".format("{0:02d}".format(index))
            print("{} -> {}".format(proxy_loc, tongue_ctrl_grp))
            pm.delete(pm.parentConstraint(proxy_loc, tongue_ctrl_grp, mo=False))

        return
