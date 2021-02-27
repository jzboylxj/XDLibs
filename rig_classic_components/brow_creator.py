# coding: utf-8


from imp import reload
from pymel import core as pm
from pymel.util import path

from animation import common

# import maya.cmds as cmds
# from pymel.util import path
# from rig.names import template_dir
from core import utils
from rig import template_dir

reload(common)
reload(utils)

AUTHOR = "XiaoJun Li"
VERSION = [1, 0, 0]
TYPE = "brow_01"
NAME = "brow"
DESCRIPTION = ""


class Creator:
    def __init__(self):
        self.module_name = "Brow_01"
        self.brow_segment = 7
        self.control_num = 4

        self.left_brow_surface = ""
        self.right_brow_surface = ""

        self.left_brow_curve = ""
        self.right_brow_curve = ""

        self.left_master_ctrl_surface = ""
        self.right_master_ctrl_surface = ""

    def sub_control(self, side="LF", index=1, parent_node=None):
        control = "{}_{}_Sub_{}_Ctrl".format(
            side, self.module_name, "{0:02d}".format(index))
        control_grp = "{}_Grp".format(control)
        squeeze_grp = control.replace("Ctrl", "Jnt_Squeeze_Grp")
        local_scale_grp = control.replace("Ctrl", "Jnt_LocalScale_Grp")

        pm.createNode("transform", name=local_scale_grp)
        pm.createNode("transform", name=squeeze_grp, p=local_scale_grp)
        pm.createNode("transform", name=control_grp, p=squeeze_grp)

        pm.sphere(name=control, p=[0, 0, 0], ax=[
                  0, 1, 0], ssw=0, esw=360, r=0.3, d=3, ut=0, tol=0.01, s=4, nsp=2, ch=0)

        pm.parent(control, control_grp)

        if parent_node is not None:
            if not pm.objExists(parent_node):
                pm.error(u"场景中缺少{}".format(parent_node))
            else:
                pm.parent(local_scale_grp, parent_node)
                pm.PyNode(local_scale_grp).translate.set([0, 0, 0])
                pm.PyNode(local_scale_grp).rotate.set([0, 0, 0])

        return control

    def creat_sub_controllers(self, side="LF", sub_surface="", sub_curve=""):
        u"""利用毛囊创建次级控制器

        :return: None
        """

        surface_shape = pm.PyNode(sub_surface).getShape()

        if not pm.attributeQuery("squeeze", node=sub_surface, ex=True):
            pm.addAttr(sub_surface, ln="squeeze", at="double", dv=0)
            pm.setAttr("{}.squeeze".format(sub_surface), e=True, k=True)

        stretch_md_node = self.create_curve_info_node(side, sub_curve, sub_surface)
        print("stretch_md_node:{}".format(stretch_md_node))

        for index in range(0, self.brow_segment):
            # 根据段数在sub_curve均等分创建毛囊，次级控制器就创建在这些毛囊的层级下，这些毛囊产生位移的时候，
            # 层级下的控制器也会被带动，达到次级控制的效果
            follicle_node = "{}_{}_Sub_{}_Follicle".format(side, self.module_name, "{0:02d}".format(index + 1))
            follicle_shape = utils.xd_follicle_node(
                name=follicle_node,
                worldMatrixInput=surface_shape.attr("worldMatrix[0]"),
                surfaceInput=surface_shape.attr("local"),
                outTranslateToParent=True,
                outRotateToParent=False,
                parentNode="{}_{}_Sub_Output_Jnt_Grp".format(
                    side, self.module_name)
            ).getShape()

            # 毛囊会根据parameterV的值，调整它在曲面上面的位置
            follicle_shape.attr("parameterU").set(0.5)
            if index == 0:
                follicle_shape.attr("parameterV").set(0)
            elif index == self.brow_segment - 1:
                follicle_shape.attr("parameterV").set(1)
            else:
                follicle_shape.attr("parameterV").set(0.167 * index)

            # 连接毛囊的rotate属性, 修正master ctrl旋转的时候次级控制器的朝向不跟随的错误
            self.connect_follicle_rotate(side=side, rotate_node=follicle_node)

            # 添加次级控制器到毛囊的子层级
            sub_control = self.sub_control(side=side, index=index + 1, parent_node=follicle_shape.getParent())

            pm.setAttr("{}.visibility".format(sub_control), lock=True, k=False, cb=False)

            if side == "RT":
                pm.PyNode(sub_control).getParent().scaleX.set(-1)

            if index == 0:
                main_ctrl = "{}_{}_Main_{}_Ctrl".format(side, self.module_name, "{0:02d}".format(index + 1))
                if pm.objExists(main_ctrl):
                    pm.orientConstraint(main_ctrl, pm.PyNode(sub_control).getParent(), mo=True)
            elif index == (self.brow_segment - 1):
                main_ctrl = "{}_{}_Main_{}_Ctrl".format(side, self.module_name, "{0:02d}".format(self.control_num))
                if pm.objExists(main_ctrl):
                    pm.orientConstraint(main_ctrl, pm.PyNode(sub_control).getParent(), mo=True)

            self.make_sub_control_scale_work(side=side, index=(index + 1), sub_surface=sub_surface)

            sub_null = "{}_{}_Sub_{}_Null".format(side, self.module_name, "{0:02d}".format(index + 1))
            bone = "{}_{}_Sub_{}_Jnt".format(side, self.module_name, "{0:02d}".format(index + 1))
            rig_track_grp = "{}_{}_LocalRig_Track_Grp".format(side, self.module_name)
            rig_out_grp = "{}_{}_LocalRig_Out_Grp".format(side, self.module_name)

            self.local_rig_out(
                sub_ctrl=sub_control,
                sub_null=sub_null,
                bone=bone,
                rig_track_grp=rig_track_grp,
                rig_out_grp=rig_out_grp)

            self.make_master_control_squeeze(
                side=side,
                index=index,
                sub_surface=sub_surface,
                stretch_md_node=stretch_md_node,
                sub_ctrl=sub_control)

        print(u"{}的次级控制器已经创建完成".format(self.module_name))
        return

    def init_structure(self, side="LF"):
        u"""初始化模块的节点结构

        :return None
        """
        if not pm.objExists("Head_01_Grp"):
            pm.createNode("transform", name="Head_01_Grp", p="Master_Ctrl")

        # for side in ["LF", "RT"]:
        side_module_grp = "{}_{}_Grp".format(side, self.module_name)
        if not pm.objExists(side_module_grp):
            pm.createNode("transform", name=side_module_grp, p="Head_01_Grp")

        if side == "LF":
            self.left_output_jnt_grp = "{}_{}_Sub_Output_Jnt_Grp".format(side, self.module_name)
            side_output_jnt_grp = self.left_output_jnt_grp
        elif side == "RT":
            self.right_output_jnt_grp = "{}_{}_Sub_Output_Jnt_Grp".format(side, self.module_name)
            side_output_jnt_grp = self.right_output_jnt_grp

        if not pm.objExists(side_output_jnt_grp):
            pm.createNode("transform", name=side_output_jnt_grp, p=side_module_grp)
            pm.PyNode(side_output_jnt_grp).attr("inheritsTransform").set(0)

        return

    def build_master_control(self, side="LF", master_surface=""):
        u"""创建主控制器

        此方法会首先根据self.left_master_ctrl_surface或self.right_master_ctrl_surface的中心位置创建一个毛囊，
        然后利用4段nurbs圆环创建一个控制器作为眉毛的模块主控制器，并将这个对象进行打组放到毛囊的层级下成为它的子物体

        :return master_ctrl
        """

        master_surface_shape = pm.PyNode(master_surface).getShape()
        master_follicle_name = "{}_{}_Master_Ctrl_Follicle".format(side, self.module_name)

        if not pm.objExists(master_follicle_name) and pm.objExists(master_surface):
            follicle_shape = utils.xd_follicle_node(
                name=master_follicle_name,
                worldMatrixInput=master_surface_shape.attr("worldMatrix[0]"),
                surfaceInput=master_surface_shape.attr("local"),
                parentNode="{}_{}_Grp".format(side, self.module_name)).getShape()
            follicle_shape.attr("parameterU").set(0.5)
            follicle_shape.attr("parameterV").set(0.5)

        # todo 等待抽出重构控制器的创建方式
        master_ctrl = "{}_{}_Master_Ctrl".format(side, self.module_name)
        master_ctrl_grp = "{}_Grp".format(master_ctrl)
        if not pm.objExists(master_ctrl_grp):
            pm.createNode("transform", name=master_ctrl_grp)

        if not pm.objExists(master_ctrl):
            pm.torus(name=master_ctrl,
                     p=[0, 0, 0],
                     ax=[0, 0, 1],
                     ssw=0,
                     esw=360,
                     msw=360,
                     r=1,
                     hr=0.1,
                     d=1,
                     ut=0,
                     tol=0.01,
                     s=4,
                     nsp=5,
                     ch=1)
            pm.PyNode(master_ctrl).rotateZ.set(45)
            pm.makeIdentity(apply=True, t=1, r=1, s=1, n=0, pn=1)
            pm.parent(master_ctrl, master_ctrl_grp)

            if not pm.attributeQuery("ctrlVis", node=master_ctrl, ex=True):
                pm.addAttr(master_ctrl, ln="ctrlVis", at="long", dv=0, min=0, max=1)
                pm.setAttr("{}.ctrlVis".format(master_ctrl), e=True, k=True)

            if not pm.attributeQuery("squeeze", node=master_ctrl, ex=True):
                pm.addAttr(master_ctrl, ln="squeeze", at="double", dv=0)
                pm.setAttr("{}.squeeze".format(master_ctrl), e=True, k=True)

        pm.parent(master_ctrl_grp, master_follicle_name)
        pm.PyNode(master_ctrl_grp).translate.set([0, 0, 0])

        if side == "LF":
            pm.PyNode(master_ctrl_grp).rotate.set([0, 0, 0])
        else:
            pm.PyNode(master_ctrl_grp).rotate.set([180, 0, 0])
            pm.PyNode(master_ctrl_grp).scale.set([1, 1, -1])

        pm.setAttr("{}.visibility".format(master_ctrl), lock=True, k=False, cb=False)
        pm.select(master_ctrl)
        pm.mel.eval('DeleteHistory;')

        # 根据控制器的方向位置添加一些节点，为后面的整体控制做准备
        if side == "LF":
            sub_output_jnt_grp = self.left_output_jnt_grp
            sub_surface = self.left_brow_surface
        elif side == "RT":
            sub_output_jnt_grp = self.right_output_jnt_grp
            sub_surface = self.right_brow_surface

        # 连接主控制器的ctrlVis属性和 LF_Brow_01_Sub_Output_Jnt_Grp或 RT_Brow_01_Sub_Output_Jnt_Grp的visibility属性，
        # 用来控制次级控制器组的可视状态
        self.master_ctrl_vis(side=side, master_ctrl=master_ctrl, output_jnt_grp=sub_output_jnt_grp)

        # 在LF_Brow_01_Sub_Output_Jnt_Grp 和 RT_Brow_01_Sub_Output_Jnt_Grp层级下创建一个空节点，
        # 主控制器会对其进行方向约束，后面会用这个空节点对次级控制的毛囊进行方向约束，
        # 用来修正模块控制器旋转的时候，次级控制器的朝向没有跟随主控制器的错误
        sub_ori_null = "{}_{}_Sub_Ori_Null".format(side, self.module_name)
        if not pm.objExists(sub_ori_null):
            pm.createNode("transform", name=sub_ori_null, p=sub_output_jnt_grp)
        pm.orientConstraint(master_ctrl, sub_ori_null, mo=False)

        self.create_scale_null_node(side=side, master_ctrl=master_ctrl, sub_surface=sub_surface)

        local_rig_track_grp = "{}_{}_LocalRig_Track_Grp".format(side, self.module_name)
        if not pm.objExists(local_rig_track_grp):
            pm.createNode("transform", name=local_rig_track_grp)
            pm.parent(local_rig_track_grp, master_ctrl_grp)

        local_rig_out_grp = "{}_{}_LocalRig_Out_Grp".format(side, self.module_name)
        if not pm.objExists(local_rig_out_grp):
            pm.createNode("transform", name=local_rig_out_grp, p="{}_{}_Deformer_Grp".format(side, self.module_name))

        pm.PyNode(master_ctrl).attr("squeeze").connect(pm.PyNode(sub_surface).attr("squeeze"))

        pm.PyNode(master_surface).visibility.set(0)

        print(u"{}的主控制器构建完成".format(self.module_name))
        return master_ctrl

    def create_master_sub_controllers(self, side="LF", master_ctrl="", sub_curve="", sub_surface=""):
        u"""创造眉毛主要的4个控制器

        Args:
            side (str): 方向.
            master_ctrl (str): 模块的主控制器
            sub_curve (str):     
            sub_surface (str): 

        Returns:
            [type]: [description]
        """

        surface_skin_items = []

        for index in range(0, self.control_num):
            temp_loc = pm.spaceLocator()
            temp_mp_node = pm.pathAnimation(
                [temp_loc, sub_curve],
                fractionMode=True,
                follow=True,
                followAxis="x",
                upAxis="y",
                worldUpType="vector",
                worldUpVector=[0, 1, 0],
                inverseUp=False,
                inverseFront=False,
                bank=False)

            if index < 1:
                pm.PyNode(temp_mp_node).attr("uValue").set(0)
            else:
                pm.PyNode(temp_mp_node).attr("uValue").set(
                    float(index) / (float(self.control_num - 1)))

            control_name = "{}_{}_Main_{}_Ctrl".format(
                side, self.module_name, "{0:02d}".format(index + 1))

            print(u"----------- 开始创建控制器: {} ---------------".format(control_name))

            control_grp = utils.control_grp_have_joint(
                name=control_name, parent_node=master_ctrl)
            pm.delete(pm.parentConstraint(temp_loc, control_grp, mo=False, skipRotate=["x", "z"]))

            pm.setAttr("{}.visibility".format(control_name), lock=True, k=False, cb=False)

            if side == "RT":
                rotate_angle = pm.PyNode(control_grp).rotateY.get()
                if rotate_angle > 180:
                    pm.PyNode(control_grp).rotateY.set(rotate_angle - 180.0)
                else:
                    pm.PyNode(control_grp).rotateY.set(rotate_angle * -1)

            # 次级控制器
            if index == 0:
                sub_controller_grp = "{}_{}_Sub_{}_Ctrl_Grp".format(side, self.module_name, "{0:02d}".format(index + 1))
                if pm.objExists(sub_controller_grp):
                    pm.orientConstraint(control_name, sub_controller_grp, mo=True)
            elif index == (self.control_num - 1):
                sub_controller_grp = "{}_{}_Sub_{}_Ctrl_Grp".format(
                    side, self.module_name, "{0:02d}".format(self.brow_segment))
                if pm.objExists(sub_controller_grp):
                    pm.orientConstraint(control_name, sub_controller_grp, mo=True)

            surface_skin_items.append("{}_Jnt".format(control_name))
            pm.delete(temp_loc, temp_mp_node)

            print(u"----------- 控制器: {} 创建完成---------------".format(control_name))

        surface_skin_items.append(sub_surface)
        skin_name = "{}_SC".format(sub_surface)
        pm.skinCluster(surface_skin_items, tsb=True, name=skin_name)

        pm.PyNode(sub_curve).visibility.set(0)
        pm.PyNode(sub_surface).visibility.set(0)

        print(u"----------- 控制器: {}_{} 已经创建完成 ---------------".format(side, self.module_name))
        return True

    def connect_follicle_rotate(self, side="LF", rotate_node=""):
        sub_ori_null = "{}_{}_Sub_Ori_Null".format(side, self.module_name)

        if pm.objExists(sub_ori_null):
            pm.PyNode(sub_ori_null).rotate.connect(pm.PyNode(rotate_node).rotate)
        else:
            pm.errors(u"场景中缺少{}, 这个节点应该在创建master ctrl过程被创建".format(sub_ori_null))
        return

    def make_master_control_squeeze(self, side="LF", index=1, sub_surface="",  stretch_md_node="", sub_ctrl=""):

        squeeze_md = "{}_{}_Sub_Squeeze_{}_MD".format(side, self.module_name, "{0:02d}".format(index+1))
        if not pm.objExists(squeeze_md):
            pm.createNode("multiplyDivide", name=squeeze_md)
            pm.PyNode(squeeze_md).attr("operation").set(3)
        pm.PyNode(stretch_md_node).attr("outputX").connect(pm.PyNode(squeeze_md).attr("input1X"))

        squeeze_mdl = "{}_{}_Sub_Squeeze_{}_MDL".format(side, self.module_name, "{0:02d}".format(index+1))
        if not pm.objExists(squeeze_mdl):
            pm.createNode("multDoubleLinear", name=squeeze_mdl)
        pm.PyNode(sub_surface).attr("squeeze").connect(pm.PyNode(squeeze_mdl).attr("input1"))
        pm.PyNode(sub_surface).attr("squeeze{}".format("{0:02d}".format(index))).connect(
            pm.PyNode(squeeze_mdl).attr("input2"))
        pm.PyNode(squeeze_mdl).attr("output").connect(pm.PyNode(squeeze_md).attr("input2X"))

        jnt_squeeze_grp = pm.PyNode(sub_ctrl).getParent().getParent()
        pm.PyNode(squeeze_md).attr("outputX").connect(pm.PyNode(jnt_squeeze_grp).scaleY)
        pm.PyNode(squeeze_md).attr("outputX").connect(pm.PyNode(jnt_squeeze_grp).scaleZ)

        return

    def create_curve_info_node(self, side, sub_curve, sub_surface):
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
        stretch_md_node = "{}_{}_Sub_Stretch_MD".format(side, self.module_name)
        if not pm.objExists(stretch_md_node):
            pm.createNode("multiplyDivide", name=stretch_md_node)
            pm.PyNode(stretch_md_node).attr("operation").set(2)
        pm.PyNode(length_mdl_node).attr("output").connect(
            pm.PyNode(stretch_md_node).attr("input1X"))
        pm.PyNode(curve_info_node).attr("arcLength").connect(
            pm.PyNode(stretch_md_node).attr("input2X"))
        return stretch_md_node

    def make_sub_control_scale_work(self, side, index, sub_surface):
        for scale_attr in ["scaleX", "scaleY", "scaleZ"]:
            pm.PyNode(sub_surface).attr("globalScale").connect(
                pm.PyNode("{}_{}_Sub_{}_Follicle".format(side, self.module_name,
                                                         "{0:02d}".format(index))).attr(scale_attr))
        sub_db_scale_md_node = "{}_{}_Sub_DBScale_{}_MD".format(side, self.module_name, "{0:02d}".format(index))
        if not pm.objExists(sub_db_scale_md_node):
            pm.createNode("multiplyDivide", name=sub_db_scale_md_node)
            pm.PyNode(sub_db_scale_md_node).attr("operation").set(2)
        pm.PyNode(sub_surface).attr("globalScale").connect(pm.PyNode(sub_db_scale_md_node).attr("input2X"))
        sub_surface_shape = pm.PyNode(sub_surface).getShape()
        sub_index_01_posi = "{}_{}_Sub_{}_01_POSI".format(side, self.module_name, "{0:02d}".format(index))
        if not pm.objExists(sub_index_01_posi):
            pm.createNode("pointOnSurfaceInfo", name=sub_index_01_posi)
            pm.PyNode(sub_index_01_posi).attr("parameterU").set(0)
            pm.PyNode(sub_index_01_posi).attr("parameterV").set(float(index - 1) / float(self.brow_segment - 1))
        sub_surface_shape.attr("worldSpace[0]").connect(pm.PyNode(sub_index_01_posi).attr("inputSurface"))

        sub_index_02_posi = "{}_{}_Sub_{}_02_POSI".format(side, self.module_name, "{0:02d}".format(index))
        if not pm.objExists(sub_index_02_posi):
            pm.createNode("pointOnSurfaceInfo", name=sub_index_02_posi)
            pm.PyNode(sub_index_02_posi).attr("parameterU").set(1)
            pm.PyNode(sub_index_02_posi).attr("parameterV").set(
                float(index - 1) / float(self.brow_segment - 1))
        sub_surface_shape.attr("worldSpace[0]").connect(pm.PyNode(sub_index_02_posi).attr("inputSurface"))
        distance_node = "{}_{}_Sub_{}_DB".format(side, self.module_name, "{0:02d}".format(index))
        if not pm.objExists(distance_node):
            pm.createNode("distanceBetween", name=distance_node)
        pm.PyNode(sub_index_01_posi).attr("position").connect(pm.PyNode(distance_node).attr("point1"))
        pm.PyNode(sub_index_02_posi).attr("position").connect(pm.PyNode(distance_node).attr("point2"))
        pm.PyNode(distance_node).attr("distance").connect(pm.PyNode(sub_db_scale_md_node).attr("input1X"))

        sub_local_scale_md = "{}_{}_Sub_LocalScale_{}_MD".format(side, self.module_name, "{0:02d}".format(index))
        if not pm.objExists(sub_local_scale_md):
            pm.createNode("multiplyDivide", name=sub_local_scale_md)
            pm.PyNode(sub_local_scale_md).attr("operation").set(2)
        pm.PyNode(sub_db_scale_md_node).attr("outputX").connect(pm.PyNode(sub_local_scale_md).attr("input1X"))
        pm.PyNode(sub_local_scale_md).attr("input2X").set(pm.PyNode(sub_db_scale_md_node).attr("outputX").get())
        pm.PyNode(sub_local_scale_md).attr("outputX").connect(
            pm.PyNode("{}_{}_Sub_{}_Jnt_LocalScale_Grp".format(side, self.module_name, "{0:02d}".format(index))).scaleX)
        pm.PyNode(sub_local_scale_md).attr("outputX").connect(
            pm.PyNode("{}_{}_Sub_{}_Jnt_LocalScale_Grp".format(side, self.module_name, "{0:02d}".format(index))).scaleY)
        pm.PyNode(sub_local_scale_md).attr("outputX").connect(
            pm.PyNode("{}_{}_Sub_{}_Jnt_LocalScale_Grp".format(side, self.module_name, "{0:02d}".format(index))).scaleZ)

    def create_scale_null_node(self, side, master_ctrl, sub_surface):
        sub_scale_null = "{}_{}_Scale_Null".format(side, self.module_name)
        if not pm.objExists(sub_scale_null):
            pm.createNode("transform", name=sub_scale_null,
                          p="{}_{}_Deformer_Grp".format(side, self.module_name))
        pm.scaleConstraint(master_ctrl, sub_scale_null, mo=False)
        pm.PyNode(sub_scale_null).scaleX.connect(
            pm.PyNode(sub_surface).attr("globalScale"))

    def master_ctrl_vis(self, side="LF", master_ctrl="", output_jnt_grp=""):
        if not pm.attributeQuery("ctrlVis", node=master_ctrl, ex=True):
            pm.addAttr(master_ctrl, ln="ctrlVis", at="double", min=0, max=1, dv=0)
            pm.setAttr("{}.ctrlVis".format(master_ctrl), e=True, k=True)

        if pm.objExists(output_jnt_grp):
            pm.PyNode(master_ctrl).attr("ctrlVis").connect(
                pm.PyNode(output_jnt_grp).attr("visibility"))

        master_follicle = "{}_{}_Master_Ctrl_Follicle".format(side, self.module_name)
        pm.PyNode(master_follicle).getShape().attr("visibility").set(0)

        return

    def local_rig_out(self, sub_ctrl="", sub_null="", bone="", rig_track_grp="", rig_out_grp=""):
        u"""创建local rig joint

        Args:
            sub_ctrl (str, optional): [description]. Defaults to "".
            sub_null (str, optional): [description]. Defaults to "".
            bone (str, optional): [description]. Defaults to "".
            rig_track_grp (str, optional): [description]. Defaults to "".
            rig_out_grp (str, optional): [description]. Defaults to "".
        """
        if not pm.objExists(sub_null):
            pm.createNode("transform", name=sub_null, p=rig_track_grp)
            pm.PyNode(sub_null).scaleX.set(-1)

        pm.parentConstraint(sub_ctrl, sub_null, mo=False)
        pm.scaleConstraint(sub_ctrl, sub_null, mo=True)

        if not pm.objExists(bone):
            pm.select(cl=True)
            bone = pm.joint(name=bone)
            bone.visibility.set(0)
            pm.parent(bone, rig_out_grp)

        pm.PyNode(sub_null).translate.connect(pm.PyNode(bone).translate)
        pm.PyNode(sub_null).rotate.connect(pm.PyNode(bone).rotate)
        pm.PyNode(sub_null).scale.connect(pm.PyNode(bone).scale)
        return

    def build(self):
        u"""开始构建模块

        :return:
        """

        for side in ["LF", "RT"]:
            self.init_structure(side=side)
            print(u"模块系统结构准备已完成")

            if side == "LF":
                self.left_master_ctrl = self.build_master_control(
                    side=side,
                    master_surface=self.left_master_ctrl_surface)
                self.create_master_sub_controllers(
                    side=side,
                    master_ctrl=self.left_master_ctrl,
                    sub_curve=self.left_brow_curve,
                    sub_surface=self.left_brow_surface)
                self.creat_sub_controllers(
                    side=side,
                    sub_surface=self.left_brow_surface,
                    sub_curve=self.left_brow_curve)
            elif side == "RT":
                self.right_master_ctrl = self.build_master_control(
                    side=side,
                    master_surface=self.right_master_ctrl_surface)
                self.create_master_sub_controllers(
                    side=side,
                    master_ctrl=self.right_master_ctrl,
                    sub_curve=self.right_brow_curve,
                    sub_surface=self.right_brow_surface)
                self.creat_sub_controllers(
                    side=side,
                    sub_surface=self.right_brow_surface,
                    sub_curve=self.right_brow_curve)

        # self.local_rig_out()

        return True


