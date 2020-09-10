#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/9/7 9:39
# @Author  : Li XiaoJun
# @Site    : 
# @File    : face_editor.py

import os
import json
from imp import reload

from animation.common import moving_target
from animation.helper import str_to_list, manager_version, zero_locator
from pymel import core as pm
from animation import common
from animation import test_node

reload(common)
reload(test_node)


def get_channel_values(jnt, pre=5):
    """
    获取骨骼在通道里面的值

    列取骨骼在通道栏里面的属性及当前的值，数值小数点后保留5位，
    其中位移属性的值需要缩小100倍，也就是乘以0.01，
    这是为了解决FBX文件在MAYA，U3D这两个软件内比例单位的差异化造成的错误

    :param jnt: 目标骨骼的名称
    :param pre: 小数点后面保留几位
    :return
    """
    jnt_value = [
        round(pm.PyNode(jnt).translateX.get() * 0.01, pre),
        round(pm.PyNode(jnt).translateY.get() * 0.01, pre),
        round(pm.PyNode(jnt).translateZ.get() * 0.01, pre),
        round(pm.PyNode(jnt).rotateX.get(), pre),
        round(pm.PyNode(jnt).rotateY.get(), pre),
        round(pm.PyNode(jnt).rotateZ.get(), pre),
        round(pm.PyNode(jnt).scaleX.get(), pre),
        round(pm.PyNode(jnt).scaleY.get(), pre),
        round(pm.PyNode(jnt).scaleZ.get(), pre),
    ]
    return jnt_value


def build_driven(driver, axis_data, driver_attr):
    joint_name = axis_data["BoneName"]
    translate_dv = pm.PyNode(joint_name).translate.get()
    rotate_dv = pm.PyNode(joint_name).rotate.get()
    scale_dv = pm.PyNode(joint_name).scale.get()

    attr_list = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

    for dv_attr in attr_list:
        pm.PyNode(joint_name).translate.set(translate_dv)
        pm.PyNode(joint_name).rotate.set(rotate_dv)
        pm.PyNode(joint_name).scale.set(scale_dv)
        pm.setDrivenKeyframe(
            "{}.{}".format(joint_name, dv_attr),
            cd="{}.{}".format(driver, driver_attr),
            dv=1)

        pm.setDrivenKeyframe(
            "{}.{}".format(joint_name, dv_attr),
            cd="{}.{}".format(driver, driver_attr),
            dv=0)

        # Max value
        pm.PyNode(joint_name).translate.set([
            axis_data["Max"][0] * 100 + translate_dv[0],
            axis_data["Max"][1] * 100 + translate_dv[1],
            axis_data["Max"][2] * 100 + translate_dv[2]])
        pm.PyNode(joint_name).rotate.set([
            axis_data["Max"][3] + rotate_dv[0],
            axis_data["Max"][4] + rotate_dv[1],
            axis_data["Max"][5] + rotate_dv[2]])
        pm.PyNode(joint_name).scale.set([
            axis_data["Max"][6],
            axis_data["Max"][7],
            axis_data["Max"][8]])
        pm.setDrivenKeyframe(
            "{}.{}".format(joint_name, dv_attr),
            cd="{}.{}".format(driver, driver_attr),
            dv=1)

        # Min value
        pm.PyNode(joint_name).translate.set([
            axis_data["Min"][0] * 100 + translate_dv[0],
            axis_data["Min"][1] * 100 + translate_dv[1],
            axis_data["Min"][2] * 100 + translate_dv[2]])
        pm.PyNode(joint_name).rotate.set([
            axis_data["Min"][3] + rotate_dv[0],
            axis_data["Min"][4] + rotate_dv[1],
            axis_data["Min"][5] + rotate_dv[2]])
        pm.PyNode(joint_name).scale.set([
            axis_data["Min"][6],
            axis_data["Min"][7],
            axis_data["Min"][8]])
        pm.setDrivenKeyframe(
            "{}.{}".format(joint_name, dv_attr),
            cd="{}.{}".format(driver, driver_attr),
            dv=-1)

    pm.setAttr("%s.%s" % (driver, driver_attr), 0)

    return


