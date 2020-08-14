#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/20 11:03
# @Author  : Li XiaoJun
# @Site    :
# @File    : module_rig.py
from imp import reload

from pymel import core as pm
# import maya.mel as mel

from animation import common
from animation import helper
from rig.module import node

reload(common)
reload(helper)
reload(node)

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

        # 头部根节点
        self.head_grp = None
        self.head_config_node = None

        # 当前TabLayout选择状态的选择索引
        self.current_tab_index = 2
        self.text_field_button_grp_width = [110, 100, 100]

        self.show()
        self.initialize()

    def show(self):
        """
        显示主窗口
        :return: window
        """
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
            ann=u"创建头部根骨骼模块",
            c=lambda *args: self.create_head_root_module())

        pm.symbolButton(
            image=eye_icon,
            ann=u"创建眼睛绑定模块",
            c=lambda *args: self.create_eye_module())
        pm.separator(w=2)
        pm.button(
            label="Jaw And Mouth",
            ann=u"创建下巴和舌头、牙齿模块",
            c=lambda *args: self.create_jaw_and_chin_module())
        pm.separator(w=2)
        pm.button(
            label="Nose",
            ann=u"创建鼻子模块",
            c=lambda *args: self.create_nose_module())
        pm.separator(w=2)
        pm.button(
            label="Ears",
            ann=u"创建耳朵模块",
            c=lambda *args: self.create_ears_module())

        pm.tabLayout(
            tool_tab_bar,
            edit=True,
            tabLabel=(
                (face_action_bar, u'组件'),
            ))

        data_form = pm.paneLayout(configuration='vertical2', p=main_layout)
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
        pm.treeView(
            self.tree_view,
            edit=True,
            # pressCommand=[(1, pressTreeCallBack),
            #               (2, pressTreeCallBack),
            #               (3, pressTreeCallBack)],
            # selectCommand=selectTreeCallBack
        )

        data_frame = pm.frameLayout(
            label=u"数据栏", mw=5, mh=5, bgs=True, p=data_form)

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
        """
        初始化窗口的数值
        :return:
        """
        if pm.objExists("head_config"):
            self.init_tree_view()
            self.head_config_node = "head_config"

    def init_tree_view(self):
        """
        初始化
        :return:
        """
        config_list = pm.PyNode("head_config").getChildren()
        for config_node in config_list:
            module_name = pm.PyNode(config_node).attr("module").get()
            module_parent = pm.PyNode(config_node).attr("parentModule").get()
            new_item = [module_name, module_parent]
            print(new_item)
            pm.treeView(self.tree_view, e=True, addItem=new_item)
        return

    def refresh_tree_view(self):
        print(pm.treeView(self.tree_view, q=True, ch=True))

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
            bc=lambda *args: self.create_eye_module(
                side="right",
                text_field=self.right_eye_bone_control))
        self.left_eye_bone_control = pm.textFieldButtonGrp(
            label="Left Eye",
            bl="Set",
            cw3=self.text_field_button_grp_width,
            adj=2,
            bc=lambda *args: self.create_eye_module(
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

    def create_head_root_module(self):
        """
        创建头部根骨骼
        :return: head bone
        """
        if pm.objExists("head_BND") or pm.objExists("head_config"):
            # pm.error(u"场景中已经存在Head_BND，请确认是否已经有绑定")
            user_confirm = pm.confirmDialog(
                title='Confirm',
                message=u"场景中已经存在表情绑定，请确认！",
                button=['Continue', 'Cancel'],
                defaultButton='Continue',
                cancelButton='Cancel',
                dismissString='Cancel')
            if user_confirm == "Continue":
                pass
            elif user_confirm == "Cancel":
                pass
        else:
            self.head_grp = pm.createNode("transform", name="head_GRP").name()
            # 创建配置节点来存储头部绑定的一些配置信息
            if not pm.objExists("head_config"):
                self.head_config_node = common.null_node(name="head_config")
                pm.parent(self.head_config_node, self.head_grp)
            else:
                self.head_config_node = "head_config"

            head = node.DoJointGrp(name="head")
            head.build_mode_3(parent=self.head_grp, have_sub=True)
            head.setting_config_node("parentModule", "")
            pm.parent(head.config_node, self.head_config_node)
            pm.treeView(self.tree_view,
                        e=True, addItem=["head", ""])

            # 创建头部上半部分的根骨骼
            head_top = node.DoJointGrp(name="headTop")
            head_top.build_mode_3(parent=head.bnd_name, offset_value=[0, 2, 2])
            head_top.setting_config_node(attr="parentModule", value=head.name)
            pm.parent(head_top.config_node, self.head_config_node)
            pm.treeView(self.tree_view,
                        e=True, addItem=["headTop", "head"])

            # 创建头部下半部分的根骨骼
            head_bot = node.DoJointGrp(name="headBottom")
            head_bot.build_mode_3(parent=head.bnd_name,
                                  offset_value=[0, 1.5, 2])
            head_bot.setting_config_node(attr="parentModule", value=head.name)
            pm.parent(head_bot.config_node, self.head_config_node)
            pm.treeView(self.tree_view,
                        e=True, addItem=["headBottom", "head"])

        return True

    def create_eye_module(self):
        eye_grp = "eye_GRP"
        head_top = node.DoJointGrp(name="headTop")

        if not pm.objExists(eye_grp):
            eye_grp = pm.createNode("transform", name=eye_grp)
            pm.parent(eye_grp, head_top.bnd_name)
            eye_grp.translate.set([0, 0, 0])
            eye_grp.rotate.set([0, 0, 0])

        side_list = ["left", "right"]
        prefix = ""
        offset_value = [0, 0, 0]
        for side in side_list:
            if side == "left":
                offset_value = [2, 0, 0]
                prefix = "L_"
            elif side == "right":
                offset_value = [-2, 0, 0]
                prefix = "R_"

            eye_bone = node.DoJointGrp(name="%seyeMove" % prefix)
            eye_bone.build_mode_2(parent=eye_grp, offset_value=offset_value)
            eye_bone.setting_config_node(
                attr="parentModule", value=head_top.name)
            pm.parent(eye_bone.config_node, self.head_config_node)
            pm.treeView(self.tree_view,
                        e=True, addItem=["%seyeMove" % prefix, "headTop"])

        return True

    def create_jaw_and_chin_module(self):
        head_bot = node.DoJointGrp(name="headBottom")
        # Jaw
        jaw_bone = node.DoJointGrp(name="jaw")
        jaw_bone.build_mode_3(parent=head_bot.bnd_name,
                              offset_value=[0, -2, 2])
        jaw_bone.setting_config_node(attr="parentModule", value=head_bot.name)
        pm.parent(jaw_bone.config_node, self.head_config_node)
        pm.treeView(self.tree_view,
                    e=True, addItem=["jaw", "headBottom"])
        # chin
        chin_bone = node.DoJointGrp(name="chin")
        chin_bone.build_mode_3(parent=jaw_bone.bnd_name,
                               offset_value=[0, 0, 0])
        chin_bone.setting_config_node(
            attr="parentModule", value=jaw_bone.name)
        pm.parent(chin_bone.config_node, self.head_config_node)
        pm.treeView(self.tree_view,
                    e=True, addItem=["chin", "jaw"])

        # lower teeth
        lower_teeth_bone = node.DoJointGrp(name="teethBot")
        lower_teeth_bone.build_mode_3(parent=jaw_bone.bnd_name,
                                      offset_value=[0, -2, 2])
        lower_teeth_bone.setting_config_node(
            attr="parentModule", value=jaw_bone.name)
        pm.parent(lower_teeth_bone.config_node, self.head_config_node)
        pm.treeView(self.tree_view,
                    e=True, addItem=["teethBot", "jaw"])

        # upper teeth
        upper_teeth_bone = node.DoJointGrp(name="teethTop")
        upper_teeth_bone.build_mode_3(parent=head_bot.bnd_con,
                                      offset_value=[0, 2, 2])
        upper_teeth_bone.setting_config_node(
            attr="parentModule", value=head_bot.name)
        pm.parent(upper_teeth_bone.config_node, self.head_config_node)
        pm.treeView(self.tree_view,
                    e=True, addItem=["teethTop", "headBottom"])

        # tongue
        tongue_segments = 6
        for index in range(1, tongue_segments + 1):
            tongue_bone = node.DoJointGrp(name="tongue_00%s" % index)
            if index == 1:
                tongue_bone.build_mode_3(
                    parent=jaw_bone.bnd_name, offset_value=[0, -2, 2])
                tongue_bone.setting_config_node(
                    attr="parentModule", value=jaw_bone.name)
                pm.parent(tongue_bone.config_node, self.head_config_node)
                pm.treeView(self.tree_view,
                            e=True, addItem=["tongue_00%s" % index, "jaw"])
            else:
                tongue_parent_module = node.DoJointGrp(
                    name="tongue_00%s" % (index - 1))
                tongue_bone.build_mode_3(
                    parent=tongue_parent_module.bnd_name,
                    offset_value=[0, -2, 2])
                tongue_bone.setting_config_node(
                    attr="parentModule", value=tongue_parent_module.name)
                pm.parent(tongue_bone.config_node, self.head_config_node)
                pm.treeView(
                    self.tree_view,
                    e=True,
                    addItem=["tongue_00%s" % index,
                             ("tongue_00%s" % (index - 1))])

        return True

    def create_nose_module(self):
        head_bone = node.DoJointGrp("head")

        nose_grp = ""
        nose_ears_grp = ""
        if not pm.objExists("nose_GRP"):
            nose_grp = pm.createNode("transform", n="nose_GRP")
        if not pm.objExists("noseAndEars_GRP"):
            nose_ears_grp = pm.createNode("transform", n="noseAndEars_GRP")
        pm.parent(nose_grp, nose_ears_grp)
        pm.parent(nose_ears_grp, head_bone.bnd_name)

        # nose 根骨骼
        nose_bone = node.DoJointGrp("nose")
        nose_bone.build_mode_3(parent=nose_grp, offset_value=[0, -2, 2])
        nose_bone.setting_config_node(
            attr="parentModule", value=head_bone.name)
        pm.parent(nose_bone.config_node, self.head_config_node)
        pm.treeView(self.tree_view,
                    e=True, addItem=["nose", "head"])

        # nose tip
        nose_tip_bone = node.DoJointGrp("noseTip")
        nose_tip_bone.build_mode_3(
            parent=nose_bone.bnd_name, offset_value=[0, 2, 2])
        nose_tip_bone.setting_config_node(
            attr="parentModule", value=nose_bone.name)
        pm.parent(nose_tip_bone.config_node, self.head_config_node)
        pm.treeView(self.tree_view,
                    e=True, addItem=["noseTip", "nose"])

        # right nostril
        right_nostril_bone = node.DoJointGrp("R_nostril")
        right_nostril_bone.build_mode_3(
            parent=nose_bone.bnd_name, offset_value=[-2, 0, 0])
        right_nostril_bone.setting_config_node(
            attr="parentModule", value=nose_bone.name)
        pm.parent(right_nostril_bone.config_node, self.head_config_node)
        pm.treeView(self.tree_view,
                    e=True, addItem=["R_nostril", "nose"])

        # left nostril
        left_nostril_bone = node.DoJointGrp("L_nostril")
        left_nostril_bone.build_mode_3(
            parent=nose_bone.bnd_name, offset_value=[2, 0, 0])
        left_nostril_bone.setting_config_node(
            attr="parentModule", value=nose_bone.name)
        pm.parent(left_nostril_bone.config_node, self.head_config_node)
        pm.treeView(self.tree_view,
                    e=True, addItem=["L_nostril", "nose"])

        return True

    def create_ears_module(self):
        # todo 耳朵模块没有实现
        print(u"点击'创建耳朵模块按钮'")
        return


def selectTreeCallBack(*args):
    print('selection : ' + args[0] + ' onoff= ' + str(args[1]))
    return True


def pressTreeCallBack(*args):
    print('press :- str= ' + args[0] + ' onoff= ' + str(args[1]))
