#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/12/18 9:57
# @Author  : Li XiaoJun
# @Site    : 
# @File    : face_feature_manager.py
import os
from imp import reload

import pymel.core as pm
from animation import common as xd_com, helper

reload(xd_com)

version = 0.2


def get_module_list(path="", return_type="folders"):
    u"""扫描文件夹，将目录列取出来，如果目录下有对应的文件（例：文件夹名face, 对应的文件）

    :param return_type: 返回类型
    """
    json_list = []
    json_file = ""
    folder_list = []
    if path != '':
        path_dir = os.listdir(path)
        for json_file in path_dir:
            if json_file == ".mayaSwatches":
                continue
            full_path = os.path.join(path, json_file)
            if os.path.isdir(full_path):
                folder_list.append(json_file)
            elif os.path.isfile(full_path):
                # 获取JSON文件的名字后，清理文件的后缀名
                file_name = os.path.splitext(json_file)[0]
                json_list.append(file_name)
        if return_type == "files":
            return json_file
        elif return_type == "folders":
            return folder_list


class FeatureControllerGroup():
    def __init__(self, file):
        self.file = file
        self._data = self.get_data()

    def get_data(self):
        return xd_com.read_json(file_path=self.file)

    def get_controller_group_data(self, controller):
        return self._data[controller]


class FeatureController():
    def __init__(self, file):
        self.file = file
        self._data = self.get_data()
        self._feature_name = self.get_feature_name()

    def get_data(self):
        return xd_com.read_json(file_path=self.file)

    def get_feature_name(self):
        self._feature_name = self._data.keys()[0]
        return self._feature_name

    def get_controller_data(self, index):
        feature = self.get_feature_name()
        controller_data = self._data[feature][index]
        return controller_data

    def get_controller_list(self):
        controller_list = []
        feature = self.get_feature_name()
        for controller_dict in self._data[feature]:
            controller_list.append(controller_dict["ControllerName"])
        return controller_list

    def __str__(self):
        return self.get_feature_name()


class FeatureComponent():
    def __init__(self, data):
        self._data = data

        self.name = self.get_shape_type()
        self.control_group = self.get_control_group()

    def get_shape_type(self):
        return self._data["shapeType"]

    def get_control_group(self):
        return self._data["ControlGroup"]

    def build_widget(self, parent):
        for axis_data in self.control_group:
            tab = self.axis_widget(data=axis_data, parent=parent)
            pm.tabLayout(parent, e=True, tabLabel=((tab, axis_data["GroupName"])))

    def axis_widget(self, data=None, parent=""):
        name = data["GroupName"]

        print("axis_widget:{}".format(name))

        joint_list = []
        for bone_data in data["BoneRange"]:
            joint_list.append(bone_data["BoneName"])

        layout = pm.formLayout("{}_FormLayout".format(name), p=parent)
        joint_list_frame = pm.frameLayout(
            "{}_JointListFrameLayout".format(name), label="Joint List", p=layout)
        pm.textScrollList("{}_JointListWidget".format(name),
                          w=120, a=joint_list,
                          sc=lambda *args: self.select_joint("{}_JointListWidget".format(name)))
        pm.popupMenu()
        pm.menuItem(label=u"添加骨骼", c=lambda *args: self.add_axis_joints())
        pm.setParent(joint_list_frame)

        joint_meta_frame = pm.frameLayout(
            "{}_JointMetaFrameWidget".format(name), label="Joint Meta", p=layout)
        pm.button(label=u"Update Max", c=lambda *args: self.update_joints_meta(value="Max"))
        pm.button(label=u"Update Min", c=lambda *args: self.update_joints_meta(value="Min"))
        pm.setParent("..")

        pm.formLayout(layout, edit=True,
                      attachForm=[
                          (joint_list_frame, 'top', 10),
                          (joint_list_frame, 'left', 10),
                          (joint_list_frame, 'bottom', 10),
                          (joint_meta_frame, 'top', 10),
                          (joint_meta_frame, 'right', 10),
                          (joint_meta_frame, 'bottom', 10),
                      ],
                      attachControl=[
                          (joint_meta_frame, 'left', 5, joint_list_frame),
                      ])

        pm.setParent(layout)

        return layout

    def select_joint(self, widget):
        pm.select(pm.textScrollList(widget, q=True, si=True)[0])


