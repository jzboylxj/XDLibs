# coding=utf-8
from pymel import core as pm
import os

import maya.cmds as cmds
import maya.mel as mel

import common

reload(common)

__author__ = 'Li Xiao Jun'
__version__ = '0.2'

definition_jnts = ['hair_slot',
                   'definition_jaw03_L',
                   'definition_jaw03_R',
                   'definition_cheek3_L',
                   'definition_cheek3_R',
                   'definition_cheek2_L',
                   'definition_cheek2_R',
                   'definition_jaw03_M',
                   'definition_facial_R_LowerEyeInn',
                   'definition_facial_R_LowerEyeOut',
                   'definition_facial_R_LowerEyeMid',
                   'definition_facial_R_BLidInn',
                   'definition_facial_R_BLidMid',
                   'definition_facial_R_BLidOut',
                   'definition_facial_R_UpperEyeOut',
                   'definition_facial_R_UpperEyeMid',
                   'definition_facial_R_UpperEyeInn',
                   'definition_facial_R_TLidOut',
                   'definition_facial_R_TLidMid',
                   'definition_facial_R_TLidInn',
                   'definition_facial_R_EyeOutCorner',
                   'definition_facial_R_EyeInnCorner',
                   'R_eyeBall_socket',
                   'L_eyeBall_socket',
                   'definition_facial_L_TLidMid',
                   'definition_facial_L_TLidOut',
                   'definition_facial_L_TLidInn',
                   'definition_facial_L_UpperEyeInn',
                   'definition_facial_L_UpperEyeMid',
                   'definition_facial_L_UpperEyeOut',
                   'definition_facial_L_EyeOutCorner',
                   'definition_facial_L_EyeInnCorner',
                   'definition_facial_L_BLidMid',
                   'definition_facial_L_BLidOut',
                   'definition_facial_L_BLidInn',
                   'definition_facial_L_LowerEyeInn',
                   'definition_facial_L_LowerEyeMid',
                   'definition_facial_L_LowerEyeOut',
                   'definition_L_LowLipOut_outer',
                   'definition_R_LowLipInn_mid',
                   'definition_R_LowLipInn_inner',
                   'definition_R_LowLipInn_outer',
                   'definition_R_LowLipMid_mid',
                   'definition_R_LowLipMid_inner',
                   'definition_R_LowLipMid_outer',
                   'definition_R_LowLipOut_mid',
                   'definition_R_LowLipOut_inner',
                   'definition_R_LowLipOut_outer',
                   'definition_R_UpLipOut_mid',
                   'definition_R_UpLipOut_inner',
                   'definition_R_UpLipOut_outer',
                   'definition_R_UpLipInn_mid',
                   'definition_R_UpLipInn_inner',
                   'definition_R_UpLipInn_outer',
                   'definition_R_UpLipMid_mid',
                   'definition_R_UpLipMid_inner',
                   'definition_R_UpLipMid_outer',
                   'definition_C_LowLip_mid',
                   'definition_C_LowLip_inner',
                   'definition_C_LowLip_outer',
                   'definition_C_UpLip_mid',
                   'definition_C_UpLip_inner',
                   'definition_C_UpLip_outer',
                   'definition_L_UpLipOut_mid',
                   'definition_L_UpLipOut_inner',
                   'definition_L_UpLipOut_outer',
                   'definition_L_UpLipMid_mid',
                   'definition_L_UpLipMid_inner',
                   'definition_L_UpLipMid_outer',
                   'definition_L_UpLipInn_mid',
                   'definition_L_UpLipInn_inner',
                   'definition_L_UpLipInn_outer',
                   'definition_L_LowLipInn_mid',
                   'definition_L_LowLipInn_inner',
                   'definition_L_LowLipInn_outer',
                   'definition_L_LowLipMid_mid',
                   'definition_L_LowLipMid_inner',
                   'definition_L_LowLipMid_outer',
                   'definition_L_LowLipOut_mid',
                   'definition_L_LowLipOut_inner',
                   'definition_Mouth_L_Corner',
                   'definition_Mouth_R_Corner',
                   'definition_M_brow',
                   'definition_L_brow_1',
                   'definition_L_brow_2',
                   'definition_L_brow_3',
                   'definition_L_brow_4',
                   'definition_L_brow_5',
                   'definition_R_brow_1',
                   'definition_R_brow_2',
                   'definition_R_brow_3',
                   'definition_R_brow_4',
                   'definition_R_brow_5',
                   'definition_facial_R_OrbitalOut',
                   'definition_facial_R_OrbitalMid',
                   'definition_facial_R_OrbitalInn',
                   'definition_facial_L_OrbitalOut',
                   'definition_facial_L_OrbitalMid',
                   'definition_facial_L_OrbitalInn',
                   'definition_facial_C_NoseBridge',
                   'definition_facial_L_Cheek03',
                   'definition_facial_R_Cheek03',
                   'definition_facial_L_Cheek01',
                   'definition_facial_R_Cheek01',
                   'definition_facial_L_Cheek02',
                   'definition_facial_R_Cheek02',
                   'definition_facial_L_NoseBase',
                   'definition_facial_L_Nostril',
                   'definition_facial_R_Nostril',
                   'definition_facial_R_NoseBase',
                   'definition_facial_C_NoseTip',
                   'definition_facial_C_NoseBase']


def add_item_to_text_scroll(scroll_list=None):
    """
    将所选择的元素添加到列表栏

    :param scroll_list: 列表栏
    :return:
    """
    mesh_list = pm.ls(sl=True)
    objs_in_tsl = pm.textScrollList(scroll_list, q=True, ai=True)
    for mesh in mesh_list:
        if mesh.name() not in objs_in_tsl:
            objs_in_tsl.append(mesh.name())
    pm.textScrollList(scroll_list, e=True, ra=True)
    pm.textScrollList(scroll_list, e=True, a=objs_in_tsl)


def remove_item_to_text_scroll(scroll_list=None):
    """
    将列表中所选择的元素从列表栏中移除

    :param scroll_list: 列表栏
    :return:
    """
    objs_in_tsl = pm.textScrollList(scroll_list, q=True, ai=True)
    selected_item = pm.textScrollList(scroll_list, q=True, si=True)
    for item in selected_item:
        objs_in_tsl.remove(item)
    pm.textScrollList(scroll_list, e=True, ra=True)
    pm.textScrollList(scroll_list, e=True, a=objs_in_tsl)


