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


class EyeCreator:
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
                temp_mp = main.mp_node(node_name=temp_mp_name,
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
                base_ctrl_grp = main.yellow_component(
                    name=ctrl_name, shape_type="nurbsPlane", parent_node=base_ctrl_group)

                pm.delete(pm.orientConstraint(temp_loc_name, base_ctrl_grp, mo=False))

                main.dm_node(
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
                loc_grp = main.jnt_or_control_grp(name=loc_name, object_type="locator")

                if item == "Low":
                    master_curve = "{}_Low_Master_Curve".format(prefix)
                else:
                    master_curve = "{}_Up_Master_Curve".format(prefix)

                ctrl = "{}_{}_Ctrl".format(prefix, item)
                ctrl_grp = "{}_Grp".format(ctrl)
                pm.delete(pm.orientConstraint(ctrl_grp, loc_grp, mo=False))

                postion = None
                if item == "Outer":
                    postion = main.point_on_curve_position(master_curve, 1.0)
                    pm.PyNode(ctrl).translate.connect(pm.PyNode(loc_name).translate)
                elif item == "Inner":
                    postion = main.point_on_curve_position(master_curve, 0)
                    pm.PyNode(ctrl).translate.connect(pm.PyNode(loc_name).translate)
                elif item == "Low" or "Up":
                    postion = main.point_on_curve_position(master_curve, 0.5)
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

                    mp = main.mp_node(node_name=loc_name.replace("Loc", "MP"),
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
                        main.custom_show_channel(
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
                    tweak_ctrl_grp = main.yellow_component(name=tweak_ctrl,
                                                           shape_type="sphere",
                                                           parent_node=tweak_ctrl_group)
                    main.dm_node(
                        node_name="{}_Inverse_DM".format(tweak_ctrl),
                        matrix_input=pm.PyNode(tweak_ctrl).attr("inverseMatrix"),
                        translate_output=pm.PyNode(tweak_ctrl).getParent().translate,
                        rotate_output=pm.PyNode(tweak_ctrl).getParent().rotate)

                    mp = main.mp_node(node_name=tweak_ctrl.replace("Ctrl", "MP"),
                                      geometry_path_input=out_curve.getShape().attr("worldSpace[0]"),
                                      all_coordinates_output=pm.PyNode(tweak_ctrl_grp).translate)
                    u_value = float(index) / float(seg + 1)
                    pm.PyNode(mp).attr("uValue").set(u_value)

                    master_ctrl.scale.connect(pm.PyNode(tweak_ctrl_grp).scale)
                    pm.orientConstraint(master_ctrl, tweak_ctrl_grp)

                    ctrl_jnt = "{}_Jnt".format(tweak_ctrl)
                    ctrl_jnt_grp = main.jnt_or_control_grp(name=ctrl_jnt, parent_node=tweak_jnt_group)
                    pm.delete(pm.pointConstraint(tweak_ctrl_grp, ctrl_jnt_grp, mo=False))

                    pm.PyNode(tweak_ctrl).translate.connect(pm.PyNode(ctrl_jnt).translate)

                    tweak_skin_items.append(ctrl_jnt)

                if vertical == "Up":
                    for horizontal in ["Inner", "Outer"]:
                        tweak_ctrl = "{}_{}Tweak_Ctrl".format(prefix, horizontal)
                        tweak_ctrl_grp = main.yellow_component(name=tweak_ctrl,
                                                               shape_type="sphere",
                                                               parent_node=tweak_ctrl_group)

                        main.dm_node(
                            node_name="{}_Inverse_DM".format(tweak_ctrl),
                            matrix_input=pm.PyNode(tweak_ctrl).attr("inverseMatrix"),
                            translate_output=pm.PyNode(tweak_ctrl).getParent().translate,
                            rotate_output=pm.PyNode(tweak_ctrl).getParent().rotate)

                        mp = main.mp_node(node_name=tweak_ctrl.replace("Ctrl", "MP"),
                                          geometry_path_input=out_curve.getShape().attr("worldSpace[0]"),
                                          all_coordinates_output=pm.PyNode(tweak_ctrl_grp).translate)
                        if horizontal == "Inner":
                            pm.PyNode(mp).attr("uValue").set(0)
                        else:
                            pm.PyNode(mp).attr("uValue").set(1)

                        master_ctrl.scale.connect(pm.PyNode(tweak_ctrl_grp).scale)
                        pm.orientConstraint(master_ctrl, tweak_ctrl_grp)

                        ctrl_jnt = "{}_Jnt".format(tweak_ctrl)
                        ctrl_jnt_grp = main.jnt_or_control_grp(name=ctrl_jnt, parent_node=tweak_jnt_group)
                        pm.delete(pm.pointConstraint(tweak_ctrl_grp, ctrl_jnt_grp, mo=False))

                        pm.PyNode(tweak_ctrl).translate.connect(pm.PyNode(ctrl_jnt).translate)

                        tweak_skin_items.append(ctrl_jnt)

                pm.skinCluster(tweak_skin_items, tsb=True, name="{}_SC".format(tweak_curve))
        return

    def make_blink_work(self):
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            master_ctrl = "{}_Master_Ctrl".format(prefix)  # LF_Eye_01_Master_Ctrl

            main.custom_show_channel(master_ctrl,
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
                    follicle = main.xd_follicle_node(
                        name="{}_{}_{}_Shape_Follicle".format(prefix, vertical, "{0:02d}".format(index)),
                        worldMatrixInput=shape_surface.getShape().attr("worldMatrix[0]"),
                        surfaceInput=shape_surface.getShape().attr("local"),
                        parentNode=shape_ctrl_group)
                    pm.PyNode(follicle).getShape().attr("parameterU").set(0.5)
                    pm.PyNode(follicle).getShape().attr("parameterV").set(float(index) / float(seg + 1))

                    shape_ctrl = main.jnt_or_control_grp(
                        name="{}_{}_{}_Shape_Ctrl".format(prefix, vertical, "{0:02d}".format(index)),
                        object_type="sphere",
                        parent_node=follicle)

                    if side == "LF":
                        pm.PyNode(shape_ctrl).rotate.set([90, 0, 90])
                    else:
                        pm.PyNode(shape_ctrl).rotate.set([90, 0, -90])

                main_shape_ctrl = "{}_{}_Main_Shape_Ctrl".format(prefix, vertical)
                main_shape_ctrl_grp = main.control_grp_have_joint(
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
                    jnt_grp = main.yellow_component(
                        name=jnt,
                        shape_type="joint",
                        parent_node=shape_jnt_group)

                    shape_ctrl_jnt_mm = pm.createNode("multMatrix", name="{}_MM".format(jnt))
                    shape_follicle = pm.PyNode("{}_{}_{}_Shape_Follicle".format(
                        prefix, vertical, "{0:02d}".format(index)))
                    shape_follicle.attr("worldMatrix[0]").connect(shape_ctrl_jnt_mm.attr("matrixIn[0]"))
                    eye_group.attr("worldInverseMatrix[0]").connect(shape_ctrl_jnt_mm.attr("matrixIn[1]"))

                    jnt_dm = "{}_{}_{}_Shape_Ctrl_Jnt_DM".format(prefix, vertical, "{0:02d}".format(index))
                    main.dm_node(node_name=jnt_dm,
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
            aim_ctrl_grp = main.jnt_or_control_grp(
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
            eye_aim_ctrl_grp = main.jnt_or_control_grp(
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
        main_aim_ctrl_grp = main.jnt_or_control_grp(
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