EDITOR_VERSION = 1.10


class Editor(common.Singleton):
    name = "xdBrowCreatorEditor"

    def __init__(self):
        super(Editor, self).__init__()

        self.creator = Creator()
        self.left_brow_surface = ""
        self.right_brow_surface = ""
        self.left_brow_curve = ""
        self.right_brow_curve = ""
        self.left_master_ctrl_surface = ""
        self.right_master_ctrl_surface = ""

        self.brow_seg = 7

        self.create_window()

    def create_window(self):
        if pm.window(self.name, ex=True):
            pm.deleteUI(self.name)

        with pm.window(self.name, title=u"Brow Creator Version {}".format(EDITOR_VERSION)):
            with pm.columnLayout(adj=1) as layout:
                self.create_layout(parent=layout)

        pm.showWindow(self.name)

        # 初始化数据
        self.init_data()

    def create_layout(self, parent):
        with parent:
            with pm.frameLayout(p=parent, lv=False, mh=10, mw=10) as frame:
                with pm.frameLayout(label=u"Components", mh=10, mw=10, bgs=True):
                    pm.textFieldButtonGrp(
                        "xdLeftBrowSurfaceField",
                        label="Left brow surface",
                        adj=2,
                        text=self.left_brow_surface,
                        bl="Get Object",
                        bc=lambda *args: self.brow_follicle_field(
                            template_name="lf_brow_sub_surface",
                            field="xdLeftBrowSurfaceField",
                            side="LF",
                            module="Brow_01",
                        ))
                    pm.textFieldButtonGrp(
                        "xdRightBrowSurfaceField",
                        label="Right brow surface",
                        adj=2,
                        text=self.right_brow_surface,
                        bl="Get Object",
                        bc=lambda *args: self.brow_follicle_field(
                            template_name="rt_brow_sub_surface",
                            field="xdRightBrowSurfaceField",
                            side="RT",
                            module="Brow_01",
                        ))
                    pm.textFieldButtonGrp(
                        "xdLeftBrowCurveField",
                        label="Left brow curve",
                        adj=2,
                        text=self.left_brow_curve,
                        bl="Get Object",
                        bc=lambda *args: utils.get_object_in_field("xdLeftBrowCurveField"))
                    pm.textFieldButtonGrp(
                        "xdRightBrowCurveField",
                        label="Right brow curve",
                        adj=2,
                        text=self.right_brow_curve,
                        bl="Get Object",
                        bc=lambda *args: utils.get_object_in_field("xdRightBrowCurveField"))
                    pm.textFieldButtonGrp(
                        "xdLeftBrowMasterSurfaceField",
                        label="Left master surface",
                        adj=2,
                        text=self.left_master_ctrl_surface,
                        bl="Get Object",
                        bc=lambda *args: utils.get_object_in_field("xdLeftBrowMasterSurfaceField"))
                    pm.textFieldButtonGrp(
                        "xdRightBrowMasterSurfaceField",
                        label="Right master surface",
                        adj=2,
                        text=self.right_master_ctrl_surface,
                        bl="Get Object",
                        bc=lambda *args: utils.get_object_in_field("xdRightBrowMasterSurfaceField"))

                with pm.frameLayout(label=u"Parameters", mh=5, mw=10, bgs=True):
                    pm.intFieldGrp(
                        "xdBrowSubSegmentField",
                        label=u"Segment",
                        numberOfFields=1,
                        value1=self.brow_seg)

                pm.button(label="Build Module",
                          c=lambda *args: self.build_module())

        return frame

    def init_data(self):
        u"""初始化数据

        :return:
        """
        lf_sub_surface = "LF_Brow_01_Sub_Surface"
        if pm.objExists(lf_sub_surface):
            pm.textFieldButtonGrp("xdLeftBrowSurfaceField", e=True, text=lf_sub_surface)
            self.left_brow_surface = lf_sub_surface

        rt_sub_surface = "RT_Brow_01_Sub_Surface"
        if pm.objExists(rt_sub_surface):
            pm.textFieldButtonGrp("xdRightBrowSurfaceField", e=True, text=rt_sub_surface)
            self.right_brow_surface = rt_sub_surface

        lf_sub_curve = "LF_Brow_01_Sub_Curve"
        if pm.objExists(lf_sub_curve):
            pm.textFieldButtonGrp("xdLeftBrowCurveField", e=True, text=lf_sub_curve)
            self.left_brow_curve = lf_sub_curve

        rt_sub_curve = "RT_Brow_01_Sub_Curve"
        if pm.objExists(rt_sub_curve):
            pm.textFieldButtonGrp("xdRightBrowCurveField", e=True, text=rt_sub_curve)
            self.right_brow_curve = rt_sub_curve

        lf_master_surface = "LF_Brow_01_Master_Ctrl_Follicle_Surface"
        if pm.objExists(lf_master_surface):
            pm.textFieldButtonGrp(
                "xdLeftBrowMasterSurfaceField", e=True, text=lf_master_surface)
            self.left_master_ctrl_surface = lf_master_surface

        rt_master_surface = "RT_Brow_01_Master_Ctrl_Follicle_Surface"
        if pm.objExists(rt_master_surface):
            pm.textFieldButtonGrp(
                "xdRightBrowMasterSurfaceField", e=True, text=rt_master_surface)
            self.right_master_ctrl_surface = rt_master_surface

    def brow_follicle_field(self,
                            template_name="template_name",
                            field="filed_control",
                            side="LF",
                            module="Brow_01"):
        u"""导入眉毛的surface模板

        :param template_name: 模板文件的名字
        :param field:
        :param side:
        :param module:
        :return:
        """
        sub_surface = "{}_{}_Sub_Surface".format(side, module)
        if not pm.objExists(sub_surface):
            deformer_grp = "{}_{}_Deformer_Grp".format(side, module)
            if not pm.objExists(deformer_grp):
                pm.createNode("transform", name=deformer_grp, p="Deformer_Grp")

            sub_deformer_grp = "{}_{}_Sub_Deformer_Grp".format(side, module)
            if not pm.objExists(sub_deformer_grp):
                pm.createNode("transform", name=sub_deformer_grp,
                              p=deformer_grp)

            template_file = path(template_dir).joinpath(
                "{}.mb".format(template_name))
            pm.rename(utils.imported_object(template_file), sub_surface)
            pm.parent(sub_surface, sub_deformer_grp)

        pm.textFieldButtonGrp(field, e=True, text=sub_surface)

        return True

    def build_module(self):
        u"""构建模块"""
        if self.before_build():
            print(u"模块构建准备检查已完成")
            self.creator.build()

        return True

    def before_build(self):
        u"""创建模块前，检查场景中是否已经准备好"""
        self.left_brow_surface = pm.textFieldButtonGrp(
            "xdLeftBrowSurfaceField", q=True, text=True)
        if self.left_brow_surface == "" or self.left_brow_surface is None:
            pm.error(u"left brow surface不能为空\n")
        self.creator.left_brow_surface = self.left_brow_surface

        self.right_brow_surface = pm.textFieldButtonGrp(
            "xdRightBrowSurfaceField", q=True, text=True)
        if self.right_brow_surface == "" or self.right_brow_surface is None:
            pm.error(u"right brow surface不能为空\n")
        self.creator.right_brow_surface = self.right_brow_surface

        self.left_brow_curve = pm.textFieldButtonGrp(
            "xdLeftBrowCurveField", q=True, text=True)
        if self.left_brow_curve == "" or self.left_brow_curve is None:
            pm.error(u"left brow curve不能为空")
        self.creator.left_brow_curve = self.left_brow_curve

        self.right_brow_curve = pm.textFieldButtonGrp(
            "xdRightBrowCurveField", q=True, text=True)
        if self.right_brow_curve == "" or self.right_brow_curve is None:
            pm.error(u"right brow curve不能为空")
        self.creator.right_brow_curve = self.right_brow_curve

        self.left_master_ctrl_surface = pm.textFieldButtonGrp(
            "xdLeftBrowMasterSurfaceField", q=True, text=True)
        if self.left_master_ctrl_surface == "" or self.left_master_ctrl_surface is None:
            pm.error(u"left master ctrl surface不能为空")
        self.creator.left_master_ctrl_surface = self.left_master_ctrl_surface

        self.right_master_ctrl_surface = pm.textFieldButtonGrp(
            "xdRightBrowMasterSurfaceField", q=True, text=True)
        if self.right_master_ctrl_surface == "" or self.right_master_ctrl_surface is None:
            pm.error(u"right master ctrl surface不能为空")
        self.creator.right_master_ctrl_surface = self.right_master_ctrl_surface

        return True
