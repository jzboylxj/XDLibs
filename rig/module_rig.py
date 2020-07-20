#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/20 11:03
# @Author  : Li XiaoJun
# @Site    : 
# @File    : module_rig.py

from pymel import core as pm
from animation import common

reload(common)

tool_version = 0.1


class ModuleRig(common.Singleton):

    def __init__(self):
        super(ModuleRig, self).__init__()

        # 当前TabLayout选择状态的选择索引
        self.current_tab_index = 2

        self.initialize()
        self.show()

    def show(self):
        if pm.window("xdModuleRigUI", ex=True):
            pm.deleteUI("xdModuleRigUI")
        pm.window(
            "xdModuleRigUI",
            t=u"XD模块化绑定 %s" % tool_version,
            mb=True,
            cc=lambda *args: self._closed_window_cmd())

        self.menu_bar()

        self.main_tab = pm.tabLayout(
            "jsonManagerMainTabLayout",
            innerMarginWidth=5, innerMarginHeight=5)
        child1 = self.tab_rig_body()
        child2 = self.tab_rig_face()

        pm.tabLayout(
            self.main_tab,
            edit=True,
            tabLabel=(
                (child1, u'Body'),
                (child2, u'Face'),
            ),
            sti=self.current_tab_index)

        pm.showWindow("xdModuleRigUI")

    def initialize(self):
        pass

    def _closed_window_cmd(self):
        pass

    def menu_bar(self):
        pass

    def tab_rig_body(self):
        form_layout = pm.formLayout()
        pm.setParent("..")
        return form_layout

    def tab_rig_face(self):
        scroll_layout = pm.scrollLayout(cr=False)
        face_pre_layout = pm.frameLayout(
            label=u"Pre",
            cll=True,
            cl=False,
            bgs=True,
            mw=5, mh=5)

        input_items = [
            "Mask",
            "Face",
            "All Head",
            "Right Eye",
            "Left Eye",
            "Upper Teeth",
            "Lower Teeth",
            "Tongue",
            "Eyebrow",
            "Eyelash",
            "Extras",
        ]

        for index in range(0, len(input_items)):
            if input_items[index] == "Mask":
                pm.text(label=u"Polygons:", al="left")
            if input_items[index] == "Face":
                pm.separator(h=5, style="none")
                pm.text(label=u"Objects:", al="left")
            if input_items[index] == "Upper Teeth":
                pm.separator(h=5, style="none")
                pm.text(label=u"Options:", al="left")

            pm.rowColumnLayout(nc=3)
            pm.button(l=unicode(input_items[index]), w=120)
            pm.textField(w=150, en=False)
            pm.button("?")
            pm.setParent("..")

        pm.separator(h=5, style="in")

        form_layout = pm.formLayout()
        rig_type_options = pm.optionMenuGrp(
            label=u"Rig-type:", cw2=[52, 300], adj=2)
        rig_type_options_help = pm.button("?")
        symmetrical_check_box = pm.checkBox(label=u"Non symmetrical")
        symmetrical_check_help = pm.button(label="?")
        game_engine_check_box = pm.checkBox(label=u"Game engine")
        game_engine_check_help = pm.button(label="?")
        advanced_check_box = pm.checkBox(label=u"Advanced")
        advanced_check_help = pm.button(label="?")

        pm.formLayout(
            form_layout,
            edit=True,
            attachForm=[
                (rig_type_options, 'top', 2),
                (rig_type_options, 'left', 0),
                (rig_type_options_help, 'right', 0),
                (symmetrical_check_box, 'left', 0),
                (symmetrical_check_help, 'right', 0),
                (game_engine_check_help, 'right', 0),
                (advanced_check_help, 'right', 0),
            ],
            attachControl=[
                (rig_type_options, 'right', 5, rig_type_options_help),
                (symmetrical_check_box, 'top', 9, rig_type_options),
                (game_engine_check_box, 'top', 12, symmetrical_check_box),
                (advanced_check_box, 'top', 12, game_engine_check_box),
                (symmetrical_check_help, 'top', 6, rig_type_options),
                (game_engine_check_help, 'top', 2, symmetrical_check_help),
                (advanced_check_help, 'top', 2, game_engine_check_help),
            ]
        )
        pm.setParent("..")

        pm.setParent("..")  # end of face_pre_layout
        pm.setParent("..")  # end of scroll_layout
        return scroll_layout

    # def face_pre_layout(self):
    #     layout = pm.frameLayout(label=u"Pre", cll=True, cl=False, bgs=True)
    #
    #     pm.text(label="Polygons:")
    #
    #     pm.setParent("..")
    #     return layout
