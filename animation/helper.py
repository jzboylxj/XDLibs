# coding=utf-8
"""

JSON数据管理工具

"""
import os
from pymel import core as pm
import maya.cmds as cmds
import maya.mel as mel

import json
import common
import test_node

reload(common)
reload(test_node)

version = 0.2


def str_to_list(str):
    """
    解析字符串，将字符串转换成列表

    :param str: 需要解析的字符串
    :return: List
    """
    str_list = str.split(";")
    str_list = [x.strip() for x in str_list if x.strip() != '']

    return str_list


def zero_locator(name):
    """
    创建一个通道栏属性全部锁定并隐藏的locator

    :param name: Locator的名字
    :return: Locator
    """
    locator = pm.spaceLocator(name=name, p=[0, 0, 0])
    for attr in ["tx", "ty", "tz",
                 "rx", "ry", "rz",
                 "sx", "sy", "sz",
                 "v"]:
        pm.setAttr("%s.%s" % (name, attr), lock=True, k=False, cb=False)
    return locator


def position_joint(jnt_name, value=None):
    """
    将指定骨骼移动到指定位置

    :param jnt_name: 指定骨骼的名字
    :param value: 骨骼的位置参数(list)
    :return: None
    """
    if value is None:
        value = [0, 0, 0, 0, 0, 0, 1, 1, 1]
    pm.PyNode(jnt_name).translateX.set(value[0])
    pm.PyNode(jnt_name).translateY.set(value[1])
    pm.PyNode(jnt_name).translateZ.set(value[2])
    pm.PyNode(jnt_name).rotateX.set(value[3])
    pm.PyNode(jnt_name).rotateY.set(value[4])
    pm.PyNode(jnt_name).rotateZ.set(value[5])
    pm.PyNode(jnt_name).scaleX.set(value[6])
    pm.PyNode(jnt_name).scaleY.set(value[7])
    pm.PyNode(jnt_name).scaleZ.set(value[8])

    return