class FaceFeatureModule():
    def __init__(self, name, data_path):
        self.name = name
        self.data_root = data_path
        self.control_group_file = "{}/{}/{}ControlGroup.json".format(self.data_root, self.name, self.name)
        self.control_file = "{}/{}/{}Controller.json".format(self.data_root, self.name, self.name)

        self.control_group_data = None
        self.control_data = None

    def feature_widget(self, parent):
        layout = pm.formLayout("{}FormTabLayout".format(self.name), p=parent)

        controller_list_frame = pm.frameLayout("{}ControllerListFrameLayout".format(self.name),
                                               bgs=True, mh=10, mw=10, p=layout,
                                               label=("{} Controllers".format(self.name).title()))
        pm.textScrollList("{}ControllerListWidget".format(self.name), w=120, h=130,
                          sc=lambda *args: self.select_controller())

        pm.popupMenu()
        pm.menuItem(label=u"创建测试代理体", c=lambda *args: self.build_test_proxy())

        pm.button("{}ControllerBuildBtn".format(self.name), label="New", w=100,
                  c=lambda *args: self.command_new_control())
        pm.setParent(controller_list_frame)

        controller_meta_frame = pm.frameLayout("{}ControllerMetaFrameLayout".format(self.name),
                                               bgs=True, mh=10, mw=10, p=layout,
                                               label=("{} meta".format(self.name).title()))
        pm.radioButtonGrp("{}ControllerSideField".format(self.name),
                          label=u'控制器位置',
                          numberOfRadioButtons=2, labelArray2=['Middle', 'LF And RT'], cw3=[140, 80, 80])
        pm.textFieldGrp("{}ControllerNameField".format(
            self.name), label=u"控制器")
        pm.textFieldGrp("{}ControllerBoneNameField".format(
            self.name), label=u"控制器挂点骨骼")
        pm.floatFieldGrp("{}ControllerPositionOffsetField".format(self.name),
                         label=u'控制器位置偏移', numberOfFields=3,
                         value1=0.0, value2=0.0, value3=0.0, cw4=[140, 50, 50, 50])
        pm.checkBoxGrp("{}ControllerAxisControlField".format(self.name),
                       label=u'控制器滑竿',
                       numberOfCheckBoxes=3, labelArray3=['XAxis', 'YAxis', 'ZAxis'],
                       cw4=[140, 80, 80, 80])
        pm.button("{}ControllerMetaUpdateBtn".format(self.name),
                  label=u"更新", c=lambda *args: self.update_meta_data())
        pm.setParent(controller_meta_frame)

        joint_list_frame = pm.frameLayout("{}ControlJointListFrameLayout".format(self.name),
                                          bgs=True, mh=10, mw=10, p=layout,
                                          label=("{} control joints".format(self.name).title()))
        pm.tabLayout("{}ControlJointListTabLayout".format(self.name), p=joint_list_frame)

        pm.setParent("..")
        pm.setParent(joint_list_frame)

        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (controller_list_frame, 'top', 10),
                (controller_list_frame, 'left', 10),
                (controller_meta_frame, 'top', 10),
                (controller_meta_frame, 'right', 10),
                (joint_list_frame, 'left', 10),
                (joint_list_frame, 'right', 10),
                (joint_list_frame, 'bottom', 10),
            ],
            attachControl=[
                (controller_meta_frame, 'left', 5, controller_list_frame),
                (joint_list_frame, 'top', 5, controller_meta_frame),
            ])

        pm.setParent("..")

        self.init_data()

        return layout

    def init_data(self):
        self.control_data = FeatureController(self.control_file)
        self.control_group_data = FeatureControllerGroup(self.control_group_file)
        controller_list = self.control_data.get_controller_list()
        pm.textScrollList("{}ControllerListWidget".format(self.name), e=True, a=controller_list)

        return

    def select_controller(self):
        selected_index = pm.textScrollList("{}ControllerListWidget".format(self.name), q=True, sii=True)[0]
        controller_data = self.control_data.get_controller_data(index=selected_index - 1)
        self.refresh_meta_data(controller_data)

        selected_controller = pm.textScrollList("{}ControllerListWidget".format(self.name), q=True, si=True)[0]
        selected_control_group = self.control_group_data.get_controller_group_data(selected_controller)
        self.refresh_control_group_meta_data(selected_control_group)

        return selected_index

    def refresh_meta_data(self, data):
        # print(data)
        pm.textFieldGrp("{}ControllerNameField".format(self.name), e=True, text=data["ControllerName"])
        pm.textFieldGrp("{}ControllerBoneNameField".format(self.name), e=True, text=data["ControllerBoneName"])
        pm.floatFieldGrp("{}ControllerPositionOffsetField".format(self.name), e=True,
                         value1=data["ControllerPositionOffset"][0] * 100,
                         value2=data["ControllerPositionOffset"][1] * 100,
                         value3=data["ControllerPositionOffset"][2] * 100)

        if data["AxisControl"]["XAxis"] == "":
            axis_x = False
        else:
            axis_x = True
        if data["AxisControl"]["YAxis"] == "":
            axis_y = False
        else:
            axis_y = True
        if data["AxisControl"]["ZAxis"] == "":
            axis_z = False
        else:
            axis_z = True
        pm.checkBoxGrp("{}ControllerAxisControlField".format(self.name), e=True,
                       value1=axis_x, value2=axis_y, value3=axis_z)

    def refresh_control_group_meta_data(self, data):
        tab_list = pm.tabLayout("{}ControlJointListTabLayout".format(self.name), q=True, ca=True)
        if not tab_list is None:
            for tab in tab_list:
                pm.deleteUI(tab)

        axis_tabs = FeatureComponent(data)
        axis_tabs.build_widget(parent="{}ControlJointListTabLayout".format(self.name))

    def build_test_proxy(self):
        selected_controller = pm.textScrollList("{}ControllerListWidget".format(self.name), q=True, si=True)[0]
        selected_tab = self.name

        if not pm.objExists("TestProxyGrp"):
            pm.createNode("transform", name="TestProxyGrp")

        test_controller = pm.spaceLocator(name="Test{}".format(selected_controller))
        pm.parent(test_controller, "TestProxyGrp")

        control_group = self.control_group_data.get_controller_group_data(selected_controller)["ControlGroup"]
        for control_data in control_group:
            pm.addAttr(test_controller, ln=control_data["GroupName"], at="double", dv=0, min=-1, max=1)
            pm.setAttr("{}.{}".format(test_controller, control_data["GroupName"]), e=True, k=True)
            self.sdk_bone(source="{}.{}".format(test_controller, control_data["GroupName"]),
                          target_data=control_data)

        return

    def sdk_bone(self, source, target_data):
        print(source)
        print(target_data)
        attr_list = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

        if len(target_data["BoneRange"]) > 0:
            for bone in target_data["BoneRange"]:
                for dv_attr in attr_list:
                    pm.setDrivenKeyframe(
                        "%s.%s" % (bone["BoneName"], dv_attr),
                        cd=source,
                        dv=0)

                max_value = bone["Max"]
                dv_value = [
                    max_value[0] * 100,
                    max_value[1] * 100,
                    max_value[2] * 100,
                    max_value[3],
                    max_value[4],
                    max_value[5],
                    max_value[6],
                    max_value[7],
                    max_value[8],
                ]
                helper.position_joint(bone["BoneName"], value=dv_value)
                for dv_attr in attr_list:
                    pm.setDrivenKeyframe(
                        "%s.%s" % (bone["BoneName"], dv_attr),
                        cd=source,
                        dv=1)

                min_value = bone["Min"]
                dv_value = [
                    min_value[0] * 100,
                    min_value[1] * 100,
                    min_value[2] * 100,
                    min_value[3],
                    min_value[4],
                    min_value[5],
                    min_value[6],
                    min_value[7],
                    min_value[8],
                ]
                helper.position_joint(bone["BoneName"], value=dv_value)
                for dv_attr in attr_list:
                    pm.setDrivenKeyframe(
                        "%s.%s" % (bone["BoneName"], dv_attr),
                        cd=source,
                        dv=-1)


            pm.setAttr(source, 0)
        return

    def __str__(self):
        return self.name


