# coding: utf-8

from imp import reload
from animation import common
from core import utils

from pymel import core as pm

reload(common)
reload(utils)

class Creator:
    def __init__(self):
        self.module_name = "Nose_01"
        
        self.proxy_bridge = ""
        self.proxy_master = ""
        self.proxy_tip = ""
        self.proxy_left = ""
        self.proxy_right = ""
        self.proxy_up = ""


    def update_init(self):
        self.proxy_bridge = pm.textFieldButtonGrp("xdBridgeProxyField", q=True, text=True)
        self.proxy_master = pm.textFieldButtonGrp("xdMasterProxyField", q=True, text=True)
        self.proxy_tip = pm.textFieldButtonGrp("xdTipProxyField", q=True, text=True)
        self.proxy_left = pm.textFieldButtonGrp("xdLeftProxyField", q=True, text=True)
        self.proxy_right = pm.textFieldButtonGrp("xdRightProxyField", q=True, text=True)
        self.proxy_up = pm.textFieldButtonGrp("xdUpProxyField", q=True, text=True)
        return

    def proxy(self):
        if not pm.objExists("Proxy_Grp"):
            pm.createNode("transform", name="Proxy_Grp")

        if pm.objExists("Proxy_Nose_Grp"):
            pm.error(u"场景中已经存在代理对象")

        pm.createNode("transform", name="Proxy_Nose_Grp", p="Proxy_Grp")

        for item in ["Bridge", "Master", "MD", "LF", "RT", "Up"]:
            pm.parent(
                pm.spaceLocator(name="proxyNose{}Loc".format(item)), 
                "Proxy_Nose_Grp")

        pm.PyNode("proxyNoseBridgeLoc").translateY.set(3)
        pm.PyNode("proxyNoseBridgeLoc").rotateX.set(-15)

        pm.parent("proxyNoseMasterLoc", "proxyNoseBridgeLoc")
        pm.PyNode("proxyNoseMasterLoc").translateY.set(-2.5)
        pm.PyNode("proxyNoseMasterLoc").rotateX.set(15)

        pm.parent("proxyNoseMDLoc", "proxyNoseLFLoc", "proxyNoseRTLoc", "proxyNoseMasterLoc")
        pm.PyNode("proxyNoseMDLoc").translateY.set(-0.5)
        pm.PyNode("proxyNoseMDLoc").translateZ.set(3)
        pm.PyNode("proxyNoseLFLoc").translate.set([1.5, -0.5, 1.5])
        pm.PyNode("proxyNoseRTLoc").translate.set([-1.5, -0.5, 1.5])

        pm.PyNode("proxyNoseUpLoc").translateY.set(4)

        return True

    def build_module(self):
        ctrl_list = self.local_rig_out_grp()
        # todo 右边鼻翼控制器scaleX应该为-1，而不是scaleZ的值为-1
        self.make_ctrl_work(ctrl_list)

    def local_rig_out_grp(self):
        self.update_init()

        mid_prefix = "MD_{}".format(self.module_name)
        lf_prefix = "LF_{}".format(self.module_name)
        rt_prefix = "RT_{}".format(self.module_name)

        ctrl_list = []

        deformer_grp = "{}_Deformer_Grp".format(mid_prefix)
        if not pm.objExists(deformer_grp):
            pm.createNode("transform", name=deformer_grp, p="Deformer_Grp")

        control_grp = "{}_Grp".format(mid_prefix)
        if not pm.objExists(control_grp):
            pm.createNode("transform", name=control_grp, p="Head_02_Grp")

        local_rig_out_grp = "{}_LocalRig_Out_Grp".format(mid_prefix)
        if not pm.objExists(local_rig_out_grp):
            pm.createNode("transform", name=local_rig_out_grp, p="{}_Deformer_Grp".format(mid_prefix))

        bridge_jnt_grp = utils.jnt_or_control_grp(
            name="{}_Bridge_Ctrl_Jnt".format(mid_prefix), parent_node=local_rig_out_grp)
        pm.delete(pm.parentConstraint(self.proxy_bridge, bridge_jnt_grp, mo=False))
        bridge_ctrl_grp = utils.jnt_or_control_grp(
            name="{}_Bridge_Ctrl".format(mid_prefix), object_type="plane", parent_node=control_grp)
        pm.delete(pm.parentConstraint(self.proxy_bridge, bridge_ctrl_grp, mo=False))
        ctrl_list.append("{}_Bridge_Ctrl".format(mid_prefix))

        master_jnt_grp = utils.yellow_component(
            name="{}_Master_Ctrl_Jnt".format(mid_prefix),
            shape_type="joint",
            parent_node="{}_Bridge_Ctrl_Jnt".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_master, master_jnt_grp, mo=False))
        master_ctrl_grp = utils.yellow_component(
            name="{}_Master_Ctrl".format(mid_prefix),
            shape_type="sphere",
            parent_node="{}_Bridge_Ctrl".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_master, master_ctrl_grp, mo=False))
        ctrl_list.append("{}_Master_Ctrl".format(mid_prefix))

        tip_jnt_grp = utils.jnt_or_control_grp(
            name="{}_Ctrl_Jnt".format(mid_prefix),
            object_type='joint',
            parent_node="{}_Master_Ctrl_Jnt".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_tip, tip_jnt_grp, mo=False))
        tip_ctrl_grp = utils.jnt_or_control_grp(
            name="{}_Ctrl".format(mid_prefix),
            object_type='plane',
            parent_node="{}_Master_Ctrl".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_tip, tip_ctrl_grp, mo=False))
        ctrl_list.append("{}_Ctrl".format(mid_prefix))

        left_jnt_grp = utils.yellow_component(
            name="{}_Ctrl_Jnt".format(lf_prefix),
            shape_type="joint",
            parent_node="{}_Master_Ctrl_Jnt".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_left, left_jnt_grp, mo=False))
        left_ctrl_grp = utils.yellow_component(
            name="{}_Ctrl".format(lf_prefix),
            shape_type="sphere",
            parent_node="{}_Master_Ctrl".format(mid_prefix))
        pm.delete(pm.parentConstraint(self.proxy_left, left_ctrl_grp, mo=False))
        ctrl_list.append("{}_Ctrl".format(lf_prefix))

        right_jnt_grp = utils.yellow_component(
            name="{}_Ctrl_Jnt".format(rt_prefix), shape_type="joint",
            parent_node="{}_Master_Ctrl_Jnt".format(mid_prefix))
        pm.PyNode(right_jnt_grp).scaleZ.set(-1)
        pm.delete(pm.parentConstraint(self.proxy_right, right_jnt_grp, mo=False))

        right_ctrl_grp = utils.yellow_component(
            name="{}_Ctrl".format(rt_prefix),
            shape_type="sphere",
            parent_node="{}_Master_Ctrl".format(mid_prefix))
        pm.PyNode(right_ctrl_grp).scaleX.set(-1)
        pm.delete(pm.parentConstraint(self.proxy_right, right_ctrl_grp, mo=False))

        ctrl_list.append("{}_Ctrl".format(rt_prefix))

        up_jnt_grp = utils.jnt_or_control_grp(
            name="{}_Up_Ctrl_Jnt".format(mid_prefix),
            object_type="joint",
            parent_node=local_rig_out_grp)
        pm.delete(pm.parentConstraint(self.proxy_up, up_jnt_grp, mo=False))
        up_ctrl_grp = utils.jnt_or_control_grp(
            name="{}_Up_Ctrl".format(mid_prefix),
            object_type="plane",
            parent_node="Head_02_Grp")
        pm.delete(pm.parentConstraint(self.proxy_up, up_ctrl_grp, mo=False))
        ctrl_list.append("{}_Up_Ctrl".format(mid_prefix))

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

    def create_layout(self, parent):
        with parent:
            with pm.frameLayout(p=parent, lv=False, mh=10, mw=10) as frame:
                with pm.frameLayout(label=u"Proxy", mh=10, mw=10, bgs=True):
                    pm.button(label=u"Build Proxy",
                              c=lambda *args: self.creator.proxy())

                    with pm.frameLayout(label=u"component detail", cl=False, cll=True, mh=10, mw=10):
                        pm.textFieldButtonGrp(
                            "xdBridgeProxyField",
                            label=u"Nose bridge",
                            adj=2,
                            bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdBridgeProxyField"))
                        pm.textFieldButtonGrp(
                            "xdMasterProxyField",
                            label=u"Nose master",
                            adj=2,
                            bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdMasterProxyField"))
                        pm.textFieldButtonGrp(
                            "xdTipProxyField",
                            label=u"Nose tip",
                            adj=2,
                            bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdTipProxyField"))
                        pm.textFieldButtonGrp(
                            "xdLeftProxyField",
                            label=u"Nose left",
                            adj=2,
                            bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdLeftProxyField"))
                        pm.textFieldButtonGrp(
                            "xdRightProxyField",
                            label=u"Nose right",
                            adj=2,
                            bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdRightProxyField"))
                        pm.textFieldButtonGrp(
                            "xdUpProxyField",
                            label=u"Nose up",
                            adj=2,
                            bl="Get object",
                            bc=lambda *args: utils.get_object_in_field("xdUpProxyField"))

                pm.button(label=u"Build Module", c=lambda *args: self.creator.build_module())

        return frame
