#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/10/12 23:26
# @Author  : Li XiaoJun
# @Site    : 
# @File    : main.py

from pymel import core as pm
from animation import common

reload(common)


class Creator(common.Singleton):

    def __init__(self):
        super(Creator, self).__init__()

        self.show()
        self.initialize()

    def show(self):
        pass

    def initialize(self):
        pass


class EyeCreator(Creator):
    def __init__(self):
        super(EyeCreator, self).__init__()

        self.left_up_master_curve_setter = None
        self.left_low_master_curve_setter = None
        self.right_up_master_curve_setter = None
        self.right_low_master_curve_setter = None

        self.left_up_out_curve_setter = None
        self.left_low_out_curve_setter = None
        self.right_up_out_curve_setter = None
        self.right_low_out_curve_setter = None

        self.show()
        self.initialize()

    def show(self):
        if pm.window("eyeCreator", ex=True):
            pm.deleteUI("eyeCreator")
        pm.window("eyeCreator", title="Eye Creator")
        main_layout = pm.scrollLayout(cr=True)

        pm.frameLayout(p=main_layout, label=u"Pre", cll=True, cl=False, bgs=True, mw=5, mh=5)
        pm.columnLayout(adj=1, rs=2)
        pm.text(
            label=u"Step1: 创建Master Curve",
            al="left",
            ann=u"这根曲线将会约束眼皮的蒙皮骨骼")
        self.left_up_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setter(self.left_up_master_curve_setter))
        self.left_low_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setter(self.left_low_master_curve_setter))

        self.right_up_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setter(self.right_up_master_curve_setter))
        self.right_low_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setter(self.right_low_master_curve_setter))

        pm.separator(h=10, style="in")

        pm.text(
            label=u"Step2: 创建Out Curve",
            al="left",
            ann=u"这根曲线将会实现眼睛的开合功能")
        self.left_up_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setter(self.left_up_out_curve_setter))
        self.left_low_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setter(self.left_low_out_curve_setter))

        self.right_up_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setter(self.right_up_out_curve_setter))
        self.right_low_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setter(self.right_low_out_curve_setter))

        pm.setParent("..")

        pm.showWindow("eyeCreator")

    def initialize(self):
        pass

    def curve_setter(self, widget):
        select = pm.ls(sl=True)[0]
        if select:
            pm.textFieldButtonGrp(widget, e=True, text=select.name())
        else:
            pm.error(u"获取曲线失败，请确认当前是否选择一根曲线")
        return