def get_skin_node(source_mesh):
    skin_cluster_on_source = None

    source_mesh = pm.PyNode(source_mesh)
    input_nodes = pm.listConnections(
        pm.PyNode(source_mesh).getShape(), s=True, t='skinCluster')
    if len(input_nodes) < 1:
        input_nodes = pm.listConnections(
            pm.PyNode(source_mesh).getShape(), s=True, t="objectSet")
        # clean list
        new_list = []
        for node in input_nodes:
            if node not in new_list:
                new_list.append(node)
        input_nodes = new_list

        for inputNode in input_nodes:
            if inputNode.type() == 'objectSet':
                skin_cluster_node = inputNode.listConnections(
                    s=True, t="skinCluster")
                if len(skin_cluster_node) > 0:
                    skin_cluster_on_source = skin_cluster_node
    else:
        skin_cluster_on_source = input_nodes
    return skin_cluster_on_source


class TransferSkinTool(common.Singleton):
    """
    蒙皮传递工具

    """

    def __init__(self):
        super(TransferSkinTool, self).__init__()

        self.list_source_mesh = None
        self.list_target_mesh = None
        self.transfer_dict = None

        self.show_window()

    def show_window(self):
        if pm.window('transferSkinWnd', q=True, ex=True):
            pm.deleteUI('transferSkinWnd')

        pm.window('transferSkinWnd', title="Transfer Skin Tool")
        pm.columnLayout(adj=1)
        pm.separator(height=10, style='in')
        pm.formLayout("meshForms")
        source_mesh_layout = self.source_mesh_layout()
        target_mesh_layout = self.target_mesh_layout()
        transfer_skin_button = self.transfer_skin_layout()
        pm.formLayout("meshForms", edit=True,
                      af=[(source_mesh_layout, 'top', 5),
                          (source_mesh_layout, 'left', 5),
                          (target_mesh_layout, 'top', 5),
                          (target_mesh_layout, 'left', 5),
                          (transfer_skin_button, 'top', 5),
                          (transfer_skin_button, 'left', 5),
                          (transfer_skin_button, 'right', 5),
                          (transfer_skin_button, 'bottom', 5),
                          ],
                      ac=[(target_mesh_layout, 'left', 5, source_mesh_layout),
                          (transfer_skin_button, 'top', 5,
                           source_mesh_layout), ]
                      )
        pm.setParent("..")  # end of formlayout

        pm.showWindow('transferSkinWnd')

    def source_mesh_layout(self):
        layout = pm.columnLayout(adj=1, rs=5)
        label_source_mesh = pm.text("Source mesh:", align="left")
        self.list_source_mesh = pm.textScrollList(
            w=220, ams=True)
        pm.rowColumnLayout(numberOfColumns=2,
                           columnSpacing=[2, 5],
                           columnWidth=[(1, 75), (2, 75)])
        pm.button(label="Add",
                  c=lambda *args: add_item_to_text_scroll(
                      self.list_source_mesh))
        pm.button(label="Remove",
                  c=lambda *args: remove_item_to_text_scroll(
                      self.list_source_mesh))
        pm.setParent("..")
        pm.setParent("..")
        return layout

    def target_mesh_layout(self):
        layout = pm.columnLayout(adj=1, rs=5)
        label_target_mesh = pm.text("Target mesh:", align="left")
        self.list_target_mesh = pm.textScrollList(
            w=220, ams=True,
            sc=(lambda *args: self.action_selected_item()))
        pm.rowColumnLayout(numberOfColumns=2,
                           columnSpacing=[2, 5],
                           columnWidth=[(1, 75), (2, 75)])
        pm.button(label="Add",
                  c=lambda *args: add_item_to_text_scroll(
                      self.list_target_mesh))
        pm.button(label="Remove",
                  c=lambda *args: remove_item_to_text_scroll(
                      self.list_target_mesh))
        pm.setParent("..")
        pm.setParent("..")
        return layout

    def transfer_skin_layout(self):
        layout = pm.columnLayout(adj=1, rs=10)
        button_transfer = pm.button(
            label="Transfer Skin",
            c=(lambda *args: self.execute_transfer_skin()))
        pm.setParent("..")
        return layout

    def transfer_dict_layout(self):
        layout = pm.frameLayout(
            label="Transfer skin data", cll=True, cl=True)
        self.transfer_dict = pm.text(label="None", align="left", ww=True)
        pm.setParent("..")
        return layout

    def action_selected_item(self):
        current_target_item = pm.textScrollList(
            self.list_target_mesh, q=True, si=True)
        pm.select(current_target_item)

    def execute_transfer_skin(self):
        current_source_item = pm.textScrollList(
            self.list_source_mesh, q=True, si=True)
        if len(current_source_item) > 1:
            pm.error(u"请只选择一个元素作为蒙皮的源数据对象，当前选择数为%s" %
                     (len(current_source_item)))
        current_target_item = pm.textScrollList(
            self.list_target_mesh, q=True, si=True)
        source_skin_node = get_skin_node(current_source_item[0])[0]
        source_bind_joints = pm.skinCluster(source_skin_node, q=True, inf=True)
        for target_item in current_target_item:
            target_skin_node = pm.skinCluster(target_item,
                                              source_bind_joints,
                                              tsb=True)
            pm.copySkinWeights(ss=source_skin_node,
                               ds=target_skin_node, nm=True, sa="closestPoint",
                               ia=["oneToOne", "closestJoint", "closestBone"])

        print (u"传递权重已经完成")


def copy_skin():
    source_obj = None
    target_objs = None
    current_selected = pm.ls(sl=True)
    if len(current_selected) < 2:
        pm.error(u"出错了，请至少选择两个geometry对象。"
                 u"首先应该选择的是被拷贝对象，接着是接受权重信息的拷贝对象")
    else:
        source_obj = current_selected[0]
        target_objs = current_selected[1:len(current_selected)]

    source_skin_node = get_skin_node(source_obj)[0]
    source_bind_joints = pm.skinCluster(
        source_skin_node, q=True, inf=True)
    for target_obj in target_objs:
        target_skin_node = pm.skinCluster(
            target_obj, source_bind_joints, tsb=True)
        pm.copySkinWeights(
            ss=source_skin_node, ds=target_skin_node, nm=True,
            sa="closestPoint", ia=["oneToOne", "closestJoint", "closestBone"])

    return


