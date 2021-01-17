# coding: utf-8

from pymel import core as pm
from rig.core.utils import jnt_or_control_grp


class NeckEarCreator:
    def __init__(self):
        self.module_name = "Neck_01"

    def proxy(self):
        if not pm.objExists("Proxy_Grp"):
            pm.createNode("transform", name="Proxy_Grp")

        if pm.objExists("Proxy_neck_head_Grp"):
            pm.error(u"场景中已经存在代理对象")

        pm.createNode("transform", name="Proxy_neck_head_Grp", p="Proxy_Grp")

        pm.parent(pm.spaceLocator(name="proxyHeadLoc"), "Proxy_neck_head_Grp")

        for side in ["LF", "RT"]:
            pm.parent(pm.spaceLocator(name="proxy{}EarLoc".format(side)), "proxyHeadLoc")
            if side == "LF":
                pm.PyNode("proxy{}EarLoc".format(side)).translate.set([5, 2, 0])
            else:
                pm.PyNode("proxy{}EarLoc".format(side)).translate.set([-5, 2, 0])

        return True

    def build_module(self):
        neck_ctrl_group = "MD_{}_Grp".format(self.module_name)
        if not pm.objExists(neck_ctrl_group):
            pm.createNode("transform", name=neck_ctrl_group, p="Master_Ctrl")

        head_ctrl = "MD_{}_Head_Ctrl".format(self.module_name)
        head_ctrl_grp = jnt_or_control_grp(
            name=head_ctrl, object_type="tours", parent_node=neck_ctrl_group, have_jnt=True)
        if not pm.objExists("proxyHeadLoc"):
            pm.error(u"缺少代理物体")
        pm.delete(pm.pointConstraint("proxyHeadLoc", head_ctrl_grp, mo=False))

        for side in ["LF", "RT"]:
            ear_fk_ctrl = "{}_Ear_01_01_FK_Ctrl".format(side)
            ear_fk_ctrl_grp = jnt_or_control_grp(
                name=ear_fk_ctrl, object_type="cylinder", parent_node=head_ctrl, have_jnt=True)
            pm.delete(pm.parentConstraint("proxy{}EarLoc".format(side), ear_fk_ctrl_grp, mo=False))

        return

    def __str__(self):
        return self.module_name