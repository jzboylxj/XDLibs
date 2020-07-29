#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/20 11:03
# @Author  : Li XiaoJun
# @Site    :
# @File    : module_rig.py

from pymel import core as pm
# import maya.mel as mel

from animation import common

reload(common)

tool_version = 0.3


class ModuleRig(common.Singleton):

    def __init__(self):
        super(ModuleRig, self).__init__()

        # 当前TabLayout选择状态的选择索引
        self.current_tab_index = 2

        self.initialize()
        self.show()

    def show(self):
        if pm.window("xdModuleRigUI", ex=True):
            pm.deleteUI("xdModuleRigUI")
        pm.window(
            "xdModuleRigUI",
            t=u"XD模块化绑定 %s" % tool_version,
            mb=True,
            cc=lambda *args: self._closed_window_cmd())

        self.menu_bar()

        self.main_tab = pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        child1 = self.tab_body()
        child2 = self.tab_face()

        pm.tabLayout(
            self.main_tab,
            edit=True,
            tabLabel=(
                (child1, u'Body'),
                (child2, u'Face'),
            ),
            sti=self.current_tab_index)

        pm.showWindow("xdModuleRigUI")

    def initialize(self):
        pass

    def _closed_window_cmd(self):
        pass

    def menu_bar(self):
        pm.menu(label=u"工具", tearOff=True)
        pm.menuItem(
            label=u"Add LOC",
            ann=u"为选择对线添加一个locator作为它的父节点",
            # c=lambda *args: add_node_as_parent()
        )

    def tab_body(self):
        form_layout = pm.formLayout()
        pm.setParent("..")
        return form_layout

    def tab_face(self):
        layout = self.face_pre_layout()
        return layout

    def face_pre_layout(self):
        layout = pm.frameLayout(label="Pre", mw=10, mh=5, lv=False)

        pm.columnLayout(adj=1, rs=2)
        head_component_control_width = [80, 100, 100]
        self.head_bone_control = pm.textFieldButtonGrp(
            label="Head",
            bl="Set",
            cw3=head_component_control_width,
            adj=2,
            bc=lambda *args: self.set_head_field())

        self.head_top_bone_control = pm.textFieldButtonGrp(
            label="Head Top",
            bl="Set",
            cw3=head_component_control_width,
            adj=2,
            bc=lambda *args: self.set_head_top_field())

        self.head_bottom_bone_control = pm.textFieldButtonGrp(
            label="Head Bottom",
            bl="Set",
            cw3=head_component_control_width,
            adj=2,
            bc=lambda *args: self.set_head_bottom_field())

        pm.text(label="Top:", al="center")

        self.right_eye_bone_control = pm.textFieldButtonGrp(
            label="Right Eye",
            bl="Set",
            cw3=head_component_control_width,
            adj=2,
            bc=lambda *args: self.set_eye_field(
                side="right",
                text_field=self.right_eye_bone_control))

        self.left_eye_bone_control = pm.textFieldButtonGrp(
            label="Left Eye",
            bl="Set",
            cw3=head_component_control_width,
            adj=2,
            bc=lambda *args: self.set_eye_field(
                side="left",
                text_field=self.left_eye_bone_control))

        pm.text(label="Bottom:", al="center")

        self.jaw_bone_control = pm.textFieldButtonGrp(
            label="Jaw",
            bl="Set",
            cw3=head_component_control_width,
            adj=2,
            bc=lambda *args: self.set_jaw_field())

        self.chin_bone_control = pm.textFieldButtonGrp(
            label="Chin",
            bl="Set",
            cw3=head_component_control_width,
            adj=2,
            bc=lambda *args: self.set_chin_field())

        self.lower_teeth_bone_control = pm.textFieldButtonGrp(
            label="Lower Teeth",
            bl="Set",
            cw3=head_component_control_width,
            adj=2,
            bc=lambda *args: self.set_lower_teeth_field())

        pm.setParent("..")

        pm.setParent("..")  # end of layout

        if pm.objExists("head_BND"):
            pm.textFieldButtonGrp(
                self.head_bone_control, e=True, text="head_BND")
        if pm.objExists("headTop_BND"):
            pm.textFieldButtonGrp(
                self.head_top_bone_control, e=True, text="headTop_BND")
        if pm.objExists("headBottom_BND"):
            pm.textFieldButtonGrp(
                self.head_bottom_bone_control, e=True, text="headBottom_BND")
        if pm.objExists("L_eyeMove_BND"):
            pm.textFieldButtonGrp(
                self.left_eye_bone_control, e=True, text="L_eyeMove_BND")
        if pm.objExists("R_eyeMove_BND"):
            pm.textFieldButtonGrp(
                self.right_eye_bone_control, e=True, text="R_eyeMove_BND")
        if pm.objExists("jaw_BND"):
            pm.textFieldButtonGrp(
                self.jaw_bone_control, e=True, text="jaw_BND")
        if pm.objExists("chin_BND"):
            pm.textFieldButtonGrp(
                self.chin_bone_control, e=True, text="chin_BND")
        if pm.objExists("teethBot_BND"):
            pm.textFieldButtonGrp(
                self.lower_teeth_bone_control, e=True, text="teethBot_BND")

        return layout

    def set_head_field(self):
        pm.textFieldButtonGrp(
            self.head_bone_control,
            e=True,
            text=self.create_head_bone())
        return

    def create_head_bone(self):
        """
        创建头部根骨骼
        :return: head bone
        """
        head_bone = None
        if pm.objExists("head_BND"):
            # pm.error(u"场景中已经存在Head_BND，请确认是否已经有绑定")
            user_confirm = pm.confirmDialog(
                title='Confirm',
                message=u"场景中已经存在Head_BND，请确认是否已经有绑定",
                button=['Continue', 'Cancel'],
                defaultButton='Continue',
                cancelButton='Cancel',
                dismissString='Cancel')
            if user_confirm == "Continue":
                head_bone = "Head_BND"
                return head_bone
            elif user_confirm == "Cancel":
                head_bone = ""
                return head_bone
        else:
            head_bone = pm.joint(name="head_BND")
            pm.select(head_bone)
            head_sub_con = add_node_as_parent(
                head_bone.name(),
                search_field="_BND", suffix="Sub_CON", node_type="circle")
            head_con = add_node_as_parent(
                head_sub_con,
                search_field="Sub_CON", suffix="_CON", node_type="circle")
            head_bnd_loc = add_node_as_parent(
                head_con,
                search_field="_CON", suffix="_BND_LOC", node_type="locator")
            head_grp = add_node_as_parent(
                head_bnd_loc,
                search_field="_BND_LOC", suffix="_GRP", node_type="transform")

        return head_bone

    def set_head_top_field(self):
        pm.textFieldButtonGrp(
            self.head_top_bone_control,
            e=True,
            text=self.create_head_component_bone(name="headTop_BND"))
        return

    def set_head_bottom_field(self):
        pm.textFieldButtonGrp(
            self.head_bottom_bone_control,
            e=True,
            text=self.create_head_component_bone(name="headBottom_BND"))
        return

    def create_head_component_bone(self, name):
        pm.select(cl=True)
        head_top_bone = None
        head_bone = pm.textFieldButtonGrp(
            self.head_bone_control, q=True, text=True)
        if pm.objExists(head_bone):
            create_three_layout_bone(name=name)
        else:
            pm.error(u"缺少head_BND骨骼")
        return head_top_bone

    def set_eye_field(self, side, text_field):
        eye_grp = "eye_GRP"
        if not pm.objExists(eye_grp):
            eye_grp = pm.createNode("transform", name=eye_grp)
            head_top_bone = pm.textFieldButtonGrp(
                self.head_top_bone_control, q=True, text=True)
            pm.parent(eye_grp, head_top_bone)
            eye_grp.translate.set([0, 0, 0])
            eye_grp.rotate.set([0, 0, 0])

        eye_bone = None
        if side == "left":
            eye_bone = self.create_eye_component(side="left")
        elif side == "right":
            eye_bone = self.create_eye_component(side="right")

        pm.textFieldButtonGrp(text_field, e=True, text=eye_bone)

        return

    def create_eye_component(self, side):
        offset_value = []
        prefix = ""

        if side == "left":
            offset_value = [2, 0, 0]
            prefix = "L_"
        elif side == "right":
            offset_value = [-2, 0, 0]
            prefix = "R_"

        eye_bone = create_two_layout_bone(
            name="%seyeMove_BND" % prefix,
            parent="eye_GRP",
            offset_value=offset_value)

        eye_loc = pm.spaceLocator(name="%seye_LOC" % prefix)
        pm.parent(eye_loc, pm.PyNode(eye_bone).getParent())
        eye_loc.translate.set([0, 0, 0])
        eye_loc.rotate.set([0, 0, 0])

        pm.select(cl=True)
        eyeball_bnd = pm.joint(name="%seye_BND" % prefix)
        pm.parent(eyeball_bnd, eye_loc)
        eyeball_bnd.translate.set([0, 0, 0])
        eyeball_bnd.rotate.set([0, 0, 0])

        eyeball_con = add_node_as_parent(
            eyeball_bnd,
            search_field="_BND", suffix="_CON", node_type="circle")
        eyeball_con_grp = add_node_as_parent(
            eyeball_con,
            search_field="_CON", suffix="_CON_GRP", node_type="transform")

        return eye_bone

    def set_jaw_field(self):
        pm.textFieldButtonGrp(
            self.jaw_bone_control,
            e=True,
            text=self.create_jaw_bone())

    def create_jaw_bone(self):
        jaw_parent = pm.textFieldButtonGrp(
            self.head_bottom_bone_control, q=True, text=True)
        jaw_bone = create_three_layout_bone(
            name="jaw_BND",
            parent=jaw_parent,
            offset_value=[0, -2, 2])
        return jaw_bone

    def set_chin_field(self):
        pm.textFieldButtonGrp(
            self.chin_bone_control,
            e=True,
            text=self.create_chin_bone())

    def create_chin_bone(self):
        chin_parent = pm.textFieldButtonGrp(
            self.jaw_bone_control, q=True, text=True)
        chin_bone = create_three_layout_bone(
            name="chin_BND",
            parent=chin_parent,
            offset_value=[0, -2, 2])
        return chin_bone

    def set_lower_teeth_field(self):
        pm.textFieldButtonGrp(
            self.lower_teeth_bone_control,
            e=True,
            text=self.create_lower_teeth_bone())

    def create_lower_teeth_bone(self):
        teeth_parent = pm.textFieldButtonGrp(
            self.jaw_bone_control, q=True, text=True)
        teeth_bone = create_three_layout_bone(
            name="teethBot_BND",
            parent=teeth_parent,
            offset_value=[0, -2, 2])
        return teeth_bone