class ChannelBoxSaver(common.Singleton):
    """
    通道栏属性保存工具

    获取选择对象的通道栏里面的属性值后，转换成字典写入一个json文件里面
    """

    def __init__(self):
        super(ChannelBoxSaver, self).__init__()

        self.slider_mode = 1
        self.output_path = ''
        self.dict_data = {}

        self.initialize()

    def initialize(self):
        if pm.optionVar(q='doChannelBoxSavePath'):
            self.output_path = pm.optionVar(
                q='doChannelBoxSavePath')
        if pm.optionVar(q='sliderWokeMode'):
            self.slider_mode = int(pm.optionVar(
                q='sliderWokeMode'))

    def show(self):
        if pm.window("channelBoxSaver", ex=True):
            pm.deleteUI("channelBoxSaver")
        pm.window(
            "channelBoxSaver",
            title=u"Json数据备份工具 Ver %s" % version,
            closeCommand=lambda *args: self._closed_window_cmd())
        form_layout = pm.formLayout()

        dict_layout = pm.frameLayout(mh=5, mw=10, label=u"定义数据", bgs=True)

        pm.radioButtonGrp(
            "sliderWokeMode",
            label=u'工作模式:',
            labelArray2=[u'滑竿(多项)', u'单项'],
            cw3=[60, 100, 100],
            sl=self.slider_mode,
            cc=lambda *args: self.change_slider(),
            numberOfRadioButtons=2)

        pm.textScrollList("dataExportList", ams=True)

        pm.popupMenu()
        pm.menuItem(
            label=u"添加场景中的选择对象",
            c=lambda *args: self.add_slider())
        pm.menuItem(
            label=u"从列表中移除选择对象",
            # c=lambda *args: self.add_slider_key("sliderY", "sliderKeyList")
        )
        pm.menuItem(
            label=u"从列表中移除所有对象",
            c=lambda *args: self.clean_list()
        )

        pm.setParent("..")

        file_layout = pm.frameLayout(mh=5, mw=10, label=u"定义输出", bgs=True)

        pm.columnLayout(adj=1, rs=10)
        pm.textFieldButtonGrp(
            "channelBoxSavePathInput",
            label=u"保存路径",
            bl=u"选择地址",
            adj=2,
            cw3=[55, 100, 60],
            text=self.output_path,
            bc=lambda *args: self._set_output_path())
        pm.setParent("..")

        pm.button(label=u"保存", c=lambda *args: self.map_channel_box())
        pm.setParent("..")

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (dict_layout, 'top', 10),
                (dict_layout, 'left', 10),
                (dict_layout, 'right', 10),
                (file_layout, 'left', 10),
                (file_layout, 'right', 10),
                (file_layout, 'bottom', 10),
            ],
            attachControl=[
                (dict_layout, 'bottom', 5, file_layout),
            ],
        )

        pm.showWindow("channelBoxSaver")

    def change_slider(self):
        self.slider_mode = pm.radioButtonGrp("sliderWokeMode", q=True, sl=True)
        return

    def add_slider(self):
        for item in pm.ls(sl=True):
            if (item not in pm.textScrollList(
                    "dataExportList", q=True, ai=True)):
                pm.textScrollList("dataExportList", e=True, a=item)

        # print pm.textScrollList("dataExportList", q=True, ai=True)

    def clean_list(self):
        pm.textScrollList("dataExportList", e=True, ra=True)

    def _get_slider(self):
        select_slider = pm.ls(sl=True)[0]
        pm.textFieldButtonGrp("sliderGetBtn", e=True, text=select_slider)

        current_sliders = pm.textScrollList("sliderKeyList", q=True, ai=True)

        slider_attrs = pm.listAttr(select_slider, k=True)
        for slider_attr in slider_attrs:
            if select_slider not in current_sliders:
                pm.textScrollList("sliderKeyList", e=True, a=slider_attr)

        for item in pm.textScrollList("sliderKeyList", q=True, ai=True):
            self.dict_data[item] = dict()

        return

    def _select_slider(self):
        current_select = pm.textScrollList("sliderKeyList", q=True, si=True)[0]
        print current_select
        pm.textScrollList("rangeKeyList", e=True, ra=True)
        pm.textScrollList(
            "rangeKeyList", e=True, a=self.dict_data[current_select].keys())
        pm.textScrollList("jointKeyList", e=True, ra=True)

        return

    def _select_range(self):
        current_slider = pm.textScrollList("sliderKeyList", q=True, si=True)[0]
        current_range = pm.textScrollList("rangeKeyList", q=True, si=True)[0]
        print "%s.%s" % (current_slider, current_range)
        pm.textScrollList("jointKeyList", e=True, ra=True)
        pm.textScrollList(
            "jointKeyList",
            e=True,
            a=self.dict_data[current_slider][current_range].keys())
        return

    def _select_joints(self):
        pm.select(pm.textScrollList("jointKeyList", q=True, si=True))

    def add_range_field(self, field, scrollList):
        current_slider = pm.textScrollList("sliderKeyList", q=True, si=True)[0]

        if (not self._check_field_exists(field, scrollList)):
            pm.textScrollList(scrollList, e=True, a=[field])
            self.dict_data[current_slider][field] = dict()

    def _append_joints(self):
        current_slider = pm.textScrollList("sliderKeyList", q=True, si=True)[0]
        current_range = pm.textScrollList("rangeKeyList", q=True, si=True)[0]
        current_joints = pm.textScrollList("jointKeyList", q=True, ai=True)

        for jnt in pm.ls(sl=True):
            if jnt not in current_joints:
                pm.textScrollList("jointKeyList", e=True, a=jnt)
                jnt_value = [
                    round(jnt.translateX.get() * 0.01, 5),
                    round(jnt.translateY.get() * 0.01, 5),
                    round(jnt.translateZ.get() * 0.01, 5),
                    round(jnt.rotateX.get(), 5),
                    round(jnt.rotateY.get(), 5),
                    round(jnt.rotateZ.get(), 5),
                    round(jnt.scaleX.get(), 5),
                    round(jnt.scaleY.get(), 5),
                    round(jnt.scaleZ.get(), 5),
                ]
                self.dict_data[
                    current_slider][current_range][jnt.name()] = jnt_value
        return

    def _check_field_exists(self, field, scrollList):
        scrollList = pm.textScrollList(scrollList, q=True, ai=True)
        if field in scrollList:
            return True
        else:
            return False

    def add_slider_key(self, slider, scrollList):
        if (not self._check_field_exists(slider, scrollList)):
            pm.textScrollList(scrollList, e=True, a=slider)
        for item in pm.textScrollList(scrollList, q=True, ai=True):
            self.dict_data[item] = dict()
        return

    def _set_output_path(self):
        output_path = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3, okc=u"选择文件夹")
        if output_path:
            pm.textFieldButtonGrp(
                "channelBoxSavePathInput", e=True,
                text=output_path[0])
            self.output_path = output_path[0]
        return

    def parse_str(self, str):
        str_list = str.split(";")
        str_list = [x.strip() for x in str_list if x.strip() != '']

        return str_list

    def joint_cb_list(self, item):
        jnt_value = [
            round(pm.PyNode(item).translateX.get() * 0.01, 5),
            round(pm.PyNode(item).translateY.get() * 0.01, 5),
            round(pm.PyNode(item).translateZ.get() * 0.01, 5),
            round(pm.PyNode(item).rotateX.get(), 5),
            round(pm.PyNode(item).rotateY.get(), 5),
            round(pm.PyNode(item).rotateZ.get(), 5),
            round(pm.PyNode(item).scaleX.get(), 5),
            round(pm.PyNode(item).scaleY.get(), 5),
            round(pm.PyNode(item).scaleZ.get(), 5),
        ]
        return jnt_value

    def get_joint_data(self, controller, slider):
        jnt_str = ""
        if slider == "sliderX":
            jnt_str = "jointsX"
        if slider == "sliderY":
            jnt_str = "jointsY"
        if slider == "sliderZ":
            jnt_str = "jointsZ"
        for item in self.parse_str(
                pm.getAttr("%s.%s" % (controller, jnt_str))):
            # print item
            self.dict_data[slider][item] = dict()

            pm.setAttr("%s.%s" % (controller, slider), 1)
            self.dict_data[slider][item]["max"] = self.joint_cb_list(item)

            if pm.radioButtonGrp("sliderWokeMode", q=True, sl=True) == 1:
                pm.setAttr("%s.%s" % (controller, slider), -1)
                self.dict_data[slider][item]["min"] = self.joint_cb_list(item)

            pm.setAttr("%s.%s" % (controller, slider), 0)

    def map_channel_box(self):
        """
        获取选择对象通道栏里面的属性值后，转换成字典

        :return:
        """

        controller_list = pm.textScrollList("dataExportList", q=True, ai=True)
        for controller in controller_list:
            self.dict_data = {}
            if pm.attributeQuery('sliderX', node=controller, ex=True):
                self.dict_data['sliderX'] = dict()
                # 设置控制器的属性为1，这个也是max状态
                self.get_joint_data(controller, 'sliderX')
            if pm.attributeQuery('sliderY', node=controller, ex=True):
                self.dict_data["sliderY"] = dict()
                self.get_joint_data(controller, 'sliderY')
            if pm.attributeQuery('sliderZ', node=controller, ex=True):
                self.dict_data["sliderZ"] = dict()
                self.get_joint_data(controller, 'sliderZ')

            folder = pm.textFieldButtonGrp(
                "channelBoxSavePathInput", q=True, text=True)

            json_name = ("%s/%s.json" % (folder, controller))
            common.write_json(dict_data=self.dict_data, file_path=json_name)
            print u"%s 转化完毕" % controller
        return

    def _closed_window_cmd(self):
        pm.optionVar(sv=('doChannelBoxSavePath', self.output_path))
        pm.optionVar(sv=('sliderWokeMode', self.slider_mode))


