#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/2 9:34
# @Author  : Li XiaoJun
# @Site    : 
# @File    : test_node.py
# @Software: PyCharm
from animation.common import moving_target
from pymel import core as pm


class TestEditorController:
    """
    这个是用于测试捏脸系统上的控制器的助手类

    """

    def __init__(self):
        self.name = ""
        self.group_name = ""
        self.bone_name = ""
        self.position_offset = []
        self.axis_control = {}

        self.bone_range_X = []
        self.bone_range_Y = []
        self.bone_range_Z = []

        self.locator_controller = ""

    def get_controller_from_data(self, controller_data, control_group_data):
        self.name = controller_data["controllerName"]
        self.group_name = controller_data["ControllerGroupName"]
        self.bone_name = controller_data["ControllerBoneName"]
        self.position_offset = controller_data["ControllerPositionOffset"]
        self.axis_control = controller_data["AxisControl"]

        control_group = control_group_data["ControlGroup"]
        for item in control_group:
            if item["GroupName"] == ("%s_X" % self.name):
                self.bone_range_X = item["BoneRange"]
            if item["GroupName"] == ("%s_Y" % self.name):
                self.bone_range_Y = item["BoneRange"]
            if item["GroupName"] == ("%s_Z" % self.name):
                self.bone_range_Z = item["BoneRange"]
        return

    def create_locator_controller(self):
        self.locator_controller = pm.spaceLocator(name=self.name, p=[0, 0, 0])
        for attr in ["tx", "ty", "tz",
                     "rx", "ry", "rz",
                     "sx", "sy", "sz",
                     "v"]:
            pm.setAttr("%s.%s" % (self.name, attr),
                       lock=True, k=False, cb=False)

        if self.axis_control["XAxis"] != "":
            pm.addAttr(self.locator_controller,
                       ln="sliderX", at="double", min=-1, max=1, dv=0)
            pm.setAttr("%s.sliderX" % self.locator_controller, e=True, k=True)
            self.set_drive_key_with_locator_and_joint("sliderX")

        if self.axis_control["YAxis"] != "":
            pm.addAttr(self.locator_controller,
                       ln="sliderY", at="double", min=-1, max=1, dv=0)
            pm.setAttr("%s.sliderY" % self.locator_controller, e=True, k=True)
            self.set_drive_key_with_locator_and_joint("sliderY")

        if self.axis_control["ZAxis"] != "":
            pm.addAttr(self.locator_controller,
                       ln="sliderZ", at="double", min=-1, max=1, dv=0)
            pm.setAttr("%s.sliderZ" % self.locator_controller, e=True, k=True)
            self.set_drive_key_with_locator_and_joint("sliderZ")

        return self.locator_controller

    def set_drive_key_with_locator_and_joint(self, attr):
        if attr == "sliderX":
            self.sdk_locator_with_joint(
                locator=self.locator_controller,
                bone_range=self.bone_range_X,
                slider_attr=attr)

        if attr == "sliderY":
            self.sdk_locator_with_joint(
                locator=self.locator_controller,
                bone_range=self.bone_range_Y,
                slider_attr=attr)

        if attr == "sliderZ":
            self.sdk_locator_with_joint(
                locator=self.locator_controller,
                bone_range=self.bone_range_Z,
                slider_attr=attr)

        return

    def sdk_locator_with_joint(self, locator, bone_range, slider_attr):
        attr_list = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

        for jnt_dict in bone_range:
            print "Bone Name: %s" % jnt_dict["BoneName"]
            for dv_attr in attr_list:
                moving_target(jnt_dict["BoneName"])
                pm.setDrivenKeyframe(
                    "%s.%s" % (jnt_dict["BoneName"], dv_attr),
                    cd="%s.%s" % (locator, slider_attr),
                    dv=0)

                # Max value
                value = jnt_dict["Max"]
                dv_value = [
                    value[0] * 100, value[1] * 100, value[2] * 100,
                    value[3], value[4], value[5],
                    value[6], value[7], value[8],
                ]
                moving_target(jnt_dict["BoneName"], value=dv_value)
                pm.setDrivenKeyframe(
                    "%s.%s" % (jnt_dict["BoneName"], dv_attr),
                    cd="%s.%s" % (locator, slider_attr),
                    dv=1)

                # Min value
                value = jnt_dict["Min"]
                dv_value = [
                    value[0] * 100, value[1] * 100, value[2] * 100,
                    value[3], value[4], value[5],
                    value[6], value[7], value[8],
                ]
                moving_target(jnt_dict["BoneName"], value=dv_value)
                pm.setDrivenKeyframe(
                    "%s.%s" % (jnt_dict["BoneName"], dv_attr),
                    cd="%s.%s" % (locator, slider_attr),
                    dv=-1)
        pm.setAttr("%s.%s" % (locator, slider_attr), 0)

        return