def create_two_layout_bone(name, parent, offset_value=None):
    pm.select(cl=True)
    if offset_value is None:
        offset_value = [0, 1, 0]
    bone = pm.joint(name=name)
    con = add_node_as_parent(
        bone.name(),
        search_field="_BND",
        suffix="_CON",
        node_type="circle")
    bnd_grp = add_node_as_parent(
        con,
        search_field="_CON",
        suffix="_GRP",
        node_type="transform")
    pm.parent(bnd_grp, parent)
    bnd_grp.translateX.set(offset_value[0])
    bnd_grp.translateY.set(offset_value[1])
    bnd_grp.translateZ.set(offset_value[2])
    return bone


def create_three_layout_bone(name, parent, offset_value=None):
    if offset_value is None:
        offset_value = [0, 1, 0]
    bone = pm.joint(name=name)
    con = add_node_as_parent(
        bone.name(),
        search_field="_BND",
        suffix="_CON",
        node_type="circle")
    bnd_loc = add_node_as_parent(
        con,
        search_field="_CON",
        suffix="_BND_LOC",
        node_type="locator")
    bnd_grp = add_node_as_parent(
        bnd_loc,
        search_field="_BND_LOC",
        suffix="_BND_GRP", node_type="transform")
    pm.parent(bnd_grp, parent)
    bnd_grp.translateX.set(offset_value[0])
    bnd_grp.translateY.set(offset_value[1])
    bnd_grp.translateZ.set(offset_value[2])
    return bone


def add_node_as_parent(
        target, search_field="_BND", suffix="_LOC", node_type="locator"):
    """
    为目标节点添加一个指定节点作为它的父节点

    这个函数常用来将目标节点的通道栏参数归零
    :param target: 目标节点
    :param node_type: 节点类型
    :return: 新的创建的节点
    """
    new_parent_node = None

    new_parent_name = target.replace(search_field, suffix)

    if node_type == "locator":
        new_parent_node = pm.spaceLocator(name=new_parent_name)
    if node_type == "circle":
        new_parent_node = pm.circle(
            c=(0, 0, 0), nr=(0, 1, 0), name=new_parent_name, ch=0)[0]
    if node_type == "transform":
        new_parent_node = pm.createNode("transform", name=new_parent_name)

    pm.delete(pm.parentConstraint(target, new_parent_node, mo=False))

    current_parent = pm.PyNode(target).getParent()

    if current_parent is not None:
        pm.parent(target, new_parent_node)
        pm.parent(new_parent_node, current_parent)
    else:
        pm.parent(target, new_parent_node)
    return new_parent_node