class ImproveFacialSdk(common.Singleton):
    """
    修正面部表情SDK控制的工具
    """

    def __init__(self):
        super(ImproveFacialSdk, self).__init__()

        self.template_path = ""
        self.sdk_dict = None
        self.driver_controllers = None

        self.initialize()
        self.show_window()

    def show_window(self):
        if pm.window("facialSDKManager", ex=True):
            pm.deleteUI("facialSDKManager")
        pm.window(
            "facialSDKManager",
            t=u"Facial SDK 管理 %s" % __version__,
            mb=True,
            cc=lambda *args: self.close_main_window())

        form_layout = pm.formLayout()

        template_path_field = pm.textFieldButtonGrp(
            "improveFacialSdkTemplatePath",
            label=u"模板",
            bl=u"指定文件",
            cw3=[25, 200, 50],
            adj=2,
            text=self.template_path,
            bc=lambda *args: self.load_template_file())

        driver_frame = self.driver_frame()

        driven_frame = self.driven_frame()

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (template_path_field, 'top', 10),
                (template_path_field, 'left', 10),
                (template_path_field, 'right', 10),
                (driver_frame, 'left', 10),
                (driver_frame, 'right', 10),
                (driven_frame, 'left', 10),
                (driven_frame, 'right', 10),
                (driven_frame, 'bottom', 10),
            ],
            attachControl=[
                (driver_frame, 'top', 10, template_path_field),
                # (driver_frame, 'bottom', 10, driven_frame),
                (driven_frame, 'top', 10, driver_frame)
            ])

        pm.showWindow("facialSDKManager")

    def driven_frame(self):
        frame_layout = pm.frameLayout(
            "improveFacialSdkDrivenFrame",
            label="Driven Frame", mh=5, mw=10, cll=False, cl=False)
        pm.scrollLayout("improveFacialSdkDrivenList", cr=True, h=200)
        pm.setParent("..")
        return frame_layout

    def driver_frame(self):
        frame_layout = pm.frameLayout(
            "improveFacialSdkDriverFrame",
            label="Driver Frame", mh=5, mw=10, bgs=True)
        pm.columnLayout(adj=1)

        pm.rowColumnLayout(nc=2)

        # ---------------------
        pm.columnLayout(adj=1, rs=5)
        pm.text(label=u"控制器列表")
        pm.textScrollList(
            "improveFacialSdkDriverControllers",
            w=250,
            a=self.driver_controllers,
            sc=lambda *args: self.selected_list_item(
                widget="improveFacialSdkDriverControllers"))
        pm.popupMenu()
        pm.menuItem(
            label=u"移除选择",
            c=lambda *args: self._remove_selected_item())
        pm.menuItem(
            label=u"移除所有",
            c=lambda *args: self._remove_all_item())
        pm.setParent("..")  # end of columnLayout
        # ------------------------------

        # ------------------------------
        pm.columnLayout(adj=1, rs=5)
        pm.text(label=u"属性列表")
        pm.textScrollList(
            "improveFacialSdkDriverControllerAttrs",
            w=250,
            sc=lambda *args: self.click_attr_item())
        pm.setParent("..")  # end of columnLayout
        # ------------------------------

        pm.setParent("..")  # end of rowColumnLayout

        pm.floatSliderGrp(
            "improveFacialSdkDriverValue",
            enable=False,
            label=u"参数",
            field=True,
            minValue=0,
            maxValue=1.0,
            fieldMinValue=0,
            fieldMaxValue=1.0,
            pre=3,
            adj=3,
            value=0,
            cw3=[25, 60, 100],
        )
        pm.setParent("..")  # end of frameLayout
        pm.setParent("..")  # end of frameLayout

        return frame_layout

    def initialize(self):
        """
        初始化数据

        从MAYA的保存的属性数据里面获取一些值

        :return:
        """
        if pm.optionVar(q='improveFacialSdkTemplatePath'):
            self.template_path = pm.optionVar(
                q='improveFacialSdkTemplatePath')

        self.load_dict_data()

    def close_main_window(self):
        pm.optionVar(sv=('improveFacialSdkTemplatePath', self.template_path))

    def load_template_file(self):
        json_location = pm.fileDialog2(
            dialogStyle=2, fileMode=1, okc=u"选择模板配置文件")
        if json_location:
            pm.textFieldButtonGrp(
                "improveFacialSdkTemplatePath", e=True, text=json_location[0])
            self.template_path = json_location[0]

        self.load_dict_data()

        return

    def load_dict_data(self):
        item_list = []
        if os.path.isfile(self.template_path):
            dict_data = common.read_json(file_path=self.template_path)
            # print dict_data
            self.sdk_dict = dict_data
            self.driver_controllers = dict_data.keys()

    @staticmethod
    def selected_list_item(widget=None):
        selected_item = pm.textScrollList(widget, q=True, si=True)[0]
        print selected_item
        if pm.objExists(selected_item):
            pm.select(selected_item)
            item_attrs = pm.listAttr(selected_item, k=True)
            pm.textScrollList(
                "improveFacialSdkDriverControllerAttrs", e=True, ra=True)
            pm.textScrollList(
                "improveFacialSdkDriverControllerAttrs", e=True, a=item_attrs)
        return

    def click_attr_item(self):
        selected_attr_item = pm.textScrollList(
            "improveFacialSdkDriverControllerAttrs", q=True, si=True)[0]
        selected_ctrl_item = pm.textScrollList(
            "improveFacialSdkDriverControllers", q=True, si=True)[0]
        current_selected_driver = pm.PyNode(
            "%s.%s" % (selected_ctrl_item, selected_attr_item))

        driver_dict = self.sdk_dict[selected_ctrl_item]

        limit_state = None
        limit_value = None
        if selected_attr_item in driver_dict.keys():
            # pm.floatSliderGrp(
            #     "improveFacialSdkDriverValue",
            #     e=True, enable=True)
            if selected_attr_item == "translateX":
                limit_state = pm.transformLimits(
                    selected_ctrl_item, q=True, etx=True)
            elif selected_attr_item == "translateY":
                limit_state = pm.transformLimits(
                    selected_ctrl_item, q=True, ety=True)
                limit_value = pm.transformLimits(
                    selected_ctrl_item, q=True, ty=True)

            elif selected_attr_item == "translateZ":
                limit_state = pm.transformLimits(
                    selected_ctrl_item, q=True, etz=True)
            elif selected_attr_item == "rotateX":
                limit_state = pm.transformLimits(
                    selected_ctrl_item, q=True, erx=True)
            elif selected_attr_item == "rotateY":
                limit_state = pm.transformLimits(
                    selected_ctrl_item, q=True, ery=True)
            elif selected_attr_item == "rotateZ":
                limit_state = pm.transformLimits(
                    selected_ctrl_item, q=True, erz=True)
            else:
                limit_state = [
                    pm.Attribute("%s.%s" % (
                        selected_ctrl_item, selected_attr_item)).getMin(),
                    pm.Attribute("%s.%s" % (
                        selected_ctrl_item, selected_attr_item)).getMax()]

            current_value = pm.Attribute("%s.%s" % (
                selected_ctrl_item, selected_attr_item)).get()

            pm.floatSliderGrp(
                "improveFacialSdkDriverValue", e=True,
                enable=True,
                minValue=limit_value[0],
                maxValue=limit_value[1],
                fieldMinValue=limit_value[0],
                fieldMaxValue=limit_value[1],
                value=current_value,
                cc=lambda *args: self.improve_value(
                    "%s.%s" % (selected_ctrl_item, selected_attr_item)))
            pm.connectControl(
                'improveFacialSdkDriverValue',
                "%s.%s" % (selected_ctrl_item, selected_attr_item))

            print "selected_attr_item : %s" % selected_attr_item
            print "driver_dict : %s" % driver_dict
            if selected_attr_item in driver_dict.keys():
                self.scroll_list_content(
                    dict_data=driver_dict[selected_attr_item])
        else:
            pm.floatSliderGrp(
                "improveFacialSdkDriverValue", e=True, enable=False)
            if pm.columnLayout("improveFacialSdkDrivenListItem", ex=True):
                pm.deleteUI("improveFacialSdkDrivenListItem")
        # print current_selected_driver

    def improve_value(self, attr):
        value = pm.floatSliderGrp(
            "improveFacialSdkDriverValue", q=True, value=True)
        pm.setAttr(attr, value)

    def scroll_list_content(self, dict_data=None):
        if dict_data is None:
            dict_data = {}
        print "dict_data : %s" % dict_data

        if pm.columnLayout("improveFacialSdkDrivenListItem", ex=True):
            pm.deleteUI("improveFacialSdkDrivenListItem")

        pm.columnLayout(
            "improveFacialSdkDrivenListItem",
            adj=1,
            rs=5,
            parent="improveFacialSdkDrivenList")

        for item in dict_data.keys():
            # print type(item)
            pm.frameLayout(label=item, mw=10, mh=5)
            for item_attr in dict_data[item].keys():
                pm.rowColumnLayout(nr=1, co=[2, "left", 50])
                pm.text(label=item_attr, al="left")
                anim_curve = pm.PyNode(dict_data[item][item_attr])
                control_name = "IFSdkDrivenAttr_%s_%s" % (item, item_attr)
                print control_name
                pm.floatFieldGrp(
                    control_name,
                    numberOfFields=anim_curve.numKeys(),
                    pre=3)
                slider_value = []
                for index in range(0, anim_curve.numKeys()):
                    slider_value.append(anim_curve.getValue(index))
                # print slider_value
                slider_value.append(0.0)
                pm.floatFieldGrp(
                    control_name, e=True,
                    value=slider_value,
                    cc=lambda *args: self.improve_sdk_curve(
                        widget=control_name,
                        curve=anim_curve.name()))
                pm.setParent("..")
            pm.setParent("..")

        pm.setParent("..")

    def improve_sdk_curve(self, widget="", curve=""):
        print pm.floatFieldGrp(widget, q=True, value=True)
        print curve

    def _remove_selected_item(self):
        pass

    def _remove_all_item(self):
        pass