class FaceFeatureManager(xd_com.Singleton):
    u"""脸部特征管理器"""

    def __init__(self):
        super(FaceFeatureManager, self).__init__()
        self.toolName = "FaceFeatureManager"

        self.json_path = ''
        self.module_sections = []

        self.create_window()
        self.create_layout()
        self.initialize()

    def create_window(self):
        if pm.window(self.toolName, ex=True):
            pm.deleteUI(self.toolName)
        pm.window(self.toolName,
                  t=u"角色脸部特征编辑器 {}".format(version),
                  mb=True,
                  cc=lambda *args: self._closed_window_cmd())
        pm.showWindow(self.toolName)

    def create_layout(self):
        form_layout = pm.formLayout(p=self.toolName)

        config_frame = pm.frameLayout(
            p=form_layout, label=u"配置面板", mw=5, mh=5, bgs=True, cll=False, cl=False)
        pm.textFieldButtonGrp(
            "XDFaceEditDataStoreField", label=u"存储路径", bl=u"设置", adj=2, cw3=[60, 100, 40],
            bc=lambda *args: self.setting_json_path())
        pm.textFieldButtonGrp(
            "XDFaceEditNewModuleField", label=u"特征模块", bl=u"新建", adj=2, cw3=[60, 100, 40],
            bc=lambda *args: self.command_new_module())
        pm.setParent(config_frame)

        main_tab = pm.tabLayout("XDFeatureManagerTabLayout",
                                p=form_layout, innerMarginWidth=5, innerMarginHeight=5)
        pm.setParent(main_tab)

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (config_frame, 'top', 5),
                (config_frame, 'left', 5),
                (config_frame, 'right', 5),
                (main_tab, 'left', 5),
                (main_tab, 'right', 5),
                (main_tab, 'bottom', 5),
            ],
            attachControl=[
                (main_tab, 'top', 5, config_frame),
            ])
        pm.setParent(form_layout)

    def _closed_window_cmd(self):
        pm.optionVar(sv=('jsonManagerFolder', self.json_path))

    def initialize(self):
        if pm.optionVar(q='jsonManagerFolder'):
            self.json_path = pm.optionVar(q='jsonManagerFolder')
            pm.textFieldButtonGrp("XDFaceEditDataStoreField", e=True, text=self.json_path)
            self.module_sections = get_module_list(path=self.json_path, return_type="folders")
            for module_name in self.module_sections:
                module = FaceFeatureModule(module_name, self.json_path)
                layout = module.feature_widget(parent="XDFeatureManagerTabLayout")
                pm.tabLayout("XDFeatureManagerTabLayout", edit=True, tabLabel=((layout, module_name)))

    def setting_json_path(self):
        json_folder = pm.fileDialog2(
            dialogStyle=2, fileFilter="JSON File (*.json);;", fileMode=3, okc=u"选择文件夹")
        if json_folder[0]:
            self.json_path = json_folder[0]
            pm.textFieldButtonGrp("XDFaceEditDataStoreField", e=True, text=self.json_path)

        return


def show_feature_manager():
    FaceFeatureManager()