class CustomAttrHelper(common.Singleton):
    """
    管理自定义控制器的自定义属性的窗口工具
    """

    def __init__(self):
        super(CustomAttrHelper, self).__init__()

        self.initialize()

        self.show()

    def initialize(self):
        pass

    def show(self):
        if pm.window("customAttrHelper", q=True, ex=True):
            pm.deleteUI("customAttrHelper")

        pm.window("customAttrHelper", title="Custom Attr Helper")

        self.main_form = pm.formLayout()
        self.frame_layout = pm.frameLayout(
            label="Custome Attr Helper", bgs=True)

        self.form_layout = pm.formLayout()
        self.controller_field = pm.textFieldButtonGrp(
            "customControllerGetter",
            label=u"控制器名称：",
            bl=u" Get ",
            cw3=[75, 70, 70],
            adj=2,
            bc=lambda *args: self.get_custom_controller())
        self.select_controller_btn = pm.button(
            label=u"选择控制器",
            c=lambda *args: self.select_controller())
        self.controller_attr_options = pm.radioButtonGrp(
            "customControllerAttrOptions",
            label=u'控制器属性：',
            labelArray3=['jointsX', 'jointsY', 'jointsZ'],
            cw4=[75, 70, 70, 70],
            sl=1,
            numberOfRadioButtons=3,
            cc=lambda *args: self.select_radio_item())
        self.add_joint_btn = pm.button(
            label=u"添加影响骨骼",
            c=lambda *args: self.joint_string_value())
        self.text_scroll = pm.textScrollList(ams=True)
        pm.popupMenu()
        pm.menuItem(label=u"选择所选",
                    c=lambda *args: self.select_item())

        pm.formLayout(
            self.form_layout,
            edit=True,
            attachForm=[
                (self.controller_field, 'top', 10),
                (self.controller_field, 'left', 10),
                (self.select_controller_btn, 'top', 10),
                (self.select_controller_btn, 'right', 10),
                (self.controller_attr_options, 'left', 10),
                (self.controller_attr_options, 'right', 10),
                (self.add_joint_btn, 'left', 10),
                (self.add_joint_btn, 'right', 10),
                (self.text_scroll, 'left', 10),
                (self.text_scroll, 'right', 10),
                (self.text_scroll, 'bottom', 10)
            ],
            attachControl=[
                (
                    self.controller_field, 'right', 5,
                    self.select_controller_btn),
                (
                    self.controller_attr_options, 'top', 5,
                    self.controller_field),
                (self.add_joint_btn, 'top', 5, self.controller_attr_options),
                (self.text_scroll, 'top', 5, self.add_joint_btn),
            ],
        )

        pm.setParent("..")  # end of formLayout
        pm.setParent("..")  # end of frameLayout

        pm.formLayout(
            self.main_form,
            edit=True,
            attachForm=[
                (self.frame_layout, 'top', 10),
                (self.frame_layout, 'left', 10),
                (self.frame_layout, 'bottom', 10),
                (self.frame_layout, 'right', 10),
            ],
            attachControl=[
                # (self.controller_field, 'right', 5, self.select_controller_btn),
            ],
        )

        pm.showWindow("customAttrHelper")

    def _closed_window_cmd(self):
        pass

    def select_item(self):
        joint_list = pm.textScrollList(self.text_scroll, q=True, si=True)
        pm.select(joint_list)
        return joint_list

    def select_controller(self):
        pm.select(
            pm.textFieldButtonGrp(self.controller_field, q=True, text=True)
        )
        return

    def select_radio_item(self):
        label_array = ['jointsX', 'jointsY', 'jointsZ']
        radio_index = pm.radioButtonGrp(
            "customControllerAttrOptions", q=True, sl=True)
        controller_name = pm.textFieldButtonGrp(
            "customControllerGetter", q=True, text=True)
        select_attr = label_array[radio_index - 1]
        if pm.PyNode(controller_name).hasAttr(select_attr):
            joint_list = str_to_list(
                pm.getAttr("%s.%s" % (controller_name, select_attr)))
            pm.textScrollList(self.text_scroll, e=True, ra=True)
            pm.textScrollList(self.text_scroll, e=True, a=joint_list)
        else:
            pm.textScrollList(self.text_scroll, e=True, ra=True)

    def joint_string_value(self):
        index = pm.radioButtonGrp(
            "customControllerAttrOptions", q=True, sl=True)
        controller = pm.textFieldButtonGrp(
            "customControllerGetter", q=True, text=True)

        sel_joints = pm.ls(sl=True)
        name = ""
        for item in sel_joints:
            name = name + item.name() + ";"

        attr_name = ""
        if index == 1:
            attr_name = "jointsX"
        elif index == 2:
            attr_name = "jointsY"
        elif index == 3:
            attr_name = "jointsZ"

        pm.setAttr(("%s.%s" % (controller, attr_name)), name, type="string")
        pm.textScrollList(self.text_scroll, e=True, a=sel_joints)

        return

    def get_custom_controller(self):
        attr_list = ['jointsX', 'jointsY', 'jointsZ']

        controller_name = pm.ls(sl=True)[0].name()
        pm.textFieldButtonGrp(
            "customControllerGetter",
            e=True,
            text=controller_name)

        print controller_name
        select_index = pm.radioButtonGrp(
            "customControllerAttrOptions", q=True, sl=True)
        select_attr = attr_list[select_index - 1]
        if pm.PyNode(controller_name).hasAttr(select_attr):
            joint_list = str_to_list(
                pm.getAttr("%s.%s" % (controller_name, select_attr)))
            pm.textScrollList(self.text_scroll, e=True, ra=True)
            pm.textScrollList(self.text_scroll, e=True, a=joint_list)
        return