def add_grp_to_parent():
    """
    为选择的对象添加一个空组作为它的父节点

    这样做可以让选择的对象的通道栏的数值全部归零。

    :return:
    """
    target_list = pm.ls(sl=True)
    for target_item in target_list:
        grp = pm.createNode("transform",
                            name=("%s_offset" % target_item.name()))
        pm.delete(pm.parentConstraint(target_item, grp, mo=False))
        pm.parent(target_item, grp)
    return


def joint_convert_grp():
    """
    将骨骼转换成空组

    :return:
    """

    target_list = pm.ls(sl=True)
    for target_item in target_list:
        grp = pm.createNode(
            "transform", name=("%s_offset" % target_item.name()))
        pm.delete(pm.parentConstraint(target_item, grp, mo=False))
        target_parent = target_item.getParent()
        pm.parent(grp, target_parent)
        # pm.parent(target_item, grp)
        for item in target_item.getChildren():
            if item.type() in ["transform", "joint"]:
                pm.parent(item, grp)
            if item.type() == "parentConstraint":
                constraint_objs = pm.parentConstraint(
                    item, q=True, targetList=True)
                pm.parentConstraint(constraint_objs, grp, mo=True)
            if item.type() == "scaleConstraint":
                constraint_objs = pm.scaleConstraint(
                    item, q=True, targetList=True)
                pm.scaleConstraint(constraint_objs, grp, mo=True)

        new_name = target_item.name()
        pm.delete(target_item)
        pm.rename(grp, new_name)

    return


def transfer_constraint():
    if len(pm.ls(sl=True)) == 2:
        source_object, target_object = pm.ls(sl=True)
        for item in source_object.getChildren():
            if item.type() == "parentConstraint":
                constraint_objs = pm.parentConstraint(
                    item, q=True, targetList=True)
                pm.parentConstraint(constraint_objs, target_object, mo=True)
                # print item
                # pm.delete(item)
            if item.type() == "scaleConstraint":
                constraint_objs = pm.scaleConstraint(
                    item, q=True, targetList=True)
                pm.scaleConstraint(constraint_objs, target_object, mo=True)
                # print item
                # pm.delete(item)

        # print source_object, target_object


