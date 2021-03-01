# coding: utf-8

from imp import reload
from re import S

from pymel.core.general import parent
from animation import common
from core import utils

from pymel import core as pm

reload(common)
reload(utils)

nose_config = {
    "proxyNoseBridgeLoc": {
        "translateY": 3.0,
        "rotateX": -15.0
    },
    "proxyNoseMasterLoc": {
        "translateY": -2.50,
        "rotateX": 15.0
    },
}


class Creator:
    def __init__(self):
        self.module_name = "Nose_01"

        self.proxy_bridge = ""
        self.proxy_master = ""
        self.proxy_tip = ""
        self.proxy_left = ""
        self.proxy_right = ""
        self.proxy_up = ""

        self.deformer_grp = ""
        self.control_grp = ""
        self.local_rig_out_grp = ""

    def proxy(self):
        if not pm.objExists("Proxy_Grp"):
            pm.createNode("transform", name="Proxy_Grp")

        if pm.objExists("Proxy_Nose_Grp"):
            pm.error(u"场景中已经存在代理对象")

        pm.createNode("transform", name="Proxy_Nose_Grp", p="Proxy_Grp")

        for item in ["Bridge", "Master", "Tip", "LF", "RT", "Up"]:
            pm.parent(pm.spaceLocator(name="proxyNose{}Loc".format(item)), "Proxy_Nose_Grp")

        pm.PyNode("proxyNoseBridgeLoc").translateY.set(3)
        pm.PyNode("proxyNoseBridgeLoc").rotateX.set(-15)

        pm.parent("proxyNoseMasterLoc", "proxyNoseBridgeLoc")
        pm.PyNode("proxyNoseMasterLoc").translateY.set(-2.5)
        pm.PyNode("proxyNoseMasterLoc").rotateX.set(15)

        pm.parent("proxyNoseTipLoc", "proxyNoseLFLoc", "proxyNoseRTLoc", "proxyNoseMasterLoc")
        pm.PyNode("proxyNoseTipLoc").translateY.set(-0.5)
        pm.PyNode("proxyNoseTipLoc").translateZ.set(3)

        pm.PyNode("proxyNoseLFLoc").translate.set([1.5, -0.5, 1.5])
        pm.PyNode("proxyNoseRTLoc").translate.set([-1.5, -0.5, 1.5])

        pm.PyNode("proxyNoseUpLoc").translateY.set(4)

        return True

    def build_module(self):
        self.init_structure()

        for item in ["bridge", "master", "tip", "left", "right", "up"]:
            print(self.__dict__["proxy_{}".format(item)])

        ctrl_list = self.create_local_rig()

        self.make_ctrl_work(ctrl_list)

        print(u"------------ {}模块创建完毕 ------------".format(self.module_name))
        return

    def init_structure(self):
        if not pm.objExists("MD_Nose_01_Deformer_Grp"):
            self.deformer_grp = pm.createNode("transform", name="MD_Nose_01_Deformer_Grp", p="Deformer_Grp")

        if not pm.objExists("MD_Nose_01_Grp"):
            self.control_grp = pm.createNode("transform", name="MD_Nose_01_Grp", p="Head_02_Grp")

        if not pm.objExists("MD_Nose_01_LocalRig_Out_Grp"):
            self.local_rig_out_grp = pm.createNode("transform", name="MD_Nose_01_LocalRig_Out_Grp", p=self.deformer_grp)

    def create_local_ctrl(self, name="item", jnt_parent="jnt_parent", ctrl_parent="ctrl_parent"):
        jnt = "MD_Nose_01_{}_Ctrl_Jnt".format(name)
        ctrl = "MD_Nose_01_{}_Ctrl".format(name)
        proxy = self.__dict__["proxy_{}".format(name)]

        jnt_grp = utils.jnt_or_control_grp(name=jnt, parent_node=jnt_parent)
        pm.delete(pm.parentConstraint(proxy, jnt_grp, mo=False))
        ctrl_grp = utils.jnt_or_control_grp(name=ctrl, object_type="plane", parent_node=ctrl_parent)
        pm.delete(pm.parentConstraint(proxy, ctrl_grp, mo=False))

        return ctrl

    def create_local_rig(self):

        ctrl_list = []

        # for item in ["Bridge", "Master", "Tip", "LF", "RT", "Up"]:
        #     jnt_name = "MD_Nose_01_{}_Ctrl_Jnt".format(item)
        #     ctrl_name = "MD_Nose_01_{}_Ctrl".format(item)
            
        #     if item == "Bridge":
        #         parent_node = self.local_rig_out_grp
        #     elif item == "Master":
        #         parent_node = "MD_Nose_01_Bridge_Ctrl_Jnt"
                
        #     jnt_grp = utils.jnt_or_control_grp(name=jnt_name, parent_node=parent_node)
        #     pm.delete(pm.parentConstraint(self.proxy_bridge, jnt_grp, mo=False))
            
        #     ctrl_grp = utils.jnt_or_control_grp(name=ctrl_name, object_type="plane", parent_node=self.control_grp)
        #     pm.delete(pm.parentConstraint(self.proxy_bridge, ctrl_grp, mo=False))
            
        #     ctrl_list.append(ctrl_name)

        # bridge_ctrl = self.create_local_ctrl("Bridge", jnt_parent=self.local_rig_out_grp, ctrl_parent=self.control_grp)
        # ctrl_list.append(bridge_ctrl)
        bridge_jnt_grp = utils.jnt_or_control_grp(name="MD_Nose_01_Bridge_Ctrl_Jnt", parent_node=self.control_grp)
        pm.delete(pm.parentConstraint(self.proxy_bridge, bridge_jnt_grp, mo=False))
        bridge_ctrl_grp = utils.jnt_or_control_grp(
            name="MD_Nose_01_Bridge_Ctrl", object_type="plane", parent_node=self.control_grp)
        pm.delete(pm.parentConstraint(self.proxy_bridge, bridge_ctrl_grp, mo=False))
        ctrl_list.append("MD_Nose_01_Bridge_Ctrl")

        master_jnt = "MD_Nose_01_Master_Ctrl_Jnt"
        master_jnt_grp = utils.yellow_component(
            name=master_jnt, shape_type="joint", parent_node="MD_Nose_01_Bridge_Ctrl_Jnt")
        pm.delete(pm.parentConstraint(self.proxy_master, master_jnt_grp, mo=False))
        master_ctrl = "MD_Nose_01_Master_Ctrl"
        master_ctrl_grp = utils.yellow_component(
            name=master_ctrl, shape_type="sphere", parent_node="MD_Nose_01_Bridge_Ctrl")
        pm.delete(pm.parentConstraint(self.proxy_master, master_ctrl_grp, mo=False))
        ctrl_list.append("MD_Nose_01_Master_Ctrl")

        tip_jnt_grp = utils.jnt_or_control_grp(
            name="MD_Nose_01_Ctrl_Jnt", object_type='joint', parent_node="MD_Nose_01_Master_Ctrl_Jnt")
        pm.delete(pm.parentConstraint(self.proxy_tip, tip_jnt_grp, mo=False))
        tip_ctrl_grp = utils.jnt_or_control_grp(
            name="MD_Nose_01_Ctrl", object_type='plane', parent_node="MD_Nose_01_Master_Ctrl")
        pm.delete(pm.parentConstraint(self.proxy_tip, tip_ctrl_grp, mo=False))
        # tip_ctrl = self.create_local_ctrl("Tip", jnt_parent=master_jnt, ctrl_parent=master_ctrl)
        # ctrl_list.append(tip_ctrl)

        left_jnt_grp = utils.yellow_component(
            name="LF_Nose_01_Ctrl_Jnt", shape_type="joint", parent_node="MD_Nose_01_Master_Ctrl_Jnt")
        pm.delete(pm.parentConstraint(self.proxy_left, left_jnt_grp, mo=False))
        left_ctrl_grp = utils.yellow_component(
            name="LF_Nose_01_Ctrl", shape_type="sphere", parent_node="MD_Nose_01_Master_Ctrl")
        pm.delete(pm.parentConstraint(self.proxy_left, left_ctrl_grp, mo=False))
        ctrl_list.append("LF_Nose_01_Ctrl")

        right_jnt_grp = utils.yellow_component(
            name="RT_Nose_01_Ctrl_Jnt", shape_type="joint", parent_node="MD_Nose_01_Master_Ctrl_Jnt")
        pm.PyNode(right_jnt_grp).scaleZ.set(-1)
        pm.delete(pm.parentConstraint(self.proxy_right, right_jnt_grp, mo=False))
        right_ctrl_grp = utils.yellow_component(
            name="RT_Nose_01_Ctrl", shape_type="sphere", parent_node="MD_Nose_01_Master_Ctrl")
        pm.PyNode(right_ctrl_grp).scaleX.set(-1)
        pm.delete(pm.parentConstraint(self.proxy_right, right_ctrl_grp, mo=False))
        ctrl_list.append("RT_Nose_01_Ctrl")

        up_jnt_grp = utils.jnt_or_control_grp(
            name="MD_Nose_01_Up_Ctrl_Jnt", object_type="joint", parent_node=self.local_rig_out_grp)
        pm.delete(pm.parentConstraint(self.proxy_up, up_jnt_grp, mo=False))
        up_ctrl_grp = utils.jnt_or_control_grp(
            name="MD_Nose_01_Up_Ctrl", object_type="plane", parent_node="Head_02_Grp")
        pm.delete(pm.parentConstraint(self.proxy_up, up_ctrl_grp, mo=False))
        ctrl_list.append("MD_Nose_01_Up_Ctrl")

        return ctrl_list



    def make_ctrl_work(self, ctrl_list):
        for ctrl in ctrl_list:
            jnt = "{}_Jnt".format(ctrl)
            pm.PyNode(ctrl).translate.connect(pm.PyNode(jnt).translate)
            pm.PyNode(ctrl).getParent().translate.connect(pm.PyNode(jnt).getParent().translate)
            pm.PyNode(ctrl).rotate.connect(pm.PyNode(jnt).rotate)
            pm.PyNode(ctrl).getParent().rotate.connect(pm.PyNode(jnt).getParent().rotate)
            pm.PyNode(ctrl).scale.connect(pm.PyNode(jnt).scale)
        # todo 鼻子的微表情


