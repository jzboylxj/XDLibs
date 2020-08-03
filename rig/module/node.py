#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/31 15:59
# @Author  : Li XiaoJun
# @Site    :
# @File    : node.py
from animation import common
from pymel import core as pm

reload(common)


class DoJointGrp:
    def __init__(self, name=""):
        self.name = name
        self.bnd_name = ""
        self.sub_con = ""
        self.bnd_con = ""
        self.bnd_loc = ""
        self.bnd_grp = ""
        self.parent_module = ""

        self.parent_node = ""
        self.have_sub = False
        self.offset_value = [0, 0, 0]

        self.config_node = ""

        self.init()

    def init(self):
        if pm.objExists(self.name):
            self.parent_module = pm.PyNode(
                self.name).attr("parentModule").get()
            self.parent_node = pm.PyNode(self.name).attr("parentNode").get()
            self.bnd_grp = pm.PyNode(self.name).attr("bndGrp").get()
            self.bnd_loc = pm.PyNode(self.name).attr("bndLoc").get()
            self.bnd_con = pm.PyNode(self.name).attr("bndCon").get()
            self.sub_con = pm.PyNode(self.name).attr("subCon").get()
            self.bnd_name = pm.PyNode(self.name).attr("bndName").get()

    def build_mode_3(self, parent="", have_sub=False, offset_value=None):
        self.parent_node = parent
        self.have_sub = have_sub
        if offset_value is not None:
            self.offset_value = offset_value
        else:
            self.offset_value = [0, 0, 0]

        pm.select(cl=True)
        self.bnd_name = pm.joint(name=(self.name + "_BND")).name()
        if self.have_sub:
            self.sub_con = common.add_node_as_parent(
                self.bnd_name,
                search_field="_BND", suffix="Sub_CON", node_type="circle")
            self.bnd_con = common.add_node_as_parent(
                self.sub_con,
                search_field="Sub_CON", suffix="_CON", node_type="circle")
            self.bnd_loc = common.add_node_as_parent(
                self.bnd_con,
                search_field="_CON", suffix="_BND_LOC", node_type="locator")
            self.bnd_grp = common.add_node_as_parent(
                self.bnd_loc,
                search_field="_BND_LOC",
                suffix="_BND_GRP", node_type="transform")
        else:
            self.bnd_con = common.add_node_as_parent(
                self.bnd_name,
                search_field="_BND", suffix="_CON", node_type="circle")
            self.bnd_loc = common.add_node_as_parent(
                self.bnd_con,
                search_field="_CON", suffix="_BND_LOC", node_type="locator")
            self.bnd_grp = common.add_node_as_parent(
                self.bnd_loc, search_field="_BND_LOC", suffix="_BND_GRP",
                node_type="transform")
        pm.parent(self.bnd_grp, self.parent_node)
        pm.PyNode(self.bnd_grp).translate.set(self.offset_value)

        self.create_config_node()

        self.setting_config_node("module", self.name)
        self.setting_config_node("parentModule",
                                 value=self.parent_module)
        self.setting_config_node("parentNode", self.parent_node)
        self.setting_config_node("bndGrp", self.bnd_grp)
        self.setting_config_node("bndLoc", self.bnd_loc)
        self.setting_config_node("bndCon", self.bnd_con)
        self.setting_config_node("subCon", self.sub_con)
        self.setting_config_node("bndName", self.bnd_name)

        return True

    def build_mode_2(self, parent="", have_sub=False, offset_value=None):
        self.parent_node = parent
        self.have_sub = have_sub
        if offset_value is not None:
            self.offset_value = offset_value
        else:
            self.offset_value = [0, 0, 0]

        pm.select(cl=True)
        self.bnd_name = pm.joint(name=(self.name + "_BND")).name()

        self.bnd_con = common.add_node_as_parent(
            self.bnd_name,
            search_field="_BND", suffix="_CON", node_type="circle")
        self.bnd_grp = common.add_node_as_parent(
            self.bnd_con, search_field="_CON", suffix="_GRP",
            node_type="transform")

        pm.parent(self.bnd_grp, self.parent_node)
        pm.PyNode(self.bnd_grp).translate.set(self.offset_value)

        self.create_config_node()

        self.setting_config_node("module", self.name)
        self.setting_config_node("parentModule", value=self.parent_module)
        self.setting_config_node("parentNode", self.parent_node)
        self.setting_config_node("bndGrp", self.bnd_grp)
        self.setting_config_node("bndLoc", self.bnd_loc)
        self.setting_config_node("bndCon", self.bnd_con)
        self.setting_config_node("subCon", self.sub_con)
        self.setting_config_node("bndName", self.bnd_name)

        return True

    def create_config_node(self):
        attr_list = [
            "module", "parentModule", "parentNode", "bndGrp", "bndLoc",
            "bndCon", "subCon", "bndName"
        ]
        self.config_node = common.null_node(name=self.name)
        for attr in attr_list:
            common.quick_add_attr(self.config_node, attr=attr)
        return self.config_node

    def setting_config_node(self, attr, value):
        pm.PyNode(self.config_node).attr(attr).set(value)
        return True

    def __str__(self):
        return self.name