class ExpressionStateSaver(common.Singleton):
    def __init__(self):
        super(ExpressionStateSaver, self).__init__()

        self.version = 0.1

        self.template_path = ""
        self.controller = ""
        self.controller_id_list = []

        # self.output_path = ""
        # self.sdk_dict = None
        # self.driver_controllers = None

        self.initialize()
        self.show_window()

    def initialize(self):
        """
        初始化数据

        从MAYA的保存的属性数据里面获取一些值

        :return:
        """
        if pm.optionVar(q='esswTemplatePath'):
            self.template_path = pm.optionVar(
                q='esswTemplatePath')

        if pm.optionVar(q='esswChannelController'):
            self.controller = pm.optionVar(
                q='esswChannelController')

            if pm.objExists(self.controller):
                self.controller_id_list = pm.listAttr(
                    self.controller, k=True)

    def show_window(self):
        if pm.window("expressionStateSaverWin", ex=True):
            pm.deleteUI("expressionStateSaverWin")
        pm.window(
            "expressionStateSaverWin",
            t=u"表情状态保存 %s" % self.version,
            mb=True,
            cc=lambda *args: self.close_main_window())

        form_layout = pm.formLayout()

        template_path_field = pm.textFieldButtonGrp(
            "esswTemplatePath",
            label=u"模板存放路径",
            bl=u"指定目录",
            cw3=[75, 200, 50],
            adj=2,
            text=self.template_path,
            bc=lambda *args: self._set_output_location())

        channel_controller_field = pm.textFieldButtonGrp(
            "esswChannelController",
            label=u"通道管理对象",
            bl=u"指定对象",
            cw3=[75, 200, 50],
            adj=2,
            text=self.controller,
            bc=lambda *args: self.load_controller())

        driver_frame = self.driver_frame()

        writer = pm.button(label=u"保存数据", c=lambda *args: self.write_json())

        # driven_frame = self.driven_frame()
        #
        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (template_path_field, 'top', 10),
                (template_path_field, 'left', 10),
                (template_path_field, 'right', 10),
                (channel_controller_field, 'left', 10),
                (channel_controller_field, 'right', 10),
                (driver_frame, 'left', 10),
                (driver_frame, 'right', 10),
                (writer, 'left', 10),
                (writer, 'right', 10),
                (writer, 'bottom', 10),
            ],
            attachControl=[
                (channel_controller_field, 'top', 10, template_path_field),
                (driver_frame, 'top', 10, channel_controller_field),
                (driver_frame, 'bottom', 10, writer),
            ])

        pm.showWindow("expressionStateSaverWin")

    def close_main_window(self):
        pm.optionVar(sv=('esswTemplatePath', self.template_path))
        pm.optionVar(sv=('esswChannelController', self.controller))

    def driver_frame(self):
        frame_layout = pm.frameLayout(
            label="Channel Control Frame", mh=5, mw=10, bgs=True)

        pm.rowColumnLayout(nc=2)

        pm.columnLayout(adj=1, rs=5)
        pm.textScrollList(
            "esswChannelAttrList",
            w=250,
            h=350,
            a=self.controller_id_list,
            sc=lambda *args: self.selected_list_item())
        pm.setParent("..")

        pm.columnLayout(adj=1, rs=5)
        pm.textScrollList(
            "esswChannelAttrMap",
            w=250,
            h=350,
            # sc=lambda *args: self.click_attr_item()
        )
        pm.rowColumnLayout()
        pm.button(label=u"添加影响骨骼", c=lambda *args: self.add_joint())
        pm.setParent("..")

        pm.setParent("..")

        pm.setParent("..")  # end of rowColumnLayout

        pm.setParent("..")  # end of frameLayout

        return frame_layout

    def _set_output_location(self):
        output_location = pm.fileDialog2(
            dialogStyle=2, fileMode=3, okc=u"选择文件夹")
        if output_location:
            pm.textFieldButtonGrp(
                'esswTemplatePath', e=True,
                text=output_location[0])
            self.template_path = output_location[0]
        return

    def load_controller(self):
        controller = pm.ls(sl=True)
        if len(controller) > 1 or len(controller) < 1:
            pm.error(u"请选择单个控制器")
        else:
            pm.textFieldButtonGrp(
                "esswChannelController", e=True, text=controller[0])
            self.controller = controller[0]

        attr_list = pm.listAttr(controller[0], k=True)
        pm.textScrollList("esswChannelAttrList", e=True, ra=True)
        pm.textScrollList("esswChannelAttrList", e=True, a=attr_list)

    def selected_list_item(self):
        selected_item = pm.textScrollList(
            "esswChannelAttrList", q=True, si=True)[0]
        print selected_item

        # 让所有通道属性归0，选择的属性数值设置为1
        self.zero_channel(selected_item)

        json_file = "%s/%s.json" % (self.template_path, selected_item)
        # print json_file
        if os.path.exists(json_file):
            self.load_data(file=json_file)
        else:
            pm.textScrollList("esswChannelAttrMap", e=True, ra=True)

        # if pm.objExists(selected_item):
        #     pm.select(selected_item)
        #     item_attrs = pm.listAttr(selected_item, k=True)
        #     pm.textScrollList(
        #         "improveFacialSdkDriverControllerAttrs", e=True, ra=True)
        #     pm.textScrollList(
        #         "improveFacialSdkDriverControllerAttrs", e=True, a=item_attrs)
        # return

    def add_joint(self):
        target_joints = pm.ls(sl=True)
        for target_joint in target_joints:
            if target_joint not in pm.textScrollList(
                    "esswChannelAttrMap", q=True, ai=True):
                pm.textScrollList(
                    "esswChannelAttrMap", e=True, a=target_joints)

    def write_json(self):
        selected_item = pm.textScrollList(
            "esswChannelAttrList", q=True, si=True)[0]
        json_file = "%s/%s.json" % (self.template_path, selected_item)

        output_map = {}
        output_item = pm.textScrollList(
            "esswChannelAttrList", q=True, si=True)[0]

        print output_item

        target_joints = pm.textScrollList(
            "esswChannelAttrMap", q=True, ai=True)

        for target_joint in target_joints:
            str_key = target_joint
            attr_dict = {}
            print str_key

            attr_dict["translate"] = list(pm.PyNode(str_key).translate.get())
            attr_dict["rotate"] = list(pm.PyNode(str_key).rotate.get())
            attr_dict["scale"] = list(pm.PyNode(str_key).scale.get())

            output_map[str_key] = attr_dict

        print output_map

        common.write_json(dict_data=output_map, file_path=json_file)

        print "Done!"

    def load_data(self, file):
        if os.path.isfile(file):
            dict_data = common.read_json(file_path=file)
            joint_list = dict_data.keys()
            pm.textScrollList("esswChannelAttrMap", e=True, ra=True)
            pm.textScrollList("esswChannelAttrMap", e=True, a=joint_list)
            print dict_data

    def zero_channel(self, target_attr):
        # print self.controller
        for item in pm.textScrollList('esswChannelAttrList', q=True, ai=True):
            pm.setAttr("%s.%s" % (self.controller, item), 0)

        pm.setAttr("%s.%s" % (self.controller, target_attr), 1)
        return