class FaceEditor(common.Singleton):
    """
    Json数据文件管理工具
    """

    def __init__(self):
        super(FaceEditor, self).__init__()

        self.json_folder = ''

        self.face_data = {}
        self.face = None

        self.pre_build_window()
        self.show()
        self.init_system()

    def show(self):
        """
        显示工具窗口

        :return: window
        """
        if pm.window("faceEditorWnd", ex=True):
            pm.deleteUI("faceEditorWnd")
        pm.window(
            "faceEditorWnd",
            t=u"Face Editor %s" % manager_version,
            mb=True,
            cc=lambda *args: self._closed_window_cmd())

        self.menu_list()

        pm.formLayout("editor_main_layout")
        pm.textFieldButtonGrp(
            "config_file_widget",
            label="Config",
            bl="Setting",
            cw3=[50, 100, 50],
            adj=2,
            p="editor_main_layout",
            bc=lambda *args: self.action_json_folder())

        pm.optionMenuGrp(
            "module_selector_widget",
            label="Module",
            adj=2,
            cw2=[50, 100],
            p="editor_main_layout",
            cc=lambda *args: self.action_change_module())
        if len(self.face_data.keys()) > 0:
            for menu_item in self.face_data.keys():
                pm.menuItem(label=menu_item)

        pm.frameLayout(
            "controller_list_grp", label="Controller List:", w=180, h=180)
        pm.textScrollList(
            "controller_list_widget",
            sc=lambda
                *args: self.action_selected_controller())  # 控制器列表(Controller list)控件
        pm.setParent("..")

        # Controller basic info frame
        pm.frameLayout(
            "controller_info_grp",
            label="Controller Basic info:", bgs=True, mh=6)
        pm.textFieldButtonGrp(
            "controller_name_widget",
            label=u"控制器名",
            cw3=[60, 200, 140],
            bl=u"更新")
        pm.textFieldButtonGrp(
            "controller_group_widget",
            label=u"控制器组",
            cw3=[60, 200, 140],
            bl=u"更新")
        pm.textFieldButtonGrp(
            "controller_bone_widget",
            label=u"挂点位置",
            cw3=[60, 200, 140],
            bl=u"更新")
        pm.floatFieldGrp(
            "controller_offset_widget",
            numberOfFields=3,
            pre=3,
            label=u'挂点偏移',
            cw4=[60, 50, 50, 50])
        pm.checkBoxGrp(
            "axis_group_widget",
            label=u"Axis:",
            labelArray3=['X', 'Y', 'Z'],
            cw4=[60, 50, 50, 50],
            numberOfCheckBoxes=3)
        pm.setParent("..")

        separator1 = pm.separator(style="in", h=10)

        pm.tabLayout("axis_setting_grp")

        axis_x_tab = self.axis_attr_tab(attr="x")
        axis_y_tab = self.axis_attr_tab(attr="y")
        # axis_y_tab = pm.frameLayout(
        #     p="axis_setting_grp", label="YAxis", lv=False)
        # axis_y_form = pm.formLayout(p=axis_y_tab)
        # self.axis_y_joint_list = pm.textScrollList(
        #     p=axis_y_form,
        #     w=174,
        #     sc=lambda *args: self.action_axis_list(
        #         widget=self.axis_y_joint_list))
        # self.axis_y_test_widget = pm.floatSliderGrp(
        #     enable=False,
        #     label=u"滑竿测试",
        #     field=True,
        #     minValue=-1.0,
        #     maxValue=1.0,
        #     fieldMinValue=-1.0,
        #     fieldMaxValue=1.0,
        #     pre=3,
        #     adj=3,
        #     value=0,
        #     cw3=[60, 60, 100])
        # self.axis_y_max_range_widget = pm.frameLayout(
        #     label="Max", p=axis_y_form, cll=True, cl=False, mw=5, mh=5,
        #     bgs=True)
        # self.axis_y_max_translate_field = pm.floatFieldGrp(
        #     label="Translate", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_y_max_range_widget)
        # self.axis_y_max_rotate_field = pm.floatFieldGrp(
        #     label="Rotate", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_y_max_range_widget)
        # self.axis_y_max_scale_field = pm.floatFieldGrp(
        #     label="Scale", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_y_max_range_widget)
        # pm.button(label="Update", p=self.axis_y_max_range_widget)
        #
        # self.axis_y_min_range_widget = pm.frameLayout(
        #     label="Min", p=axis_y_form, cll=True, cl=False, mw=5, mh=5,
        #     bgs=True)
        # self.axis_y_min_translate_field = pm.floatFieldGrp(
        #     label="Translate", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_y_min_range_widget)
        # self.axis_y_min_rotate_field = pm.floatFieldGrp(
        #     label="Rotate", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_y_min_range_widget)
        # self.axis_y_min_scale_field = pm.floatFieldGrp(
        #     label="Scale", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_y_min_range_widget)
        # pm.button(label="Update", p=self.axis_y_min_range_widget)
        # pm.formLayout(
        #     axis_y_form, e=True,
        #     attachForm=[
        #         (self.axis_y_joint_list, 'left', 2),
        #         (self.axis_y_joint_list, 'top', 5),
        #         (self.axis_y_joint_list, 'bottom', 5),
        #         (self.axis_y_test_widget, 'top', 5),
        #         (self.axis_y_test_widget, 'right', 7),
        #         (self.axis_y_max_range_widget, 'right', 2),
        #         (self.axis_y_min_range_widget, 'right', 2),
        #     ],
        #     attachControl=[
        #         (self.axis_y_test_widget, 'left', 5,
        #          self.axis_y_joint_list),
        #         (self.axis_y_max_range_widget, 'left', 5,
        #          self.axis_y_joint_list),
        #         (self.axis_y_max_range_widget, 'top', 5,
        #          self.axis_y_test_widget),
        #         (self.axis_y_min_range_widget, 'left', 5,
        #          self.axis_y_joint_list),
        #         (self.axis_y_min_range_widget, 'top', 5,
        #          self.axis_y_max_range_widget),
        #     ])
        axis_z_tab = self.axis_attr_tab(attr="z")
        # axis_z_tab = pm.frameLayout(
        #     p="axis_setting_grp", label="ZAxis", lv=False)
        # axis_z_form = pm.formLayout(p=axis_z_tab)
        # self.axis_z_joint_list = pm.textScrollList(
        #     p=axis_z_form,
        #     w=174,
        #     sc=lambda *args: self.action_axis_list(
        #         widget=self.axis_z_joint_list))
        # self.axis_z_test_widget = pm.floatSliderGrp(
        #     enable=False,
        #     label=u"滑竿测试",
        #     field=True,
        #     minValue=-1.0,
        #     maxValue=1.0,
        #     fieldMinValue=-1.0,
        #     fieldMaxValue=1.0,
        #     pre=3,
        #     adj=3,
        #     value=0,
        #     cw3=[60, 60, 100])
        # self.axis_z_max_range_widget = pm.frameLayout(
        #     label="Max", p=axis_z_form, cll=True, cl=False, mw=5, mh=5,
        #     bgs=True)
        # self.axis_z_max_translate_field = pm.floatFieldGrp(
        #     label="Translate", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_z_max_range_widget)
        # self.axis_z_max_rotate_field = pm.floatFieldGrp(
        #     label="Rotate", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_z_max_range_widget)
        # self.axis_z_max_scale_field = pm.floatFieldGrp(
        #     label="Scale", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_z_max_range_widget)
        # pm.button(label="Update", p=self.axis_z_max_range_widget)
        #
        # self.axis_z_min_range_widget = pm.frameLayout(
        #     label="Min", p=axis_z_form, cll=True, cl=False, mw=5, mh=5,
        #     bgs=True)
        # self.axis_z_min_translate_field = pm.floatFieldGrp(
        #     label="Translate", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_z_min_range_widget)
        # self.axis_z_min_rotate_field = pm.floatFieldGrp(
        #     label="Rotate", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_z_min_range_widget)
        # self.axis_z_min_scale_field = pm.floatFieldGrp(
        #     label="Scale", nf=3, cw4=[50, 80, 80, 80],
        #     numberOfFields=3,
        #     pre=3,
        #     p=self.axis_z_min_range_widget)
        # pm.button(label="Update", p=self.axis_z_min_range_widget)
        # pm.formLayout(
        #     axis_z_form, e=True,
        #     attachForm=[
        #         (self.axis_z_joint_list, 'left', 2),
        #         (self.axis_z_joint_list, 'top', 5),
        #         (self.axis_z_joint_list, 'bottom', 5),
        #         (self.axis_z_test_widget, 'right', 7),
        #         (self.axis_z_test_widget, 'top', 5),
        #         (self.axis_z_max_range_widget, 'right', 2),
        #         (self.axis_z_min_range_widget, 'right', 2),
        #     ],
        #     attachControl=[
        #         (self.axis_z_test_widget, 'left', 5,
        #          self.axis_z_joint_list),
        #         (self.axis_z_max_range_widget, 'top', 5,
        #          self.axis_z_test_widget),
        #         (self.axis_z_max_range_widget, 'left', 5,
        #          self.axis_z_joint_list),
        #         (self.axis_z_min_range_widget, 'left', 5,
        #          self.axis_z_joint_list),
        #         (self.axis_z_min_range_widget, 'top', 5,
        #          self.axis_z_max_range_widget),
        #     ])

        pm.tabLayout(
            "axis_setting_grp", e=True,
            tl=[(axis_x_tab, 'XAxis'),
                (axis_y_tab, 'YAxis'),
                (axis_z_tab, 'ZAxis')])
        pm.setParent("..")

        pm.formLayout(
            "editor_main_layout", edit=True,
            attachForm=[
                ("config_file_widget", 'left', 2),
                ("config_file_widget", 'right', 2),
                ("config_file_widget", 'top', 5),
                ("module_selector_widget", 'left', 2),
                ("module_selector_widget", 'right', 2),
                ("controller_list_grp", 'left', 2),
                ("controller_info_grp", 'right', 2),
                (separator1, 'left', 2),
                (separator1, 'right', 2),
                ("axis_setting_grp", 'left', 2),
                ("axis_setting_grp", 'right', 2),
                ("axis_setting_grp", 'bottom', 5),
            ],
            attachControl=[
                ("module_selector_widget", 'top', 5,
                 "config_file_widget"),
                ("controller_list_grp", 'top', 5,
                 "module_selector_widget"),
                ("controller_info_grp", 'top', 5,
                 "module_selector_widget"),
                ("controller_info_grp", 'left', 2,
                 "controller_list_grp"),
                (separator1, 'top', 5, "controller_list_grp"),
                ("axis_setting_grp", 'top', 5, separator1),
            ])

        pm.showWindow("faceEditorWnd")

    def axis_attr_tab(self, attr="x"):
        label = None
        if attr == "x":
            label = "X"
        if attr == "y":
            label = "Y"
        if attr == "z":
            label = "Z"

        layout = pm.frameLayout(
            "axis_{}_tab".format(attr),
            p="axis_setting_grp",
            label="{}Axis".format(label),
            lv=False)
        pm.formLayout(
            "axis_{}_form".format(attr),
            p="axis_{}_tab".format(attr))
        pm.textScrollList(
            "axis_{}_joint_list".format(attr),
            p="axis_{}_form".format(attr),
            w=174,
            sc=lambda *args: self.action_axis_list(
                widget="axis_{}_joint_list".format(attr)))
        pm.popupMenu()
        pm.menuItem(
            label=u"添加影响骨骼",
            c=lambda *args: self.axis_list_signal(attr=attr, method="post"))
        pm.menuItem(divider=True)
        pm.menuItem(
            label=u"移除选择骨骼",
            c=lambda *args: self.axis_list_signal(attr=attr, method="delete"))
        pm.floatSliderGrp(
            "axis_{}_test_widget".format(attr),
            enable=False,
            label=u"滑竿测试",
            field=True,
            minValue=-1.0,
            maxValue=1.0,
            fieldMinValue=-1.0,
            fieldMaxValue=1.0,
            pre=3,
            adj=3,
            value=0,
            cw3=[60, 60, 100])
        pm.frameLayout(
            "axis_{}_max_range_widget".format(attr),
            label="Max",
            p="axis_{}_form".format(attr),
            cll=True, cl=False, mw=5, mh=5,
            bgs=True)
        pm.floatFieldGrp(
            "axis_{}_max_translate_field".format(attr),
            label="Translate", nf=3, cw4=[50, 80, 80, 80],
            numberOfFields=3,
            pre=3,
            p="axis_{}_max_range_widget".format(attr))
        pm.floatFieldGrp(
            "axis_{}_max_rotate_field".format(attr),
            label="Rotate", nf=3, cw4=[50, 80, 80, 80],
            numberOfFields=3,
            pre=3,
            p="axis_{}_max_range_widget".format(attr))
        pm.floatFieldGrp(
            "axis_{}_max_scale_field".format(attr),
            label="Scale", nf=3, cw4=[50, 80, 80, 80],
            numberOfFields=3,
            pre=3,
            p="axis_{}_max_range_widget".format(attr))
        pm.button(
            "axis_{}_max_update_btn".format(attr),
            label="Update",
            p="axis_{}_max_range_widget".format(attr),
            c=lambda *args: self.axis_list_signal(
                attr=attr, method="update", update="Max"))
        pm.frameLayout(
            "axis_{}_min_range_widget".format(attr),
            label="Min",
            p="axis_{}_form".format(attr),
            cll=True, cl=False, mw=5, mh=5,
            bgs=True)
        pm.floatFieldGrp(
            "axis_{}_min_translate_field".format(attr),
            label="Translate", nf=3, cw4=[50, 80, 80, 80],
            numberOfFields=3,
            pre=3,
            p="axis_{}_min_range_widget".format(attr))
        pm.floatFieldGrp(
            "axis_{}_min_rotate_field".format(attr),
            label="Rotate", nf=3, cw4=[50, 80, 80, 80],
            numberOfFields=3,
            pre=3,
            p="axis_{}_min_range_widget".format(attr))
        pm.floatFieldGrp(
            "axis_{}_min_scale_field".format(attr),
            label="Scale", nf=3, cw4=[50, 80, 80, 80],
            numberOfFields=3,
            pre=3,
            p="axis_{}_min_range_widget".format(attr))
        pm.button(
            "axis_{}_min_update_btn".format(attr),
            label="Update",
            p="axis_{}_min_range_widget".format(attr),
            c=lambda *args: self.axis_list_signal(
                attr=attr, method="update", update="Min"))
        pm.formLayout(
            "axis_{}_form".format(attr),
            e=True,
            attachForm=[
                ("axis_{}_joint_list".format(attr), 'left', 2),
                ("axis_{}_joint_list".format(attr), 'top', 5),
                ("axis_{}_joint_list".format(attr), 'bottom', 5),
                ("axis_{}_test_widget".format(attr), 'top', 5),
                ("axis_{}_test_widget".format(attr), 'right', 7),
                ("axis_{}_max_range_widget".format(attr), 'right', 2),
                ("axis_{}_min_range_widget".format(attr), 'right', 2),
            ],
            attachControl=[
                ("axis_{}_test_widget".format(attr), 'left', 5,
                 "axis_{}_joint_list".format(attr)),
                ("axis_{}_max_range_widget".format(attr), 'top', 5,
                 "axis_{}_test_widget".format(attr)),
                ("axis_{}_max_range_widget".format(attr), 'left', 5,
                 "axis_{}_joint_list".format(attr)),
                ("axis_{}_min_range_widget".format(attr), 'left', 5,
                 "axis_{}_joint_list".format(attr)),
                ("axis_{}_min_range_widget".format(attr), 'top', 5,
                 "axis_{}_max_range_widget".format(attr)),
            ])
        return layout

    def menu_list(self):
        """
        工具菜单栏

        :return:
        """
        pm.menu(label=u"设置", tearOff=False)
        pm.menuItem(
            label=u"设置Json存放目录",
            c=lambda *args: self.setting_json_folder())
        pm.menuItem(
            label=u"调试模式", cb=False)

        pm.menu(label=u"模块", tearOff=False)
        pm.menuItem(
            label=u"创建新模块",
            c=lambda *args: self.new_module())
        pm.menuItem(
            label=u"创建控制器",
            c=lambda *args: self.new_controller())

        pm.menu(label=u"Test", tearOff=False)
        pm.menuItem(
            label=u"创建测试用控制器",
            c=lambda *args: self.new_test_controller())

        return

    def init_system(self):
        """
        初始化，将配置信息填充到面板上

        :return:
        """
        pm.textFieldButtonGrp(
            "config_file_widget", e=True, text=self.json_folder)

        # 填充controller list
        current_module = pm.optionMenuGrp(
            "module_selector_widget", q=True, value=True)
        for controller in self.face_data[current_module]:
            pm.textScrollList("controller_list_widget", e=True,
                              a=controller["controllerName"])

        pm.textScrollList("controller_list_widget", e=True, sii=1)

        controller_index = int(pm.textScrollList(
            "controller_list_widget", q=True, sii=True)[0])
        controller_data = self.face_data[current_module][controller_index - 1]
        self.update_controller_widget_data(data=controller_data)

    def pre_build_window(self):
        if pm.optionVar(q='faceEditorConfig'):
            self.json_folder = pm.optionVar(q='faceEditorConfig')
            self.face_data = common.read_json(self.json_folder)
            # self.face = FaceData(common.read_json(self.json_folder))

    def _closed_window_cmd(self):
        pm.optionVar(sv=('faceEditorConfig', self.json_folder))
        # pm.optionVar(sv=('arFileLocation', self.ar_file_location))
        # self.current_tab_index = pm.tabLayout(
        #     self.main_tab, q=True, sti=True)
        # print(self.current_tab_index)
        # pm.optionVar(
        #     sv=('faceEditorMainTabIndex', self.current_tab_index))

        # pm.optionVar(
        #     sv=('jsonManagerDiscardBrowFilePath', self.brow_file_folder))
        # pm.optionVar(
        #     sv=('jsonManagerDiscardEyeFilePath', self.eye_file_folder))
        # pm.optionVar(
        #     sv=('jsonManagerDiscardNoseFilePath', self.nose_file_folder))
        # pm.optionVar(
        #     sv=('jsonManagerDiscardMouthFilePath', self.mouth_file_folder))
        # pm.optionVar(
        #     sv=('jsonManagerDiscardFaceFilePath', self.face_file_folder))

    def setting_json_folder(self):
        json_folder = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=5, okc=u"应用")[0]

        if json_folder:
            self.json_folder = json_folder
            if not (os.path.exists(self.json_folder)):
                with open(self.json_folder, "w") as f:
                    data = {}
                    json.dump(data, f, indent=2)
        else:
            pass

        return json_folder

    def action_json_folder(self):
        json_location = self.setting_json_folder()
        pm.textFieldButtonGrp(
            "config_file_widget", e=True, text=json_location)
        return

    # def generate_custom_data(self):
    #     dict_data = {}
    #     self.dict_data = list()
    #
    #     for index in range(0, pm.scrollLayout(
    #             "controllerListLayout", q=True, nch=True)):
    #         dict_data = {}
    #         axis_control = {}
    #
    #         dict_data["controllerName"] = pm.textFieldButtonGrp(
    #             "controllerNameWidget%s" % index, q=True, text=True)
    #         dict_data["ControllerGroupName"] = pm.textFieldButtonGrp(
    #             "controllerGrpNameWidget%s" % index, q=True, text=True)
    #         dict_data["ControllerBoneName"] = pm.textFieldButtonGrp(
    #             "controllerBoneNameWidget%s" % index, q=True, text=True)
    #         dict_data["ControllerPositionOffset"] = pm.floatFieldGrp(
    #             "controllerBoneOffsetWidget%s" % index, q=True, value=True)
    #
    #         axis_control["XAxis"] = pm.textFieldGrp(
    #             "controller%sAxisX" % index, q=True, text=True)
    #         axis_control["YAxis"] = pm.textFieldGrp(
    #             "controller%sAxisY" % index, q=True, text=True)
    #         axis_control["ZAxis"] = pm.textFieldGrp(
    #             "controller%sAxisZ" % index, q=True, text=True)
    #
    #         dict_data["AxisControl"] = axis_control
    #
    #         self.dict_data.append(dict_data)

    # def save_custom_data(self):
    #     """
    #     保存自定义捏脸数据
    #
    #     :return: None
    #     """
    #     menu_item_selected = pm.optionMenuGrp(
    #         "faceModuleOptionsWidget", q=True, value=True)
    #
    #     self.generate_custom_data()
    #     control_file_path = "%s/%s/%sController.json" % (
    #         self.json_folder, menu_item_selected, menu_item_selected)
    #
    #     controller_data = {}
    #     controller_data["%sController" % menu_item_selected] = self.dict_data
    #     with open(control_file_path, "w") as f:
    #         json.dump(controller_data, f, indent=4)
    #
    #     self.generate_custom_detail_data()
    #     detail_file_path = "%s/%s/%sControlGroup.json" % (
    #         self.json_folder, menu_item_selected, menu_item_selected)
    #     with open(detail_file_path, "w") as f:
    #         json.dump(self.detail_data, f, indent=4)
    #
    #     print(u"保存成功")
    #
    #     return

    def new_module(self):
        """
        模块创建引导窗口
        :return:
        """
        if pm.window("moduleBuilderWnd", ex=True):
            pm.deleteUI("moduleBuilderWnd")

        pm.window("moduleBuilderWnd", title="Module Builder")
        main_layout = pm.columnLayout(adj=1)
        base_frame = pm.frameLayout(
            label="Module Base", p=main_layout, mw=5, mh=5,
            cll=False, cl=True)

        module_selector = pm.optionMenuGrp(
            label="Module:", p=base_frame, cw2=[48, 150])
        pm.menuItem(label="eye")
        pm.menuItem(label="brow")
        pm.menuItem(label="nose")
        pm.menuItem(label="mouth")
        pm.menuItem(label="ear")
        pm.menuItem(label="feature")

        pm.button(
            label="Build Module",
            p=base_frame,
            c=lambda *args: self.build_module(
                module=pm.optionMenuGrp(module_selector, q=True, value=True)))

        pm.showWindow("moduleBuilderWnd")

    def build_module(self, module):
        face_data = common.read_json(self.json_folder)
        module_list = face_data.keys()

        if module == "eye":
            new_module = "{}Controller".format(module)
            if new_module not in module_list:
                self.build_eye_controller()
        if module == "mouth":
            new_module = "{}Controller".format(module)
            if new_module not in module_list:
                self.build_mouth_controller()

        print(module_list)

        if pm.window("moduleBuilderWnd", ex=True):
            pm.deleteUI("moduleBuilderWnd")

    def build_eye_controller(self, data=[]):
        face_data = common.read_json(self.json_folder)
        print(face_data)

        face_data["eyeController"] = data
        print(face_data)
        with open(self.json_folder, "w") as f:
            json.dump(face_data, f, indent=4)

    def build_mouth_controller(self, data=[]):
        face_data = common.read_json(self.json_folder)
        print(face_data)

        face_data["mouthController"] = data
        print(face_data)
        with open(self.json_folder, "w") as f:
            json.dump(face_data, f, indent=4)

    def new_controller(self):
        if pm.window("controllerBuilderWnd", ex=True):
            pm.deleteUI("controllerBuilderWnd")

        pm.window("controllerBuilderWnd", title="Module Builder")
        main_layout = pm.columnLayout(adj=1)
        module_parent = pm.textFieldGrp(label="Module")

        # module_selector = pm.optionMenuGrp(
        #     label="Module:", p=base_frame, cw2=[48, 150])
        # pm.menuItem(label="eye")
        # pm.menuItem(label="brow")
        # pm.menuItem(label="nose")
        # pm.menuItem(label="mouth")
        # pm.menuItem(label="ear")
        # pm.menuItem(label="feature")
        #
        # pm.button(
        #     label="Build Module",
        #     p=base_frame,
        #     c=lambda *args: self.build_module(
        #         module=pm.optionMenuGrp(module_selector, q=True, value=True)))

        pm.showWindow("controllerBuilderWnd")

        current_tab = pm.tabLayout("module_tabs", q=True, st=True)
        pm.textFieldGrp(module_parent, e=True, text=current_tab)

    def clean_controller_widget_data(self, module):
        """
        清空控制器面板部件内的数据

        :param module:
        :return:
        """
        # Controller Basic info frame
        pm.textFieldButtonGrp("controller_name_widget", e=True, text="")
        pm.textFieldButtonGrp("controller_group_widget", e=True, text="")
        pm.textFieldButtonGrp("controller_bone_widget", e=True, text="")
        pm.floatFieldGrp("controller_offset_widget", e=True,
                         value=[0, 0, 0, 0])
        pm.checkBoxGrp("axis_group_widget", e=True, v1=False, v2=False,
                       v3=False)

        # 清除Axis面板部件内的数据
        pm.textScrollList("axis_x_joint_list", e=True, ra=True)
        pm.textScrollList("axis_y_joint_list", e=True, ra=True)
        pm.textScrollList("axis_z_joint_list", e=True, ra=True)

        # 清除Axis面部骨骼运动范围的数据
        self.clean_axis_widget("x")
        self.clean_axis_widget("y")
        self.clean_axis_widget("z")

        return

    def clean_axis_widget(self, attr):
        pm.floatSliderGrp(
            "axis_{}_test_widget".format(attr),
            e=True, en=False)
        pm.floatFieldGrp(
            "axis_{}_max_translate_field".format(attr),
            e=True, v1=0, v2=0, v3=0)
        pm.floatFieldGrp(
            "axis_{}_max_rotate_field".format(attr),
            e=True, v1=0, v2=0, v3=0)
        pm.floatFieldGrp(
            "axis_{}_max_scale_field".format(attr),
            e=True, v1=1, v2=1, v3=1)
        pm.floatFieldGrp(
            "axis_{}_min_translate_field".format(attr),
            e=True, v1=0, v2=0, v3=0)
        pm.floatFieldGrp(
            "axis_{}_min_rotate_field".format(attr),
            e=True, v1=0, v2=0, v3=0)
        pm.floatFieldGrp(
            "axis_{}_min_scale_field".format(attr),
            e=True, v1=1, v2=1, v3=1)
        return

    def update_controller_widget_data(self, data):
        """
        为控制器面板部件填充数据

        :param data: 单个控制器的字典类型数据
        :return:
        """
        pm.textFieldButtonGrp(
            "controller_name_widget",
            e=True, text=data["controllerName"])
        pm.textFieldButtonGrp(
            "controller_group_widget",
            e=True, text=data["ControllerGroupName"])
        pm.textFieldButtonGrp(
            "controller_bone_widget",
            e=True, text=data["ControllerBoneName"])
        pm.floatFieldGrp(
            "controller_offset_widget",
            e=True,
            value=[
                data["ControllerPositionOffset"][0],
                data["ControllerPositionOffset"][1],
                data["ControllerPositionOffset"][2], 0])

        if (data["AxisControl"]["XAxis"]["GroupName"]) == "":
            pm.checkBoxGrp(
                "axis_group_widget", e=True, v1=False)
        else:
            pm.checkBoxGrp(
                "axis_group_widget", e=True, v1=True)

        if (data["AxisControl"]["YAxis"]["GroupName"]) == "":
            pm.checkBoxGrp(
                "axis_group_widget", e=True, v2=False)
        else:
            pm.checkBoxGrp(
                "axis_group_widget", e=True, v2=True)

        if (data["AxisControl"]["ZAxis"]["GroupName"]) == "":
            pm.checkBoxGrp(
                "axis_group_widget", e=True, v3=False)
        else:
            pm.checkBoxGrp(
                "axis_group_widget", e=True, v3=True)

        # 为Axis部分填充数据
        axis_x_joints_grp = data["AxisControl"]["XAxis"]
        for axis_x_joint in axis_x_joints_grp["BoneRange"]:
            pm.textScrollList(
                "axis_x_joint_list", e=True, a=axis_x_joint["BoneName"])
        if len(axis_x_joints_grp["BoneRange"]) > 0:
            pm.textScrollList("axis_x_joint_list", e=True, sii=1)

        axis_y_joints_grp = data["AxisControl"]["YAxis"]
        for axis_y_joint in axis_y_joints_grp["BoneRange"]:
            pm.textScrollList(
                "axis_y_joint_list", e=True, a=axis_y_joint["BoneName"])
        if len(axis_y_joints_grp["BoneRange"]) > 0:
            pm.textScrollList("axis_y_joint_list", e=True, sii=1)

        axis_z_joints_grp = data["AxisControl"]["ZAxis"]
        for axis_z_joint in axis_z_joints_grp["BoneRange"]:
            pm.textScrollList(
                "axis_z_joint_list", e=True, a=axis_z_joint["BoneName"])
        if len(axis_z_joints_grp["BoneRange"]) > 0:
            pm.textScrollList("axis_z_joint_list", e=True, sii=1)

        # 为XAxis骨骼的控制范围填充数据
        self.update_axis_widget("x", data)
        # 为YAxis骨骼的控制范围填充数据
        self.update_axis_widget("y", data)
        # 为ZAxis骨骼的控制范围填充数据
        self.update_axis_widget("z", data)

        return

    def update_axis_widget(self, attr, data):
        label = None
        if attr == "x":
            label = "X"
        if attr == "y":
            label = "Y"
        if attr == "z":
            label = "Z"

        if pm.textScrollList(
                "axis_{}_joint_list".format(attr), q=True, ni=True) > 0:
            axis_index = int(pm.textScrollList(
                "axis_{}_joint_list".format(attr), q=True, sii=True)[0])
            axis_attr_data = data[
                "AxisControl"]["{}Axis".format(label)]["BoneRange"][
                axis_index - 1]
            axis_max_value = axis_attr_data["Max"]
            # print("axis_a_max: {}".format(axis_a_max))
            pm.floatFieldGrp(
                "axis_{}_max_translate_field".format(attr),
                e=True,
                v1=axis_max_value[0], v2=axis_max_value[1],
                v3=axis_max_value[2])
            pm.floatFieldGrp(
                "axis_{}_max_rotate_field".format(attr),
                e=True,
                v1=axis_max_value[3], v2=axis_max_value[4],
                v3=axis_max_value[5])
            pm.floatFieldGrp(
                "axis_{}_max_scale_field".format(attr),
                e=True,
                v1=axis_max_value[6], v2=axis_max_value[7],
                v3=axis_max_value[8])

            axis_min_value = axis_attr_data["Min"]
            pm.floatFieldGrp(
                "axis_{}_min_translate_field".format(attr),
                e=True,
                v1=axis_min_value[0], v2=axis_min_value[1],
                v3=axis_min_value[2])
            pm.floatFieldGrp(
                "axis_{}_min_rotate_field".format(attr),
                e=True,
                v1=axis_min_value[3], v2=axis_min_value[4],
                v3=axis_min_value[5])
            pm.floatFieldGrp(
                "axis_{}_min_scale_field".format(attr),
                e=True,
                v1=axis_min_value[6], v2=axis_min_value[7],
                v3=axis_min_value[8])

            if pm.objExists(data["controllerName"]):
                pm.floatSliderGrp(
                    "axis_{}_test_widget".format(attr), e=True, en=True)
                pm.connectControl(
                    "axis_{}_test_widget".format(attr),
                    pm.PyNode(data["controllerName"]).attr(
                        "slider{}".format(label)))
        return

    def action_change_module(self):
        """
        切换模块时调用的方法

        :return:
        """
        selected_module = pm.optionMenuGrp(
            "module_selector_widget", q=True, value=True)
        print(selected_module)

    def action_selected_controller(self):
        """
        controller list控件里面选择controller时调用的函数

        :return:
        """
        current_module = pm.optionMenuGrp(
            "module_selector_widget", q=True, value=True)

        selected_index = int(pm.textScrollList(
            "controller_list_widget", q=True, sii=True)[0])
        # print(selected_index)

        # 清除当前面板上面的数据
        self.clean_controller_widget_data(module=current_module)

        # 填充数据
        controller_data = self.face_data[current_module][selected_index - 1]
        # print(controller_data)
        self.update_controller_widget_data(data=controller_data)

    def new_test_controller(self):
        """
        创建测试用控制器

        """
        if not pm.objExists("TestGeoGrp"):
            pm.createNode("transform", name="TestGeoGrp")

        selected_controller = pm.textScrollList(
            "controller_list_widget", q=True, si=True)[0]
        print(selected_controller)

        if pm.objExists(selected_controller):
            pm.error("The {} was exists in scene".format(selected_controller))
        else:
            test_controller = pm.polySphere(
                r=0.5, sx=20, sy=20, ax=[0, 1, 0], cuv=2, ch=1,
                name=selected_controller)[0]
            test_grp = pm.createNode("transform",
                                     name="{}Grp".format(selected_controller))
            pm.parent(test_controller, test_grp)
            pm.parent(test_grp, "TestGeoGrp")

            controller_bone_name = pm.textFieldButtonGrp(
                "controller_bone_widget", q=True, text=True)
            pm.parentConstraint(controller_bone_name, test_grp, mo=False)

            controller_offset = pm.floatFieldGrp(
                "controller_offset_widget", q=True, value=True)

            common.lock_and_hide_attr(
                test_controller, translate=False, vis=True)
            test_controller.translate.set([
                controller_offset[0] * 100,
                controller_offset[1] * 100,
                controller_offset[2] * 100])

            current_module = pm.optionMenuGrp(
                "module_selector_widget", q=True, value=True)
            current_controller = int(pm.textScrollList(
                "controller_list_widget", q=True, sii=True)[0])
            axis_data = self.face_data[current_module][
                current_controller - 1]["AxisControl"]
            # 为测试控制器添加测试属性
            if pm.checkBoxGrp("axis_group_widget", q=True, v1=True):
                pm.addAttr(test_controller,
                           ln="sliderX", at="double",
                           min=-1, max=1,
                           dv=0)
                pm.setAttr("{}.sliderX".format(test_controller), e=True,
                           keyable=True)
                driver_data_list = axis_data["XAxis"]["BoneRange"]
                for driver_data in driver_data_list:
                    build_driven(
                        driver=test_controller,
                        axis_data=driver_data,
                        driver_attr="sliderX")
                pm.floatSliderGrp("axis_x_test_widget", e=True, en=True)
                pm.connectControl(
                    "axis_x_test_widget",
                    test_controller.attr("sliderX"))
            if pm.checkBoxGrp("axis_group_widget", q=True, v2=True):
                pm.addAttr(test_controller,
                           ln="sliderY", at="double",
                           min=-1, max=1,
                           dv=0)
                pm.setAttr("{}.sliderY".format(test_controller), e=True,
                           keyable=True)
                driver_data_list = axis_data["YAxis"]["BoneRange"]
                for driver_data in driver_data_list:
                    build_driven(
                        driver=test_controller,
                        axis_data=driver_data,
                        driver_attr="sliderY")
                pm.floatSliderGrp("axis_y_test_widget", e=True, en=True)
                pm.connectControl(
                    "axis_y_test_widget",
                    test_controller.attr("sliderY"))
            if pm.checkBoxGrp("axis_group_widget", q=True, v3=True):
                pm.addAttr(test_controller,
                           ln="sliderZ", at="double",
                           min=-1, max=1,
                           dv=0)
                pm.setAttr("{}.sliderZ".format(test_controller), e=True,
                           keyable=True)
                driver_data_list = axis_data["ZAxis"]["BoneRange"]
                for driver_data in driver_data_list:
                    build_driven(
                        driver=test_controller,
                        axis_data=driver_data,
                        driver_attr="sliderZ")
                pm.floatSliderGrp("axis_z_test_widget", e=True, en=True)
                pm.connectControl(
                    "axis_z_test_widget",
                    test_controller.attr("sliderZ"))

            print(controller_offset)

        return

    def action_axis_list(self, widget):
        current_module = pm.optionMenuGrp(
            "module_selector_widget", q=True, value=True)
        controller_index = int(pm.textScrollList(
            "controller_list_widget", q=True, sii=True)[0])
        controller_data = self.face_data[current_module][controller_index - 1]

        current_axis_selected = pm.textScrollList(widget, q=True, si=True)
        pm.select(current_axis_selected[0])
        # print(current_axis_selected)
        axis_tab_list = pm.tabLayout("axis_setting_grp", q=True, tl=True)
        axis_tab_index = pm.tabLayout("axis_setting_grp", q=True, sti=True)
        tab_label = axis_tab_list[axis_tab_index - 1]

        if tab_label == "XAxis":
            self.update_axis_widget(attr="x", data=controller_data)
        if tab_label == "YAxis":
            self.update_axis_widget(attr="y", data=controller_data)
        if tab_label == "ZAxis":
            self.update_axis_widget(attr="z", data=controller_data)

    def axis_list_signal(self, attr="", method="", update=""):
        """
        删除XAxis中的骨骼

        :return:
        """
        label = ""
        if attr == "x":
            label = "X"
        if attr == "y":
            label = "Y"
        if attr == "z":
            label = "Z"

        current_module = pm.optionMenuGrp(
            "module_selector_widget", q=True, value=True)
        controller_index = int(pm.textScrollList(
            "controller_list_widget", q=True, sii=True)[0])

        axis_tab_list = pm.tabLayout("axis_setting_grp", q=True, tl=True)
        axis_tab_index = pm.tabLayout("axis_setting_grp", q=True, sti=True)
        axis_tab_label = axis_tab_list[axis_tab_index - 1]
        # print("axis_tab_label:{}".format(axis_tab_label))

        if method == "delete":
            current_selected = int(pm.textScrollList(
                "axis_{}_joint_list".format(attr),
                q=True, sii=True)[0])
            # print("current_selected:{}".format(current_selected))
            # controller_data = self.face_data[
            #     current_module][controller_index - 1]["AxisControl"][
            #     axis_tab_label]["BoneRange"][current_selected-1]
            # print("controller_data:{}".format(controller_data))
            self.face_data[current_module][controller_index - 1][
                "AxisControl"][axis_tab_label]["BoneRange"].pop(
                current_selected - 1)
            pm.textScrollList("axis_{}_joint_list".format(attr), e=True, rii=1)
        if method == "post":
            new_jnt = pm.ls(sl=True)[0]
            new_jnt_default_value = get_channel_values(new_jnt.name())
            new_jnt_data = {
                "BoneName": new_jnt.name(),
                "Max": [0, 0, 0, 0, 0, 0, 1, 1, 1],
                "Min": [0, 0, 0, 0, 0, 0, 1, 1, 1],
                "def": new_jnt_default_value,
            }
            self.face_data[current_module][controller_index - 1][
                "AxisControl"][axis_tab_label]["BoneRange"].append(
                new_jnt_data)
            pm.textScrollList(
                "axis_{}_joint_list".format(attr), e=True, a=new_jnt.name())
            pm.textScrollList(
                "axis_{}_joint_list".format(attr), e=True, si=new_jnt.name())
        if method == "update":
            current_selected_index = int(pm.textScrollList(
                "axis_{}_joint_list".format(attr), q=True, sii=True)[0])
            current_selected = pm.textScrollList(
                "axis_{}_joint_list".format(attr), q=True, si=True)[0]
            print("current_selected_index:{}".format(current_selected_index))
            print("current_selected:{}".format(current_selected))
            current_jnt_value = get_channel_values(current_selected)
            print(current_jnt_value)
            default_jnt_value = self.face_data[current_module][
                controller_index - 1]["AxisControl"][axis_tab_label][
                "BoneRange"][current_selected_index - 1]["def"]
            print(default_jnt_value)
            offset_value = [
                current_jnt_value[0] - default_jnt_value[0],
                current_jnt_value[1] - default_jnt_value[1],
                current_jnt_value[2] - default_jnt_value[2],
                current_jnt_value[3] - default_jnt_value[3],
                current_jnt_value[4] - default_jnt_value[4],
                current_jnt_value[5] - default_jnt_value[5],
                current_jnt_value[6],
                current_jnt_value[7],
                current_jnt_value[8],
            ]
            if update == "Max":
                self.face_data[current_module][
                    controller_index - 1]["AxisControl"][axis_tab_label][
                    "BoneRange"][current_selected_index - 1][
                    "Max"] = offset_value
            if update == "Min":
                self.face_data[current_module][
                    controller_index - 1]["AxisControl"][axis_tab_label][
                    "BoneRange"][current_selected_index - 1][
                    "Min"] = offset_value

        common.write_json(dict_data=self.face_data, file_path=self.json_folder)

        axis_x_data = self.face_data[current_module][controller_index - 1]
        self.clean_axis_widget(attr)
        self.update_axis_widget(attr=attr, data=axis_x_data)

        return


class FaceData:
    def __init__(self, data):
        self.eye = None
        self.brow = None
        self.nose = None
        self.mouth = None
        self.feature = None

        self.init_from_data(data)

    def init_from_data(self, data):
        if "eyeController" in data.keys():
            self.eye = Controller(data=data["eyeController"])
        if "mouthController" in data.keys():
            self.mouth = Controller(data=data["mouthController"])


class Controller:
    def __init__(self, data):
        self.controllerName = ""
        self.controllerGroupName = ""
        self.controllerBoneName = ""
        self.controllerPositionOffset = [0, 0, 0]
        self.axisControl = {}

        self.init_from_dict(dict_data=data)

    def init_from_dict(self, dict_data=None):
        if dict_data is None:
            dict_data = {}
        self.controllerName = dict_data["controllerName"]
        self.controllerGroupName = dict_data["ControllerGroupName"]
        self.controllerBoneName = dict_data["ControllerBoneName"]
        self.controllerPositionOffset = dict_data["ControllerPositionOffset"]
        self.axisControl = dict_data["AxisControl"]
        return
