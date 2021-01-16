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


class BrowCreator:
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
                follicle = main.xd_follicle_node(
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
                follicle = main.xd_follicle_node(
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
                control_grp = main.control_grp_have_joint(name=control_name, parent_node=master_ctrl)
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