class CleanDefinitionAnim(common.Singleton):
    def __init__(self):
        super(CleanDefinitionAnim, self).__init__()

        self.search_field = ""
        self.replace_field = ""
        self.output_files = []
        self.output_path = ""

        self.initialize()
        self.show_window()

    def initialize(self):
        if pm.optionVar(q='cdaOutputPathSetter'):
            self.output_path = pm.optionVar(
                q='cdaOutputPathSetter')

        if pm.optionVar(q='cdaSearchField'):
            self.search_field = pm.optionVar(
                q='cdaSearchField')

        if pm.optionVar(q='cdaReplaceField'):
            self.replace_field = pm.optionVar(
                q='cdaReplaceField')

    def show_window(self):
        if pm.window("cleanDefinitionAnim", ex=True):
            pm.deleteUI("cleanDefinitionAnim")
        pm.window(
            "cleanDefinitionAnim",
            title=u"批量输出工具",
            mb=True,
            cc=lambda *args: self.close_window())

        self.menu_list()

        layout = pm.formLayout(numberOfDivisions=100)
        file_export_list_frame = pm.frameLayout(
            label=u"FBX文件列表：", mw=10, mh=10, bgs=True)

        pm.textScrollList('cdaFileList', ams=True)
        pm.popupMenu()
        pm.menuItem(
            label=u"移除选择",
            c=lambda *args: self._remove_selected_item())
        pm.menuItem(
            label=u"移除所有",
            c=lambda *args: self._remove_all_item())
        pm.setParent("..")

        export_options_frame = pm.frameLayout(
            label=u"输出选项：", mw=10, mh=10, bgs=True)
        pm.textFieldButtonGrp(
            'cdaOutputPathSetter',
            label=u"存放路径",
            bl=u"设置",
            adj=2,
            cw3=[52, 100, 60],
            cat=[(2, "left", 5), (3, "left", 5)],
            text=self.output_path,
            bc=lambda *args: self._set_output_location())
        pm.textFieldGrp(
            "cdaSearchField", label="Search:", cw2=[56, 200],
            text=self.search_field,
            cc=lambda *args: self.save_search_field())
        pm.textFieldGrp(
            "cdaReplaceField", label="Replace:", cw2=[56, 200],
            text=self.replace_field,
            cc=lambda *args: self.save_replace_field())
        pm.radioButtonGrp(
            "cdaWorkOptions",
            label='Mode Options:',
            labelArray3=[u'输出', u'优化', u'清理捏脸骨骼动画'],
            sl=2,
            cw4=[94, 50, 50, 100],
            numberOfRadioButtons=3)

        pm.setParent("..")
        execute_button = pm.button(
            label=u"输出！",
            c=lambda *args: self.start_export_work())
        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (file_export_list_frame, 'top', 10),
                (file_export_list_frame, 'left', 10),
                (file_export_list_frame, 'right', 10),
                (export_options_frame, 'left', 10),
                (export_options_frame, 'right', 10),
                (execute_button, 'left', 10),
                (execute_button, 'right', 10),
                (execute_button, 'bottom', 10)],
            attachControl=[
                # (file_export_list_frame, 'top', 5, project_store_path_frame),
                (file_export_list_frame, 'bottom', 5, export_options_frame),
                (export_options_frame, 'bottom', 5, execute_button)],
            # attachPosition=[(b1, 'right', 5, 75),
            #                                 (column, 'left', 0, 75)],
            #                 attachNone=(b2, 'top'))
        )
        pm.setParent("..")

        pm.showWindow("cleanDefinitionAnim")

    def menu_list(self):
        pm.menu(label=u"文件", tearOff=True)
        pm.menuItem(
            label=u"添加数据文件",
            c=lambda *args: self._append_file())

    def close_window(self):
        # pm.optionVar(sv=('transferAnimToolTemplatePath', self.template_path))
        pm.optionVar(sv=('cdaOutputPathSetter', self.output_path))
        pm.optionVar(sv=('cdaSearchField', self.search_field))
        pm.optionVar(sv=('cdaReplaceField', self.replace_field))

    def _append_file(self):
        multiple_filters = ("FBX Files (*.fbx);;"
                            "Maya Files (*.ma *.mb);;"
                            "Maya ASCII (*.ma);;"
                            "Maya Binary (*.mb);;")
        current_export_list = pm.textScrollList(
            'cdaFileList', q=True, ai=True)
        export_files = pm.fileDialog2(
            fileFilter=multiple_filters,
            dialogStyle=2, fileMode=4, okc=u"添加")
        if export_files:
            for export_file in export_files:
                if export_file not in current_export_list:
                    pm.textScrollList(
                        'cdaFileList', edit=True, append=export_file)

        self.output_files = pm.textScrollList(
            'cdaFileList', q=True, ai=True)
        return

    def _set_output_location(self):
        output_location = pm.fileDialog2(
            dialogStyle=2, fileMode=3, okc=u"选择文件夹")
        if output_location:
            pm.textFieldButtonGrp(
                'cdaOutputPathSetter', e=True,
                text=output_location[0])
            self.output_path = output_location[0]
        return

    def start_export_work(self):
        if len(self.output_files) < 1:
            pm.error(u"数据文件不能为空")

        if self.output_path == '':
            pm.error(u"输出路径不能为空")
        if not os.path.exists(self.output_path):
            pm.error(u"输出路径不存在")

        for export_file in self.output_files:
            # 新建场景，打开指定场景
            cmds.file(new=True, force=True)
            cmds.file(export_file, o=True)
            file_name = cmds.file(
                q=1, sceneName=True, shortName=True).split('.')[0]
            print (file_name + ' already open!')

            # cmds.file(export_file, loadReference="chaCRN",
            #           type="FBX", options="fbx")

            # 将MAYA的时间格式改成ntsc(30帧每秒)
            common.set_time_unit(unit='ntsc')

            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)

            full_path = "%s/%s.fbx" % (self.output_path, file_name)

            # time_range = common.get_anim_range_from_node("chaC:Bip001")
            # print time_range

            # 修改名字
            search_field = pm.textFieldGrp(
                "cdaSearchField", q=True, text=True)
            replace_filed = pm.textFieldGrp(
                "cdaReplaceField", q=True, text=True)

            cmd = '''searchReplaceNames "%s" "%s" "all";''' % (
                search_field, replace_filed)
            mel.eval(cmd)

            if pm.radioButtonGrp("cdaWorkOptions", q=True, sl=True) == 2:
                pm.select("definition_*")
                for item in pm.ls(sl=True, type="joint"):
                    if item.type() == "joint":
                        cmd = ''' cutKey -cl -t ":" -f ":" -at "tx" %s ;''' % item.name()
                        mel.eval(cmd)
                        cmd = ''' cutKey -cl -t ":" -f ":" -at "ty" %s ''' % item.name()
                        mel.eval(cmd)
                        cmd = ''' cutKey -cl -t ":" -f ":" -at "tz" %s ''' % item.name()
                        mel.eval(cmd)
                        cmd = ''' cutKey -cl -t ":" -f ":" -at "rx" %s ''' % item.name()
                        mel.eval(cmd)
                        cmd = ''' cutKey -cl -t ":" -f ":" -at "ry" %s ''' % item.name()
                        mel.eval(cmd)
                        cmd = ''' cutKey -cl -t ":" -f ":" -at "rz" %s ''' % item.name()
                        mel.eval(cmd)
                for item in pm.ls(type="joint"):
                    if item.type() == "joint":
                        cmd = ''' cutKey -cl -t ":" -f ":" -at "sx" %s ''' % item.name()
                        mel.eval(cmd)
                        cmd = ''' cutKey -cl -t ":" -f ":" -at "sy" %s ''' % item.name()
                        mel.eval(cmd)
                        cmd = ''' cutKey -cl -t ":" -f ":" -at "sz" %s ''' % item.name()
                        mel.eval(cmd)

                cmd = '''file -force -options "fbx" -type "FBX export" -pr -ea "%s";''' % full_path
                # cmds.file(full_path,
                #           force=True,
                #           # option="fbx",
                #           type="FBX export",
                #           pr=True,
                #           ea=True)
                mel.eval(cmd)
            if pm.radioButtonGrp('cdaWorkOptions', q=True, sl=True) == 3:
                pm.select("definition_*")
                definition_jnts = []
                for item in pm.ls(sl=True, type="joint"):
                    print pm.PyNode(item).type()
            if pm.radioButtonGrp("cdaWorkOptions", q=True, sl=True) == 1:
                namespace_list = pm.namespaceInfo(an=True, lon=True)
                namespace_list.remove(":UI")
                namespace_list.remove(":shared")

                for namespace in namespace_list:
                    pm.select("%s:character_root" * namespace,
                              "%s:final_model_grp" % namespace)
                    cmd = '''file -force -options "fbx" -type "FBX export" -pr -es "%s";''' % full_path
                    mel.eval(cmd)

            print (u"%s 工作全部完成" % export_file)

    def save_search_field(self):
        self.search_field = pm.textFieldGrp(
            'cdaSearchField', q=True, text=True)
        print self.search_field

    def save_replace_field(self):
        self.replace_field = pm.textFieldGrp(
            'cdaReplaceField', q=True, text=True)
        print self.replace_field

    def _remove_selected_item(self):
        selected_item = pm.textScrollList(
            'cdaFileList', q=True, si=True)
        for item in selected_item:
            pm.textScrollList('cdaFileList', e=True, ri=item)

    def _remove_all_item(self):
        pm.textScrollList('cdaFileList', e=True, ra=True)


