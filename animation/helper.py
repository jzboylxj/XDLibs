# coding=utf-8
"""

JSON数据管理工具

"""
import json
import os
from imp import reload

from animation import common
from animation import test_node
from pymel import core as pm

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


def list_to_str(data=None):
    """
    解析列表，将所有的成员转换成列表，中间用空格分隔开

    :param data: 需要解析的字符串
    :return: string
    """

    if data is None:
        data = []
    str_data = ""
    for item in data:
        str_data = str_data + " " + item
    return str_data.strip()


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
        # print(current_select)
        pm.textScrollList("rangeKeyList", e=True, ra=True)
        pm.textScrollList(
            "rangeKeyList", e=True, a=self.dict_data[current_select].keys())
        pm.textScrollList("jointKeyList", e=True, ra=True)

        return

    def _select_range(self):
        current_slider = pm.textScrollList("sliderKeyList", q=True, si=True)[0]
        current_range = pm.textScrollList("rangeKeyList", q=True, si=True)[0]
        # print("%s.%s" % (current_slider, current_range))
        pm.textScrollList("jointKeyList", e=True, ra=True)
        pm.textScrollList(
            "jointKeyList",
            e=True,
            a=self.dict_data[current_slider][current_range].keys())
        return

    def _select_joints(self):
        pm.select(pm.textScrollList("jointKeyList", q=True, si=True))

    def add_range_field(self, field, scroll_list):
        current_slider = pm.textScrollList("sliderKeyList", q=True, si=True)[0]

        if not self._check_field_exists(field, scroll_list):
            pm.textScrollList(scroll_list, e=True, a=[field])
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
                    current_slider][current_range][jnt.controller_name()] = jnt_value
        return

    def _check_field_exists(self, field, scroll_list):
        scroll_list = pm.textScrollList(scroll_list, q=True, ai=True)
        if field in scroll_list:
            return True
        else:
            return False

    def add_slider_key(self, slider, scroll_list):
        if not self._check_field_exists(slider, scroll_list):
            pm.textScrollList(scroll_list, e=True, a=slider)
        for item in pm.textScrollList(scroll_list, q=True, ai=True):
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

    def parse_str(self, str_data):
        str_list = str_data.split(";")
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
            print(u"%s 转化完毕" % controller)
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
            label="Custom Attr Helper", bgs=True)

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
                # (self.controller_field, 'right', 5,
                # self.select_controller_btn),
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
            name = name + item.controller_name() + ";"

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

        controller_name = pm.ls(sl=True)[0].controller_name()
        pm.textFieldButtonGrp(
            "customControllerGetter",
            e=True,
            text=controller_name)

        # print(controller_name)
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


manager_version = 0.2


class FaceController:
    def __init__(self):
        self.controller_name = ""

    def from_dict(self, dict_data):
        self.controller_name = dict_data["ControllerName"]
        self.controller_bone_name = dict_data["ControllerBoneName"]
        self.controller_group_name = dict_data["ControllerGroupName"]
        self.controller_postion_offset = dict_data["ControllerPositionOffset"]
        self.controller_axis_control = dict_data["AxisControl"]

    def __str__(self):
        return self.controller_name


