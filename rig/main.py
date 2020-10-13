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

        self.left_eyeball_setter = None
        self.right_eyeball_setter = None

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

        pm.frameLayout(p=main_layout, label=u"Pre", cll=True, cl=False, mw=5)

        pm.frameLayout(
            label=u"Step1: 基本体设置",
            mw=5,
            bgs=True,
            cll=True, cl=False)
        self.left_eyeball_setter = pm.textFieldButtonGrp(
            label=u"Left Eye:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(self.left_eyeball_setter))
        self.right_eyeball_setter = pm.textFieldButtonGrp(
            label=u"Right Eye:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(self.right_eyeball_setter))

        pm.setParent("..")

        pm.frameLayout(
            label=u"Step2: 创建Master Curve",
            ann=u"这根曲线将会约束眼皮的蒙皮骨骼",
            mw=5,
            bgs=True,
            cll=True, cl=False)
        self.left_up_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.left_up_master_curve_setter))
        self.left_low_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.left_low_master_curve_setter))

        self.right_up_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.right_up_master_curve_setter))
        self.right_low_master_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.right_low_master_curve_setter))
        pm.setParent("..")

        pm.frameLayout(
            label=u"Step3: 创建Out Curve",
            ann=u"这根曲线将会实现眼睛的开合功能",
            mw=5,
            bgs=True,
            cll=True, cl=False)
        self.left_up_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(self.left_up_out_curve_setter))
        self.left_low_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Left Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(self.left_low_out_curve_setter))

        self.right_up_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Up:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(self.right_up_out_curve_setter))
        self.right_low_out_curve_setter = pm.textFieldButtonGrp(
            label=u"Right Down:",
            bl=u"Setting",
            adj=2,
            cw3=[70, 100, 100],
            bc=lambda *args: self.curve_setting(
                self.right_low_out_curve_setter))
        pm.setParent("..")

        pm.setParent("..")

        pm.separator(h=20, style="none")

        pm.frameLayout(
            label=u"Builder",
            mw=5, mh=5,
            bgs=True,
            cll=True, cl=False)
        pm.button(label=u"Builder Master Ctrl",
                  c=lambda *args: self.build_master_ctrl())
        pm.setParent("..")

        pm.showWindow("eyeCreator")

    def initialize(self):
        pass

    def curve_setting(self, widget):
        select = pm.ls(sl=True)[0]
        if select:
            pm.textFieldButtonGrp(widget, e=True, text=select.name())
        else:
            pm.error(u"获取曲线失败，请确认当前是否选择一根曲线")
        return

    def build_master_ctrl(self):
        left_eyeball_geo = pm.textFieldButtonGrp(
            self.left_eyeball_setter, q=True, text=True)
        left_master_ctrl = pm.torus(
            name="LF_Eye_01_Master_Ctrl",
            p=[0, 0, 0],
            ax=[0, 0, 1],
            ssw=0,
            esw=360,
            msw=360,
            r=0.6,
            hr=0.02,
            d=3,
            ut=0,
            tol=0.01,
            s=8,
            nsp=4,
            ch=1)
        pm.delete(left_eyeball_geo, )

        return