class BatchExportModel(common.Singleton):
    def __init__(self):
        super(BatchExportModel, self).__init__()

        self.output_path = None
        self.skin_grp = None

        self.initialize()
        self.show_window()

    def initialize(self):
        if pm.optionVar(q='bemOutputPathSetter'):
            self.output_path = pm.optionVar(
                q='bemOutputPathSetter')

        if pm.optionVar(q='bemSkinGrpField'):
            self.skin_grp = pm.optionVar(
                q='bemSkinGrpField')

    def show_window(self):
        if pm.window("batchExportModel", ex=True):
            pm.deleteUI("batchExportModel")
        pm.window(
            "batchExportModel",
            title=u"批量输出工具",
            mb=True,
            cc=lambda *args: self.close_window())

        # self.menu_list()

        layout = pm.formLayout(numberOfDivisions=100)

        file_export_list_frame = pm.frameLayout(
            label=u"输出对象列表：", mw=10, mh=10, bgs=True)
        pm.textFieldButtonGrp(
            "bemSkinGrpField",
            label=u"骨骼组",
            bl=u"指定",
            cw3=[35, 200, 100],
            adj=2,
            text=self.skin_grp,
            cc=lambda *args: self.set_skin_field(),
            bc=lambda *args: self.set_skin_field())
        pm.textScrollList('bemExportObjectList', ams=True)
        pm.popupMenu()
        pm.menuItem(
            label=u"移除选择",
            c=lambda *args: self._remove_selected_item())
        pm.menuItem(
            label=u"移除所有",
            c=lambda *args: self._remove_all_item())
        pm.button(label=u"添加输出骨骼", c=lambda *args: self.add_export_model())
        pm.setParent("..")

        export_options_frame = pm.frameLayout(
            label=u"输出选项：", mw=10, mh=10, bgs=True)
        pm.textFieldButtonGrp(
            'bemOutputPathSetter',
            label=u"存放路径",
            bl=u"设置",
            adj=2,
            cw3=[52, 100, 60],
            cat=[(2, "left", 5), (3, "left", 5)],
            text=self.output_path,
            bc=lambda *args: self._set_output_location())

        pm.setParent("..")
        execute_button = pm.button(
            label=u"输出！",
            c=lambda *args: self.start_export_work())
        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (file_export_list_frame, 'top', 10),
                (file_export_list_frame, 'left', 10),
                (file_export_list_frame, 'right', 10),
                (export_options_frame, 'left', 10),
                (export_options_frame, 'right', 10),
                (execute_button, 'left', 10),
                (execute_button, 'right', 10),
                (execute_button, 'bottom', 10)],
            attachControl=[
                # (file_export_list_frame, 'top', 5, project_store_path_frame),
                (file_export_list_frame, 'bottom', 5, export_options_frame),
                (export_options_frame, 'bottom', 5, execute_button)],
            # attachPosition=[(b1, 'right', 5, 75),
            #                                 (column, 'left', 0, 75)],
            #                 attachNone=(b2, 'top'))
        )
        pm.setParent("..")

        pm.showWindow("batchExportModel")

    def close_window(self):
        pm.optionVar(sv=('bemOutputPathSetter', self.output_path))
        pm.optionVar(sv=('bemSkinGrpField', self.skin_grp))

    def start_export_work(self):

        export_objects = pm.textScrollList(
            "bemExportObjectList", q=True, ai=True)

        for export_object in export_objects:
            if self.output_path == '':
                pm.error(u"输出路径不能为空")
            if not os.path.exists(self.output_path):
                pm.error(u"输出路径不存在")

            full_path = "%s/%s.fbx" % (self.output_path, export_object)

            if pm.objExists(self.skin_grp):
                pm.select(self.skin_grp, export_object)
                cmd = (
                    '''file -force -options "fbx" 
                            -type "FBX export" -pr -es "%s";'''
                    % full_path)
                mel.eval(cmd)

            print (u"%s 工作全部完成" % export_object)

    def _set_output_location(self):
        output_location = pm.fileDialog2(
            dialogStyle=2, fileMode=3, okc=u"选择文件夹")
        if output_location:
            pm.textFieldButtonGrp(
                'bemOutputPathSetter', e=True,
                text=output_location[0])
            self.output_path = output_location[0]
        return

    def set_skin_field(self):
        self.skin_grp = pm.ls(sl=True)[0]
        pm.textFieldButtonGrp("bemSkinGrpField", e=True, text=self.skin_grp)
        return

    def add_export_model(self):
        current_export_list = pm.textScrollList(
            "bemExportObjectList", q=True, ai=True)

        for item in pm.ls(sl=True):
            if item not in current_export_list:
                pm.textScrollList("bemExportObjectList", e=True, a=item)

        return

    def _remove_selected_item(self):
        selected_item = pm.textScrollList(
            'bemExportObjectList', q=True, si=True)
        for item in selected_item:
            pm.textScrollList('bemExportObjectList', e=True, ri=item)
        # self.output_files = pm.textScrollList(
        #     'bemExportObjectList', q=True, ai=True)

    def _remove_all_item(self):
        pm.textScrollList('bemExportObjectList', e=True, ra=True)
        # self.output_files = pm.textScrollList(
        #     'export_list_input', q=True, ai=True)