EDITOR_VERSION = 1.10


class Editor(common.Singleton):
    name = "xdNoseCreatorEditor"

    def __init__(self):
        super(Editor, self).__init__()

        self.creator = Creator()

        self.create_window()

    def create_window(self):
        if pm.window(self.name, ex=True):
            pm.deleteUI(self.name)

        with pm.window(self.name, title=u"Nose Creator Version {}".format(EDITOR_VERSION)):
            with pm.columnLayout(adj=1) as layout:
                self.create_layout(parent=layout)

        pm.showWindow(self.name)

        # 初始化数据
        self.init_data()

    def create_layout(self, parent):
        with parent:
            with pm.frameLayout(p=parent, lv=False, mh=10, mw=10) as frame:
                with pm.frameLayout(label=u"Proxy", mh=10, mw=10, bgs=True):
                    pm.button(label=u"Build Proxy", c=lambda *args: self.creator.proxy())

                    with pm.frameLayout(label=u"component detail", cl=False, cll=True, mh=10, mw=10):
                        pm.textFieldButtonGrp(
                            "xdBridgeProxyField", label=u"Nose bridge", adj=2, bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdBridgeProxyField"))
                        pm.textFieldButtonGrp(
                            "xdMasterProxyField", label=u"Nose master", adj=2, bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdMasterProxyField"))
                        pm.textFieldButtonGrp(
                            "xdTipProxyField", label=u"Nose tip", adj=2, bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdTipProxyField"))
                        pm.textFieldButtonGrp(
                            "xdLFProxyField", label=u"Nose left", adj=2, bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdLFProxyField"))
                        pm.textFieldButtonGrp(
                            "xdRTProxyField", label=u"Nose right", adj=2, bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdRTProxyField"))
                        pm.textFieldButtonGrp(
                            "xdUpProxyField", label=u"Nose up", adj=2, bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdUpProxyField"))

                pm.button(label=u"Build Module", c=lambda *args: self.build())

        return frame

    def init_data(self):
        for item in ["Bridge", "Master", "Tip", "LF", "RT", "Up"]:
            if pm.objExists("proxyNose{}Loc".format(item)):
                # print("proxyNose{}Loc".format(item))
                pm.textFieldButtonGrp("xd{}ProxyField".format(item), e=True, text="proxyNose{}Loc".format(item))

    def build(self):
        u"""创建nose模块

        :return None
        """
        # 初始化数据
        self.creator.proxy_bridge = pm.textFieldButtonGrp("xdBridgeProxyField", q=True, text=True)
        self.creator.proxy_master = pm.textFieldButtonGrp("xdMasterProxyField", q=True, text=True)
        self.creator.proxy_tip = pm.textFieldButtonGrp("xdTipProxyField", q=True, text=True)
        self.creator.proxy_left = pm.textFieldButtonGrp("xdLFProxyField", q=True, text=True)
        self.creator.proxy_right = pm.textFieldButtonGrp("xdRTProxyField", q=True, text=True)
        self.creator.proxy_up = pm.textFieldButtonGrp("xdUpProxyField", q=True, text=True)

        # 开始创建模块
        self.creator.build_module()

        return