class ChannelBoxWriter(common.Singleton):
    def __init__(self):
        super(ChannelBoxWriter, self).__init__()

        self.json_folder = ''
        self.json_files = []

        self.initialize()
        self.show()

    def initialize(self):
        if pm.optionVar(q='arFaceControllerJsonFolder'):
            self.json_folder = pm.optionVar(
                q='arFaceControllerJsonFolder')

        self.json_files = self.scanning_folder()
        # print self.json_files

    def show(self):
        if pm.window("arFaceController", ex=True):
            pm.deleteUI("arFaceController")

        pm.window(
            "arFaceController",
            mb=True,
            cc=lambda *args: self._closed_window_cmd())

        self.menu_list()

        form_layout = pm.formLayout()

        json_layout = self.json_controller_widget()

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (json_layout, 'left', 10),
                (json_layout, 'right', 10),
                # (file_layout, 'left', 10),
                # (file_layout, 'right', 10),
                # (file_layout, 'bottom', 10),
            ],
            attachControl=[
                # (dict_layout, 'bottom', 5, file_layout),
            ],
        )
        pm.showWindow("arFaceController")

    def menu_list(self):
        """
        工具菜单栏
        """
        pm.menu(label=u"设置", tearOff=True)
        pm.menuItem(
            label=u"设置Json存放目录",
            c=lambda *args: self.setting_json_folder())
        pm.menuItem(
            label=u"调试模式", cb=False)

    def json_controller_widget(self):
        layout = pm.frameLayout(
            "controllerOptionsLayout",
            label=u"Json数据管理", mw=10, mh=5, bgs=True)

        pm.radioButtonGrp(
            label=u"工作模式",
            numberOfRadioButtons=2,
            cw3=[50, 50, 50],
            sl=1,
            labelArray2=[u'创建', u'测试'])

        self.option_menu_widget()

        # 这里是程序添加空间的地方
        self.selected_controller()

        pm.setParent("..")

        return layout

    def option_menu_widget(self):
        if pm.optionMenuGrp("controllerOptionsWidget", ex=True):
            pm.deleteUI("controllerOptionsWidget")
        pm.optionMenuGrp(
            "controllerOptionsWidget",
            parent="controllerOptionsLayout",
            label=u"Controller",
            cw2=[60, 50],
            adj=2,
            cc=lambda *args: self.selected_controller())
        if len(self.json_files) > 0:
            for json_file in self.json_files:
                pm.menuItem(label=json_file)

        pm.optionMenuGrp("controllerOptionsWidget", e=True, sl=1)

    def setting_json_folder(self):
        json_folder = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3, okc=u"选择文件夹")
        if json_folder:
            self.json_folder = json_folder[0]
            self.json_files = self.scanning_folder()

            self.option_menu_widget()
            self.selected_controller()

            # print self.json_folder
        return

    def scanning_folder(self):
        json_list = []
        if self.json_folder != '':
            path_dir = os.listdir(self.json_folder)
            for json_file in path_dir:
                # 获取JSON文件的名字后，清理文件的后缀名
                file_name = os.path.splitext(json_file)[0]
                json_list.append(file_name)
        return json_list

    def selected_controller(self):
        if pm.columnLayout("controllerItemLayout", q=True, ex=True):
            pm.deleteUI("controllerItemLayout")

        pm.columnLayout(
            "controllerItemLayout", adj=1, rs=10,
            parent="controllerOptionsLayout")
        index = pm.optionMenuGrp("controllerOptionsWidget", q=True, sl=True)
        json_file_name = self.json_files[index - 1]
        json_file_path = "%s/%s.json" % (self.json_folder, json_file_name)

        if os.path.isfile(json_file_path):
            dict_data = common.read_json(file_path=json_file_path)
            for key in dict_data.keys():
                slider = pm.floatSliderGrp(
                    label=key,
                    field=True,
                    pre=3,
                    cw3=[40, 60, 100],
                    minValue=-1.0,
                    maxValue=1.0)
                pm.connectControl(slider, "%s.%s" % (json_file_name, key))

                min_value = pm.PyNode(json_file_name).attr(key).getMin()
                max_value = pm.PyNode(json_file_name).attr(key).getMax()
                pm.floatSliderGrp(
                    slider, e=True, minValue=min_value, maxValue=max_value)

                slider_joints = dict_data[key].keys()
                pm.textScrollList(a=slider_joints)

        pm.setParent("..")
        return

    def _closed_window_cmd(self):
        pm.optionVar(
            sv=('arFaceControllerJsonFolder', self.json_folder))


manager_version = 0.1