class FeatureManager():
    def __init__(self, name):
        self.name = name
        self.control_group_file = ""
        self.control_file = ""

    def json_location(self, root_path):
        self.control_group_file = os.path.join(root_path, "{}ControlGroup.json".format(self.name))
        self.control_file = os.path.join(root_path, "{}Controller.json".format(self.name))

    def __str__(self):
        return self.name

    def custom_widget(self, parent):
        u"""
        标签栏之自定义捏脸栏

        :return: layout
        """
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
                          numberOfRadioButtons=2,
                          labelArray2=['Middle', 'LF And RT'], cw3=[140, 80, 80])
        pm.textFieldGrp("{}ControllerNameField".format(
            self.name), label=u"控制器")
        pm.textFieldGrp("{}ControllerBoneNameField".format(self.name), label=u"控制器挂点骨骼")
        # pm.textFieldGrp("{}ControllerGroupNameField".format(self.name), label=u"控制器组")
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

    def axis_control_joints_widget(self, parent="", axis=""):
        layout = pm.formLayout("{}Control{}JointFormLayout".format(self.name, axis), p=parent)
        joint_list_frame = pm.frameLayout(
            "{}Control{}JointListFrameLayout".format(self.name, axis), label="Joint List", p=layout)
        # print("{}Control{}JointListWidget".format(self.name, axis))
        pm.textScrollList("{}Control{}JointListWidget".format(self.name, axis), w=120)
        pm.popupMenu()
        pm.menuItem(label=u"添加骨骼", c=lambda *args: self.add_axis_joints())
        pm.setParent(joint_list_frame)
        joint_meta_frame = pm.frameLayout(
            "{}Control{}JointMetaFrameWidget".format(self.name, axis), label="Joint Meta", p=layout)
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

    def add_axis_joints(self, value="default"):
        tabs = pm.tabLayout("{}ControlJointListTabLayout".format(
            self.name), q=True, tl=True)
        select_tab_index = pm.tabLayout(
            "{}ControlJointListTabLayout".format(self.name), q=True, sti=True)
        current_tab = (tabs[select_tab_index - 1])

        current_controller = pm.textScrollList(
            "{}ControllerListWidget".format(self.name), q=True, si=True)[0]

        select_joint = pm.ls(sl=True)

        for index in range(0, len(self.control_group_data[current_controller]["ControlGroup"])):
            if current_tab in self.control_group_data[current_controller]["ControlGroup"][index]["GroupName"]:
                bone_range = self.control_group_data[current_controller]["ControlGroup"][index]["BoneRange"]
                for joint in select_joint:
                    if joint not in pm.textScrollList(
                            "{}Control{}JointListWidget".format(self.name, current_tab), q=True, ai=True):
                        pm.textScrollList("{}Control{}JointListWidget".format(
                            self.name, current_tab), e=True, a=joint)
                        joint_data = {}
                        joint_data["BoneName"] = joint.name()
                        joint_data["Max"] = [0, 0, 0, 0, 0, 0, 1, 1, 1]
                        joint_data["Min"] = [0, 0, 0, 0, 0, 0, 1, 1, 1]
                        bone_range.append(joint_data)
                self.control_group_data[current_controller]["ControlGroup"][index]["BoneRange"] = bone_range
                common.write_json(self.control_group_data, self.control_group_file)

        return

    def update_joints_meta(self, value):
        tabs = pm.tabLayout("{}ControlJointListTabLayout".format(
            self.name), q=True, tl=True)
        select_tab_index = pm.tabLayout(
            "{}ControlJointListTabLayout".format(self.name), q=True, sti=True)
        current_tab = (tabs[select_tab_index - 1])

        # joint_list = pm.textScrollList("{}Control{}JointListWidget".format(
        #     self.name, current_tab), q=True, ai=True)

        current_controller = pm.textScrollList(
            "{}ControllerListWidget".format(self.name), q=True, si=True)[0]

        control_group = self.control_group_data[current_controller]["ControlGroup"]

        for index in range(0, len(control_group)):
            # 查找ControlGroup里面对应的字典
            if current_tab in control_group[index]["GroupName"]:
                current_axis_data = control_group[index]["BoneRange"]
                for axis_data in current_axis_data:
                    # print("axis_data:{}".format(axis_data))
                    bone_name = axis_data["BoneName"]
                    if value == "Max":
                        axis_data["Max"] = self.joint_cb_list(pm.PyNode(bone_name).getParent())
                    elif value == "Min":
                        axis_data["Min"] = self.joint_cb_list(pm.PyNode(bone_name).getParent())
                # context_control_group = control_group[index]
                # context_bone_range = context_control_group["BoneRange"]

                # for bone_item in context_bone_range:
                #     for joint in joint_list:
                #         if joint in bone_item["BoneName"]:
                #             if value == "Max":
                #                 bone_item["Max"] = self.joint_cb_list(
                #                     pm.PyNode(joint).getParent())
                #             elif value == "Min":
                #                 bone_item["Min"] = self.joint_cb_list(
                #                     pm.PyNode(joint).getParent())
                # else:
                #     joint_data = {}
                #     joint_data["BoneName"] = joint
                #     joint_data["Max"] = [0,0,0,0,0,0,1,1,1]
                #     joint_data["Min"] = [0,0,0,0,0,0,1,1,1]
                # context_bone_range.append(joint_data)
                # print(context_bone_range)

                # for control_dict in context_control_group[BoneRange]:
                # joint_dict = context_dict["BoneRange"]
                # print(control_dict)
                # bone_range = []
                # # current_meta[index]["BoneRange"] = []
                # # print(current_meta)
                # for joint in joint_list:
                #     joint_data = {}
                #     joint_data["BoneName"] = joint
                #     if value == "Default":
                #         joint_data["Max"] = [0,0,0,0,0,0,1,1,1]
                #         joint_data["Min"] = [0,0,0,0,0,0,1,1,1]
                #     if value == "Max":
                #         joint_data["Max"] = self.joint_cb_list(pm.PyNode(joint).getParent())
                #         if "Min" in joint_data.keys():
                #             joint_data["Min"] = context_bone_range[index]
                #         else:
                #             joint_data["Min"] = [0,0,0,0,0,0,1,1,1]
                #     elif value =="Min":
                #         joint_data["Min"] = self.joint_cb_list(pm.PyNode(joint).getParent())
                #         if "Max" in joint_data.keys():
                #             joint_data["Max"] = joint_data["Max"]
                #         else:
                #             joint_data["Min"] = [0,0,0,0,0,0,1,1,1]
                #     current_meta[index]["BoneRange"].append(joint_data)
                #     bone_range.append(joint_data)
                # print(bone_range)
                # context_dict["BoneRange"] = bone_range
        common.write_json(self.control_group_data, self.control_group_file)
        return

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
            # 1, 1, 1
            round(pm.PyNode(jnt).scaleX.get(), pre),
            round(pm.PyNode(jnt).scaleY.get(), pre),
            round(pm.PyNode(jnt).scaleZ.get(), pre),
        ]
        return jnt_value

    def init_data(self):
        pm.textScrollList("{}ControllerListWidget".format(self.name), e=True, ra=True)
        self.control_group_data = common.read_json(self.control_group_file)
        self.control_data = common.read_json(self.control_file)
        self.controller_list = self.control_data["{}Controller".format(self.name)]

        if len(self.controller_list) > 0:
            for controller in self.controller_list:
                control = FaceController()
                control.from_dict(controller)
                pm.textScrollList("{}ControllerListWidget".format(self.name), e=True,
                                  a=control.controller_name)
            pm.textScrollList("{}ControllerListWidget".format(self.name), e=True, sii=1)
            select_controller_index = self.select_controller()

            self.init_control_joints_frmae_data(select_controller_index)
        return

    def init_control_joints_frmae_data(self, select_controller_index):
        axis_joint_tabs = self.controller_list[select_controller_index]["AxisControl"].values()
        for tab in axis_joint_tabs:
            if not tab == "":
                # print(tab)
                layout = "{}Control{}JointFormLayout".format(self.name, tab)
                if pm.formLayout(layout, q=True, ex=True):
                    pm.deleteUI(layout)
                # if tab

                axis_joint_tab = self.axis_control_joints_widget(
                    parent="{}ControlJointListTabLayout".format(self.name), axis=tab)
                pm.tabLayout("{}ControlJointListTabLayout".format(self.name), edit=True,
                             tabLabel=((axis_joint_tab, tab)))

                controller_name = pm.textFieldGrp(
                    "{}ControllerNameField".format(self.name), q=True, text=True)

                all_bone_range = self.control_group_data[controller_name]["ControlGroup"]
                for bone_range in all_bone_range:
                    if tab in bone_range["GroupName"]:
                        for bone_dict in bone_range["BoneRange"]:
                            bone_name = bone_dict["BoneName"]
                            text_scroll_list = "{}Control{}JointListWidget".format(self.name, tab)
                            if bone_name not in pm.textScrollList(text_scroll_list, q=True, ai=True):
                                pm.textScrollList(text_scroll_list, e=True, a=bone_name)

    def command_new_control(self):
        if self.build_control():
            self.init_data()

        return

    def build_control(self):
        u"""创建新的控制器

        :return:
        """
        default_control_data = {
            "ControllerPositionOffset": [0.0, 0.0, 0.0],
            "ControllerGroupName": "{}ControlGroup".format(self.name),
            "ControllerBoneName": "",
            "AxisControl": {
                "ZAxis": "",
                "XAxis": "",
                "YAxis": ""
            },
            "ControllerName": "control"
        }
        self.control_data['{}Controller'.format(
            self.name)].append(default_control_data)
        common.write_json(self.control_data, self.control_file)

        default_control_joint_group = []
        default_control_joint_group.append({
            "BoneRange": [],
            "GroupName": "control_X"
        })
        default_control_joint_group.append({
            "BoneRange": [],
            "GroupName": "control_Y"
        })
        default_control_joint_group.append({
            "BoneRange": [],
            "GroupName": "control_Z"
        })

        default_control_group_data = {
            "ControlGroup": default_control_joint_group,
            "GroupName": "{}ControlGroup".format(self.name),
            "shapeType": "control"
        }
        self.control_group_data["control"] = default_control_group_data
        common.write_json(self.control_group_data, self.control_group_file)

        return True

    def select_controller(self):
        select_index = pm.textScrollList(
            "{}ControllerListWidget".format(self.name), q=True, sii=True)[0]
        controller_data = self.get_controller_meta_data(select_index - 1)
        self.clean_meta_data_frame()
        self.retrieve_meta_data(controller_data)

        # pm.textScrollList("{}ControllerListWidget".format(self.name), e=True, ra=True)

        select_controller = pm.textScrollList(
            "{}ControllerListWidget".format(self.name), q=True, si=True)[0]

        # for tab_layout in pm.tabLayout("{}ControlJointListTabLayout".format(self.name), q=True, tl=True):
        # pm.deleteUI(tab_layout)
        # print(tab_layout)
        print(pm.tabLayout("{}ControlJointListTabLayout".format(self.name), q=True, tl=True))
        self.init_control_joints_frmae_data(select_index - 1)

        # select_controller_index = select_index - 1
        # axis_joint_tabs = self.controller_list[select_controller_index]["AxisControl"].values()
        # for tab in axis_joint_tabs:
        #     if not tab == "":
        #         # print(tab)
        #         layout = "{}Control{}JointFormLayout".format(self.name, tab)
        #         # if pm.formLayout(layout, q=True, ex=True):
        #         #     pm.deleteUI(layout)

        # self.init_data()

        return select_index - 1

    def get_controller_meta_data(self, controller_index):
        return self.controller_list[controller_index]

    def clean_meta_data_frame(self):
        pm.textFieldGrp("{}ControllerNameField".format(
            self.name), e=True, text="")
        pm.textFieldGrp("{}ControllerBoneNameField".format(
            self.name), e=True, text="")
        # pm.textFieldGrp("{}ControllerGroupNameField".format(self.name), e=True, text="")
        pm.floatFieldGrp("{}ControllerPositionOffsetField".format(self.name), e=True,
                         value1=0.0, value2=0.0, value3=0.0)
        pm.checkBoxGrp("{}ControllerAxisControlField".format(self.name), e=True,
                       value1=False, value2=False, value3=False)
        return

    def retrieve_meta_data(self, data):
        u"""查询控制器元数据

        :return
        """

        if "_LF" in data["ControllerName"] or "RT" in data["ControllerName"]:
            pm.radioButtonGrp("{}ControllerSideField".format(
                self.name), e=True, sl=2)
        else:
            pm.radioButtonGrp("{}ControllerSideField".format(
                self.name), e=True, sl=1)

        pm.textFieldGrp("{}ControllerNameField".format(
            self.name), e=True, text=data["ControllerName"])
        pm.textFieldGrp("{}ControllerBoneNameField".format(
            self.name), e=True, text=data["ControllerBoneName"])
        # pm.textFieldGrp("{}ControllerGroupNameField".format(self.name), e=True, text=data["ControllerGroupName"])
        pm.floatFieldGrp("{}ControllerPositionOffsetField".format(self.name), e=True,
                         value1=data["ControllerPositionOffset"][0],
                         value2=data["ControllerPositionOffset"][1],
                         value3=data["ControllerPositionOffset"][2])
        axis_control_check_grp = data["AxisControl"]
        if axis_control_check_grp["XAxis"] == "":
            axis_x = False
        else:
            axis_x = True
        if axis_control_check_grp["YAxis"] == "":
            axis_y = False
        else:
            axis_y = True
        if axis_control_check_grp["ZAxis"] == "":
            axis_z = False
        else:
            axis_z = True
        pm.checkBoxGrp("{}ControllerAxisControlField".format(self.name), e=True,
                       value1=axis_x, value2=axis_y, value3=axis_z)
        return

    def update_meta_data(self):
        U""" 更新元数据

        :return: True
        """
        meta_data = {}

        controller_name = pm.textFieldGrp(
            "{}ControllerNameField".format(self.name), q=True, text=True)
        meta_data["ControllerName"] = controller_name

        meta_data["ControllerBoneName"] = pm.textFieldGrp(
            "{}ControllerBoneNameField".format(self.name), q=True, text=True)
        meta_data["ControllerGroupName"] = "{}ControlGroup".format(self.name)
        meta_data["ControllerPositionOffset"] = pm.floatFieldGrp(
            "{}ControllerPositionOffsetField".format(self.name), q=True, value=True)
        meta_data["AxisControl"] = {}

        if pm.checkBoxGrp("{}ControllerAxisControlField".format(self.name), q=True, v1=True):
            meta_data["AxisControl"]["XAxis"] = "{}_X".format(controller_name)
        else:
            meta_data["AxisControl"]["XAxis"] = ""
        if pm.checkBoxGrp("{}ControllerAxisControlField".format(self.name), q=True, v2=True):
            meta_data["AxisControl"]["YAxis"] = "{}_Y".format(controller_name)
        else:
            meta_data["AxisControl"]["YAxis"] = ""
        if pm.checkBoxGrp("{}ControllerAxisControlField".format(self.name), q=True, v3=True):
            meta_data["AxisControl"]["ZAxis"] = "{}_Z".format(controller_name)
        else:
            meta_data["AxisControl"]["ZAxis"] = ""

        select_index = pm.textScrollList(
            "{}ControllerListWidget".format(self.name), q=True, sii=True)[0]
        select_control = pm.textScrollList(
            "{}ControllerListWidget".format(self.name), q=True, si=True)[0]

        self.controller_list[select_index - 1] = meta_data

        # print(select_control)

        # print(self.control_group_data)

        control_data = self.control_group_data[select_control]
        control_data["shapeType"] = controller_name
        control_data["GroupName"] = "{}ControlGroup".format(self.name)
        current_controller = pm.textScrollList(
            "{}ControllerListWidget".format(self.name), q=True, si=True)[0]
        for control_group in control_data["ControlGroup"]:
            control_group["GroupName"] = control_group["GroupName"].replace(
                current_controller, controller_name)

        del self.control_group_data[select_control]
        self.control_group_data[controller_name] = control_data

        # print(self.control_group_data)

        if (common.write_json(self.control_data, self.control_file) and
                common.write_json(self.control_group_data, self.control_group_file)):
            self.clean_meta_data_frame()

            all_tabs = pm.tabLayout(
                "{}ControlJointListTabLayout".format(self.name), q=True, ca=True)
            if all_tabs is not None:
                if len(all_tabs) > 1:
                    for tab in all_tabs:
                        pm.deleteUI(tab)

            self.init_data()

        return True

    def build_test_proxy(self):
        # selected_tab = self.current_select_tab("jsonManagerMainTabLayout")
        selected_tab = self.name
        selected_controller = pm.textScrollList("{}ControllerListWidget".format(self.name), q=True, si=True)[0]
        print(self.name)
        print(selected_controller)

    def current_select_tab(self, tab_object):
        tabs = pm.tabLayout(tab_object, q=True, tl=True)
        select_tab_index = pm.tabLayout(tab_object, q=True, sti=True)
        current_tab = (tabs[select_tab_index - 1])
        return current_tab


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

        self.current_tab_index = 1

        # 历史版本的json文件存放路径
        self.brow_file_folder = ""
        self.eye_file_folder = ""
        self.nose_file_folder = ""
        self.mouth_file_folder = ""
        self.face_file_folder = ""

        self.show()
        self.initialize()
        # self.selected_controller()

    def show(self):
        u"""显示工具窗口

        :return: window
        """
        if pm.window("jsonManagerUI", ex=True):
            pm.deleteUI("jsonManagerUI")
        pm.window("jsonManagerUI", t=u"角色脸部特征编辑器 %s" % manager_version, mb=True,
                  cc=lambda *args: self._closed_window_cmd())

        # self.menu_list()

        form_layout = pm.formLayout()

        config_frame = pm.frameLayout(
            p=form_layout, label=u"配置面板", mw=5, mh=5, bgs=True, cll=True, cl=False)
        pm.textFieldButtonGrp("XDFaceEditDataStoreField", label=u"存储路径", bl=u"设置", adj=2, cw3=[60, 100, 40],
                              bc=lambda *args: self.setting_json_folder())
        pm.textFieldButtonGrp("XDFaceEditNewModuleField", label=u"特征模块", bl=u"新建", adj=2, cw3=[60, 100, 40],
                              bc=lambda *args: self.command_new_module())
        pm.setParent(config_frame)

        work_frame = pm.frameLayout(
            p=form_layout, label=u"工作面板", mw=5, mh=5, bgs=True, cll=True, cl=False)
        self.main_tab = pm.tabLayout(
            "jsonManagerMainTabLayout", innerMarginWidth=5, innerMarginHeight=5)
        pm.setParent(self.main_tab)
        pm.setParent(work_frame)

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (config_frame, 'top', 10),
                (config_frame, 'left', 10),
                (config_frame, 'right', 10),
                (work_frame, 'left', 10),
                (work_frame, 'right', 10),
                (work_frame, 'bottom', 10),
            ],
            attachControl=[
                (work_frame, 'top', 5, config_frame),
            ])
        pm.setParent(form_layout)

        pm.showWindow("jsonManagerUI")

    def menu_list(self):
        u"""
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
                (tab_layout, 'top', 5, option_menu),
            ])

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
        # print(pm.textScrollList("ARIDScrollList", q=True, si=True)[0])
        selected_key = pm.textScrollList("ARIDScrollList", q=True, si=True)[0]
        # print(self.ar_data[selected_key])
        if not pm.objExists(selected_key):
            self.create_slider_controller(name=selected_key)
        return

    def create_slider_controller(self, name):
        locator = zero_locator(name=name)
        pm.addAttr(locator, ln="sliderX", at="double", min=0, max=1, dv=0)
        pm.setAttr("%s.sliderX" % locator, e=True, k=True)

        return

    def initialize(self):
        if pm.optionVar(q='jsonManagerFolder'):
            self.json_folder = pm.optionVar(q='jsonManagerFolder')
            pm.textFieldButtonGrp("XDFaceEditDataStoreField", e=True, text=self.json_folder)
            self.init_module_data()

        # if pm.optionVar(q='jsonManagerMainTabLayoutIndex'):
        #     self.current_tab_index = int(pm.optionVar(
        #         q='jsonManagerMainTabLayoutIndex'))

        # if pm.optionVar(q='jsonManagerDiscardBrowFilePath'):
        #     self.brow_file_folder = pm.optionVar(
        #         q='jsonManagerDiscardBrowFilePath')
        # if pm.optionVar(q='jsonManagerDiscardEyeFilePath'):
        #     self.eye_file_folder = pm.optionVar(
        #         q='jsonManagerDiscardEyeFilePath')
        # if pm.optionVar(q='jsonManagerDiscardNoseFilePath'):
        #     self.nose_file_folder = pm.optionVar(
        #         q='jsonManagerDiscardNoseFilePath')
        # if pm.optionVar(q='jsonManagerDiscardMouthFilePath'):
        #     self.mouth_file_folder = pm.optionVar(
        #         q='jsonManagerDiscardMouthFilePath')
        # if pm.optionVar(q='jsonManagerDiscardFaceFilePath'):
        #     self.face_file_folder = pm.optionVar(
        #         q='jsonManagerDiscardFaceFilePath')

    def init_module_data(self):
        self.module_sections = self.scanning_folder("folders")
        for module_section in self.module_sections:
            module = FeatureManager(module_section)
            module.json_location(os.path.join(self.json_folder, module_section))
            layout = module.custom_widget(parent=self.main_tab)
            pm.tabLayout(self.main_tab, edit=True, tabLabel=((layout, module_section)))
            # for module

    def _closed_window_cmd(self):
        pm.optionVar(sv=('jsonManagerFolder', self.json_folder))
        # pm.optionVar(sv=('arFileLocation', self.ar_file_location))

        # self.current_tab_index = pm.tabLayout(self.main_tab, q=True, sti=True)

        # pm.optionVar(
        #     sv=('jsonManagerMainTabLayoutIndex', self.current_tab_index))

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
            dialogStyle=2, fileFilter="JSON File (*.json);;", fileMode=3, okc=u"选择文件夹")
        if json_folder[0]:
            self.json_folder = json_folder[0]
            self.module_sections = self.scanning_folder("folders")
            pm.textFieldButtonGrp("XDFaceEditDataStoreField",
                                  e=True, text=json_folder[0])

        return

    def scanning_folder(self, return_type):
        u"""扫描文件夹，将目录列取出来，如果目录下有对应的文件（例：文件夹名face, 对应的文件）

        :param return_type: 返回类型
        """
        json_list = []
        json_file = ""
        folder_list = []
        if self.json_folder != '':
            path_dir = os.listdir(self.json_folder)
            for json_file in path_dir:
                if json_file == ".mayaSwatches":
                    continue
                full_path = "%s/%s" % (self.json_folder, json_file)
                if os.path.isdir(full_path):
                    # print("%s it's a directory" % full_path)
                    folder_list.append(json_file)
                elif os.path.isfile(full_path):
                    # print("%s it's a normal file" % full_path)
                    # 获取JSON文件的名字后，清理文件的后缀名
                    file_name = os.path.splitext(json_file)[0]
                    json_list.append(file_name)
        if return_type == "files":
            return json_file
        elif return_type == "folders":
            return folder_list

    def command_new_module(self):
        if self.new_module():
            self.init_module_data()

    def new_module(self):
        u"""创建新的特征模块

        :return:
        """
        data_root = self.json_folder
        module_name = pm.textFieldButtonGrp(
            "XDFaceEditNewModuleField", q=True, text=True)
        if not module_name == "":
            module_path = os.path.join(data_root, module_name)
            # print(module_path)
            if not os.path.exists(module_path):
                os.makedirs(module_path)
                if self.new_module_data_file(module_name, module_path):
                    pm.textFieldButtonGrp(
                        "XDFaceEditNewModuleField", e=True, text="")
            else:
                pm.error(u"{}模块创建过程错误，目录下已经存在同名模块".format(module_name))
        else:
            pm.error(u"模块的名字不能缺")
        return True

    def new_module_data_file(self, module_name, module_path):
        module_control_group_file = "{}ControlGroup.json".format(module_name)
        module_control_group_file_path = os.path.join(
            module_path, module_control_group_file)
        module_control_group_data = {}
        print(module_control_group_file_path)
        common.write_json(module_control_group_data,
                          file_path=module_control_group_file_path)

        module_control_file = "{}Controller.json".format(module_name)
        module_control_file_path = os.path.join(
            module_path, module_control_file)
        module_control_data = {}
        module_control_data["{}Controller".format(module_name)] = []
        print(module_control_file_path)
        common.write_json(module_control_data,
                          file_path=module_control_file_path)

        return True

    def option_menu_widget(self, parent_widget):
        if pm.optionMenuGrp("faceModuleOptionsWidget", ex=True):
            pm.deleteUI("faceModuleOptionsWidget")
        widget = pm.optionMenuGrp(
            "faceModuleOptionsWidget",
            parent=parent_widget,
            label=u"模块名称",
            cw2=[50, 50],
            adj=2,
            cc=lambda *args: self.selected_controller(pm.optionMenuGrp(widget, q=True, value=True)))
        if len(self.module_sections) > 0:
            for json_file in self.module_sections:
                pm.menuItem(label=json_file)

        return widget

    def selected_controller(self, module):
        u"""
        选择控制器
        """
        selected_controller = pm.optionMenuGrp(
            "faceModuleOptionsWidget", q=True, value=True)
        # print("selected controller: %s" % selected_controller)
        controller_file = "%s/%s/%sController.json" % (
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

    def add_module(self):
        u"""
        添加模块

        模块实际上是一个文件夹。
        每当新建一个模块，程序会在文件夹下面创建两个JSON文件。分别为控制器文件和控制器的细节信息文件。
        例如：
            模块名 Face
                控制器文件 FaceController.json
                细节文件 FaceControlGroup.json

        :return: True
        """
        # 文件模式
        file_path = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=3,
            okc=u"设置模块路径")
        folder_name = file_path[0].split("/")[len(file_path[0].split("/")) - 1]

        # 将新添加的模块添加到菜单项
        pm.menuItem(label=folder_name, parent="faceModuleOptionsWidget|OptionMenu")

        controller_path = "%s/%sController.json" % (file_path[0], folder_name)

        dict_data = {}
        controller_key = "%sController" % folder_name
        dict_data[controller_key] = []
        common.write_json(dict_data=dict_data, file_path=controller_path)
        control_group_path = "%s/%sControlGroup.json" % (file_path[0], folder_name)
        common.write_json(dict_data={}, file_path=control_group_path)

        # 将菜单栏的当前选择修改为新添加的模块
        pm.optionMenuGrp("faceModuleOptionsWidget", e=True, value=folder_name)

        return True

    def add_controller(self):
        controller_index = pm.scrollLayout("controllerListLayout", q=True, nch=True)
        self.controller[controller_index] = ("controllerGrp%s" % controller_index)
        self.add_controller_widget(index=controller_index, parent="controllerListLayout")

    def add_controller_widget(self, index=0, parent=""):
        if pm.columnLayout("controllerListItemLayout%s" % index, q=True, ex=True):
            pm.deleteUI("controllerListItemLayout%s" % index)

        layout = pm.columnLayout("controllerListItemLayout%s" % index, adj=1, parent=parent)

        pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                              label=u"控制器名", cw3=[60, 200, 140], bl=u"指定",
                              bc=lambda *args: self.get_custom_controller(index))
        pm.textFieldButtonGrp("controllerGrpNameWidget%s" % index,
                              label=u"控制器组", cw3=[60, 200, 140], bl=u"指定")
        pm.textFieldButtonGrp(
            "controllerBoneNameWidget%s" % index, label=u"挂点名称", cw3=[60, 200, 140], bl=u"指定",
            bc=lambda *args: self.get_sample_node(text_widget="controllerBoneNameWidget%s" % index))
        pm.floatFieldGrp("controllerBoneOffsetWidget%s" % index,
                         numberOfFields=3, pre=3, label=u'挂点偏移', cw4=[60, 50, 50, 50])

        pm.textFieldGrp("controller%sAxisX" % index, label=u"XAxis", cw2=[60, 200])
        pm.textFieldGrp("controller%sAxisY" % index, label=u"YAxis", cw2=[60, 200])
        pm.textFieldGrp("controller%sAxisZ" % index, label=u"ZAxis", cw2=[60, 200])

        pm.separator(style='in', height=20)

        pm.setParent("..")  # end of layout

        return layout

    def add_control_detail_widget(self):
        parent = "controllerDetailListLayout"
        for index in range(0, pm.scrollLayout("controllerListLayout", q=True, nch=True)):
            if pm.frameLayout("controllerDetailListItemLayout%s" % index, q=True, ex=True):
                pm.deleteUI("controllerDetailListItemLayout%s" % index)

            pm.frameLayout("controllerDetailListItemLayout%s" % index,
                           bgs=True, mw=10, mh=5, cll=True, cl=False, parent=parent)
            pm.textFieldButtonGrp("controllerDetailControlType%s" % index,
                                  label=u"控制类型", bl=u"指定", cw3=[48, 200, 140])
            pm.textFieldButtonGrp("controllerDetailControlGroup%s" % index,
                                  label=u"控制器组", bl=u"指定", cw3=[48, 200, 140])
            pm.text(label=u"滑竿控制", al="left", width=100)
            pm.text(label="SliderX:", al="left")
            pm.textScrollList("controllerDetailSliderXBone%s" % index)
            pm.text(label="SliderY:", al="left")
            pm.textScrollList("controllerDetailSliderYBone%s" % index)
            pm.text(label="SliderZ:", al="left")
            pm.textScrollList("controllerDetailSliderZBone%s" % index)
            pm.setParent("..")

            # 自动录入一些数据
            frame_label = pm.textFieldButtonGrp("controllerNameWidget%s" % index, q=True, text=True)
            pm.frameLayout("controllerDetailListItemLayout%s" % index, e=True, label=frame_label)

            control_type = pm.optionMenuGrp("faceModuleOptionsWidget", q=True, value=True)
            pm.textFieldButtonGrp("controllerDetailControlType%s" % index, e=True, text=control_type)

            control_grp = pm.textFieldButtonGrp("controllerGrpNameWidget%s" % index, q=True, text=True)
            pm.textFieldButtonGrp("controllerDetailControlGroup%s" % index, e=True, text=control_grp)

            control_name = pm.textFieldButtonGrp("controllerNameWidget%s" % index, q=True, text=True)

            axis_x = pm.textFieldGrp("controller%sAxisX" % index, q=True, text=True)
            if axis_x != "" and axis_x is not None:
                definition_joints = pm.PyNode(control_name).attr("jointsX").get()
                pm.textScrollList("controllerDetailSliderXBone%s" % index, e=True, a=str_to_list(definition_joints))

            axis_y = pm.textFieldGrp("controller%sAxisY" % index, q=True, text=True)
            if axis_y != "" and axis_y is not None:
                definition_joints = pm.PyNode(control_name).attr("jointsY").get()
                pm.textScrollList("controllerDetailSliderYBone%s" % index, e=True, a=str_to_list(definition_joints))

            axis_z = pm.textFieldGrp("controller%sAxisZ" % index, q=True, text=True)
            if axis_z != "" and axis_z is not None:
                definition_joints = pm.PyNode(control_name).attr("jointsZ").get()
                pm.textScrollList("controllerDetailSliderZBone%s" % index, e=True, a=str_to_list(definition_joints))

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

        # print("Detail item : %s" % pm.scrollLayout(
        #     "controllerDetailListLayout", q=True, nch=True))

        for index in range(0, pm.scrollLayout("controllerDetailListLayout", q=True, nch=True)):
            # dict_data = {}

            key_name = pm.frameLayout("controllerDetailListItemLayout%s" % index,
                                      q=True, label=True)
            dict_data[key_name] = {}
            dict_data[key_name]["shapeType"] = pm.optionMenuGrp(
                "faceModuleOptionsWidget", q=True, value=True)
            dict_data[key_name]["GroupName"] = pm.textFieldButtonGrp(
                "controllerDetailControlGroup%s" % index, q=True, text=True)

            dict_data[key_name]["ControlGroup"] = []

            axis_x = dict()
            axis_x["GroupName"] = "%s_X" % key_name
            axis_x["BoneRange"] = []

            for jnt in pm.textScrollList("controllerDetailSliderXBone%s" % index, q=True, ai=True):
                jnt_dict = dict()
                jnt_dict["BoneName"] = jnt
                jnt_dict["Max"] = []
                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderX"), 1)
                    jnt_dict["Max"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderX"), 0)
                jnt_dict["Min"] = []
                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderX"), -1)
                    jnt_dict["Min"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderX"), 0)

                axis_x["BoneRange"].append(jnt_dict)
            dict_data[key_name]["ControlGroup"].append(axis_x)

            axis_y = dict()
            axis_y["GroupName"] = "%s_Y" % key_name
            axis_y["BoneRange"] = []

            for jnt in pm.textScrollList("controllerDetailSliderYBone%s" % index, q=True, ai=True):
                jnt_dict = dict()
                jnt_dict["BoneName"] = jnt
                jnt_dict["Max"] = []
                jnt_dict["Min"] = []

                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderY"), 1)
                    jnt_dict["Max"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderY"), 0)
                jnt_dict["Min"] = []
                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderY"), -1)
                    jnt_dict["Min"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderY"), 0)

                axis_y["BoneRange"].append(jnt_dict)
            dict_data[key_name]["ControlGroup"].append(axis_y)

            axis_z = dict()
            axis_z["GroupName"] = "%s_Z" % key_name
            axis_z["BoneRange"] = []

            for jnt in pm.textScrollList("controllerDetailSliderZBone%s" % index, q=True, ai=True):
                jnt_dict = dict()
                jnt_dict["BoneName"] = jnt
                jnt_dict["Max"] = []
                jnt_dict["Min"] = []

                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderZ"), 1)
                    jnt_dict["Max"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderZ"), 0)
                jnt_dict["Min"] = []
                if jnt:
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderZ"), -1)
                    jnt_dict["Min"] = self.joint_cb_list(jnt)
                    pm.setAttr(pm.PyNode(pm.textFieldButtonGrp("controllerNameWidget%s" % index,
                                                               q=True, text=True)).attr("sliderZ"), 0)

                axis_z["BoneRange"].append(jnt_dict)

            dict_data[key_name]["ControlGroup"].append(axis_z)

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

        controller_data = dict()
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
        # print(tab_array[current_tab_index])
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


def join_list_item(list_data):
    output_str = ""
    for item in list_data:
        print(item)
        output_str = output_str + ":" + item
        print(output_str)
    return output_str


class DataPasteHelper(common.Singleton):
    def __init__(self):
        super(DataPasteHelper, self).__init__()

        self.expression_data = {}
        self.joint_number = 0

        self.target_list = []

        self.show()

    def show(self):
        if pm.window("ExpressionHelper", ex=True):
            pm.deleteUI("ExpressionHelper")
        pm.window("ExpressionHelper", t=u"数据粘贴助手", mb=True)

        form_layout = pm.formLayout()

        column_layout = pm.columnLayout(adj=1, rs=2)
        self.work_mode_control = pm.radioButtonGrp(
            p=column_layout,
            label=u"工作模式：",
            labelArray3=[u'镜像', u'翻转', u'粘贴'],
            numberOfRadioButtons=3,
            cw4=[60, 60, 60, 60],
            sl=1)

        pm.frameLayout(p=column_layout, label=u"约束轴", mw=5, mh=5, bgs=True)
        self.translate_offset_value = pm.checkBoxGrp(
            label="Translate:",
            numberOfCheckBoxes=3,
            labelArray3=['X', 'Y', 'Z'],
            va3=[True, False, False],
            cw4=[60, 50, 50, 50])
        self.rotate_offset_value = pm.checkBoxGrp(
            label="Rotate:",
            numberOfCheckBoxes=3,
            labelArray3=['X', 'Y', 'Z'],
            va3=[False, True, True],
            cw4=[60, 50, 50, 50])
        self.scale_offset_value = pm.checkBoxGrp(
            label="Scale:",
            numberOfCheckBoxes=3,
            labelArray3=['X', 'Y', 'Z'],
            va3=[False, False, False],
            cw4=[60, 50, 50, 50])
        pm.setParent("..")

        self.label_control = pm.text(
            p=column_layout, label=u"搜索和替换选项：", al="left")
        self.search_field_control = pm.textFieldGrp(
            p=column_layout, label=u"搜索：", cw2=[60, 240], text="_L_")
        self.replace_field_control = pm.textFieldGrp(
            p=column_layout, label=u"替换：", cw2=[60, 240], text="_R_")
        self.task_info_control = pm.text(
            p=column_layout,
            label=u"已经复制%s个对象的通道栏数据" % self.joint_number,
            w=300,
            al="left")
        pm.setParent(column_layout)

        self.copy_button = pm.button(
            p=form_layout,
            label=u"复制数据", w=80, c=lambda *args: self.copy_expression())
        self.select_source_button = pm.button(
            p=form_layout,
            label=u"选择来源",
            w=80, c=lambda *args: self.select_source_object())
        self.select_target_button = pm.button(
            p=form_layout,
            label=u"选择目标",
            w=80, c=lambda *args: self.select_target_object())
        self.paste_button = pm.button(
            p=form_layout,
            label=u"拷贝数据", w=80, c=lambda *args: self.paste_expression())

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (column_layout, "top", 10),
                (column_layout, "left", 10),
                (column_layout, "right", 10),
                (self.copy_button, 'left', 10),
                (self.copy_button, 'bottom', 10),
                (self.select_source_button, 'bottom', 10),
                (self.select_target_button, 'bottom', 10),
                (self.paste_button, 'bottom', 10),
                (self.paste_button, 'right', 10),
            ],
            attachControl=[
                (column_layout, 'bottom', 10, self.copy_button),
                (self.select_source_button, 'left', 10, self.copy_button),
                (self.select_target_button, 'left', 10,
                 self.select_source_button),
                (self.paste_button, 'left', 10, self.select_target_button),
            ])
        pm.showWindow("ExpressionHelper")

    def copy_expression(self):
        self.expression_data = {}
        sel_joints = pm.ls(sl=True)
        for jnt in sel_joints:
            self.expression_data[jnt.shortName()] = [
                round(pm.PyNode(jnt).translateX.get(), 5),
                round(pm.PyNode(jnt).translateY.get(), 5),
                round(pm.PyNode(jnt).translateZ.get(), 5),
                round(pm.PyNode(jnt).rotateX.get(), 5),
                round(pm.PyNode(jnt).rotateY.get(), 5),
                round(pm.PyNode(jnt).rotateZ.get(), 5),
                round(pm.PyNode(jnt).scaleX.get(), 5),
                round(pm.PyNode(jnt).scaleY.get(), 5),
                round(pm.PyNode(jnt).scaleZ.get(), 5),
            ]
        self.joint_number = len(sel_joints)
        pm.text(self.task_info_control,
                e=True,
                label=u"已经复制%s根骨骼的信息" % self.joint_number)
        return True

    def select_source_object(self):
        source_objects = self.expression_data.keys()
        pm.select(source_objects)
        return

    def select_target_object(self):
        target_objects = self.target_list
        pm.select(target_objects)
        return

    def convert_check_list(self, check_list=[]):
        new_list = [1, 1, 1]
        if check_list[0]:
            new_list[0] = -1
        else:
            new_list[0] = 1

        if check_list[1]:
            new_list[1] = -1
        else:
            new_list[1] = 1

        if check_list[2]:
            new_list[2] = -1
        else:
            new_list[2] = 1
        return new_list

    def paste_expression(self):
        work_mode_list = ['mirror', 'flip', 'paste']
        current_mode_index = pm.radioButtonGrp(
            self.work_mode_control, q=True, sl=True)
        work_mode = work_mode_list[current_mode_index - 1]
        translate_offset_value = self.convert_check_list(
            pm.checkBoxGrp(self.translate_offset_value, q=True, va3=True))
        rotate_offset_value = self.convert_check_list(
            pm.checkBoxGrp(self.rotate_offset_value, q=True, va3=True))
        scale_offset_value = self.convert_check_list(
            pm.checkBoxGrp(self.scale_offset_value, q=True, va3=True))
        self.target_list = []
        for jnt in self.expression_data.keys():
            search_field = pm.textFieldGrp(
                self.search_field_control, q=True, text=True)
            replace_field = pm.textFieldGrp(
                self.replace_field_control, q=True, text=True)
            target_jnt = jnt.replace(search_field, replace_field)
            self.target_list.append(target_jnt)
            value = self.expression_data[jnt]
            if work_mode == 'mirror':
                new_value = [
                    value[0] * translate_offset_value[0],
                    value[1] * translate_offset_value[1],
                    value[2] * translate_offset_value[2],
                    value[3] * rotate_offset_value[0],
                    value[4] * rotate_offset_value[1],
                    value[5] * rotate_offset_value[2],
                    value[6] * scale_offset_value[0],
                    value[7] * scale_offset_value[1],
                    value[8] * scale_offset_value[2]
                ]
                pm.PyNode(target_jnt).translate.set(
                    [new_value[0], new_value[1], new_value[2]])
                pm.PyNode(target_jnt).rotate.set(
                    [new_value[3], new_value[4], new_value[5]])
                pm.PyNode(target_jnt).scale.set(
                    [new_value[6], new_value[7], new_value[8]])
        else:
            pass

        return True


class DataHelper(common.Singleton):
    def __init__(self):
        super(DataHelper, self).__init__()

        self.show()

    def sdk_layout(self, parent):
        layout = pm.frameLayout(
            p=parent, label="SDK Mirror Helper", bgs=True, mw=10, mh=10)
        pm.textFieldGrp(label="Search", cw2=[80, 150])
        pm.textFieldGrp(label="Replace", cw2=[80, 150])
        pm.setParent(layout)
        return layout

    def show(self):
        if pm.window("xdDataHelperWnd", ex=True):
            pm.deleteUI("xdDataHelperWnd")
        pm.window(
            "xdDataHelperWnd",
            t=u"数据镜像操作助手",
            mb=True)

        form_layout = pm.formLayout()

        work_mode_layout = pm.rowColumnLayout(nr=1, p=form_layout)
        pm.text(label=u"工作模式：")
        collection1 = pm.radioCollection()
        rb1 = pm.radioButton(label='SDK')
        rb2 = pm.radioButton(label='Attribute')
        pm.setParent('..')
        pm.setParent(work_mode_layout)

        container_layout = pm.columnLayout(adj=1, p=form_layout)
        self.sdk_layout(parent=container_layout)
        pm.setParent(container_layout)

        mirror_btn = pm.button(label="Mirror", p=form_layout)

        # column_layout = pm.columnLayout(adj=1, rs=2)
        # self.work_mode_control = pm.radioButtonGrp(
        #     p=column_layout,
        #     label=u"工作模式：",
        #     labelArray3=[u'镜像', u'翻转', u'粘贴'],
        #     numberOfRadioButtons=3,
        #     cw4=[60, 60, 60, 60],
        #     sl=1)

        # pm.frameLayout(p=column_layout, label=u"约束轴", mw=5, mh=5, bgs=True)
        # self.translate_offset_value = pm.checkBoxGrp(
        #     label="Translate:",
        #     numberOfCheckBoxes=3,
        #     labelArray3=['X', 'Y', 'Z'],
        #     va3=[True, False, False],
        #     cw4=[60, 50, 50, 50])
        # self.rotate_offset_value = pm.checkBoxGrp(
        #     label="Rotate:",
        #     numberOfCheckBoxes=3,
        #     labelArray3=['X', 'Y', 'Z'],
        #     va3=[False, True, True],
        #     cw4=[60, 50, 50, 50])
        # self.scale_offset_value = pm.checkBoxGrp(
        #     label="Scale:",
        #     numberOfCheckBoxes=3,
        #     labelArray3=['X', 'Y', 'Z'],
        #     va3=[False, False, False],
        #     cw4=[60, 50, 50, 50])
        # pm.setParent("..")

        # self.label_control = pm.text(
        #     p=column_layout, label=u"搜索和替换选项：", al="left")
        # self.search_field_control = pm.textFieldGrp(
        #     p=column_layout, label=u"搜索：", cw2=[60, 240], text="_L_")
        # self.replace_field_control = pm.textFieldGrp(
        #     p=column_layout, label=u"替换：", cw2=[60, 240], text="_R_")
        # self.task_info_control = pm.text(
        #     p=column_layout,
        #     label=u"已经复制%s个对象的通道栏数据" % self.joint_number,
        #     w=300,
        #     al="left")
        # pm.setParent(column_layout)

        # self.copy_button = pm.button(
        #     p=form_layout,
        #     label=u"复制数据", w=80, c=lambda *args: self.copy_expression())
        # self.select_source_button = pm.button(
        #     p=form_layout,
        #     label=u"选择来源",
        #     w=80, c=lambda *args: self.select_source_object())
        # self.select_target_button = pm.button(
        #     p=form_layout,
        #     label=u"选择目标",
        #     w=80, c=lambda *args: self.select_target_object())
        # self.paste_button = pm.button(
        #     p=form_layout,
        #     label=u"拷贝数据", w=80, c=lambda *args: self.paste_expression())

        pm.radioCollection(collection1, edit=True, select=rb1)

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (work_mode_layout, "top", 5),
                (work_mode_layout, "left", 10),
                (work_mode_layout, "right", 10),
                (container_layout, 'left', 10),
                (container_layout, 'right', 10),
                (mirror_btn, 'left', 10),
                (mirror_btn, 'right', 10),
                (mirror_btn, 'bottom', 10),
            ],
            attachControl=[
                (container_layout, 'top', 10, work_mode_layout),
            ])
        pm.showWindow("xdDataHelperWnd")
