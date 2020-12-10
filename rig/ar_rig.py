#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/22 13:56
# @Author  : Li XiaoJun
# @Site    :
# @File    : ar_rig.py

import os
from imp import reload

from animation.common import write_json
from pymel import core as pm
# import maya.cmds as cmds
# import maya.mel as mel

import json
from animation import common
from animation import test_node
from animation import helper
from rig import channel

reload(common)
reload(test_node)
reload(helper)

manager_version = 0.31


class ARFaceData:
    def __init__(self):
        self.dict_data = {}
        self.ar_channels = []
        self.filename = ""

        self.unity_data = {}

    def decode_from_json(self, filename):
        if filename != '':
            with open(filename, 'r') as data:
                self.dict_data = json.load(data)
                # print self.dict_data
            ID_list = self.dict_data.keys()
            if len(ID_list) > 0:
                # 对列表进行排序
                ID_list.sort()
                self.ar_channels = ID_list
            self.filename = filename

    def set_channel_joint(self, channel, joint, data=None):
        u"""设置通道骨骼

        :param channel: 通道
        :param joint: 骨骼
        :return:
        """
        self.dict_data[channel][joint] = {}
        if data is not None:
            self.dict_data[channel][joint] = data

        return True

    def get_channel_joints(self, channel):
        return self.dict_data[channel].keys()

    def set_channel_joint_attr(self, channel, joint, value):
        self.dict_data[channel][joint]["max"] = value

        return True

    def get_channel_joint_attr(self, channel, joint):
        return self.dict_data[channel][joint]["max"]

    def data_to_json(self):
        with open(self.filename, "w") as f:
            json.dump(self.dict_data, f, indent=2)

        return True

    def export_for_unity(self, filename):
        channel_list = self.dict_data.keys()
        for channel in channel_list:
            for jnt in self.dict_data[channel].keys():
                if jnt not in self.unity_data.keys():
                    jnt_dict = {channel: self.dict_data[channel][jnt]["max"]}
                    self.unity_data[jnt] = jnt_dict
                else:
                    self.unity_data[jnt][channel] = self.dict_data[
                        channel][jnt]["max"]

        print("self.unity_data: %s" % self.unity_data)

        with open(filename, "w") as f:
            json.dump(self.unity_data, f, indent=2)

        return