class mirror_channel(common.Singleton):
    def __init__(self):
        super(mirror_channel, self).__init__()

        self.initialize()
        self.show_window()

    def initialize(self):
        pass

    def show_window(self):
        if pm.window("mirrorChannelTool", ex=True):
            pm.deleteUI("mirrorChannelTool")
        pm.window(
            "mirrorChannelTool",
            title=u"镜像通道工具",
            mb=True,
            cc=lambda *args: self.close_window())

        layout = pm.formLayout(numberOfDivisions=100)

        translate_attrs = pm.checkBoxGrp(
            numberOfCheckBoxes=3,
            label='Translate:',
            cw4=[70, 50, 50, 50],
            cat=[1, "right", 10],
            labelArray3=['X', 'Y', 'Z'])

        rotate_attrs = pm.checkBoxGrp(
            numberOfCheckBoxes=3,
            label='Rotate:',
            cw4=[70, 50, 50, 50],
            cat=[1, "right", 10],
            labelArray3=['X', 'Y', 'Z'])

        scale_attrs = pm.checkBoxGrp(
            numberOfCheckBoxes=3,
            label='Scale:',
            cw4=[70, 50, 50, 50],
            cat=[1, "right", 10],
            labelArray3=['X', 'Y', 'Z'])

        execute_btn = pm.button(
            label=u"镜像", c=lambda *args: self.mirror_channel_value())

        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (translate_attrs, 'top', 10),
                (translate_attrs, 'left', 20),
                (translate_attrs, 'right', 20),
                (rotate_attrs, 'left', 20),
                (rotate_attrs, 'right', 20),
                (scale_attrs, 'left', 20),
                (scale_attrs, 'right', 20),
                (execute_btn, 'left', 10),
                (execute_btn, 'right', 10),
                (execute_btn, 'bottom', 10),
            ],
            attachControl=[
                (rotate_attrs, 'top', 10, translate_attrs),
                (scale_attrs, 'top', 10, rotate_attrs),
            ],
            # attachPosition=[(b1, 'right', 5, 75),
            #                                 (column, 'left', 0, 75)],
            #                 attachNone=(b2, 'top'))
        )

        pm.showWindow("mirrorChannelTool")

    def close_window(self):
        pass

    def mirror_channel_value(self):
        current_selects = pm.ls(sl=True)
        if len(current_selects) > 1:
            source = current_selects[0]
            current_selects.pop(0)
            target_list = current_selects
            channel_attrs = pm.listAttr(source, k=True)
            for channel_attr in channel_attrs:
                source_value = pm.PyNode(source).attr(channel_attr).get()
                for target in target_list:
                    # if channel_attr == "rotateX":
                    #     pm.PyNode(target).attr(channel_attr).set(source_value*-1)
                    # if channel_attr == "rotateY":
                    #     pm.PyNode(target).attr(channel_attr).set(source_value*1)
                    # if channel_attr == "rotateZ":
                    #     pm.PyNode(target).attr(channel_attr).set(source_value*1)
                    if channel_attr == "translateX":
                        pm.PyNode(target).attr(
                            channel_attr).set(source_value * -1)
                    if channel_attr == "translateY":
                        pm.PyNode(target).attr(
                            channel_attr).set(source_value * 1)
                    if channel_attr == "translateZ":
                        pm.PyNode(target).attr(
                            channel_attr).set(source_value * 1)
