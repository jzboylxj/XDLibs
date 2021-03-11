# coding: utf-8


from imp import reload
from pymel import core as pm
from pymel.util import path

from core import utils
from animation import common
# import maya.cmds as cmds
# from pymel.util import path
# from rig.names import template_dir
from rig import template_dir

reload(utils)
reload(common)


class Creator:
    def __init__(self):
        self.module_name = "Eye_01"

        # guide curves
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

        # controllers
        self.left_master_ctrl = ""
        self.right_master_ctrl = ""

        self.left_base_ctrl_group = ""
        self.right_base_ctrl_group = ""

    def init_structure(self):
        for side in ["LF", "RT"]:
            deformer_group = "{}_{}_Deformer_Grp".format(side, self.module_name)
            if not pm.objExists(deformer_group):
                pm.createNode("transform", name=deformer_group, p="Deformer_Grp")

            guid_curve_grp = "{}_{}_Curve_Grp".format(side, self.module_name)
            if not pm.objExists(guid_curve_grp):
                pm.createNode("transform", name=guid_curve_grp, p=deformer_group)

            control_group = "{}_{}_Grp".format(side, self.module_name)
            if not pm.objExists(control_group):
                pm.createNode("transform", name=control_group, p="Head_01_Grp")

        return True

    def build(self):
        self.init_structure()

        for side in ["LF", "RT"]:
            if side == "LF":
                master_ctrl = self.left_master_ctrl
                if not pm.objExists(master_ctrl):
                    pm.error(u"场景中缺少{}".format(master_ctrl))

                self.left_base_ctrl_group = "{}_Eye_01_Base_Ctrl_Grp".format(side)
                if not pm.objExists(self.left_base_ctrl_group):
                    pm.createNode("transform", name=self.left_base_ctrl_group)
                    pm.parent(self.left_base_ctrl_group, pm.PyNode(master_ctrl).getParent())

                base_ctrl_group = self.left_base_ctrl_group

            else:
                master_ctrl = self.right_master_ctrl
                if not pm.objExists(master_ctrl):
                    pm.error(u"场景中缺少{}".format(master_ctrl))

                self.right_base_ctrl_group = "{}_Eye_01_Base_Ctrl_Grp".format(side)
                if not pm.objExists(self.right_base_ctrl_group):
                    pm.createNode("transform", name=self.right_base_ctrl_group)
                    pm.parent(self.right_base_ctrl_group, pm.PyNode(master_ctrl).getParent())

                base_ctrl_group = self.right_base_ctrl_group

            deformer_loc_group = "{}_Eye_01_Loc_Grp".format(side)
            if not pm.objExists(deformer_loc_group):
                pm.createNode("transform", name=deformer_loc_group)
                pm.parent(deformer_loc_group, "{}_Eye_01_Deformer_Grp".format(side))

            # master_ctrl = "{}_Eye_01_Master_Ctrl".format(side)
            pm.delete(pm.parentConstraint(master_ctrl, deformer_loc_group, mo=False))

            base_loc_group = "{}_Eye_01_Base_Loc_Grp".format(side)
            if not pm.objExists(base_loc_group):
                pm.createNode("transform", name=base_loc_group, p=deformer_loc_group)

            root_jnt_group = "{}_Eye_01_Jnt_Grp".format(side)   # LF_Eye_01_Jnt_Grp
            if not pm.objExists(root_jnt_group):
                pm.createNode("transform", name=root_jnt_group,
                              p="{}_Eye_01_Deformer_Grp".format(side))  # LF_Eye_01_Deformer_Grp
            pm.delete(pm.parentConstraint(master_ctrl, root_jnt_group, mo=False))

            master_ctrl_jnt_group = "{}_Eye_01_Master_Ctrl_Jnt_Grp".format(side)    # LF_Eye_01_Master_Ctrl_Jnt_Grp
            pm.createNode("transform", name=master_ctrl_jnt_group, p=root_jnt_group)

            base_jnt_group = "{}_Eye_01_Base_Jnt_Grp".format(side)  # LF_Eye_01_Base_Jnt_Grp
            pm.createNode("transform", name=base_jnt_group, p=master_ctrl_jnt_group)

            for item in ["Up", "Low", "Inner", "Outer"]:
                self.build_base_ctrl_group(side, master_ctrl, base_ctrl_group, item)
                self.build_base_loc_group(side, item, base_loc_group)

            self.build_base_jnt_group(side, base_jnt_group)
            self.build_bind_loc_group(side)
            self.build_bind_jnt_group(side)
            self.skin_out_curve(side)
            self.tweak_ctrl_group(side)
            self.make_blink_work(side)
            self.skin_master_curve(side)
            self.make_master_ctrl_work(side)
            self.build_shape_ctrl_group(side)
            self.build_shape_jnt_group(side)
            self.build_eyeball_ctrl_group(side)
        self.build_aim_ctrl_group()

        print("Build Done!")

        return

    def build_base_ctrl_group(self, side, master_ctrl, base_ctrl_group, item):
        # for item in ["Up", "Low", "Inner", "Outer"]:
        if item == "Low":
            out_curve = "{}_Eye_01_Low_Out_Curve".format(side)
        else:
            out_curve = "{}_Eye_01_Up_Out_Curve".format(side)

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
        temp_mp = utils.mp_node(node_name=temp_mp_name,
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

        elif side == "RT":
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

        ctrl_name = "{}_Eye_01_{}_Ctrl".format(side, item)
        base_ctrl_grp = utils.yellow_component(
            name=ctrl_name, shape_type="nurbsPlane", parent_node=base_ctrl_group)

        pm.delete(pm.orientConstraint(temp_loc_name, base_ctrl_grp, mo=False))

        utils.dm_node(
            node_name="{}_Eye_01_{}_Ctrl_Inverse_DM".format(side, item),
            matrix_input=pm.PyNode(ctrl_name).attr("inverseMatrix"),
            translate_output=pm.PyNode(ctrl_name).getParent().translate,
            rotate_output=pm.PyNode(ctrl_name).getParent().rotate)

        mp_node_name = "{}_Eye_01_{}Master_MP".format(side, item)

        if not pm.objExists(mp_node_name):
            pm.createNode("motionPath", name=mp_node_name)
        pm.PyNode(mp_node_name).attr("uValue").set(u_value)

        pm.PyNode(out_curve).getShape().attr('worldSpace[0]').connect(pm.PyNode(mp_node_name).attr('geometryPath'))
        pm.PyNode(mp_node_name).attr("allCoordinates").connect(pm.PyNode(base_ctrl_grp).translate)
        pm.PyNode(master_ctrl).scale.connect(pm.PyNode(base_ctrl_grp).scale)
        pm.orientConstraint(master_ctrl, base_ctrl_grp, mo=True)

        pm.delete(temp_loc)

        return

    def build_base_loc_group(self, side, item, base_loc_group):
        base_loc = "{}_Eye_01_{}_Ctrl_Loc".format(side, item)
        loc_grp = utils.jnt_or_control_grp(name=base_loc, object_type="locator")

        if item == "Low":
            master_curve = "{}_Eye_01_Low_Master_Curve".format(side)
        else:
            master_curve = "{}_Eye_01_Up_Master_Curve".format(side)

        ctrl = "{}_Eye_01_{}_Ctrl".format(side, item)
        ctrl_grp = "{}_Grp".format(ctrl)
        pm.delete(pm.orientConstraint(ctrl_grp, loc_grp, mo=False))

        postion = None
        if item == "Outer":
            postion = utils.point_on_curve_position(master_curve, 1.0)
            pm.PyNode(ctrl).translate.connect(pm.PyNode(base_loc).translate)
        elif item == "Inner":
            postion = utils.point_on_curve_position(master_curve, 0)
            pm.PyNode(ctrl).translate.connect(pm.PyNode(base_loc).translate)
        elif item == "Low" or "Up":
            postion = utils.point_on_curve_position(master_curve, 0.5)
            pm.PyNode(ctrl).translateX.connect(pm.PyNode(base_loc).translateX)
            pm.PyNode(ctrl).translateZ.connect(pm.PyNode(base_loc).translateZ)

        pm.PyNode(ctrl).rotate.connect(pm.PyNode(base_loc).rotate)

        pm.PyNode(loc_grp).translate.set(postion)
        pm.parent(loc_grp, base_loc_group)

        return

    def build_base_jnt_group(self, side, base_jnt_group):
        if side == "LF":
            proxy_eye = self.left_eye_proxy
        elif side == "RT":
            proxy_eye = self.right_eye_proxy

        temp_locs = []

        temp_root = pm.spaceLocator(name="temp_root_loc")
        pm.delete(pm.parentConstraint(proxy_eye, temp_root, mo=False))

        temp_locs.append(temp_root)

        for item in ["Up", "Low", "Inner", "Outer"]:
            base_loc = "{}_Eye_01_{}_Ctrl_Loc".format(side, item)
            temp_loc = pm.spaceLocator(name="temp_{}_loc".format(item))
            pm.delete(pm.parentConstraint(base_loc, temp_loc, mo=False))
            temp_locs.append(temp_loc)

            pm.select(cl=True)
            pm.joint(name="{}_Eye_01_{}_Ctrl_01_Jnt".format(side, item), p=pm.PyNode(temp_root).translate.get())
            pm.joint(name="{}_Eye_01_{}_Ctrl_02_Jnt".format(side, item), p=pm.PyNode(temp_loc).translate.get())
            pm.joint("{}_Eye_01_{}_Ctrl_01_Jnt".format(side, item), e=True, zso=True, oj="xyz", sao="yup")

            pm.parent("{}_Eye_01_{}_Ctrl_01_Jnt".format(side, item), base_jnt_group)

            pm.aimConstraint(
                pm.PyNode(base_loc), "{}_Eye_01_{}_Ctrl_01_Jnt".format(side, item),
                worldUpType="objectrotation",
                worldUpObject=base_loc,
                mo=True)

        pm.delete(temp_locs)

        return

    def build_bind_loc_group(self, side):
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

                mp = utils.mp_node(
                    node_name=loc_name.replace("Loc", "MP"),
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
                    utils.custom_show_channel(
                        up_ctrl,
                        attr_list=["translateX", "translateY", "rotateX", "rotateY", "rotateZ"])
                    if not pm.attributeQuery("collideGap", node=up_ctrl, ex=True):
                        pm.addAttr(up_ctrl, ln="collideGap", at="double", dv=0)
                        pm.setAttr("{}.collideGap".format(up_ctrl), e=True, k=True)

                    adl = pm.createNode("addDoubleLinear",
                                        name="{}_Low_{}_ADL".format(prefix, "{0:02d}".format(index)))

                    pm.PyNode(up_loc).translateY.connect(adl.attr("input1"))
                    pm.PyNode(up_ctrl).attr("collideGap").connect(adl.attr("input2"))

                    clamp = pm.createNode("clamp",
                                          name="{}_Low_{}_CMP".format(prefix, "{0:02d}".format(index)))
                    clamp.attr("minR").set(-9999.0)
                    adl.attr("output").connect(clamp.attr("maxR"))
                    mp.attr("yCoordinate").connect(clamp.attr("inputR"))
                    clamp.attr("outputR").connect(bind_loc.attr("translateY"), f=True)

        return

    def build_bind_jnt_group(self, side):
        prefix = "{}_{}".format(side, self.module_name)

        master_ctrl_jnt_group = "{}_Master_Ctrl_Jnt_Grp".format(prefix)

        bind_jnt_group = "{}_Bind_Jnt_Grp".format(prefix)
        pm.createNode("transform", name=bind_jnt_group, p=master_ctrl_jnt_group)

        side_name = "LF"
        if side == "LF":
            side_name = "Left"
        elif side == "RT":
            side_name = "Right"

        proxy_eye = pm.textFieldButtonGrp("xdEyeCreator{}EyeProxyField".format(side_name), q=True, text=True)

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

    def skin_out_curve(self, side):
        seg = 10
        prefix = "{}_{}".format(side, self.module_name)
        for vertical in ["Up", "Low"]:
            out_curve = "{}_{}_Out_Curve".format(prefix, vertical)
            skin_items = [out_curve]
            for index in range(1, seg + 1):
                skin_items.append("{}_{}_{}_Jnt".format(prefix, vertical, "{0:02d}".format(index)))
            pm.skinCluster(skin_items, tsb=True, name="{}_{}_Out_Curve_SC".format(prefix, vertical))

        return

    def tweak_ctrl_group(self, side):
        seg = 4
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
                tweak_ctrl_grp = utils.yellow_component(
                    name=tweak_ctrl, shape_type="sphere", parent_node=tweak_ctrl_group)
                utils.dm_node(
                    node_name="{}_Inverse_DM".format(tweak_ctrl),
                    matrix_input=pm.PyNode(tweak_ctrl).attr("inverseMatrix"),
                    translate_output=pm.PyNode(tweak_ctrl).getParent().translate,
                    rotate_output=pm.PyNode(tweak_ctrl).getParent().rotate)

                mp = utils.mp_node(
                    node_name=tweak_ctrl.replace("Ctrl", "MP"),
                    geometry_path_input=out_curve.getShape().attr("worldSpace[0]"),
                    all_coordinates_output=pm.PyNode(tweak_ctrl_grp).translate)
                u_value = float(index) / float(seg + 1)
                pm.PyNode(mp).attr("uValue").set(u_value)

                master_ctrl.scale.connect(pm.PyNode(tweak_ctrl_grp).scale)
                pm.orientConstraint(master_ctrl, tweak_ctrl_grp)

                ctrl_jnt = "{}_Jnt".format(tweak_ctrl)
                ctrl_jnt_grp = utils.jnt_or_control_grp(name=ctrl_jnt, parent_node=tweak_jnt_group)
                pm.delete(pm.pointConstraint(tweak_ctrl_grp, ctrl_jnt_grp, mo=False))

                pm.PyNode(tweak_ctrl).translate.connect(pm.PyNode(ctrl_jnt).translate)

                tweak_skin_items.append(ctrl_jnt)

            if vertical == "Up":
                for horizontal in ["Inner", "Outer"]:
                    tweak_ctrl = "{}_{}Tweak_Ctrl".format(prefix, horizontal)
                    tweak_ctrl_grp = utils.yellow_component(
                        name=tweak_ctrl, shape_type="sphere", parent_node=tweak_ctrl_group)

                    utils.dm_node(
                        node_name="{}_Inverse_DM".format(tweak_ctrl),
                        matrix_input=pm.PyNode(tweak_ctrl).attr("inverseMatrix"),
                        translate_output=pm.PyNode(tweak_ctrl).getParent().translate,
                        rotate_output=pm.PyNode(tweak_ctrl).getParent().rotate)

                    mp = utils.mp_node(node_name=tweak_ctrl.replace("Ctrl", "MP"),
                                       geometry_path_input=out_curve.getShape().attr("worldSpace[0]"),
                                       all_coordinates_output=pm.PyNode(tweak_ctrl_grp).translate)
                    if horizontal == "Inner":
                        pm.PyNode(mp).attr("uValue").set(0)
                    else:
                        pm.PyNode(mp).attr("uValue").set(1)

                    master_ctrl.scale.connect(pm.PyNode(tweak_ctrl_grp).scale)
                    pm.orientConstraint(master_ctrl, tweak_ctrl_grp)

                    ctrl_jnt = "{}_Jnt".format(tweak_ctrl)
                    ctrl_jnt_grp = utils.jnt_or_control_grp(name=ctrl_jnt, parent_node=tweak_jnt_group)
                    pm.delete(pm.pointConstraint(tweak_ctrl_grp, ctrl_jnt_grp, mo=False))

                    pm.PyNode(tweak_ctrl).translate.connect(pm.PyNode(ctrl_jnt).translate)

                    tweak_skin_items.append(ctrl_jnt)

            pm.skinCluster(tweak_skin_items, tsb=True, name="{}_SC".format(tweak_curve))
        return

    def make_blink_work(self, side):
        prefix = "{}_{}".format(side, self.module_name)

        master_ctrl = "{}_Master_Ctrl".format(prefix)  # LF_Eye_01_Master_Ctrl

        utils.custom_show_channel(master_ctrl,
                                  attr_list=["translateX", "translateY", "translateZ",
                                             "rotateX", "rotateY", "rotateZ",
                                             "scaleX", "scaleY", "scaleZ"])

        if not pm.attributeQuery("shift", node=master_ctrl, ex=True):
            pm.addAttr(master_ctrl, ln="shift", at="double", min=0.0, max=1.0, dv=0.3)
            pm.setAttr("{}.shift".format(master_ctrl), e=True, lock=False, keyable=True)

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

    def skin_master_curve(self, side):
        # for side in ["LF", "RT"]:
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

    def make_master_ctrl_work(self, side):
        # for side in ["LF", "RT"]:
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
                    itt="linear", ott="linear")

        return

    def build_shape_ctrl_group(self, side):
        seg = 3
        prefix = "{}_{}".format(side, self.module_name)

        shape_ctrl_group = "{}_Shape_Ctrl_Grp".format(prefix)
        pm.createNode("transform", name=shape_ctrl_group, p="{}_Grp".format(prefix))
        pm.PyNode(shape_ctrl_group).attr("inheritsTransform").set(0)

        original_jnt = "{}_Original_Jnt".format(prefix)
        pm.select(cl=True)
        pm.joint(name=original_jnt)
        pm.parent(original_jnt, "{}_Grp".format(prefix))

        if side == "LF":
            proxy_eye = pm.textFieldButtonGrp("xdEyeCreator{}EyeProxyField".format("Left"), q=True, text=True)
        else:
            proxy_eye = pm.textFieldButtonGrp("xdEyeCreator{}EyeProxyField".format("Right"), q=True, text=True)
        pm.delete(pm.pointConstraint(proxy_eye, original_jnt, mo=False))

        for vertical in ["Up", "Low"]:
            shape_surface = pm.PyNode("{}_{}_Shape_Surface".format(prefix, vertical))

            for index in range(1, seg + 1):
                follicle = utils.xd_follicle_node(
                    name="{}_{}_{}_Shape_Follicle".format(prefix, vertical, "{0:02d}".format(index)),
                    worldMatrixInput=shape_surface.getShape().attr("worldMatrix[0]"),
                    surfaceInput=shape_surface.getShape().attr("local"),
                    parentNode=shape_ctrl_group)
                pm.PyNode(follicle).getShape().attr("parameterU").set(0.5)
                pm.PyNode(follicle).getShape().attr("parameterV").set(float(index) / float(seg + 1))

                shape_ctrl = utils.jnt_or_control_grp(
                    name="{}_{}_{}_Shape_Ctrl".format(prefix, vertical, "{0:02d}".format(index)),
                    object_type="sphere",
                    parent_node=follicle)

                if side == "LF":
                    pm.PyNode(shape_ctrl).rotate.set([90, 0, 90])
                else:
                    pm.PyNode(shape_ctrl).rotate.set([90, 0, -90])

            main_shape_ctrl = "{}_{}_Main_Shape_Ctrl".format(prefix, vertical)
            main_shape_ctrl_grp = utils.control_grp_have_joint(
                name=main_shape_ctrl, parent_node="{}_Grp".format(prefix))
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

    def build_shape_jnt_group(self, side):
        seg = 3
        prefix = "{}_{}".format(side, self.module_name)

        shape_jnt_group = "{}_Shape_Jnt_Grp".format(prefix)
        pm.createNode("transform", name=shape_jnt_group)
        pm.parent(shape_jnt_group, "{}_Jnt_Grp".format(prefix))

        eye_group = pm.PyNode("{}_Grp".format(prefix))

        for vertical in ["Up", "Low"]:
            for index in range(1, seg + 1):
                jnt = "{}_{}_{}_Shape_Ctrl_Jnt".format(prefix, vertical, "{0:02d}".format(index))
                jnt_grp = utils.yellow_component(
                    name=jnt,
                    shape_type="joint",
                    parent_node=shape_jnt_group)

                shape_ctrl_jnt_mm = pm.createNode("multMatrix", name="{}_MM".format(jnt))
                shape_follicle = pm.PyNode("{}_{}_{}_Shape_Follicle".format(
                    prefix, vertical, "{0:02d}".format(index)))
                shape_follicle.attr("worldMatrix[0]").connect(shape_ctrl_jnt_mm.attr("matrixIn[0]"))
                eye_group.attr("worldInverseMatrix[0]").connect(shape_ctrl_jnt_mm.attr("matrixIn[1]"))

                jnt_dm = "{}_{}_{}_Shape_Ctrl_Jnt_DM".format(prefix, vertical, "{0:02d}".format(index))
                utils.dm_node(node_name=jnt_dm,
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

    def build_eyeball_ctrl_group(self, side):
        # for side in ["LF", "RT"]:
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
        aim_ctrl_grp = utils.jnt_or_control_grp(
            name=aim_ctrl, object_type="sphere", parent_node=aim_grp)
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
            eye_aim_ctrl_grp = utils.jnt_or_control_grp(
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
        main_aim_ctrl_grp = utils.jnt_or_control_grp(
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


EDITOR_VERSION = 1.10


class Editor(common.Singleton):
    name = "xdEyeCreatorEditor"

    def __init__(self):
        super(Editor, self).__init__()

        self.creator = Creator()

        self.create_window()

    def create_window(self):
        if pm.window(self.name, ex=True):
            pm.deleteUI(self.name)

        with pm.window(self.name, title=u"Eye Creator Version {}".format(EDITOR_VERSION)):
            with pm.formLayout() as layout:
                scroll_layout = self.create_layout(parent=layout)
                button = pm.button(label=u"Build Module", c=lambda *args: self.build())

                pm.formLayout(
                    layout, edit=True,
                    attachForm=[
                        (scroll_layout, 'top', 10),
                        (scroll_layout, 'left', 5),
                        (scroll_layout, 'right', 5),
                        (button, 'left', 5),
                        (button, 'right', 5),
                        (button, 'bottom', 10),
                    ],
                    attachControl=[
                        (scroll_layout, 'bottom', 5, button),
                    ])
        pm.showWindow(self.name)

        # 初始化数据
        self.layout_init()

    def create_layout(self, parent):
        with parent:
            with pm.scrollLayout(p=parent, cr=True) as frame:
                with pm.frameLayout(label=u"Eye Guid Curve", mh=10, mw=10, cll=True, cl=False):
                    for side in ["LF", "RT"]:
                        if side == "LF":
                            label = "Left"
                        else:
                            label = "Right"

                        with pm.frameLayout(label=label, mh=10, mw=10, bgs=True, cll=True, cl=True):
                            for item in ["Master", "Blink", "Out", "Tweak", "Freshy"]:
                                for position in ["Up", "Low"]:
                                    pm.textFieldButtonGrp(
                                        "xdEyeCreator{}{}{}CurveField".format(label, position, item),
                                        label=u"{} {} {} Curve".format(label, position, item),
                                        bl=u"Get Object",
                                        adj=2,
                                        bc=lambda *args: self.parent_field_to_spec(
                                            field="xdEyeCreator{}{}{}CurveField".format(label, position, item),
                                            group="{}_Eye_01_Curve_Grp".format(side)))

                with pm.frameLayout(label=u"Eye Control location", mh=10, mw=10, bgs=True, cll=True, cl=False):
                    pm.text(label=u"* is optional", al='left')
                    pm.textFieldButtonGrp(
                        "xdEyeCreatorLeftUpShapeSurfaceField",
                        label=u"Left Up Shape Surface",
                        bl=u"Get Object",
                        adj=2,
                        bc=lambda *args: self.import_eye_up_shape_surface(
                            vertical="Up", side="LF", field="xdEyeCreatorLeftUpShapeSurfaceField"))
                    pm.textFieldButtonGrp(
                        "xdEyeCreatorLeftLowShapeSurfaceField",
                        label=u"Left Low Shape Surface",
                        bl=u"Get Object",
                        adj=2,
                        bc=lambda *args: self.import_eye_up_shape_surface(
                            vertical="Low", side="LF", field="xdEyeCreatorLeftLowShapeSurfaceField"))
                    pm.textFieldButtonGrp(
                        "xdEyeCreatorRightUpShapeSurfaceField",
                        label=u"Right Up Shape Surface",
                        bl=u"Get Object",
                        adj=2,
                        bc=lambda *args: self.parent_field_to_spec(
                            field="xdEyeCreatorRightUpShapeSurfaceField", group="RT_Eye_01_Curve_Grp"))
                    pm.textFieldButtonGrp(
                        "xdEyeCreatorRightLowShapeSurfaceField",
                        label=u"Right Low Shape Surface",
                        bl=u"Get Object",
                        adj=2,
                        bc=lambda *args: self.parent_field_to_spec(
                            field="xdEyeCreatorRightLowShapeSurfaceField", group="RT_Eye_01_Curve_Grp"))
                    pm.textFieldButtonGrp(
                        "xdEyeCreatorLeftEyeGeoField",
                        label=u"Left eye geo", bl=u"Get Object", adj=2,
                        bc=lambda *args: self.parent_field_to_spec(field="xdEyeCreatorLeftEyeGeoField"))
                    pm.textFieldButtonGrp(
                        "xdEyeCreatorRightEyeGeoField",
                        label=u"Right eye geo", bl=u"Get Object", adj=2,
                        bc=lambda *args: self.parent_field_to_spec(field="xdEyeCreatorRightEyeGeoField"))
                    pm.textFieldButtonGrp(
                        "xdEyeCreatorLeftEyeProxyField",
                        label=u"Left eye proxy(*)", bl=u"Get Object", adj=2,
                        bc=lambda *args: self.parent_field_to_spec(field="xdEyeCreatorLeftEyeProxyField"))
                    pm.textFieldButtonGrp(
                        "xdEyeCreatorRightEyeProxyField",
                        label=u"Right eye proxy(*)", bl=u"Get Object", adj=2,
                        bc=lambda *args: self.parent_field_to_spec(field="xdEyeCreatorRightEyeProxyField"))
                    pm.textFieldButtonGrp(
                        "xdEyeCreatorLeftMasterCtrlField",
                        label=u"Left master control", bl=u"Get Object", adj=2,
                        bc=lambda *args: self.eye_master_ctrl_field(
                            side="LF", field="xdEyeCreatorLeftMasterCtrlField"))
                    pm.textFieldButtonGrp(
                        "xdEyeCreatorRightMasterCtrlField",
                        label=u"Right master control", bl=u"Get Object", adj=2,
                        bc=lambda *args: self.eye_master_ctrl_field(
                            side="RT", field="xdEyeCreatorRightMasterCtrlField"))

        return frame

    def layout_init(self):
        for side in ["LF", "RT"]:
            if side == "LF":
                side_alias = "Left"
            else:
                side_alias = "Right"

            for vertical in ["Up", "Low"]:
                prefix = "{}_{}_{}".format(side, self.creator.module_name, vertical)
                for item in ["Master", "Blink", "Out", "Tweak", "Freshy"]:
                    curve = "{}_{}_Curve".format(prefix, item)
                    if pm.objExists(curve):
                        pm.textFieldButtonGrp(
                            "xdEyeCreator{}{}{}CurveField".format(side_alias, vertical, item), e=True, text=curve)
                surface = "{}_Shape_Surface".format(prefix)
                if pm.objExists(surface):
                    pm.textFieldButtonGrp(
                        "xdEyeCreator{}{}ShapeSurfaceField".format(side_alias, vertical), e=True, text=surface)
            # control location frame上面的字段
            eye_geo = "{}_Eye_Geo".format(side)
            if pm.objExists(eye_geo):
                pm.textFieldButtonGrp("xdEyeCreator{}EyeGeoField".format(side_alias), e=True, text=eye_geo)

            eye_proxy = "{}_proxy_eye".format(side)
            if pm.objExists(eye_proxy):
                pm.textFieldButtonGrp("xdEyeCreator{}EyeProxyField".format(side_alias), e=True, text=eye_proxy)

            master_ctrl = "{}_{}_Master_Ctrl".format(side, self.creator.module_name)
            if pm.objExists(master_ctrl):
                pm.textFieldButtonGrp("xdEyeCreator{}MasterCtrlField".format(side_alias), e=True, text=master_ctrl)

        return

    def import_eye_up_shape_surface(self, vertical="Up", side="LF", field=""):
        if vertical == "Up":
            template_file = path(template_dir).joinpath(
                "lf_eye_up_shape_surface.mb")
        else:
            template_file = path(template_dir).joinpath(
                "lf_eye_low_shape_surface.mb")

        import_object = pm.rename(utils.imported_object(template_file),
                                  "{}_{}_{}_Shape_Surface".format(side, self.creator.module_name, vertical))
        if pm.objExists("{}_{}_Curve_Grp".format(side, self.creator.module_name)):
            pm.parent(import_object, "{}_{}_Curve_Grp".format(side, self.creator.module_name))

        pm.textFieldButtonGrp(field, e=True, text=import_object)

        return True

    def parent_field_to_spec(self, field, group=None):
        u"""将选择的对象的名字填充到控件里面，并且放到group的层级下

        :param field: textFieldButtonGrp控件的名字
        :param group: 特殊组
        :return:
        """
        target = pm.ls(sl=True)[0]
        self.creator.init_structure()

        pm.textFieldButtonGrp(field, e=True, text=target)
        if group is not None:
            pm.parent(target, group)

        return

    def eye_master_ctrl_field(self, side, field):
        self.creator.init_structure()

        prefix = "{}_{}".format(side, self.creator.module_name)
        master_ctrl = "{}_Master_Ctrl".format(prefix)
        utils.jnt_or_control_grp(name=master_ctrl, object_type="tours", parent_node="{}_Grp".format(prefix))
        pm.textFieldButtonGrp(field, e=True, text=master_ctrl)

    def build(self):
        self.init()

        # print(self.creator.__dict__)
        # for key in self.creator.__dict__.keys():
        #     print("key:{}, value:{}".format(key, self.creator.__dict__.get(key)))

        self.creator.init_structure()
        self.creator.build()

        return

    def init(self):
        for side in ["left", "right"]:
            for item in ["master", "blink", "out", "tweak", "freshy"]:
                for position in ["up", "low"]:
                    self.creator.__dict__["{}_{}_{}_curve".format(side, position, item)] = pm.textFieldButtonGrp(
                        "xdEyeCreator{}{}{}CurveField".format(side.title(), position.title(), item.title()),
                        q=True, text=True)

        self.creator.left_up_shape_surface = pm.textFieldButtonGrp(
            "xdEyeCreatorLeftUpShapeSurfaceField", q=True, text=True)
        self.creator.left_low_shape_surface = pm.textFieldButtonGrp(
            "xdEyeCreatorLeftLowShapeSurfaceField", q=True, text=True)

        self.creator.right_up_shape_surface = pm.textFieldButtonGrp(
            "xdEyeCreatorRightUpShapeSurfaceField", q=True, text=True)
        self.creator.right_low_shape_surface = pm.textFieldButtonGrp(
            "xdEyeCreatorRightLowShapeSurfaceField", q=True, text=True)

        self.creator.left_eye_geo = pm.textFieldButtonGrp("xdEyeCreatorLeftEyeGeoField", q=True, text=True)
        self.creator.right_eye_geo = pm.textFieldButtonGrp("xdEyeCreatorRightEyeGeoField", q=True, text=True)
        self.creator.left_eye_proxy = pm.textFieldButtonGrp("xdEyeCreatorLeftEyeProxyField", q=True, text=True)
        self.creator.right_eye_proxy = pm.textFieldButtonGrp("xdEyeCreatorRightEyeProxyField", q=True, text=True)

        self.creator.left_master_ctrl = pm.textFieldButtonGrp("xdEyeCreatorLeftMasterCtrlField", q=True, text=True)
        self.creator.right_master_ctrl = pm.textFieldButtonGrp("xdEyeCreatorRightMasterCtrlField", q=True, text=True)

        print(self.creator.__dict__)

        return