class ARFaceEditor(common.Singleton):
    u"""AR人脸识别的通道模板编辑器"""

    def __init__(self):
        super(ARFaceEditor, self).__init__()

        self.ar_file_location = ""
        self.ar_data = ARFaceData()

        self.initialize()
        self.show()

    def initialize(self):
        if pm.optionVar(q='ARFaceEditor_jsonFileLocation'):
            self.ar_file_location = pm.optionVar(q='ARFaceEditor_jsonFileLocation')
        else:
            self.ar_file_location = ""

    def show(self):
        if pm.window("ARFaceEditor", ex=True):
            pm.deleteUI("ARFaceEditor")
        pm.window(
            "ARFaceEditor",
            t=u"AR人脸识别 %s" % manager_version,
            mb=True,
            cc=lambda *args: self._closed_window_cmd())

        self.menu_list()
        self.main_layout()

        pm.showWindow("ARFaceEditor")

    def _closed_window_cmd(self):
        pass

    def menu_list(self):
        u"""        工具菜单栏

        :return:
        """

        # 数据菜单栏
        pm.menu(label=u"数据", tearOff=True)
        pm.menuItem(
            label=u"输出Unity",
            c=lambda *args: self.export_for_unity())
        # 通道菜单栏
        pm.menu(label=u"通道", tearOff=True)
        pm.menuItem(
            label=u"重建选择通道",
            c=lambda *args: self.rebuild_channels_controller(type="selected"))
        pm.menuItem(
            label=u"重建所有通道",
            c=lambda *args: self.rebuild_channels_controller(type="all"))

        # 通道菜单栏
        pm.menu(label=u"骨骼", tearOff=True)
        pm.menuItem(
            label=u"添加影响骨骼",
            c=lambda *args: self.new_joint_to_ar_channel(auto_sdk=False))
        pm.menuItem(
            label=u"添加骨骼和SDK",
            c=lambda *args: self.new_joint_to_ar_channel(auto_sdk=True))
        pm.menuItem(divider=True)
        pm.menuItem(
            label=u"移除选择骨骼",
            c=lambda *args: self.remove_select_joint_in_scroll())
        pm.menuItem(divider=True)
        pm.menuItem(
            label=u"选择所有骨骼",
            c=lambda *args: self.select_all_joint_in_scroll())

        return

    def main_layout(self):
        u"""标签栏之AR控制栏

        :return: layout
        """
        layout = pm.formLayout("ARFormTab")

        self.work_mode_control = pm.radioButtonGrp(
            label=u"AR模式：", numberOfRadioButtons=2, labelArray2=['Face Unity', 'AR kit'], cw3=[60, 80, 80], sl=2)

        self.json_location_widget = pm.textFieldButtonGrp(
            "ARFileLocationField",
            label=u"存放路径：",
            bl=u"指定路径",
            adj=2,
            cw3=[60, 100, 60],
            text=self.ar_file_location,
            bc=lambda *args: self.set_json_location())

        self.ar_channel_options = pm.optionMenuGrp(
            label=u"识别通道：",
            cw2=[60, 100],
            adj=2,
            cc=lambda *args: self.selected_ar_channel())

        detail_frame = pm.frameLayout(label=u"通道属性", bgs=True, mw=10, mh=10)
        detail_form = pm.formLayout()
        ar_id_slider = pm.floatSliderGrp(
            "arIDControlSlider",
            enable=False,
            label=u"滑竿控制",
            field=True,
            minValue=0,
            maxValue=1.0,
            fieldMinValue=0,
            fieldMaxValue=1.0,
            pre=3,
            adj=3,
            value=0,
            cw3=[120, 60, 100])
        self.ar_item_scroll = pm.textScrollList(
            w=200, ams=True, sc=lambda *args: self.selected_ar_item_in_scroll())
        pm.popupMenu()
        pm.menuItem(label=u"添加映射", c=lambda *args: self.new_mapping())
        pm.menuItem(divider=True)
        pm.menuItem(label=u"添加影响骨骼", c=lambda *args: self.new_joint_to_ar_channel(auto_sdk=False))
        pm.menuItem(label=u"添加骨骼和SDK", c=lambda *args: self.new_joint_to_ar_channel(auto_sdk=True))
        pm.menuItem(divider=True)
        pm.menuItem(label=u"移除选择骨骼", c=lambda *args: self.remove_select_joint_in_scroll())
        pm.menuItem(divider=True)
        pm.menuItem(label=u"选择所有骨骼", c=lambda *args: self.select_all_joint_in_scroll())

        ar_item_data_layout = pm.columnLayout(adj=1, rs=2)
        self.ar_item_joint_name = pm.text(label=u"Joint name", al="left", fn="boldLabelFont")
        self.ar_item_attr_tx = pm.floatFieldGrp(adj=1, cw2=[80, 80], label="translateX", pre=3)
        self.ar_item_attr_ty = pm.floatFieldGrp(adj=1, cw2=[80, 80], label="translateY", pre=3)
        self.ar_item_attr_tz = pm.floatFieldGrp(adj=1, cw2=[80, 80], label="translateZ", pre=3)
        self.ar_item_attr_rx = pm.floatFieldGrp(adj=1, cw2=[80, 80], label="rotateX", pre=3)
        self.ar_item_attr_ry = pm.floatFieldGrp(adj=1, cw2=[80, 80], label="rotateY", pre=3)
        self.ar_item_attr_rz = pm.floatFieldGrp(adj=1, cw2=[80, 80], label="rotateZ", pre=3)
        self.ar_item_attr_sx = pm.floatFieldGrp(adj=1, cw2=[80, 80], label="scaleX", pre=3)
        self.ar_item_attr_sy = pm.floatFieldGrp(adj=1, cw2=[80, 80], label="scaleY", pre=3)
        self.ar_item_attr_sz = pm.floatFieldGrp(adj=1, cw2=[80, 80], label="scaleZ", pre=3)

        pm.button(label="Update Selected", c=lambda *args: self.update_sdk(type="select"))
        pm.button(label="Update All", c=lambda *args: self.update_sdk(type="all"))

        pm.setParent("..")  # end of ar_item_data_layout

        pm.formLayout(
            detail_form, edit=True,
            attachForm=[
                (ar_id_slider, 'left', 0),
                (ar_id_slider, 'right', 0),
                (self.ar_item_scroll, 'left', 0),
                (self.ar_item_scroll, 'bottom', 0),
                (ar_item_data_layout, 'right', 0),
                (ar_item_data_layout, 'bottom', 0),
            ],
            attachControl=[
                (self.ar_item_scroll, 'top', 7, ar_id_slider),
                (ar_item_data_layout, 'top', 7, ar_id_slider),
                (ar_item_data_layout, 'left', 5, self.ar_item_scroll),
            ])
        pm.setParent("..")  # end of detail_form
        pm.setParent("..")  # end of detail_frame

        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (self.work_mode_control, 'top', 5),
                (self.work_mode_control, 'left', 5),
                (self.json_location_widget, 'left', 10),
                (self.json_location_widget, 'right', 10),
                (self.ar_channel_options, 'left', 10),
                (detail_frame, 'left', 10),
                (detail_frame, 'right', 10),
                (detail_frame, 'bottom', 10),
            ],
            attachControl=[
                (self.json_location_widget, 'top', 5, self.work_mode_control),
                (self.ar_channel_options, 'top', 7, self.json_location_widget),
                (detail_frame, 'top', 10, self.ar_channel_options),
            ])

        pm.setParent("..")

        if self.ar_file_location != "":
            if os.path.isfile(self.ar_file_location):
                self.init_ar_channel_options(json_file=self.ar_file_location)
                pm.optionMenuGrp(self.ar_channel_options, e=True, sl=1)
                self.selected_ar_channel()

                if pm.textScrollList(self.ar_item_scroll, q=True, ni=True) > 1:
                    pm.textScrollList(self.ar_item_scroll, e=True, sii=1)
                    self.selected_ar_item_in_scroll()

        return layout

    def set_json_location(self):
        json_location = pm.fileDialog2(
            dialogStyle=2, fileFilter="JSON File (*.json);;", fileMode=0, okc=u"选择文件", cc=u"取消")
        if os.path.isfile(json_location[0]):
            pm.textFieldButtonGrp("ARFileLocationField", e=True, text=json_location[0])
            self.ar_file_location = json_location[0]

        else:
            dict_data = {}
            mode = pm.radioButtonGrp(self.work_mode_control, q=True, sl=True)
            if mode == 1:
                dict_data = channel.face_unity_channels
            elif mode == 2:
                dict_data = channel.arkit_channels
            write_json(dict_data=dict_data, file_path=json_location[0])
            pm.textFieldButtonGrp("ARFileLocationField", e=True, text=json_location[0])
            self.ar_file_location = json_location[0]

        self.init_ar_channel_options(json_file=json_location[0])
        pm.optionVar(sv=('ARFaceEditor_jsonFileLocation', self.ar_file_location))

        if pm.textScrollList(self.ar_item_scroll, q=True, ni=True) > 1:
            pm.textScrollList(self.ar_item_scroll, e=True, sii=1)
            self.selected_ar_item_in_scroll()

        return

    def init_ar_channel_options(self, json_file):
        self.ar_data = ARFaceData()
        self.ar_data.decode_from_json(json_file)

        pm.textScrollList(self.ar_item_scroll, e=True, ra=True)
        for menu in pm.optionMenuGrp(self.ar_channel_options, q=True, ill=True):
            pm.deleteUI(menu, mi=True)

        if len(self.ar_data.ar_channels) > 0:
            for item in self.ar_data.ar_channels:
                pm.menuItem(p=(self.ar_channel_options + "|OptionMenu"), label=item)
        return

    def selected_ar_channel(self):
        u"""选择AR通道

        :return:
        """
        current_channel = pm.optionMenuGrp(self.ar_channel_options, q=True, value=True)

        pm.textScrollList(self.ar_item_scroll, e=True, ra=True)
        if self.ar_data.get_channel_joints(current_channel):
            pm.textScrollList(
                self.ar_item_scroll,
                e=True,
                a=self.ar_data.get_channel_joints(current_channel)
            )
            pm.textScrollList(self.ar_item_scroll, e=True, sii=1)
            self.selected_ar_item_in_scroll()

        print(u"选择通道：{}".format(current_channel))
        work_mode = pm.radioButtonGrp(self.work_mode_control, q=True, sl=True)
        if pm.objExists(current_channel):
            pm.floatSliderGrp("arIDControlSlider", e=True, enable=True, label=current_channel)
            if work_mode == 1:
                pm.connectControl('arIDControlSlider', '%s.sliderX' % current_channel)
            if work_mode == 2:
                pm.connectControl('arIDControlSlider', '{}.weight'.format(current_channel))

        else:
            pass

        return

    def selected_ar_item_in_scroll(self):
        current_channel = pm.optionMenuGrp(
            self.ar_channel_options, q=True, value=True)

        # 当前选择的骨骼
        current_item = pm.textScrollList(
            self.ar_item_scroll, q=True, si=True)
        pm.select(current_item)

        current_item_attrs = self.ar_data.get_channel_joint_attr(
            current_channel, current_item[0])

        # 修改通道属性栏里面底部右侧的面板的名称
        pm.text(self.ar_item_joint_name, e=True, label=current_item[0])
        pm.floatFieldGrp(
            self.ar_item_attr_tx, e=True, v1=current_item_attrs[0] * 100)
        pm.floatFieldGrp(
            self.ar_item_attr_ty, e=True, v1=current_item_attrs[1] * 100)
        pm.floatFieldGrp(
            self.ar_item_attr_tz, e=True, v1=current_item_attrs[2] * 100)
        pm.floatFieldGrp(
            self.ar_item_attr_rx, e=True, v1=current_item_attrs[3])
        pm.floatFieldGrp(
            self.ar_item_attr_ry, e=True, v1=current_item_attrs[4])
        pm.floatFieldGrp(
            self.ar_item_attr_rz, e=True, v1=current_item_attrs[5])
        pm.floatFieldGrp(
            self.ar_item_attr_sx, e=True, v1=current_item_attrs[6])
        pm.floatFieldGrp(
            self.ar_item_attr_sy, e=True, v1=current_item_attrs[7])
        pm.floatFieldGrp(
            self.ar_item_attr_sz, e=True, v1=current_item_attrs[8])
        return

    def rebuild_channels_controller(self, type="all"):
        u"""重建通道与控制器之间的连接

        :param type: 重建类型，有效选项为all, selected
        :return: None
        """
        
        test_proxy = "ArkitPoseLib"
        
        if not pm.objExists(test_proxy):
            # pm.error(u"测试用代理体{}已经存在".format(test_proxy))
            pm.createNode("transform", name=test_proxy)
            for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]:
                pm.setAttr("{}.{}".format(test_proxy, attr), lock=True, keyable=False, channelBox=False)

                all_channel = pm.optionMenuGrp(self.ar_channel_options, q=True, ils=True)
                for channel in all_channel:
                    channel_label = pm.menuItem(channel, q=True, label=True)
                    print(channel_label)
                    pm.addAttr(test_proxy)
                    # addAttr -ln "browDown_L"  -at double  -min 0 -max 1 -dv 0 |ArkitPoseLib;
                    # setAttr -e-keyable true |ArkitPoseLib.browDown_L;

        # if type == "all":
        #     for item in pm.optionMenuGrp(self.ar_channel_options, q=True, ils=True):
        #         channel_label = pm.menuItem(item, q=True, label=True)
        #         if not pm.objExists(channel_label):
        #             self.create_slider_controller(name=channel_label)
        #             self.sdk_slider_to_rig(channel=channel_label)
        #             pm.connectControl('arIDControlSlider', '%s.sliderX' % channel_label)
        #     pm.optionMenuGrp(self.ar_channel_options, e=True, sl=1)
        #     self.selected_ar_channel()
        # elif type == "selected":
        #     all_menu_item = pm.optionMenuGrp(
        #         self.ar_channel_options, q=True, ils=True)
        #     current_index = pm.optionMenuGrp(
        #         self.ar_channel_options, q=True, sl=True) - 1
        #     channel_label = pm.menuItem(
        #         all_menu_item[current_index], q=True, label=True)
        #     if not pm.objExists(channel_label):
        #         self.create_slider_controller(name=channel_label)
        #         self.sdk_slider_to_rig(channel=channel_label)
        #         pm.connectControl(
        #             'arIDControlSlider', '%s.sliderX' % channel_label)
        #     pm.optionMenuGrp(
        #         self.ar_channel_options, e=True, sl=(current_index + 1))
        #     self.selected_ar_channel()

        return

    def create_slider_controller(self, name):
        locator = helper.zero_locator(name=name)
        pm.addAttr(locator, ln="sliderX", at="double", min=0, max=1, dv=0)
        pm.setAttr("%s.sliderX" % locator, e=True, k=True)
        print(u"%s已经创建" % locator)
        return

    def update_sdk(self, type="select", pre=5):
        current_jnts = []
        if type == "select":
            current_jnts = pm.textScrollList(
                self.ar_item_scroll, q=True, si=True)
        elif type == "all":
            current_jnts = pm.textScrollList(
                self.ar_item_scroll, q=True, ai=True)

        for current_jnt in current_jnts:
            jnt_value = [
                round(pm.PyNode(current_jnt).translateX.get() * 0.01, pre),
                round(pm.PyNode(current_jnt).translateY.get() * 0.01, pre),
                round(pm.PyNode(current_jnt).translateZ.get() * 0.01, pre),
                round(pm.PyNode(current_jnt).rotateX.get(), pre),
                round(pm.PyNode(current_jnt).rotateY.get(), pre),
                round(pm.PyNode(current_jnt).rotateZ.get(), pre),
                round(pm.PyNode(current_jnt).scaleX.get(), pre),
                round(pm.PyNode(current_jnt).scaleY.get(), pre),
                round(pm.PyNode(current_jnt).scaleZ.get(), pre),
            ]

            attr_list = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

            for dv_attr in attr_list:
                helper.position_joint(
                    current_jnt, value=[0, 0, 0, 0, 0, 0, 1, 1, 1])

                pm.setDrivenKeyframe(
                    "%s.%s" % (current_jnt, dv_attr),
                    cd="%s.sliderX" % (pm.optionMenuGrp(
                        self.ar_channel_options, q=True, value=True)),
                    dv=0)

                helper.position_joint(
                    current_jnt,
                    value=[
                        jnt_value[0] * 100,
                        jnt_value[1] * 100,
                        jnt_value[2] * 100,
                        jnt_value[3],
                        jnt_value[4],
                        jnt_value[5],
                        jnt_value[6],
                        jnt_value[7],
                        jnt_value[8]])
                pm.setDrivenKeyframe(
                    "%s.%s" % (current_jnt, dv_attr),
                    cd="%s.sliderX" % (pm.optionMenuGrp(
                        self.ar_channel_options, q=True, value=True)),
                    dv=1)

            pm.floatFieldGrp(self.ar_item_attr_tx, e=True,
                             v1=jnt_value[0] * 100)
            pm.floatFieldGrp(self.ar_item_attr_ty, e=True,
                             v1=jnt_value[1] * 100)
            pm.floatFieldGrp(self.ar_item_attr_tz, e=True,
                             v1=jnt_value[2] * 100)
            pm.floatFieldGrp(self.ar_item_attr_rx, e=True, v1=jnt_value[3])
            pm.floatFieldGrp(self.ar_item_attr_ry, e=True, v1=jnt_value[4])
            pm.floatFieldGrp(self.ar_item_attr_rz, e=True, v1=jnt_value[5])
            pm.floatFieldGrp(self.ar_item_attr_sx, e=True, v1=jnt_value[6])
            pm.floatFieldGrp(self.ar_item_attr_sy, e=True, v1=jnt_value[7])
            pm.floatFieldGrp(self.ar_item_attr_sz, e=True, v1=jnt_value[8])

            self.ar_data.set_channel_joint_attr(
                channel=pm.optionMenuGrp(
                    self.ar_channel_options, q=True, value=True),
                joint=current_jnt,
                value=jnt_value,
            )
        self.ar_data.data_to_json()
        return

    def sdk_slider_to_rig(self, channel, attr="sliderX"):
        attr_list = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        for jnt in self.ar_data.get_channel_joints(channel):
            value = self.ar_data.get_channel_joint_attr(channel, jnt)

            for dv_attr in attr_list:
                helper.position_joint(jnt, value=[0, 0, 0, 0, 0, 0, 1, 1, 1])
                pm.setDrivenKeyframe(
                    "%s.%s" % (jnt, dv_attr),
                    cd="%s.%s" % (channel, attr),
                    dv=0)
                dv_value = [
                    value[0] * 100,
                    value[1] * 100,
                    value[2] * 100,
                    value[3],
                    value[4],
                    value[5],
                    value[6],
                    value[7],
                    value[8],
                ]
                helper.position_joint(jnt, value=dv_value)
                pm.setDrivenKeyframe(
                    "%s.%s" % (jnt, dv_attr),
                    cd="%s.%s" % (channel, attr),
                    dv=1)

        pm.setAttr("%s.%s" % (channel, attr), 0)
        return

    def new_joint_to_ar_channel(self, auto_sdk=False):
        all_items = pm.textScrollList(self.ar_item_scroll, q=True, ai=True)
        for item in pm.ls(sl=True):
            if item not in all_items:
                pm.textScrollList(self.ar_item_scroll, e=True, a=item)
                self.ar_data.set_channel_joint(
                    channel=pm.optionMenuGrp(self.ar_channel_options, q=True, value=True),
                    joint=item.controller_name(),
                )
                self.ar_data.set_channel_joint_attr(
                    channel=pm.optionMenuGrp(self.ar_channel_options, q=True, value=True),
                    joint=item.controller_name(),
                    value=[0, 0, 0, 0, 0, 0, 1, 1, 1]
                )

            pm.textScrollList(self.ar_item_scroll, e=True, da=True)
            pm.textScrollList(self.ar_item_scroll, e=True, si=item)

            if auto_sdk:
                self.update_sdk(type="select")

            self.ar_data.data_to_json()

        return True

    def new_mapping(self):
        filename = pm.textFieldButtonGrp("ARFileLocationField", q=True, text=True)
        arkit_data = common.read_json(filename)

        current_channel = pm.optionMenuGrp(self.ar_channel_options, q=True, value=True)
        joint_data = {}
        # print(current_channel)
        all_items = pm.textScrollList(self.ar_item_scroll, q=True, ai=True)
        for item in pm.ls(sl=True):
            if item not in all_items:
                pm.textScrollList(self.ar_item_scroll, e=True, a=item)
            data = []
            translate = pm.PyNode(item).translate.get()
            unity_translate = [translate[0] * 0.01, translate[1] * 0.01, translate[2] * 0.01]
            data.extend(unity_translate)
            data.extend(pm.PyNode(item).rotate.get())
            data.extend(pm.PyNode(item).scale.get())

            joint_data[item.name()] = {}
            joint_data[item.name()]["max"] = data

        print(joint_data)
        #         print data

        #         self.ar_data.set_channel_joint(
        #             channel=pm.optionMenuGrp(self.ar_channel_options, q=True, value=True),
        #             joint=item.controller_name(),
        #         )
        # self.ar_data.set_channel_joint_attr(
        #     channel=pm.optionMenuGrp(self.ar_channel_options, q=True, value=True),
        #     joint=item.controller_name(),
        #     value=data
        # )
        #     pm.textScrollList(self.ar_item_scroll, e=True, da=True)
        #     pm.textScrollList(self.ar_item_scroll, e=True, si=item)

        arkit_data[current_channel] = joint_data
        print(arkit_data)
        # # self.ar_data.data_to_json()
        common.write_json(arkit_data, filename)
        return

    def select_all_joint_in_scroll(self):
        u"""选择列表里面的所有骨骼

        :return: None
        """
        all_jnt = pm.textScrollList(self.ar_item_scroll, q=True, ai=True)
        pm.select(all_jnt)
        return

    def remove_select_joint_in_scroll(self):
        u"""从列表里面移除选择的骨骼

        :return: None
        """
        select_joint = pm.textScrollList(self.ar_item_scroll, q=True, si=True)
        select_index = pm.textScrollList(self.ar_item_scroll, q=True, sii=True)

        # print "select_index: %s" % select_index[0]
        # print self.ar_data.dict_data[
        #     pm.optionMenuGrp(self.ar_channel_options, q=True, value=True)]

        helper.position_joint(select_joint[0],
                              value=[0, 0, 0, 0, 0, 0, 1, 1, 1])
        self.ar_data.dict_data[
            pm.optionMenuGrp(self.ar_channel_options, q=True, value=True)
        ].pop(select_joint[0])

        pm.textScrollList(self.ar_item_scroll, e=True, rii=select_index)

        self.ar_data.data_to_json()

        if int(select_index[0]) > 1:
            pm.textScrollList(
                self.ar_item_scroll, e=True, da=True)
            pm.textScrollList(
                self.ar_item_scroll, e=True, sii=(select_index[0] - 1))
            self.selected_ar_item_in_scroll()
        return

    def export_for_unity(self):
        json_file = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=0, okc=u"选择文件")

        if json_file:
            self.ar_data.export_for_unity(filename=json_file[0])
        return
