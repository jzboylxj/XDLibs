#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/8/13 15:49
# @Author  : Li XiaoJun
# @Site    :
# @File    : face_make.py
import json
import os
from imp import reload

from animation import common, test_node
from animation import helper
from pymel import core as pm

reload(helper)

manager_version = 0.2


class FaceMaker(common.Singleton):
    """
    捏脸滑竿编辑器
    """

    def __init__(self):
        super(FaceMaker, self).__init__()

        # 数据配置文件夹存放路径
        self.json_folder = ''
        # 模块片段数量
        self.module_sections = []

        # self.dict_data = list()
        # self.detail_data = dict()

        # self.controller = {}
        # self.controller_detail = {}

        # self.current_tab_index = 1

        # 历史版本的json文件存放路径
        # self.brow_file_folder = ""
        # self.eye_file_folder = ""
        # self.nose_file_folder = ""
        # self.mouth_file_folder = ""
        # self.face_file_folder = ""

        self.show()
        self.initialize()
        # self.selected_controller()

    def show(self):
        """
        显示工具窗口

        :return: window
        """
        if pm.window("faceMakerWnd", ex=True):
            pm.deleteUI("faceMakerWnd")
        pm.window(
            "faceMakerWnd",
            t=u"捏脸数据编辑器 %s" % manager_version,
            mb=True,
            cc=lambda *args: self._closed_window_cmd())

        self.menu_list()

        main_layout = pm.columnLayout(adj=True)

        self.config_input = pm.textFieldButtonGrp(
            label=u"配置文件",
            bl=u"指定路径",
            adj=2,
            cw3=[56, 100, 100],
            p=main_layout,
            text=self.json_folder,
            bc=lambda *args: self.setting_json_folder())

        self.work_form()

        pm.showWindow("faceMakerWnd")

    def menu_list(self):
        """
        工具菜单栏

        :return:
        """
        pm.menu(label=u"文件", tearOff=False)
        pm.menuItem(
            label=u"保存数据",
            c=lambda *args: self.save_custom_data())

        pm.menu(label=u"设置", tearOff=False)
        pm.menuItem(
            label=u"设置Json存放目录",
            c=lambda *args: self.setting_json_folder())
        pm.menuItem(
            label=u"调试模式", cb=False)

        pm.menu(label=u"模块", tearOff=False)
        pm.menuItem(
            label=u"增加模块",
            c=lambda *args: self.add_module())
        pm.menuItem(label=u"增加控制器", c=lambda *args: self.add_controller())
        pm.menuItem(
            label=u"增加控制器细节",
            c=lambda *args: self.add_control_detail_widget())

        pm.menu(label=u"测试", tearOff=False)
        pm.menuItem(
            label=u"创建测试控制器",
            c=lambda *args: self.create_editor_test_controller())

        return

    def work_form(self):
        """
        标签栏之自定义捏脸栏

        :return: layout
        """
        layout = pm.formLayout("customFormTab")

        option_menu = self.option_menu_widget(parent_widget=layout)

        line1 = pm.separator(height=5, style='in', p=layout)

        # frame_module = self.frame_module_list()
        # 控制器面板
        # controller_list_layout = self.tab_controller()
        # 影响骨骼面板
        # controller_detail_list_layout = self.tab_controller_joint()
        # 测试面板
        # controller_test_list_layout = self.tab_test_controller()

        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (option_menu, 'top', 10),
                (option_menu, 'left', 5),
                (option_menu, 'right', 5),
                (line1, 'left', 5),
                (line1, 'right', 5),
                # (controller_list_layout, 'left', 5),
                # (controller_list_layout, 'bottom', 5),
                # (controller_detail_list_layout, 'right', 5),
                # (controller_detail_list_layout, 'bottom', 5),
            ],
            attachControl=[
                (line1, 'top', 5, option_menu),
                # (controller_list_layout, 'top', 5, line1),
                # (controller_detail_list_layout, 'top', 5, option_menu),
                # (controller_detail_list_layout, 'left', 5,
                #  controller_list_layout),
            ])

        pm.setParent("..")
        return layout

    def frame_module_list(self):
        layout = pm.frameLayout(
            label=u"Module List:", bgs=True, mw=5, mh=5, w=150)
        form_layout = pm.formLayout()
        module_list_widget = pm.textScrollList()

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (module_list_widget, 'top', 10),
                (module_list_widget, 'left', 5),
                (module_list_widget, 'right', 5),
                (module_list_widget, 'bottom', 5),
            ],
            attachControl=[
                # (controller_detail_list_layout, 'left', 5,
                #  controller_list_layout),
            ])
        pm.setParent("..")
        pm.setParent("..")
        return layout

    def tab_test_controller(self):
        controller_test_list_layout = pm.formLayout()
        create_test_controller_btn = pm.button(
            label=u"创建测试控制器",
            c=lambda *args: self.create_editor_test_controller())
        test_scroll = pm.scrollLayout(
            "controllerTestListLayout", height=400)
        pm.setParent("..")
        pm.formLayout(
            controller_test_list_layout, edit=True,
            attachForm=[
                (create_test_controller_btn, 'top', 10),
                (create_test_controller_btn, 'left', 10),
                (create_test_controller_btn, 'right', 10),
                (test_scroll, "left", 10),
                (test_scroll, "right", 10),
            ],
            attachControl=[
                (test_scroll, 'top', 5, create_test_controller_btn),
            ])
        pm.setParent("..")
        return controller_test_list_layout

    def tab_controller_joint(self):
        layout = pm.frameLayout(label=u"Joint List:", w=350, bgs=True)
        controller_detail_list_layout = pm.scrollLayout(
            "controllerDetailListLayout", height=400)
        pm.setParent("..")
        pm.setParent("..")
        return layout

    def tab_controller(self):
        layout = pm.frameLayout(label=u"Controller List:", w=350, bgs=True)
        controller_list_layout = pm.formLayout()

        pm.scrollLayout("controllerListLayout", h=650)
        pm.setParent("..")

        pm.formLayout(
            controller_list_layout, edit=True,
            attachForm=[
                ("controllerListLayout", 'top', 5),
                ("controllerListLayout", 'left', 10),
                ("controllerListLayout", 'right', 10),

            ],
            attachControl=[
                # ("controllerListLayout", 'bottom', 10, save_data_btn),
            ])
        pm.setParent("..")
        pm.setParent("..")
        return layout

    def create_editor_test_controller(self):
        selected_module = pm.optionMenuGrp(
            "faceModuleOptionsWidget", q=True, value=True)

        controller_file = "%s/%s/%sController.json" % (
            self.json_folder, selected_module, selected_module)

        control_group_file = "%s/%s/%sControlGroup.json" % (
            self.json_folder, selected_module, selected_module)

        dict_data = common.read_json(file_path=controller_file)

        detail_data = common.read_json(file_path=control_group_file)

        for controller in dict_data["%sController" % selected_module]:
            self.editor_test_controller(
                controller,
                detail_data[controller["controllerName"]])

        return

    def editor_test_controller(self, controller={}, detail_data={}):
        test_controller = test_node.TestEditorController()
        test_controller.get_controller_from_data(controller, detail_data)
        test_controller.create_locator_controller()

        return test_controller

    def add_slider_for_selected(self):
        print(pm.textScrollList("ARIDScrollList", q=True, si=True)[0])

        selected_key = pm.textScrollList("ARIDScrollList", q=True, si=True)[0]
        print(self.ar_data[selected_key])

        if not pm.objExists(selected_key):
            self.create_slider_controller(name=selected_key)

        return

    def create_slider_controller(self, name):
        locator = helper.zero_locator(name=name)
        pm.addAttr(locator, ln="sliderX", at="double", min=0, max=1, dv=0)
        pm.setAttr("%s.sliderX" % locator, e=True, k=True)

        return

    def discard_tab(self):
        """
        历史遗留版本
        """
        layout = pm.formLayout()

        self.module_id_field = pm.intFieldGrp(label=u"道具ID", cw2=[50, 100])

        self.discard_child_tab_layout = pm.tabLayout(
            "jsonManagerMainTabLayout",
            innerMarginWidth=5,
            innerMarginHeight=5)
        child_brow = self.child_brow_tab()
        child_eye = self.child_eye_tab()
        child_nose = self.child_nose_tab()
        child_mouth = self.child_mouth_tab()
        child_face = self.child_face_tab()

        pm.tabLayout(
            self.discard_child_tab_layout,
            edit=True,
            tabLabel=(
                (child_brow, u'眉毛'),
                (child_eye, u'眼睛'),
                (child_nose, u'鼻子'),
                (child_mouth, u'嘴巴'),
                (child_face, u'脸型'),
            ),
            # sti=1,
        )
        pm.setParent("..")

        self.sava_json_btn = pm.button(
            label=u"保存JSON文件",
            c=lambda *args: self.save_data_to_json())

        pm.formLayout(
            layout,
            edit=True,
            attachForm=[
                (self.module_id_field, 'top', 5),
                (self.module_id_field, 'left', 5),
                (self.module_id_field, 'right', 5),
                (self.discard_child_tab_layout, 'top', 5),
                (self.discard_child_tab_layout, 'left', 10),
                (self.discard_child_tab_layout, 'right', 10),
                (self.sava_json_btn, 'left', 10),
                (self.sava_json_btn, 'right', 10),
                (self.sava_json_btn, 'bottom', 10),
            ],
            attachControl=[
                (self.discard_child_tab_layout, 'top', 10,
                 self.module_id_field),
                (self.discard_child_tab_layout, 'bottom', 10,
                 self.sava_json_btn),
            ])

        return layout

    def initialize(self):
        if pm.optionVar(q='jsonManagerFolder'):
            self.json_folder = pm.optionVar(
                q='jsonManagerFolder')
            pm.textFieldButtonGrp(
                self.config_input, e=True, text=self.json_folder)

            self.module_sections = self.scanning_folder("folders")

            if len(self.module_sections) > 0:
                for json_file in self.module_sections:
                    pm.menuItem(label=json_file)
                pm.optionMenuGrp("faceModuleOptionsWidget", e=True, sl=1)
                self.action_selected_controller(
                    pm.optionMenuGrp("faceModuleOptionsWidget",
                                     q=True, value=True))

        if pm.optionVar(q='jsonManagerMainTabLayoutIndex'):
            self.current_tab_index = int(pm.optionVar(
                q='jsonManagerMainTabLayoutIndex'))

        if pm.optionVar(q='jsonManagerDiscardBrowFilePath'):
            self.brow_file_folder = pm.optionVar(
                q='jsonManagerDiscardBrowFilePath')
        if pm.optionVar(q='jsonManagerDiscardEyeFilePath'):
            self.eye_file_folder = pm.optionVar(
                q='jsonManagerDiscardEyeFilePath')
        if pm.optionVar(q='jsonManagerDiscardNoseFilePath'):
            self.nose_file_folder = pm.optionVar(
                q='jsonManagerDiscardNoseFilePath')
        if pm.optionVar(q='jsonManagerDiscardMouthFilePath'):
            self.mouth_file_folder = pm.optionVar(
                q='jsonManagerDiscardMouthFilePath')
        if pm.optionVar(q='jsonManagerDiscardFaceFilePath'):
            self.face_file_folder = pm.optionVar(
                q='jsonManagerDiscardFaceFilePath')

    def _closed_window_cmd(self):
        pm.optionVar(sv=('jsonManagerFolder', self.json_folder))
        pm.optionVar(sv=('arFileLocation', self.ar_file_location))

        self.current_tab_index = pm.tabLayout(
            self.main_tab, q=True, sti=True)
        pm.optionVar(
            sv=('jsonManagerMainTabLayoutIndex', self.current_tab_index))

        pm.optionVar(
            sv=('jsonManagerDiscardBrowFilePath', self.brow_file_folder))
        pm.optionVar(
            sv=('jsonManagerDiscardEyeFilePath', self.eye_file_folder))
        pm.optionVar(
            sv=('jsonManagerDiscardNoseFilePath', self.nose_file_folder))
        pm.optionVar(
            sv=('jsonManagerDiscardMouthFilePath', self.mouth_file_folder))
        pm.optionVar(
            sv=('jsonManagerDiscardFaceFilePath', self.face_file_folder))

    def setting_json_folder(self):
        json_folder = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3, okc=u"选择文件夹")

        # print(json_folder)

        if json_folder:
            self.json_folder = json_folder[0]
            self.module_sections = self.scanning_folder("folders")
            pm.textFieldButtonGrp(
                self.config_input, e=True, text=json_folder[0])

        return

    def scanning_folder(self, return_type):
        """
        扫描文件件，将目录列取出来，如果目录下有对应的文件（例：文件夹名face, 对应的文件）
        """
        json_list = []
        folder_list = []
        if self.json_folder != '':
            path_dir = os.listdir(self.json_folder)

            for json_file in path_dir:
                full_path = "%s/%s" % (self.json_folder, json_file)
                if os.path.isdir(full_path):
                    print("%s it's a directory" % full_path)
                    folder_list.append(json_file)
                elif os.path.isfile(full_path):
                    print("%s it's a normal file" % full_path)
                    # 获取JSON文件的名字后，清理文件的后缀名
                    file_name = os.path.splitext(json_file)[0]
                    json_list.append(file_name)
        if return_type == "files":
            return json_file
        elif return_type == "folders":
            return folder_list

    def option_menu_widget(self, parent_widget):
        if pm.optionMenuGrp("faceModuleOptionsWidget", ex=True):
            pm.deleteUI("faceModuleOptionsWidget")
        widget = pm.optionMenuGrp(
            "faceModuleOptionsWidget",
            parent=parent_widget,
            label=u"模块名称",
            cw2=[50, 100],
            # adj=2,
            cc=lambda *args: self.action_selected_controller(
                pm.optionMenuGrp(widget, q=True, value=True)))
        if len(self.module_sections) > 0:
            for json_file in self.module_sections:
                pm.menuItem(label=json_file)

        return widget

    def action_selected_controller(self, module):
        """
        选择控制器
        """
        selected_controller = pm.optionMenuGrp(
            "faceModuleOptionsWidget", q=True, value=True)
        # print("selected controller: %s" % selected_controller)

        controller_file = "%s/%s/%sController.json" % (
            self.json_folder, module, module)

        controller_group_file = "%s/%s/%sControlGroup.json" % (
            self.json_folder, module, module)

        # print(controller_file)

        controller_list = pm.scrollLayout(
            "controllerListLayout", q=True, ca=True)

        detail_list = pm.scrollLayout(
            "controllerDetailListLayout", q=True, ca=True)

        if controller_list is not None:
            # print controller_list
            for child in controller_list:
                pm.deleteUI(child)

        if detail_list is not None:
            for child in detail_list:
                pm.deleteUI(child)

        dict_data = None
        with open(controller_file, 'r') as data:
            dict_data = json.load(data)
            # print(dict_data)
        controller_key = "%sController" % module

        for index in range(0, len(dict_data[controller_key])):
            self.add_controller_widget(
                index=index, parent="controllerListLayout")

            pm.textFieldButtonGrp(
                "controllerNameWidget%s" % index, e=True,
                text=dict_data[controller_key][index]["controllerName"])
            pm.textFieldButtonGrp(
                "controllerGrpNameWidget%s" % index, e=True,
                text=dict_data[controller_key][index]["ControllerGroupName"])
            pm.textFieldButtonGrp(
                "controllerBoneNameWidget%s" % index, e=True,
                text=dict_data[controller_key][index]["ControllerBoneName"])

            offset_value = dict_data[
                controller_key][index]["ControllerPositionOffset"]
            pm.floatFieldGrp(
                "controllerBoneOffsetWidget%s" % index,
                e=True,
                value1=offset_value[0],
                value2=offset_value[1],
                value3=offset_value[2])

            pm.textFieldGrp(
                "controller%sAxisX" % index, e=True,
                text=dict_data[controller_key][index]["AxisControl"]["XAxis"])
            pm.textFieldGrp(
                "controller%sAxisY" % index, e=True,
                text=dict_data[controller_key][index]["AxisControl"]["YAxis"])
            pm.textFieldGrp(
                "controller%sAxisZ" % index, e=True,
                text=dict_data[controller_key][index]["AxisControl"]["ZAxis"])

        joint_data = None
        with open(controller_group_file, 'r') as data:
            joint_data = json.load(data)
            print(joint_data)

        joint_key = joint_data.keys()
        print(joint_key)
        for index in range(0, len(joint_key)):
            self.add_control_detail_widget(parent="controllerDetailListLayout")

    def add_module(self):
        """
        添加模块

        模块实际上是一个文件夹。
        每当新建一个模块，程序会在文件夹下面创建两个JSON文件。分别为控制器文件和控制器的细节信息文件。
        例如：
            模块名 Face
                控制器文件 FaceController.json
                细节文件 FaceControlGroup.json

        :return: True
        """

        # 文件模模式
        file_path = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3,
            okc=u"设置模块路径")
        folder_name = file_path[0].split("/")[len(file_path[0].split("/")) - 1]

        # 将新添加的模块添加到菜单项
        pm.menuItem(label=folder_name,
                    parent="faceModuleOptionsWidget|OptionMenu")

        controller_path = "%s/%sController.json" % (
            file_path[0], folder_name)

        dict_data = {}
        controller_key = "%sController" % folder_name
        dict_data[controller_key] = []
        common.write_json(
            dict_data=dict_data,
            file_path=controller_path)
        control_group_path = "%s/%sControlGroup.json" % (
            file_path[0], folder_name)
        common.write_json(
            dict_data={},
            file_path=control_group_path)

        # 将菜单栏的当前选择修改为新添加的模块
        pm.optionMenuGrp("faceModuleOptionsWidget", e=True, value=folder_name)

        return True

    def add_controller(self):
        controller_index = pm.scrollLayout(
            "controllerListLayout", q=True, nch=True)
        self.controller[controller_index] = (
            "controllerGrp%s" % controller_index)
        self.add_controller_widget(
            index=controller_index, parent="controllerListLayout")

    def add_controller_widget(self, index=0, parent=""):
        if pm.columnLayout(
                "controllerListItemLayout%s" % index, q=True, ex=True):
            pm.deleteUI("controllerListItemLayout%s" % index)

        layout = pm.columnLayout(
            "controllerListItemLayout%s" % index,
            adj=1, parent=parent)

        pm.textFieldButtonGrp(
            "controllerNameWidget%s" % index,
            label=u"控制器名", cw3=[60, 200, 140], bl=u"指定",
            bc=lambda *args: self.get_custom_controller(index))
        pm.textFieldButtonGrp(
            "controllerGrpNameWidget%s" % index,
            label=u"控制器组", cw3=[60, 200, 140], bl=u"指定")
        pm.textFieldButtonGrp(
            "controllerBoneNameWidget%s" % index,
            label=u"挂点名称",
            cw3=[60, 200, 140], bl=u"指定",
            bc=lambda *args: self.get_sample_node(
                text_widget="controllerBoneNameWidget%s" % index))
        pm.floatFieldGrp(
            "controllerBoneOffsetWidget%s" % index,
            numberOfFields=3,
            pre=3,
            label=u'挂点偏移', cw4=[60, 50, 50, 50])

        pm.textFieldGrp(
            "controller%sAxisX" % index, label=u"XAxis", cw2=[60, 200])
        pm.textFieldGrp(
            "controller%sAxisY" % index, label=u"YAxis", cw2=[60, 200])
        pm.textFieldGrp(
            "controller%sAxisZ" % index, label=u"ZAxis", cw2=[60, 200])

        pm.separator(style='in', height=20)

        pm.setParent("..")  # end of layout

        return layout

    def add_control_detail_widget(self, parent):
        for index in range(0, pm.scrollLayout(
                "controllerListLayout", q=True, nch=True)):

            if pm.frameLayout(
                    "controllerDetailListItemLayout%s" % index,
                    q=True, ex=True):
                pm.deleteUI("controllerDetailListItemLayout%s" % index)

            pm.frameLayout(
                "controllerDetailListItemLayout%s" % index,
                bgs=True,
                mw=10, mh=5,
                cll=True,
                cl=False,
                parent=parent)
            pm.textFieldButtonGrp(
                "controllerDetailControlType%s" % index,
                label=u"控制类型", bl=u"指定", cw3=[48, 200, 140])
            pm.textFieldButtonGrp(
                "controllerDetailControlGroup%s" % index,
                label=u"控制器组", bl=u"指定", cw3=[48, 200, 140])
            pm.text(label=u"滑竿控制", al="left", width=100)
            pm.text(label="SliderX:", al="left")
            pm.textScrollList(
                "controllerDetailSliderXBone%s" % index)
            pm.text(label="SliderY:", al="left")
            pm.textScrollList(
                "controllerDetailSliderYBone%s" % index)
            pm.text(label="SliderZ:", al="left")
            pm.textScrollList(
                "controllerDetailSliderZBone%s" % index)
            pm.setParent("..")

            # 自动录入一些数据
            frame_label = pm.textFieldButtonGrp(
                "controllerNameWidget%s" % index, q=True, text=True)
            pm.frameLayout(
                "controllerDetailListItemLayout%s" % index,
                e=True, label=frame_label)

            control_type = pm.optionMenuGrp(
                "faceModuleOptionsWidget", q=True, value=True)
            pm.textFieldButtonGrp(
                "controllerDetailControlType%s" % index,
                e=True, text=control_type)

            control_grp = pm.textFieldButtonGrp(
                "controllerGrpNameWidget%s" % index, q=True, text=True)
            pm.textFieldButtonGrp(
                "controllerDetailControlGroup%s" % index,
                e=True, text=control_grp)

            control_name = pm.textFieldButtonGrp(
                "controllerNameWidget%s" % index, q=True, text=True)

            axia_X = pm.textFieldGrp(
                "controller%sAxisX" % index, q=True, text=True)
            if axia_X != "" and axia_X is not None:
                definition_joints = pm.PyNode(
                    control_name).attr("jointsX").get()
                pm.textScrollList(
                    "controllerDetailSliderXBone%s" % index,
                    e=True,
                    a=helper.str_to_list(definition_joints))

            axia_Y = pm.textFieldGrp(
                "controller%sAxisY" % index, q=True, text=True)
            if axia_Y != "" and axia_Y is not None:
                definition_joints = pm.PyNode(
                    control_name).attr("jointsY").get()
                pm.textScrollList(
                    "controllerDetailSliderYBone%s" % index,
                    e=True,
                    a=helper.str_to_list(definition_joints))

            axia_Z = pm.textFieldGrp(
                "controller%sAxisZ" % index, q=True, text=True)
            if axia_Z != "" and axia_Z is not None:
                definition_joints = pm.PyNode(
                    control_name).attr("jointsZ").get()
                pm.textScrollList(
                    "controllerDetailSliderZBone%s" % index,
                    e=True,
                    a=helper.str_to_list(definition_joints))

        return

    def get_sample_node(self, text_widget):
        """
        获取样本节点

        :param text_widget: 保存样本节点的文本输入框的名字
        :return: 样本节点的名字（字符串）
        """
        source_sample = pm.ls(sl=True)[0]
        pm.textFieldButtonGrp(text_widget, e=True, text=source_sample)
        return source_sample

    def get_custom_controller(self, index):
        custom_controller = self.get_sample_node(
            text_widget="controllerNameWidget%s" % index)
        # print custom_controller
        if "sliderX" in pm.listAttr(custom_controller, k=True):
            pm.textFieldButtonGrp("")
            pm.textFieldGrp(
                "controller%sAxisX" % index, e=True, text="sliderX")
        if "sliderY" in pm.listAttr(custom_controller, k=True):
            pm.textFieldGrp(
                "controller%sAxisY" % index, e=True, text="sliderY")
        if "sliderZ" in pm.listAttr(custom_controller, k=True):
            pm.textFieldGrp(
                "controller%sAxisZ" % index, e=True, text="sliderZ")
        return

    def generate_custom_data(self):
        dict_data = {}
        self.dict_data = list()

        for index in range(0, pm.scrollLayout(
                "controllerListLayout", q=True, nch=True)):
            dict_data = {}
            axis_control = {}

            dict_data["controllerName"] = pm.textFieldButtonGrp(
                "controllerNameWidget%s" % index, q=True, text=True)
            dict_data["ControllerGroupName"] = pm.textFieldButtonGrp(
                "controllerGrpNameWidget%s" % index, q=True, text=True)
            dict_data["ControllerBoneName"] = pm.textFieldButtonGrp(
                "controllerBoneNameWidget%s" % index, q=True, text=True)
            dict_data["ControllerPositionOffset"] = pm.floatFieldGrp(
                "controllerBoneOffsetWidget%s" % index, q=True, value=True)

            axis_control["XAxis"] = pm.textFieldGrp(
                "controller%sAxisX" % index, q=True, text=True)
            axis_control["YAxis"] = pm.textFieldGrp(
                "controller%sAxisY" % index, q=True, text=True)
            axis_control["ZAxis"] = pm.textFieldGrp(
                "controller%sAxisZ" % index, q=True, text=True)

            dict_data["AxisControl"] = axis_control

            self.dict_data.append(dict_data)

    def joint_cb_list(self, jnt, pre=5):
        """
        骨骼在通道里面的值

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

    def generate_custom_detail_data(self):
        """
        生成自定义捏脸的细节数据

        细节包括各个空间包含的骨骼的位移信息

        :return:
        """
        dict_data = {}
        self.detail_data = {}

        print("Detail item : %s" % pm.scrollLayout(
            "controllerDetailListLayout", q=True, nch=True))

        for index in range(0, pm.scrollLayout(
                "controllerDetailListLayout", q=True, nch=True)):
            # dict_data = {}

            key_name = pm.frameLayout(
                "controllerDetailListItemLayout%s" % index,
                q=True, label=True)
            dict_data[key_name] = {}
            dict_data[key_name]["shapeType"] = pm.optionMenuGrp(
                "faceModuleOptionsWidget", q=True, value=True)
            dict_data[key_name]["GroupName"] = pm.textFieldButtonGrp(
                "controllerDetailControlGroup%s" % index, q=True, text=True)

            dict_data[key_name]["ControlGroup"] = []

            axia_X = {}
            axia_X["GroupName"] = "%s_X" % key_name
            axia_X["BoneRange"] = []

            for jnt in pm.textScrollList(
                    "controllerDetailSliderXBone%s" % index, q=True, ai=True):
                jnt_dict = dict()
                jnt_dict["BoneName"] = jnt
                jnt_dict["Max"] = []
                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderX"), 1)
                    jnt_dict["Max"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderX"), 0)
                jnt_dict["Min"] = []
                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderX"), -1)
                    jnt_dict["Min"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderX"), 0)

                axia_X["BoneRange"].append(jnt_dict)
            dict_data[key_name]["ControlGroup"].append(axia_X)

            axia_Y = {}
            axia_Y["GroupName"] = "%s_Y" % key_name
            axia_Y["BoneRange"] = []

            for jnt in pm.textScrollList(
                    "controllerDetailSliderYBone%s" % index, q=True, ai=True):
                jnt_dict = dict()
                jnt_dict["BoneName"] = jnt
                jnt_dict["Max"] = []
                jnt_dict["Min"] = []

                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderY"), 1)
                    jnt_dict["Max"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderY"), 0)
                jnt_dict["Min"] = []
                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderY"), -1)
                    jnt_dict["Min"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderY"), 0)

                axia_Y["BoneRange"].append(jnt_dict)
            dict_data[key_name]["ControlGroup"].append(axia_Y)

            axia_Z = {}
            axia_Z["GroupName"] = "%s_Z" % key_name
            axia_Z["BoneRange"] = []

            for jnt in pm.textScrollList(
                    "controllerDetailSliderZBone%s" % index, q=True, ai=True):
                jnt_dict = dict()
                jnt_dict["BoneName"] = jnt
                jnt_dict["Max"] = []
                jnt_dict["Min"] = []

                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderZ"), 1)
                    jnt_dict["Max"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderZ"), 0)
                jnt_dict["Min"] = []
                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderZ"), -1)
                    jnt_dict["Min"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp(
                        "controllerNameWidget%s" % index,
                        q=True, text=True)).attr("sliderZ"), 0)

                axia_Z["BoneRange"].append(jnt_dict)

            dict_data[key_name]["ControlGroup"].append(axia_Z)

        self.detail_data = dict_data
        return

    def save_custom_data(self):
        """
        保存自定义捏脸数据

        :return: None
        """
        menu_item_selected = pm.optionMenuGrp(
            "faceModuleOptionsWidget", q=True, value=True)

        self.generate_custom_data()
        control_file_path = "%s/%s/%sController.json" % (
            self.json_folder, menu_item_selected, menu_item_selected)

        controller_data = {}
        controller_data["%sController" % menu_item_selected] = self.dict_data
        with open(control_file_path, "w") as f:
            json.dump(controller_data, f, indent=4)

        self.generate_custom_detail_data()
        detail_file_path = "%s/%s/%sControlGroup.json" % (
            self.json_folder, menu_item_selected, menu_item_selected)
        with open(detail_file_path, "w") as f:
            json.dump(self.detail_data, f, indent=4)

        print(u"保存成功")

        return

    def widget_discard_slider(self, ID_name="ID1", ID_num=12):
        for ID_index in range(1, ID_num + 1):
            pm.floatSliderGrp(
                "slider_%s_%s" % (ID_name, ID_index),
                label=u"%s.%s" % (ID_name, ID_index),
                field=True,
                minValue=0,
                maxValue=1.0,
                fieldMinValue=0,
                fieldMaxValue=1.0,
                pre=3,
                adj=3,
                value=0,
                cw3=[60, 60, 100])
            pm.connectControl(
                "slider_%s_%s" % (ID_name, ID_index),
                '%s_%s.sliderX' % (ID_name, ID_index))
        return

    def child_brow_tab(self):
        layout = pm.columnLayout(adj=1, rs=5)
        pm.rowColumnLayout(numberOfColumns=2)
        self.widget_discard_slider(ID_name="ID5", ID_num=12)
        pm.setParent('..')
        self.brow_discard_path_field = pm.textFieldButtonGrp(
            label=u"存放路径",
            bl=u"指定路径",
            adj=2,
            text=self.brow_file_folder,
            cw3=[60, 200, 100],
            bc=lambda *args: self.setting_brow_file_folder())
        pm.setParent('..')
        return layout

    def setting_brow_file_folder(self):
        json_folder = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3, okc=u"选择文件夹")
        if json_folder:
            pm.textFieldButtonGrp(
                self.brow_discard_path_field,
                e=True,
                text=json_folder[0])
            self.brow_file_folder = json_folder[0]
        return

    def child_eye_tab(self):
        layout = pm.columnLayout(adj=1)
        pm.rowColumnLayout(numberOfColumns=2)
        self.widget_discard_slider(ID_name="ID1", ID_num=16)
        pm.setParent('..')
        self.eye_discard_path_field = pm.textFieldButtonGrp(
            label=u"存放路径",
            bl=u"创建Json文件",
            adj=2,
            text=self.eye_file_folder,
            cw3=[60, 200, 100],
            bc=lambda *args: self.setting_eye_file_folder())
        pm.setParent('..')
        return layout

    def setting_eye_file_folder(self):
        json_folder = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3, okc=u"选择文件夹")
        if json_folder:
            pm.textFieldButtonGrp(
                self.eye_discard_path_field,
                e=True,
                text=json_folder[0])
            self.eye_file_folder = json_folder[0]
        return

    def child_nose_tab(self):
        layout = pm.columnLayout(adj=1)
        pm.rowColumnLayout(numberOfColumns=2)
        self.widget_discard_slider(ID_name="ID2", ID_num=14)
        pm.setParent('..')
        self.nose_discard_path_field = pm.textFieldButtonGrp(
            label=u"存放路径",
            bl=u"创建Json文件",
            adj=2,
            text=self.nose_file_folder,
            cw3=[60, 200, 100],
            bc=lambda *args: self.setting_nose_file_folder())
        pm.setParent('..')
        return layout

    def setting_nose_file_folder(self):
        json_folder = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3, okc=u"选择文件夹")
        if json_folder:
            pm.textFieldButtonGrp(
                self.nose_discard_path_field,
                e=True,
                text=json_folder[0])
            self.nose_file_folder = json_folder[0]
        return

    def child_mouth_tab(self):
        layout = pm.columnLayout(adj=1)
        pm.rowColumnLayout(numberOfColumns=2)
        self.widget_discard_slider(ID_name="ID3", ID_num=18)
        pm.setParent('..')
        self.mouth_discard_path_field = pm.textFieldButtonGrp(
            label=u"存放路径",
            bl=u"创建Json文件",
            adj=2,
            text=self.mouth_file_folder,
            cw3=[60, 200, 100],
            bc=lambda *args: self.setting_mouth_file_folder())
        pm.setParent('..')
        return layout

    def setting_mouth_file_folder(self):
        json_folder = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3, okc=u"选择文件夹")
        if json_folder:
            pm.textFieldButtonGrp(
                self.mouth_discard_path_field,
                e=True,
                text=json_folder[0])
            self.mouth_file_folder = json_folder[0]
        return

    def child_face_tab(self):
        layout = pm.columnLayout(adj=1)
        pm.rowColumnLayout(numberOfColumns=2)
        self.widget_discard_slider(ID_name="ID4", ID_num=14)
        pm.setParent('..')
        self.face_discard_path_field = pm.textFieldButtonGrp(
            label=u"存放路径",
            bl=u"创建Json文件",
            adj=2,
            text=self.face_file_folder,
            cw3=[60, 200, 100],
            bc=lambda *args: self.setting_face_file_folder())
        pm.setParent('..')
        return layout

    def setting_face_file_folder(self):
        json_folder = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3, okc=u"选择文件夹")
        if json_folder:
            pm.textFieldButtonGrp(
                self.face_discard_path_field,
                e=True,
                text=json_folder[0])
            self.face_file_folder = json_folder[0]
        return

    def save_brow_data_to_json(self):
        jnt_list = [
            "definition_M_brow",
            "definition_L_brow_1",
            "definition_L_brow_2",
            "definition_L_brow_3",
            "definition_L_brow_4",
            "definition_L_brow_5",
            "definition_R_brow_1",
            "definition_R_brow_2",
            "definition_R_brow_3",
            "definition_R_brow_4",
            "definition_R_brow_5",
        ]

        dict_data = {}
        module_id = pm.intFieldGrp(
            self.module_id_field, q=True, value=True)[0]
        dict_data['ID'] = module_id
        dict_data['BoneRange'] = {}
        for jnt in jnt_list:
            dict_data['BoneRange'][jnt] = self.joint_cb_list(jnt=jnt)

        file_path = "%s/%s.json" % (self.brow_file_folder, module_id)

        with open(file_path, "w") as f:
            json.dump(dict_data, f, indent=2)

        print(u"Brow通道：%s 数据保存成功！" % module_id)

        return

    def save_eye_data_to_json(self):
        jnt_list = [
            "L_eyeBall_socket",
            "R_eyeBall_socket",
            "definition_facial_L_TLidInn",
            "definition_facial_L_TLidMid",
            "definition_facial_L_TLidOut",
            "definition_facial_L_BLidInn",
            "definition_facial_L_BLidMid",
            "definition_facial_L_BLidOut",
            "definition_facial_R_TLidOut",
            "definition_facial_R_TLidMid",
            "definition_facial_R_TLidInn",
            'definition_facial_R_BLidInn',
            "definition_facial_R_BLidMid",
            "definition_facial_R_BLidOut",
        ]

        dict_data = {}
        module_id = pm.intFieldGrp(
            self.module_id_field, q=True, value=True)[0]
        dict_data['ID'] = module_id
        dict_data['BoneRange'] = {}
        for jnt in jnt_list:
            dict_data['BoneRange'][jnt] = self.joint_cb_list(jnt=jnt)

        file_path = "%s/%s.json" % (self.eye_file_folder, module_id)

        with open(file_path, "w") as f:
            json.dump(dict_data, f, indent=2)

        print(u"Eye通道：%s 数据保存成功！" % module_id)

        return

    def save_nose_data_to_json(self):
        jnt_list = [
            "L_eyeBall_socket",
            "R_eyeBall_socket",
            "definition_facial_C_NoseTip",
            "definition_facial_R_Nostril",
            "definition_facial_L_Nostril",
            "definition_facial_R_NoseBase",
            "definition_facial_L_NoseBase",
            "facial_C_Nose_JNT",
            "definition_facial_C_NoseBridge",
        ]

        dict_data = {}
        module_id = pm.intFieldGrp(
            self.module_id_field, q=True, value=True)[0]
        dict_data['ID'] = module_id
        dict_data['BoneRange'] = {}
        for jnt in jnt_list:
            dict_data['BoneRange'][jnt] = self.joint_cb_list(jnt=jnt)

        file_path = "%s/%s.json" % (self.nose_file_folder, module_id)

        with open(file_path, "w") as f:
            json.dump(dict_data, f, indent=2)

        print(u"Nose通道：%s 数据保存成功！" % module_id)

        return

    def save_mouth_data_to_json(self):
        jnt_list = [u'definition_L_LowLipInn_mid',
                    u'definition_L_LowLipInn_inner',
                    u'definition_L_LowLipInn_outer',
                    u'definition_Mouth_L_LowLipInn',
                    u'definition_L_LowLipMid_mid',
                    u'definition_L_LowLipMid_inner',
                    u'definition_L_LowLipMid_outer',
                    u'definition_L_LowLipOut_mid',
                    u'definition_L_LowLipOut_inner',
                    u'definition_L_LowLipOut_outer',
                    u'definition_Mouth_L_LowLipOut',
                    u'Mouth_C_All_JNT',
                    u'definition_Mouth_L_UpLipInn',
                    u'definition_L_UpLipInn_outer',
                    u'definition_L_UpLipInn_inner',
                    u'definition_L_UpLipInn_mid',
                    u'definition_Mouth_L_UpLipMid',
                    u'definition_L_UpLipMid_outer',
                    u'definition_L_UpLipMid_inner',
                    u'definition_L_UpLipMid_mid',
                    u'definition_Mouth_L_UpLipOut',
                    u'definition_L_UpLipOut_outer',
                    u'definition_L_UpLipOut_inner',
                    u'definition_L_UpLipOut_mid',
                    u'definition_Mouth_L_Corner',
                    u'definition_Mouth_C_UpLip',
                    u'definition_C_UpLip_outer',
                    u'definition_C_UpLip_inner',
                    u'definition_C_UpLip_mid',
                    u'definition_Mouth_C_LowLip',
                    u'definition_C_LowLip_outer',
                    u'definition_C_LowLip_inner',
                    u'definition_C_LowLip_mid',
                    u'definition_Mouth_R_UpLipMid',
                    u'definition_R_UpLipMid_outer',
                    u'definition_R_UpLipMid_inner',
                    u'definition_R_UpLipMid_mid',
                    u'definition_Mouth_R_UpLipInn',
                    u'definition_R_UpLipInn_outer',
                    u'definition_R_UpLipInn_inner',
                    u'definition_R_UpLipInn_mid',
                    u'definition_Mouth_R_UpLipOut',
                    u'definition_R_UpLipOut_outer',
                    u'definition_R_UpLipOut_inner',
                    u'definition_R_UpLipOut_mid',
                    u'definition_Mouth_R_Corner',
                    u'definition_Mouth_R_LowLipOut',
                    u'definition_R_LowLipOut_outer',
                    u'definition_R_LowLipOut_inner',
                    u'definition_R_LowLipOut_mid',
                    u'definition_R_LowLipMid_mid',
                    u'definition_R_LowLipMid_inner',
                    u'definition_R_LowLipMid_outer',
                    u'definition_Mouth_R_LowLipMid',
                    u'definition_R_LowLipInn_mid',
                    u'definition_R_LowLipInn_inner',
                    u'definition_R_LowLipInn_outer',
                    u'definition_Mouth_R_LowLipInn',
                    u'definition_Mouth_L_LowLipMid']

        dict_data = {}
        module_id = pm.intFieldGrp(
            self.module_id_field, q=True, value=True)[0]
        dict_data['ID'] = module_id
        dict_data['BoneRange'] = {}
        for jnt in jnt_list:
            dict_data['BoneRange'][jnt] = self.joint_cb_list(jnt=jnt)

        file_path = "%s/%s.json" % (self.mouth_file_folder, module_id)

        with open(file_path, "w") as f:
            json.dump(dict_data, f, indent=2)

        print(u"Mouth通道：%s 数据保存成功！" % module_id)

        return

    def save_data_to_json(self):
        tab_array = ['brow', 'eye', 'nose', 'mouth', 'face']
        current_tab_index = pm.tabLayout(
            self.discard_child_tab_layout,
            q=True,
            sti=True) - 1

        print(tab_array[current_tab_index])

        if tab_array[current_tab_index] == 'brow':
            self.save_brow_data_to_json()
        if tab_array[current_tab_index] == 'eye':
            self.save_eye_data_to_json()
        if tab_array[current_tab_index] == 'nose':
            self.save_nose_data_to_json()
        if tab_array[current_tab_index] == 'mouth':
            self.save_mouth_data_to_json()
        if tab_array[current_tab_index] == 'face':
            pass

        return


class FaceMakerEditor(common.Singleton):
    def __init__(self):
        super(FaceMakerEditor, self).__init__()

        self.json_folder = ''
        self.module_sections = []

        self.module_context = ""

        self.dict_data = list()
        self.detail_data = dict()

        self.controller = {}
        self.controller_detail = {}

        self.current_tab_index = 1

        # 历史版本的json文件存放路径
        self.brow_file_folder = ""
        self.eye_file_folder = ""
        self.nose_file_folder = ""
        self.mouth_file_folder = ""
        self.face_file_folder = ""

        self.show()
        self.initialize()

    def show(self):
        """
        显示工具窗口

        :return: window
        """
        if pm.window("faceMakerWnd", ex=True):
            pm.deleteUI("faceMakerWnd")
        pm.window(
            "faceMakerWnd",
            t=u"捏脸数据编辑器 %s" % manager_version,
            mb=True,
            cc=lambda *args: self._closed_window_cmd())

        self.menu_list()

        main_layout = pm.formLayout()

        self.config_input = pm.textFieldButtonGrp(
            label=u"配置文件",
            bl=u"指定路径",
            adj=2,
            cw3=[53, 100, 100],
            p=main_layout,
            text=self.json_folder,
            bc=lambda *args: self.init_controller_list())

        option_menu = self.option_menu_widget(parent_widget=main_layout)

        controller_list_label = pm.text(label="Controller list:", al="left")
        self.controller_list_widget = pm.textScrollList(
            w=150,
            sc=lambda *args: self.action_selected_controller())

        pm.scrollLayout("controllerListLayout", w=330, p=main_layout)

        pm.columnLayout(
            "controllerItemLayout",
            adj=1,
            parent="controllerListLayout")

        pm.textFieldButtonGrp(
            "controllerNameWidget",
            label=u"控制器名", cw3=[60, 200, 140], bl=u"指定",
            # bc=lambda *args: self.get_custom_controller(index)
        )
        pm.textFieldButtonGrp(
            "controllerGrpNameWidget",
            label=u"控制器组", cw3=[60, 200, 140], bl=u"指定")
        pm.textFieldButtonGrp(
            "controllerBoneNameWidget",
            label=u"挂点名称",
            cw3=[60, 200, 140], bl=u"指定",
            # bc=lambda *args: self.get_sample_node(
            #     text_widget="controllerBoneNameWidget%s" % index)
        )
        pm.floatFieldGrp(
            # "controllerBoneOffsetWidget%s" % index,
            numberOfFields=3,
            pre=3,
            label=u'挂点偏移', cw4=[60, 50, 50, 50])

        pm.separator(style='none', height=5)
        pm.text(label="Slider list:", al="left")
        pm.textScrollList()

        pm.separator(style='in', height=20)

        pm.setParent("..")  # end of layout

        pm.formLayout(
            main_layout, edit=True,
            attachForm=[
                (self.config_input, 'top', 5),
                (self.config_input, 'left', 5),
                (self.config_input, 'right', 5),
                (option_menu, 'left', 5),
                (option_menu, 'right', 5),
                (controller_list_label, 'left', 10),
                (self.controller_list_widget, 'left', 10),
                (self.controller_list_widget, 'bottom', 10),
                ("controllerListLayout", 'bottom', 10),
            ],
            attachControl=[
                (option_menu, 'top', 5, self.config_input),
                (controller_list_label, 'top', 5, option_menu),
                (self.controller_list_widget, 'top', 5, controller_list_label),
                ("controllerListLayout", 'top', 5, controller_list_label),
                ("controllerListLayout", 'left', 5,
                 self.controller_list_widget),
            ])

        pm.showWindow("faceMakerWnd")

    def initialize(self):
        if pm.optionVar(q='jsonManagerFolder'):
            self.json_folder = pm.optionVar(
                q='jsonManagerFolder')
            pm.textFieldButtonGrp(
                self.config_input, e=True, text=self.json_folder)

            self.module_sections = self.scanning_folder("folders")

            if len(self.module_sections) > 0:
                for json_file in self.module_sections:
                    pm.menuItem(label=json_file)
                pm.optionMenuGrp("faceModuleOptionsWidget", e=True, sl=1)
                self.action_selected_module(
                    pm.optionMenuGrp("faceModuleOptionsWidget",
                                     q=True, value=True))

    def _closed_window_cmd(self):
        pass

    def menu_list(self):
        """
        工具菜单栏

        :return:
        """
        pm.menu(label=u"文件", tearOff=False)
        pm.menuItem(
            label=u"保存数据",
            c=lambda *args: self.save_custom_data())

        pm.menu(label=u"设置", tearOff=False)
        pm.menuItem(
            label=u"设置Json存放目录",
            c=lambda *args: self.setting_json_folder())
        pm.menuItem(
            label=u"调试模式", cb=False)

        pm.menu(label=u"模块", tearOff=False)
        pm.menuItem(
            label=u"增加模块",
            c=lambda *args: self.add_module())
        pm.menuItem(label=u"增加控制器", c=lambda *args: self.add_controller())
        pm.menuItem(
            label=u"增加控制器细节",
            c=lambda *args: self.add_control_detail_widget())

        pm.menu(label=u"测试", tearOff=False)
        pm.menuItem(
            label=u"创建测试控制器",
            c=lambda *args: self.create_editor_test_controller())

        return

    def setting_json_folder(self):
        json_folder = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3, okc=u"选择文件夹")

        if json_folder:
            self.json_folder = json_folder[0]
            self.module_sections = self.scanning_folder("folders")
            pm.textFieldButtonGrp(
                self.config_input, e=True, text=json_folder[0])

        return

    def scanning_folder(self, return_type):
        """
        扫描文件件，将目录列取出来，如果目录下有对应的文件（例：文件夹名face, 对应的文件）
        """
        json_list = []
        folder_list = []
        if self.json_folder != '':
            path_dir = os.listdir(self.json_folder)

            for json_file in path_dir:
                full_path = "%s/%s" % (self.json_folder, json_file)
                if os.path.isdir(full_path):
                    print("%s it's a directory" % full_path)
                    folder_list.append(json_file)
                elif os.path.isfile(full_path):
                    print("%s it's a normal file" % full_path)
                    # 获取JSON文件的名字后，清理文件的后缀名
                    file_name = os.path.splitext(json_file)[0]
                    json_list.append(file_name)
        if return_type == "files":
            return json_file
        elif return_type == "folders":
            return folder_list

    def init_controller_list(self):
        self.setting_json_folder()

        self.module_sections = self.scanning_folder("folders")
        if len(self.module_sections) > 0:
            for json_file in self.module_sections:
                pm.menuItem(label=json_file)
            pm.optionMenuGrp("faceModuleOptionsWidget", e=True, sl=1)
            self.action_selected_module(
                pm.optionMenuGrp("faceModuleOptionsWidget",
                                 q=True, value=True))

    def option_menu_widget(self, parent_widget):
        if pm.optionMenuGrp("faceModuleOptionsWidget", ex=True):
            pm.deleteUI("faceModuleOptionsWidget")
        widget = pm.optionMenuGrp(
            "faceModuleOptionsWidget",
            parent=parent_widget,
            label=u"模块名称",
            cw2=[50, 100],
            # adj=2,
            cc=lambda *args: self.action_selected_module(
                pm.optionMenuGrp(widget, q=True, value=True)))
        if len(self.module_sections) > 0:
            for json_file in self.module_sections:
                pm.menuItem(label=json_file)

        return widget

    def action_selected_module(self, module):
        """
        选择控制器
        """
        selected_controller = pm.optionMenuGrp(
            "faceModuleOptionsWidget", q=True, value=True)
        # print("selected controller: %s" % selected_controller)

        controller_file = "%s/%s/%sController.json" % (
            self.json_folder, module, module)

        controller_group_file = "%s/%s/%sControlGroup.json" % (
            self.json_folder, module, module)

        pm.textScrollList(self.controller_list_widget, e=True, ra=True)

        with open(controller_file, 'r') as data:
            self.dict_data = json.load(data)
        controller_key = "%sController" % module
        self.module_context = controller_key

        for index in range(0, len(self.dict_data[controller_key])):
            controller_name = (
                self.dict_data[controller_key][index]["controllerName"])
            pm.textScrollList(self.controller_list_widget, e=True,
                              a=controller_name)

        return

    def add_controller_widget(self, index=0, parent=""):
        if pm.columnLayout(
                "controllerListItemLayout%s" % index, q=True, ex=True):
            pm.deleteUI("controllerListItemLayout%s" % index)

        layout = pm.columnLayout(
            "controllerListItemLayout%s" % index,
            adj=1, parent=parent)

        pm.textFieldButtonGrp(
            "controllerNameWidget%s" % index,
            label=u"控制器名", cw3=[60, 200, 140], bl=u"指定",
            bc=lambda *args: self.get_custom_controller(index))
        pm.textFieldButtonGrp(
            "controllerGrpNameWidget%s" % index,
            label=u"控制器组", cw3=[60, 200, 140], bl=u"指定")
        pm.textFieldButtonGrp(
            "controllerBoneNameWidget%s" % index,
            label=u"挂点名称",
            cw3=[60, 200, 140], bl=u"指定",
            bc=lambda *args: self.get_sample_node(
                text_widget="controllerBoneNameWidget%s" % index))
        pm.floatFieldGrp(
            "controllerBoneOffsetWidget%s" % index,
            numberOfFields=3,
            pre=3,
            label=u'挂点偏移', cw4=[60, 50, 50, 50])

        pm.separator(style='none', height=5)
        pm.text(label="Slider list:", al="left")
        pm.textScrollList("controller%sAxis" % index)
        # pm.textFieldGrp(
        #     "controller%sAxisX" % index, label=u"XAxis", cw2=[60, 200])
        # pm.textFieldGrp(
        #     "controller%sAxisY" % index, label=u"YAxis", cw2=[60, 200])
        # pm.textFieldGrp(
        #     "controller%sAxisZ" % index, label=u"ZAxis", cw2=[60, 200])

        pm.separator(style='in', height=20)

        pm.setParent("..")  # end of layout

        return layout

    def action_selected_controller(self):
        current_selected = pm.textScrollList(
            self.controller_list_widget, q=True, sii=True)[0]

        controller_list = pm.scrollLayout(
            "controllerListLayout", q=True, ca=True)

        # detail_list = pm.scrollLayout(
        #     "controllerDetailListLayout", q=True, ca=True)

        if controller_list is not None:
            # print controller_list
            for child in controller_list:
                pm.deleteUI(child)

        # if detail_list is not None:
        #     for child in detail_list:
        #         pm.deleteUI(child)

        self.add_controller_widget(
            index=current_selected, parent="controllerListLayout")

        pm.textFieldButtonGrp(
            "controllerNameWidget%s" % current_selected, e=True,
            text=self.dict_data[self.module_context][current_selected - 1][
                "controllerName"])
        pm.textFieldButtonGrp(
            "controllerGrpNameWidget%s" % current_selected, e=True,
            text=self.dict_data[self.module_context][current_selected - 1][
                "ControllerGroupName"])
        pm.textFieldButtonGrp(
            "controllerBoneNameWidget%s" % current_selected, e=True,
            text=self.dict_data[self.module_context][current_selected - 1][
                "ControllerBoneName"])

        offset_value = \
            self.dict_data[self.module_context][current_selected - 1][
                "ControllerPositionOffset"]
        pm.floatFieldGrp(
            "controllerBoneOffsetWidget%s" % current_selected,
            e=True,
            value1=offset_value[0],
            value2=offset_value[1],
            value3=offset_value[2])

        if (self.dict_data[self.module_context][current_selected - 1][
                "AxisControl"]["XAxis"]) != "":
            pm.textScrollList(
                "controller%sAxis" % current_selected,
                e=True,
                a=self.dict_data[self.module_context][current_selected - 1][
                    "AxisControl"]["XAxis"]
            )
        if (self.dict_data[self.module_context][current_selected - 1][
                "AxisControl"]["YAxis"]) != "":
            pm.textScrollList(
                "controller%sAxis" % current_selected,
                e=True,
                a=self.dict_data[self.module_context][current_selected - 1][
                    "AxisControl"]["YAxis"]
            )
        if (self.dict_data[self.module_context][current_selected - 1][
                "AxisControl"]["ZAxis"]) != "":
            pm.textScrollList(
                "controller%sAxis" % current_selected,
                e=True,
                a=self.dict_data[self.module_context][current_selected - 1][
                    "AxisControl"]["ZAxis"]
            )

        # self.add_control_detail_widget(parent="controllerListLayout")

    def add_control_detail_widget(self, parent):
        for index in range(0, pm.scrollLayout(
                "controllerListLayout", q=True, nch=True)):

            if pm.frameLayout(
                    "controllerDetailListItemLayout%s" % index,
                    q=True, ex=True):
                pm.deleteUI("controllerDetailListItemLayout%s" % index)

            pm.frameLayout(
                "controllerDetailListItemLayout%s" % index,
                bgs=True,
                mw=10, mh=5,
                cll=True,
                cl=False,
                parent=parent)
            pm.textFieldButtonGrp(
                "controllerDetailControlType%s" % index,
                label=u"控制类型", bl=u"指定", cw3=[48, 200, 140])
            pm.textFieldButtonGrp(
                "controllerDetailControlGroup%s" % index,
                label=u"控制器组", bl=u"指定", cw3=[48, 200, 140])
            pm.text(label=u"滑竿控制", al="left", width=100)
            pm.text(label="SliderX:", al="left")
            pm.textScrollList(
                "controllerDetailSliderXBone%s" % index)
            pm.text(label="SliderY:", al="left")
            pm.textScrollList(
                "controllerDetailSliderYBone%s" % index)
            pm.text(label="SliderZ:", al="left")
            pm.textScrollList(
                "controllerDetailSliderZBone%s" % index)
            pm.setParent("..")

            # 自动录入一些数据
            frame_label = pm.textFieldButtonGrp(
                "controllerNameWidget%s" % index, q=True, text=True)
            pm.frameLayout(
                "controllerDetailListItemLayout%s" % index,
                e=True, label=frame_label)

            control_type = pm.optionMenuGrp(
                "faceModuleOptionsWidget", q=True, value=True)
            pm.textFieldButtonGrp(
                "controllerDetailControlType%s" % index,
                e=True, text=control_type)

            control_grp = pm.textFieldButtonGrp(
                "controllerGrpNameWidget%s" % index, q=True, text=True)
            pm.textFieldButtonGrp(
                "controllerDetailControlGroup%s" % index,
                e=True, text=control_grp)

            control_name = pm.textFieldButtonGrp(
                "controllerNameWidget%s" % index, q=True, text=True)

            axia_X = pm.textFieldGrp(
                "controller%sAxisX" % index, q=True, text=True)
            if axia_X != "" and axia_X is not None:
                definition_joints = pm.PyNode(
                    control_name).attr("jointsX").get()
                pm.textScrollList(
                    "controllerDetailSliderXBone%s" % index,
                    e=True,
                    a=helper.str_to_list(definition_joints))

            axia_Y = pm.textFieldGrp(
                "controller%sAxisY" % index, q=True, text=True)
            if axia_Y != "" and axia_Y is not None:
                definition_joints = pm.PyNode(
                    control_name).attr("jointsY").get()
                pm.textScrollList(
                    "controllerDetailSliderYBone%s" % index,
                    e=True,
                    a=helper.str_to_list(definition_joints))

            axia_Z = pm.textFieldGrp(
                "controller%sAxisZ" % index, q=True, text=True)
            if axia_Z != "" and axia_Z is not None:
                definition_joints = pm.PyNode(
                    control_name).attr("jointsZ").get()
                pm.textScrollList(
                    "controllerDetailSliderZBone%s" % index,
                    e=True,
                    a=helper.str_to_list(definition_joints))

        return