class JsonManager(common.Singleton):
    """
    Json数据文件管理工具
    """

    def __init__(self):
        super(JsonManager, self).__init__()

        self.json_folder = ''
        self.module_sections = []

        self.dict_data = list()
        self.detail_data = dict()

        self.controller = {}
        self.controller_detail = {}

        self.ar_file_location = ''
        self.ar_data = {}

        self.current_tab_index = 1

        # 历史版本的json文件存放路径
        self.brow_file_folder = ""
        self.eye_file_folder = ""
        self.nose_file_folder = ""
        self.mouth_file_folder = ""
        self.face_file_folder = ""

        self.initialize()
        self.show()
        # self.selected_controller()

    def show(self):
        """
        显示工具窗口

        :return: window
        """
        if pm.window("jsonManagerUI", ex=True):
            pm.deleteUI("jsonManagerUI")
        pm.window(
            "jsonManagerUI",
            t=u"JSON数据管理器 %s" % manager_version,
            mb=True,
            cc=lambda *args: self._closed_window_cmd())

        self.menu_list()

        self.main_tab = pm.tabLayout(
            "jsonManagerMainTabLayout",
            innerMarginWidth=5, innerMarginHeight=5)
        child1 = self.custom_tab()
        child2 = self.ar_tab()
        child3 = self.discard_tab()

        pm.tabLayout(
            self.main_tab,
            edit=True,
            tabLabel=(
                (child1, u'捏脸'),
                (child2, u'AR'),
                (child3, u'历史版本')),
            sti=self.current_tab_index)

        pm.showWindow("jsonManagerUI")

    def menu_list(self):
        """
        工具菜单栏

        :return:
        """
        pm.menu(label=u"设置", tearOff=True)
        pm.menuItem(
            label=u"设置Json存放目录",
            c=lambda *args: self.setting_json_folder())
        pm.menuItem(
            label=u"调试模式", cb=False)

        return

    def custom_tab(self):
        """
        标签栏之自定义捏脸栏

        :return: layout
        """
        layout = pm.formLayout("customFormTab")

        option_menu = self.option_menu_widget(parent_widget=layout)

        add_module_btn = pm.button(
            label=u"增加模块",
            c=lambda *args: self.add_module())

        tab_layout = pm.tabLayout(
            innerMarginWidth=5, innerMarginHeight=5)

        controller_list_layout = pm.formLayout()
        add_controller_btn = pm.button(
            label=u"增加控制器",
            c=lambda *args: self.add_controller())

        add_controller_detail_btn = pm.button(
            label=u"增加控制器细节",
            c=lambda *args: self.add_control_detail_widget())

        pm.scrollLayout(
            "controllerListLayout", height=400)
        pm.setParent("..")

        save_data_btn = pm.button(
            "saveDataBtn",
            label=u"保存数据",
            c=lambda *args: self.save_custom_data())

        pm.formLayout(
            controller_list_layout, edit=True,
            attachForm=[
                # (add_module_btn, 'top', 10),
                # (add_module_btn, 'left', 10),
                (add_controller_btn, 'top', 10),
                (add_controller_btn, 'left', 10),
                (add_controller_detail_btn, 'top', 10),
                ("controllerListLayout", 'left', 10),
                ("controllerListLayout", 'right', 10),
                (save_data_btn, 'left', 10),
                (save_data_btn, 'right', 10),
                (save_data_btn, 'bottom', 10)
            ],
            attachControl=[
                # (add_controller_btn, 'left', 10, add_module_btn),
                (add_controller_detail_btn, 'left', 5, add_controller_btn),
                ("controllerListLayout", 'top', 10, add_controller_btn),
                ("controllerListLayout", 'bottom', 10, save_data_btn),
            ])
        pm.setParent("..")

        controller_detail_list_layout = pm.scrollLayout(
            "controllerDetailListLayout", height=400)
        pm.setParent("..")

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

        pm.tabLayout(
            tab_layout,
            edit=True,
            tabLabel=(
                (controller_list_layout, u'控制器'),
                (controller_detail_list_layout, u'影响骨骼'),
                (controller_test_list_layout, u'测试')
            ))
        pm.setParent("..")

        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (option_menu, 'top', 10),
                (option_menu, 'left', 10),
                (add_module_btn, 'right', 10),
                (add_module_btn, 'top', 7),
                (tab_layout, 'left', 10),
                (tab_layout, 'right', 10),
                (tab_layout, 'bottom', 10),
            ],
            attachControl=[
                (option_menu, 'right', 5, add_module_btn),
                # (add_module_btn, 'left', 5, option_menu),
                (tab_layout, 'top', 5, option_menu),
            ])

        pm.setParent("..")
        return layout

    def ar_tab(self):
        """
        标签栏之AR控制栏

        :return: layout
        """
        layout = pm.formLayout("ARFormTab")
        json_field = pm.textFieldButtonGrp(
            "ARFileLocationField",
            label=u"存放路径",
            bl=u"指定路径",
            adj=2,
            cw3=[60, 100, 100],
            text=self.ar_file_location,
            bc=lambda *args: self.setting_ar_file_location())

        self.auto_create_controller_check = pm.checkBox(
            label=u"自动创建控制器", value=True)

        ID_layout = pm.columnLayout(adj=1, rs=5)
        pm.text(label=u"通道列表", al="left")
        pm.textScrollList(
            "ARIDScrollList",
            height=400,
            sc=lambda *args: self.selected_ar_id_in_list())
        pm.popupMenu()
        pm.menuItem(label=u"为选择项添加控制器",
                    c=lambda *args: self.add_slider_for_selected())
        pm.setParent("..")

        detail_frame = pm.frameLayout(label=u"通道属性", bgs=True)
        pm.textFieldButtonGrp(
            "arIDDriverField",
            enable=False,
            label=u"控制器",
            bl=u"设置",
            adj=2,
            cw3=[60, 100, 60])
        pm.floatSliderGrp(
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
            cw3=[60, 60, 100])
        pm.setParent("..")

        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (json_field, 'top', 5),
                (json_field, 'left', 10),
                (json_field, 'right', 10),
                (self.auto_create_controller_check, 'left', 10),
                (self.auto_create_controller_check, 'right', 10),
                (ID_layout, 'left', 10),
                (ID_layout, 'right', 10),
                (detail_frame, 'left', 10),
                (detail_frame, 'right', 10),
            ],
            attachControl=[
                (self.auto_create_controller_check, 'top', 5, json_field),
                (ID_layout, 'top', 5, self.auto_create_controller_check),
                (detail_frame, 'top', 10, ID_layout),
            ])

        pm.setParent("..")

        self.append_id_to_scroll(self.ar_file_location)

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
        print pm.textScrollList("ARIDScrollList", q=True, si=True)[0]

        selected_key = pm.textScrollList("ARIDScrollList", q=True, si=True)[0]
        print self.ar_data[selected_key]

        if not pm.objExists(selected_key):
            self.create_slider_controller(name=selected_key)

        return

    def create_slider_controller(self, name):
        locator = zero_locator(name=name)
        pm.addAttr(locator, ln="sliderX", at="double", min=0, max=1, dv=0)
        pm.setAttr("%s.sliderX" % locator, e=True, k=True)

        return

    def sdk_slider_to_rig(self, slider, attr="sliderX"):
        attr_list = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        for jnt in self.ar_data[slider].keys():
            print jnt
            for dv_attr in attr_list:
                position_joint(jnt, value=[0, 0, 0, 0, 0, 0, 1, 1, 1])
                pm.setDrivenKeyframe(
                    "%s.%s" % (jnt, dv_attr),
                    cd="%s.%s" % (slider, attr),
                    dv=0)

                value = self.ar_data[slider][jnt]["max"]
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

                position_joint(jnt, value=dv_value)
                pm.setDrivenKeyframe(
                    "%s.%s" % (jnt, dv_attr),
                    cd="%s.%s" % (slider, attr),
                    dv=1)

        pm.setAttr("%s.%s" % (slider, attr), 0)
        return

    def selected_ar_id_in_list(self):
        print pm.textScrollList("ARIDScrollList", q=True, si=True)[0]

        selected_key = pm.textScrollList("ARIDScrollList", q=True, si=True)[0]
        print self.ar_data[selected_key]

        if pm.objExists(selected_key):
            pm.textFieldButtonGrp(
                "arIDDriverField", e=True, enable=True, text=selected_key)
            pm.floatSliderGrp("arIDControlSlider", e=True, enable=True)
            pm.connectControl('arIDControlSlider',
                              '%s.sliderX' % selected_key)

        else:
            if pm.checkBox(self.auto_create_controller_check, q=True, v=True):
                pm.textFieldButtonGrp(
                    "arIDDriverField", e=True, enable=True, text=selected_key)
                pm.floatSliderGrp("arIDControlSlider", e=True, enable=True)

                self.create_slider_controller(name=selected_key)
                self.sdk_slider_to_rig(slider=selected_key)
                pm.connectControl('arIDControlSlider',
                                  '%s.sliderX' % selected_key)
            else:
                pm.textFieldButtonGrp(
                    "arIDDriverField", e=True, enable=False, text='')
                pm.floatSliderGrp("arIDControlSlider", e=True, enable=False)

        return

    def setting_ar_file_location(self):
        json_location = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=1, okc=u"选择文件")
        pm.textFieldButtonGrp(
            "ARFileLocationField", e=True, text=json_location[0])

        self.ar_file_location = json_location[0]

        self.append_id_to_scroll(json_location[0])

        return

    def append_id_to_scroll(self, file_name):
        if file_name != '':
            ID_list = []
            with open(file_name, 'r') as data:
                dict_data = json.load(data)
                ID_list = dict_data.keys()

                self.ar_data = dict_data

            # 对列表进行排序
            ID_list.sort()

            # print ID_list
            pm.textScrollList("ARIDScrollList", e=True, a=ID_list)

        return

    def discard_tab(self):
        """
        历史遗留版本
        """
        layout = pm.formLayout()

        self.module_id_field = pm.intFieldGrp(label=u"道具ID", cw2=[50, 100])
        # self.discard_setting_path = pm.textFieldButtonGrp(
        #     label=u"配置文件",
        #     bl=u"指定路径",
        #     adj=2,
        #     cw3=[50, 100, 100])

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
                # (self.discard_setting_path, 'top', 5),
                # (self.discard_setting_path, 'left', 10),
                # (self.discard_setting_path, 'right', 10),
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
            self.module_sections = self.scanning_folder("folders")

        if pm.optionVar(q='arFileLocation'):
            self.ar_file_location = pm.optionVar(
                q='arFileLocation')

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
        if json_folder:
            self.json_folder = json_folder[0]
            self.module_sections = self.scanning_folder("folders")

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
                    print "%s it's a directory" % full_path
                    folder_list.append(json_file)
                elif os.path.isfile(full_path):
                    print "%s it's a normal file" % full_path
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
            cw2=[50, 50],
            adj=2,
            cc=lambda *args: self.selected_controller(
                pm.optionMenuGrp(widget, q=True, value=True)))
        if len(self.module_sections) > 0:
            for json_file in self.module_sections:
                pm.menuItem(label=json_file)

        return widget

    def selected_controller(self, module):
        """
        选择控制器
        """
        selected_controller = pm.optionMenuGrp(
            "faceModuleOptionsWidget", q=True, value=True)
        print "selected controller: %s" % selected_controller

        # print self.json_folder
        controller_file = "%s/%s/%sController.json" % (
            self.json_folder, module, module)

        print controller_file

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
            print dict_data
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

        # common.write_json(
        #     dict_data={},
        #     file_path=file_path[0])

        # (file_path, full_file_name) = os.path.split(file_path[0])
        # (file_name, extension) = os.path.splitext(full_file_name)

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

        # pm.popupMenu()
        # pm.menuItem(
        #     label=u"移除控制器",
        #     # c=lambda *args: self.add_slider()
        # )

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

    def add_control_detail_widget(self):
        parent = "controllerDetailListLayout"
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
            # print control_name

            axia_X = pm.textFieldGrp(
                "controller%sAxisX" % index, q=True, text=True)
            if axia_X != "" and axia_X is not None:
                definition_joints = pm.PyNode(
                    control_name).attr("jointsX").get()
                pm.textScrollList(
                    "controllerDetailSliderXBone%s" % index,
                    e=True,
                    a=str_to_list(definition_joints))

            axia_Y = pm.textFieldGrp(
                "controller%sAxisY" % index, q=True, text=True)
            if axia_Y != "" and axia_Y is not None:
                definition_joints = pm.PyNode(
                    control_name).attr("jointsY").get()
                pm.textScrollList(
                    "controllerDetailSliderYBone%s" % index,
                    e=True,
                    a=str_to_list(definition_joints))

            axia_Z = pm.textFieldGrp(
                "controller%sAxisZ" % index, q=True, text=True)
            if axia_Z != "" and axia_Z is not None:
                definition_joints = pm.PyNode(
                    control_name).attr("jointsZ").get()
                pm.textScrollList(
                    "controllerDetailSliderZBone%s" % index,
                    e=True,
                    a=str_to_list(definition_joints))

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

        print "Detail item : %s" % pm.scrollLayout(
            "controllerDetailListLayout", q=True, nch=True)

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
        # print self.detail_data
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

        print u"保存成功"

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
        # self.brow_id_field = pm.intFieldGrp(label="ID", cw2=[60, 100])
        # pm.separator(height=10, style='in')
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
        # pm.separator(height=10, style='in')
        # pm.button(
        #     label=u"保存JSON文件",
        #     c=lambda *args: self.save_brow_data_to_json())
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
        # self.eye_id_field = pm.intFieldGrp(label="ID", cw2=[60, 100])
        # pm.separator(height=10, style='in')
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
        # pm.separator(height=10, style='in')
        # pm.button(
        #     label=u"保存JSON文件",
        #     c=lambda *args: self.save_eye_data_to_json())
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
        # self.nose_id_field = pm.intFieldGrp(label="ID", cw2=[60, 100])
        # pm.separator(height=10, style='in')
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
        # pm.separator(height=10, style='in')
        # pm.button(
        #     label=u"保存JSON文件",
        #     c=lambda *args: self.save_nose_data_to_json())
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
        # self.mouth_id_field = pm.intFieldGrp(label="ID", cw2=[60, 100])
        # pm.separator(height=10, style='in')
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
        # pm.separator(height=10, style='in')
        # pm.button(
        #     label=u"保存JSON文件",
        #     c=lambda *args: self.save_mouth_data_to_json())
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
        # self.face_id_field = pm.intFieldGrp(label="ID", cw2=[60, 100])
        # pm.separator(height=10, style='in')
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
        # pm.separator(height=10, style='in')
        # pm.button(
        #     label=u"保存JSON文件",
        #     c=lambda *args: self.save_face_data_to_json())
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

        print u"Brow通道：%s 数据保存成功！" % module_id

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

        print u"Eye通道：%s 数据保存成功！" % module_id

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

        print u"Nose通道：%s 数据保存成功！" % module_id

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

        print u"Mouth通道：%s 数据保存成功！" % module_id

        return

    def save_data_to_json(self):
        tab_array = ['brow', 'eye', 'nose', 'mouth', 'face']
        current_tab_index = pm.tabLayout(
            self.discard_child_tab_layout,
            q=True,
            sti=True) - 1

        print tab_array[current_tab_index]

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


