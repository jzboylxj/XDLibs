#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/20 11:03
# @Author  : Li XiaoJun
# @Site    :
# @File    : module_rig.py

from pymel import core as pm
# import maya.mel as mel

from animation import common
from animation import helper

reload(common)
reload(helper)

tool_version = 0.3

icon_path = "C:/Users/86181/Documents/maya/2016.5/zh_CN/prefs/icons/"
head_icon = icon_path + "head.png"
eye_icon = icon_path + "eye2.png"


class ModuleRig(common.Singleton):
    """
    模块化绑定工具包
    """
    def __init__(self):
        super(ModuleRig, self).__init__()

        # 当前TabLayout选择状态的选择索引
        self.current_tab_index = 2
        self.text_field_button_grp_width = [110, 100, 100]

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
        main_layout = pm.formLayout()

        tool_tab_bar = pm.tabLayout(
            innerMarginWidth=5, innerMarginHeight=5, p=main_layout)

        face_action_bar = pm.rowColumnLayout(p=tool_tab_bar, nr=1)
        pm.symbolButton(
            image=head_icon,
            ann=u"创建头部根骨骼结构",
            c=lambda *args: self.set_head_field())

        pm.symbolButton(
            image=eye_icon,
            ann=u"创建眼睛绑定模块",
            c=lambda *args: self.set_eye_field())

        pm.tabLayout(
            tool_tab_bar,
            edit=True,
            tabLabel=(
                (face_action_bar, u'组件'),
            ),
            # sti=self.current_tab_index
        )

        data_form = pm.formLayout(p=main_layout)
        tree_view_frame = pm.frameLayout(
            label=u"组件栏",
            mw=5, mh=5,
            bgs=True,
            p=data_form,
            w=200)
        self.tree_view = pm.treeView(
            w=200,
            vis=True,
            parent=tree_view_frame,
            # numberOfButtons=3,
            abr=False)
        data_frame = pm.frameLayout(
            label=u"数据栏", mw=5, mh=5, bgs=True, p=data_form)
        pm.formLayout(
            data_form, edit=True,
            attachForm=[
                (tree_view_frame, "top", 5),
                (tree_view_frame, "left", 5),
                (tree_view_frame, "bottom", 5),
                (data_frame, "top", 5),
                (data_frame, "right", 5),
                (data_frame, "bottom", 5),
            ],
            attachControl=[
                (data_frame, 'left', 2, tree_view_frame),
            ]
        )

        pm.formLayout(
            main_layout, edit=True,
            attachForm=[
                (tool_tab_bar, "top", 0),
                (tool_tab_bar, "left", 0),
                (tool_tab_bar, "right", 0),
                (data_form, "left", 0),
                (data_form, "right", 0),
                (data_form, "bottom", 0),
            ],
            attachControl=[
                (data_form, 'top', 2, tool_tab_bar),
            ])

        pm.showWindow("xdModuleRigUI")

    def initialize(self):
        pass

    def _closed_window_cmd(self):
        pass

    def menu_bar(self):
        pm.menu(label=u"工具", tearOff=False)
        pm.menuItem(
            label=u"Add LOC",
            ann=u"为选择对线添加一个locator作为它的父节点",
            # c=lambda *args: add_node_as_parent()
        )
        pm.menu(label=u"窗口", tearOff=False)
        pm.menuItem(
            "facialComponentView",
            label=u"Component View",
            ann=u"绑定组件树结构窗口显示",
            cb=True,
            c=lambda *args: self.change_component_view_state()
        )

    def change_component_view_state(self):
        if pm.menuItem("facialComponentView", q=True, cb=True):
            pm.treeView(self.tree_view, e=True, vis=True)
        else:
            pm.treeView(self.tree_view, e=True, vis=False)
        return

    def tab_body(self):
        form_layout = pm.formLayout()
        pm.setParent("..")
        return form_layout

    def tab_face(self):
        layout = self.face_rig_layout()
        return layout

    def face_rig_layout(self):
        layout = pm.formLayout(numberOfDivisions=100)

        scroll_layout = pm.scrollLayout(cr=True, mcw=400, vsb=True)

        self.head_base_frame_layout()

        self.head_detail_frame_layout()

        pm.setParent("..")  # end of scroll layout

        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (scroll_layout, 'top', 0),
                (scroll_layout, 'left', 0),
                (scroll_layout, 'right', 0),
                (scroll_layout, 'bottom', 0),
            ],
            attachControl=[
                # (scroll_layout, 'bottom', 5, bottom_layout),
            ])
        pm.setParent("..")  # end of layout

        self.init_pre_layout()

        return layout

    def head_base_frame_layout(self):
        layout = pm.frameLayout(
            label="Base", mw=10, mh=5, cll=True, cl=False)
        pm.columnLayout(adj=1, rs=2)
        self.head_bone_control = pm.textFieldButtonGrp(
            label="Head",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_head_field())

        pm.frameLayout(label="Top", mw=10, mh=5, cll=True, cl=False)
        self.head_top_bone_control = pm.textFieldButtonGrp(
            label="Head Top",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_head_top_field())
        self.right_eye_bone_control = pm.textFieldButtonGrp(
            label="Right Eye",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_eye_field(
                side="right",
                text_field=self.right_eye_bone_control))
        self.left_eye_bone_control = pm.textFieldButtonGrp(
            label="Left Eye",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_eye_field(
                side="left",
                text_field=self.left_eye_bone_control))
        pm.setParent("..")

        pm.frameLayout(label="Bottom", mw=10, mh=5, cll=True, cl=False)
        self.head_bottom_bone_control = pm.textFieldButtonGrp(
            label="Head Bottom",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_head_bottom_field())
        self.jaw_bone_control = pm.textFieldButtonGrp(
            label="Jaw",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_jaw_field())
        self.chin_bone_control = pm.textFieldButtonGrp(
            label="Chin",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_chin_field())
        self.lower_teeth_bone_control = pm.textFieldButtonGrp(
            label="Lower Teeth",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_lower_teeth_field())
        self.upper_teeth_bone_control = pm.textFieldButtonGrp(
            label="Upper Teeth",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_upper_teeth_field())
        self.tongue_bone_control = pm.textFieldButtonGrp(
            label="Tongue",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_tongue_field())
        pm.setParent("..")

        pm.frameLayout(label="Nose and ears", mw=10, mh=5, cll=True, cl=False)
        self.nose_bone_control = pm.textFieldButtonGrp(
            label="Nose",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_nose_field())
        self.nose_tip_bone_control = pm.textFieldButtonGrp(
            label="Nose Tip",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_nose_tip_field())
        self.right_nostril_bone_control = pm.textFieldButtonGrp(
            label="Right Nostril",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_right_nostril_field())
        self.left_nostril_bone_control = pm.textFieldButtonGrp(
            label="Left Nostril",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_left_nostril_field())
        pm.setParent("..")

        pm.setParent("..")  # end of column layout
        pm.setParent("..")  # end of pre frame

        return layout

    def head_detail_frame_layout(self):
        layout = pm.frameLayout(
            label="Detail", mw=10, mh=5, cll=True, cl=False)
        pm.columnLayout(adj=1, rs=2)

        # 眼睛的细节
        pm.frameLayout(label="Eye Lid", mw=10, mh=5, cll=True, cl=False)
        self.left_eyecorner_inner_control = pm.textFieldButtonGrp(
            label="Left Corner Inner",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_left_eyecorner_inner_field())
        self.left_eyecorner_outer_control = pm.textFieldButtonGrp(
            label="Left Corner Outer",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_left_eyecorner_outer_field())

        self.right_eyecorner_inner_control = pm.textFieldButtonGrp(
            label="Right Corner Inner",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_right_eyecorner_inner_field())
        self.right_eyecorner_outer_control = pm.textFieldButtonGrp(
            label="Right Corner Outer",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.set_right_eyecorner_outer_field())
        pm.setParent("..")

        pm.setParent("..")
        pm.setParent("..")
        return layout

    def set_head_field(self):
        # pm.textFieldButtonGrp(
        #     self.head_bone_control,
        #     e=True,
        #     text=self.create_head_bone())
        if self.create_head_bone():
            pm.treeView(self.tree_view, e=True, addItem=("Head", ""))
            pm.treeView(self.tree_view, e=True, addItem=("HeadTop", "Head"))
            pm.treeView(self.tree_view, e=True, addItem=("HeadBot", "Head"))
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
            self.create_head_config()
            head_bone = pm.joint(name="head_BND").name()
            pm.select(head_bone)
            head_sub_con = add_node_as_parent(
                head_bone,
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

            # 创建头部上半部分的根骨骼
            head_top = DoJointGrp(
                name="headTop",
                parent=head_bone,
                offset_value=[0, 2, 2])
            # 创建头部下半部分的根骨骼
            head_bot = DoJointGrp(
                name="headBottom",
                parent=head_bone,
                offset_value=[0, 1.5, 2])

            print head_top, head_bot

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

    def set_upper_teeth_field(self):
        pm.textFieldButtonGrp(
            self.upper_teeth_bone_control,
            e=True,
            text=self.create_upper_teeth_bone())

    def create_upper_teeth_bone(self):
        teeth_parent = pm.textFieldButtonGrp(
            self.head_bottom_bone_control, q=True, text=True)
        teeth_parent = pm.PyNode(teeth_parent).getParent()
        teeth_bone = create_three_layout_bone(
            name="teethTop_BND",
            parent=teeth_parent,
            offset_value=[0, 2, 2])
        return teeth_bone

    def set_nose_field(self):
        pm.textFieldButtonGrp(
            self.nose_bone_control,
            e=True,
            text=self.create_nose_bone())

    def create_nose_bone(self):
        nose_parent = pm.textFieldButtonGrp(
            self.head_bone_control, q=True, text=True)
        pm.parent(
            pm.createNode("transform", n="nose_GRP"),
            pm.createNode("transform", n="noseAndEars_GRP"))
        pm.parent("noseAndEars_GRP", nose_parent)
        teeth_bone = create_three_layout_bone(
            name="nose_BND",
            parent="nose_GRP",
            offset_value=[0, -2, 2])
        return teeth_bone

    def set_nose_tip_field(self):
        pm.textFieldButtonGrp(
            self.nose_tip_bone_control,
            e=True,
            text=self.create_nose_tip_bone())

    def create_nose_tip_bone(self):
        nose_tip_parent = pm.textFieldButtonGrp(
            self.nose_bone_control, q=True, text=True)
        nose_tip_parent = pm.PyNode(nose_tip_parent).getParent()
        nose_tip_bone = create_three_layout_bone(
            name="noseTip_BND",
            parent=nose_tip_parent,
            offset_value=[0, 2, 2])
        return nose_tip_bone

    def set_right_nostril_field(self):
        pm.textFieldButtonGrp(
            self.right_nostril_bone_control,
            e=True,
            text=self.create_right_nostril_bone())

    def create_right_nostril_bone(self):
        nostril_parent = pm.textFieldButtonGrp(
            self.nose_bone_control, q=True, text=True)
        nostril_parent = pm.PyNode(nostril_parent).getParent()
        nose_tip_bone = create_three_layout_bone(
            name="R_nostril_BND",
            parent=nostril_parent,
            offset_value=[-2, 0, 0])
        return nose_tip_bone

    def set_left_nostril_field(self):
        pm.textFieldButtonGrp(
            self.left_nostril_bone_control,
            e=True,
            text=self.create_left_nostril_bone())

    def create_left_nostril_bone(self):
        nostril_parent = pm.textFieldButtonGrp(
            self.nose_bone_control, q=True, text=True)
        nostril_parent = pm.PyNode(nostril_parent).getParent()
        nose_tip_bone = create_three_layout_bone(
            name="L_nostril_BND",
            parent=nostril_parent,
            offset_value=[2, 0, 0])
        return nose_tip_bone

    def set_tongue_field(self):
        pm.textFieldButtonGrp(
            self.tongue_bone_control,
            e=True,
            text=self.create_tongue_bone())

    def create_tongue_bone(self):
        tongue_parent = pm.textFieldButtonGrp(
            self.jaw_bone_control, q=True, text=True)

        tongue_bone_list = []

        for index in range(1, 7):
            tongue_bone = create_three_layout_bone(
                name="tongue_00%s_BND" % index,
                parent=tongue_parent,
                offset_value=[0, -2, 2])
            tongue_parent = tongue_bone
            tongue_bone_list.append(tongue_bone)

        return helper.list_to_str(tongue_bone_list)

    def init_pre_layout(self):
        if pm.objExists("head_config"):
            pm.textFieldButtonGrp(
                self.head_bone_control,
                e=True, text=pm.getAttr("head_config.head"))
            pm.textFieldButtonGrp(
                self.head_top_bone_control,
                e=True, text=pm.getAttr("head_config.headTop"))
            pm.textFieldButtonGrp(
                self.head_bottom_bone_control,
                e=True, text=pm.getAttr("head_config.headBottom"))
            pm.textFieldButtonGrp(
                self.left_eye_bone_control,
                e=True, text=pm.getAttr("head_config.leftEye"))
            pm.textFieldButtonGrp(
                self.right_eye_bone_control,
                e=True, text=pm.getAttr("head_config.rightEye"))
            pm.textFieldButtonGrp(
                self.jaw_bone_control,
                e=True, text=pm.getAttr("head_config.jaw"))
            pm.textFieldButtonGrp(
                self.chin_bone_control,
                e=True, text=pm.getAttr("head_config.chin"))
            pm.textFieldButtonGrp(
                self.lower_teeth_bone_control,
                e=True, text=pm.getAttr("head_config.lowerTeeth"))
            pm.textFieldButtonGrp(
                self.upper_teeth_bone_control,
                e=True, text=pm.getAttr("head_config.upperTeeth"))
            pm.textFieldButtonGrp(
                self.nose_bone_control,
                e=True, text=pm.getAttr("head_config.nose"))
            pm.textFieldButtonGrp(
                self.tongue_bone_control,
                e=True, text=pm.getAttr("head_config.tongue"))
            pm.textFieldButtonGrp(
                self.nose_tip_bone_control,
                e=True, text=pm.getAttr("head_config.noseTip"))
            pm.textFieldButtonGrp(
                self.right_nostril_bone_control,
                e=True, text=pm.getAttr("head_config.rightNostril"))
            pm.textFieldButtonGrp(
                self.left_nostril_bone_control,
                e=True, text=pm.getAttr("head_config.leftNostril"))

    def set_left_eyecorner_inner_field(self):
        pass


    def create_head_config(self):
        pm.createNode()


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


class DoJointGrp:
    def __init__(self, name="", parent="", offset_value=None):
        self.name = name
        self.bnd_name = None
        self.bnd_con = None
        self.bnd_loc = None
        self.bnd_grp = None

        self.parent = parent

        if offset_value is None:
            self.offset_value = [0, 0, 0]
        else:
            self.offset_value = offset_value

        self.build()

    def __str__(self):
        return self.name

    def build(self):
        pm.select(cl=True)
        self.bnd_name = pm.joint(name=(self.name + "_BND")).name()
        self.bnd_con = add_node_as_parent(
            self.bnd_name,
            search_field="_BND",
            suffix="_CON",
            node_type="circle")
        self.bnd_loc = add_node_as_parent(
            self.bnd_con,
            search_field="_CON",
            suffix="_BND_LOC",
            node_type="locator")
        self.bnd_grp = add_node_as_parent(
            self.bnd_loc,
            search_field="_BND_LOC",
            suffix="_BND_GRP", node_type="transform")
        pm.parent(self.bnd_grp, self.parent)
        pm.PyNode(self.bnd_grp).translate.set(self.offset_value)
        return


def create_three_layout_bone(name="", parent="", offset_value=None):
    if offset_value is None:
        offset_value = [0, 1, 0]
    pm.select(cl=True)
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
        new_parent_node = pm.spaceLocator(name=new_parent_name).name()
    if node_type == "circle":
        new_parent_node = pm.circle(
            c=(0, 0, 0), nr=(0, 1, 0), name=new_parent_name, ch=0)[0].name()
    if node_type == "transform":
        new_parent_node = pm.createNode(
            "transform", name=new_parent_name).name()

    pm.delete(pm.parentConstraint(target, new_parent_node, mo=False))

    current_parent = pm.PyNode(target).getParent()

    if current_parent is not None:
        pm.parent(target, new_parent_node)
        pm.parent(new_parent_node, current_parent)
    else:
        pm.parent(target, new_parent_node)
    return new_parent_node