class ExportFBXMaster(common.Singleton):
    def __init__(self):
        super(ExportFBXMaster, self).__init__()

        self.output_files = []
        self.output_path = ""

        self.work_mode_selected = 1

        self.initialize()
        self.show()

    def show(self):
        if pm.window("autoExportFBXFileTool", ex=True):
            pm.deleteUI("autoExportFBXFileTool")
        pm.window(
            "autoExportFBXFileTool",
            # t=u"自动输出 %s" % __version__,
            mb=True,
            cc=lambda *args: self._close_main_window())

        # self.menu_list()

        self.form_layout = pm.formLayout()

        # self.work_mode = pm.radioButtonGrp(
        #     label=u'工作模式',
        #     labelArray2=[u'骨骼输出', u'捏脸动画清理'],
        #     cw3=[48, 100, 100],
        #     sl=self.work_mode_selected,
        #     numberOfRadioButtons=2)
        self.scroll_label = pm.text(label=u"输出文件列表", al="left")
        self.output_scroll = pm.textScrollList(ams=True)
        pm.popupMenu()
        pm.menuItem(label=u"添加文件",
                    c=lambda *args: self._append_file())
        pm.menuItem(label=u"移除选择",
                    c=lambda *args: self.remove_select_item())

        self.ouput_path_field = pm.textFieldButtonGrp(
            adj=2,
            label=u"存放路径",
            bl=u"指定路径",
            cw3=[60, 100, 100],
            text=self.output_path,
            bc=lambda *args: self._set_output_location())
        self.excute_btn = pm.button(
            label=u"开始输出",
            c=lambda *args: self.export_to_fbx())

        pm.formLayout(
            self.form_layout,
            edit=True,
            attachForm=[
                # (self.work_mode, 'top', 10),
                # (self.work_mode, 'left', 10),
                # (self.work_mode, 'right', 10),
                (self.scroll_label, 'top', 10),
                (self.scroll_label, 'left', 10),
                (self.scroll_label, 'right', 10),
                (self.output_scroll, 'left', 10),
                (self.output_scroll, 'right', 10),
                (self.ouput_path_field, 'left', 10),
                (self.ouput_path_field, 'right', 10),
                (self.excute_btn, 'left', 10),
                (self.excute_btn, 'right', 10),
                (self.excute_btn, 'bottom', 10)
            ],
            attachControl=[
                (self.output_scroll, 'top', 5, self.scroll_label),
                (self.output_scroll, 'bottom', 5, self.ouput_path_field),
                (self.ouput_path_field, 'bottom', 5, self.excute_btn),
            ],
        )

        pm.showWindow("autoExportFBXFileTool")

    def initialize(self):
        if pm.optionVar(q='autoExportFBXFileToolOutputPath'):
            self.output_path = pm.optionVar(
                q='autoExportFBXFileToolOutputPath')

    def _close_main_window(self):
        pm.optionVar(sv=('autoExportFBXFileToolOutputPath', self.output_path))

    def menu_list(self):
        """
        工具菜单栏
        """
        pm.menu(label=u"设置", tearOff=True)
        pm.menuItem(
            label=u"设置捏脸配置文件存放目录",
            c=lambda *args: self.setting_dedinition())
        # pm.menuItem(
        #     label=u"调试模式", cb=False)

    def _append_file(self):
        multiple_filters = (
            "Maya Files (*.ma *.mb);;"
            "Maya ASCII (*.ma);;"
            "Maya Binary (*.mb);;"
            "FBX Files (*.fbx);;"
        )
        current_export_list = pm.textScrollList(
            self.output_scroll, q=True, ai=True)
        export_files = pm.fileDialog2(
            fileFilter=multiple_filters,
            dialogStyle=2, fileMode=4, okc=u"添加")
        if export_files:
            for export_file in export_files:
                if export_file not in current_export_list:
                    pm.textScrollList(
                        self.output_scroll, edit=True, append=export_file)

        self.output_files = pm.textScrollList(
            self.output_scroll, q=True, ai=True)
        return True

    def remove_select_item(self):
        pm.textScrollList(
            self.output_scroll,
            e=True,
            ri=pm.textScrollList(self.output_scroll, q=True, si=True))
        self.output_files = pm.textScrollList(
            self.output_scroll, q=True, ai=True)
        return

    def _set_output_location(self):
        output_location = pm.fileDialog2(
            dialogStyle=2, fileMode=3, okc=u"选择文件夹")
        if output_location:
            pm.textFieldButtonGrp(
                self.ouput_path_field,
                e=True,
                text=output_location[0])
            self.output_path = output_location[0]
        return

    def start_export(self):
        # model_selected = pm.optionMenuGrp(self.work_mode, q=True, sl=True)

        # if model_selected == 1:
        self.export_to_fbx()
        # if model_selected == 2:
        #     self.clean_definition_anim()

        print u"输出成功"

        return

    def clean_definition_anim(self):
        export_grp = ["character_root", "final_model_grp"]

        system_namespace = ['UI', 'shared']

        print self.output_files

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        if len(self.output_files) > 0:
            for export_file in self.output_files:
                scence_export_grp = []

                # 新建场景，打开指定场景
                cmds.file(new=True, force=True)
                cmds.file(export_file, o=True)
                file_name = cmds.file(
                    q=1, sceneName=True, shortName=True).split('.')[0]
                print (file_name + ' already open!')

                # 将MAYA的时间格式改成ntsc(30帧每秒)
                common.set_time_unit(unit='ntsc')

                # min_time = pm.playbackOptions(q=True, minTime=True)
                # max_time = pm.playbackOptions(q=True, maxTime=True)
                # time_range = (min_time, max_time)

                # 命名空间列表
                # all_namespace_list = pm.namespaceInfo(lon=True)
                # for name in system_namespace:
                #     all_namespace_list.remove(name)
                #
                # # print all_namespace_list
                #
                # fbx_files = []
                # export_file_name = ""
                # for name in all_namespace_list:
                #     if pm.objExists("%s:character_root" % name):
                #         # 根据命名空间来获取场景中有多少角色
                #         print name
                #         for export_item in export_grp:
                #             scence_export_grp.append(
                #                 "%s:%s" % (name, export_item))
                #
                #         pm.select("%s:character_root" % name, hi=True)
                #         bake_nodes = pm.ls(sl=True)
                #
                #         pm.bakeResults(
                #             bake_nodes,
                #             simulation=True,
                #             t=time_range,
                #             sb=1,
                #             dic=True,
                #             preserveOutsideKeys=False,
                #             sparseAnimCurveBake=False,
                #             removeBakedAttributeFromLayer=False,
                #             bakeOnOverrideLayer=False,
                #             controlPoints=False,
                #             shape=False)
                #
                #         export_file_name = ""
                #         if len(all_namespace_list) == 1:
                #             export_file_name = "%s/%s.fbx" % (
                #                 self.output_path, file_name)
                #         elif len(all_namespace_list) > 1:
                #             export_file_name = "%s/%s_%s.fbx" % (
                #                 self.output_path, file_name, name)
                #
                #         pm.select(scence_export_grp)
                #         cmds.file(
                #             export_file_name,
                #             force=True,
                #             pr=True,
                #             es=True,
                #             typ="FBX export",
                #             options="v=0")
                #
                #         fbx_files.append(export_file_name)

    def export_to_fbx(self):
        export_grp = ["character_root", "final_model_grp"]

        system_namespace = ['UI', 'shared']

        print self.output_files

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        if len(self.output_files) > 0:
            for export_file in self.output_files:
                scence_export_grp = []

                # 新建场景，打开指定场景
                cmds.file(new=True, force=True)
                cmds.file(export_file, o=True)
                file_name = cmds.file(
                    q=1, sceneName=True, shortName=True).split('.')[0]
                print (file_name + ' already open!')

                # 将MAYA的时间格式改成ntsc(30帧每秒)
                common.set_time_unit(unit='ntsc')

                min_time = pm.playbackOptions(q=True, minTime=True)
                max_time = pm.playbackOptions(q=True, maxTime=True)
                time_range = (min_time, max_time)

                # 命名空间列表
                all_namespace_list = pm.namespaceInfo(lon=True)
                for name in system_namespace:
                    all_namespace_list.remove(name)

                # print all_namespace_list

                fbx_files = []
                export_file_name = ""
                for namespace in all_namespace_list:
                    if pm.objExists("%s:character_root" % namespace):
                        # 根据命名空间来获取场景中有多少角色
                        print "namespace: %s" % namespace
                        for export_item in export_grp:
                            scence_export_grp.append(
                                "%s:%s" % (namespace, export_item))

                        pm.select("%s:character_root" % namespace, hi=True)
                        bake_nodes = pm.ls(sl=True)

                        print u"烘焙动画开始"
                        pm.bakeResults(
                            bake_nodes,
                            simulation=True,
                            t=time_range,
                            sb=1,
                            dic=True,
                            preserveOutsideKeys=False,
                            sparseAnimCurveBake=False,
                            removeBakedAttributeFromLayer=False,
                            bakeOnOverrideLayer=False,
                            controlPoints=False,
                            shape=False)

                        export_file_name = ""
                        if len(all_namespace_list) == 1:
                            export_file_name = "%s/%s.fbx" % (
                                self.output_path, file_name)
                        elif len(all_namespace_list) > 1:
                            export_file_name = "%s/%s_%s.fbx" % (
                                self.output_path, file_name, namespace)

                        # print u"清理捏脸骨骼动画"
                        # pm.select("%s:head_JNT" % namespace, hi=True)
                        # for jnt in pm.ls(sl=True):
                        #     for anim_attr in pm.listAttr(jnt, k=True):
                        #         cmd = ''' cutKey -cl -t ":" -f ":" -at %s %s ;''' % (
                        #             anim_attr, jnt.name())
                        #         mel.eval(cmd)
                        #         if anim_attr in ["scaleX", "scaleY", "scaleZ", "visibility"]:
                        #             pm.setAttr("%s.%s" % (jnt, anim_attr), 1)
                        #         print anim_attr

                        pm.select(scence_export_grp)
                        cmds.file(
                            export_file_name,
                            force=True,
                            pr=True,
                            es=True,
                            typ="FBX export",
                            options="v=0")

                        fbx_files.append(export_file_name)

                # for fbx_file in fbx_files:
                #     cmds.file(new=True, force=True)
                #     cmds.file(fbx_file, o=True)
                #     new_namespace_list = pm.namespaceInfo(lon=True)
                #     for new_name in system_namespace:
                #         new_namespace_list.remove(new_name)
                #     for new_namespace in new_namespace_list:
                #         pm.namespace(
                #             removeNamespace=":%s" % new_namespace,
                #             mergeNamespaceWithParent=True)
                #     cmds.file(
                #         export_file_name,
                #         force=True,
                #         pr=True,
                #         ea=True,
                #         typ="FBX export",
                #         options="v=0")

        else:
            pm.error(u"数据文件和输出路径不能为空")


def join_list_item(list_data):
    output_str = ""
    for item in list_data:
        print item
        output_str = output_str + ":" + item
        print output_str

    return output_str
