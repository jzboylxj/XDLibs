# coding: utf-8

from pymel import core as pm

AUTHOR = "XiaoJun Li"
VERSION = [1, 0, 0]
TYPE = "module"
NAME = "module"
DESCRIPTION = ""


class ModuleSettingWindow:
    def __init__(self):
        self.toolName = "{}SettingWindow".format(TYPE)
        self.title = "{} Setting Window".format(NAME.title())
        self.name = NAME

    def window(self):
        template = pm.uiTemplate('ExampleTemplate', force=True)
        template.define(pm.button, width=100, height=30, align='left')
        template.define(pm.frameLayout, labelVisible=False, mw=5, mh=5)

        if pm.window(self.toolName, ex=True):
            pm.deleteUI(self.toolName)

        with pm.window(self.toolName, menuBar=True, menuBarVisible=True, title=self.title) as win:
            # start the template block
            with template:
                with pm.formLayout("moduleSettingWindowMainLayout"):
                    with pm.tabLayout("moduleSettingTabLayout", cr=True):
                        with pm.frameLayout("mainSettingFrameLayout", lv=False, bgs=False, mw=5, mh=5):
                            with pm.columnLayout(adj=1, rs=5):
                                with pm.frameLayout(lv=False, bgs=True, mw=10, mh=10):
                                    pm.textFieldGrp(label="Name:", cw=[140, 50], text=self.name)
                                    pm.optionMenuGrp(label="Side:")
                                    pm.menuItem(label='Center')
                                    pm.menuItem(label='Left')
                                    pm.menuItem(label='Right')

                                    pm.intSliderGrp(field=True,
                                                    label='Component Index:',
                                                    minValue=0,
                                                    maxValue=50,
                                                    fieldMinValue=0,
                                                    fieldMaxValue=50,
                                                    cw3=[140, 50, 50],
                                                    value=0)
                                    pm.optionMenuGrp(label="Connector:")
                                    pm.menuItem(label='Standard')
                                    pm.menuItem(label='Orientation')

                                with pm.frameLayout(label="Joint Settings", lv=True, bgs=True, mw=10, mh=10):
                                    with pm.rowColumnLayout(numberOfRows=1, cs=[1, 5], adj=2):
                                        pm.checkBox(v=False, label="", rs=True, w=10)
                                        pm.intSliderGrp(field=True,
                                                        label="Parent Joint Index:",
                                                        minValue=-1,
                                                        maxValue=50,
                                                        fieldMinValue=-1,
                                                        fieldMaxValue=50,
                                                        cw3=[125, 50, 100],
                                                        value=-1)
                                    with pm.rowColumnLayout(numberOfRows=1, cs=[1, 5]):
                                        pm.text(label="Joint Names(None)", w=140, al="right")
                                        pm.button(label="Configure")
                                with pm.frameLayout(label="Channels Host Settings", lv=True, bgs=True, mw=10, mh=10):
                                    with pm.rowColumnLayout(numberOfRows=1, cs=[1, 5], adj=2):
                                        pm.text(label="Host:")
                                        pm.textField(w=150, h=30)
                                        pm.button(label="<<")
                                with pm.frameLayout(label="Custom Controllers Group", lv=True, bgs=True, mw=10, mh=10):
                                    pm.textField(h=30)

                        with pm.frameLayout("componentSettingFrameLayout", lv=False):
                            with pm.columnLayout(adj=1, rs=5):
                                with pm.frameLayout(lv=False, bgs=True):
                                    pm.checkBox(label="Joint", value=False)
                                    pm.checkBox(label="Uniform Scale", value=False)
                                    pm.checkBox(label="World Space Orientation Align", value=True)
                                    pm.checkBox(label="Mirror Behaviour L and R", value=False)
                                    pm.floatSliderGrp(field=True,
                                                      label='Control Size',
                                                      minValue=0.01,
                                                      maxValue=50,
                                                      fieldMinValue=0.01,
                                                      fieldMaxValue=20000,
                                                      cw3=[100, 50, 50],
                                                      value=1.00)
                                    pm.optionMenuGrp("controlShapeSelector", label="Control Shape", cw2=[100, 130])
                                    for item in [
                                        "Arrow", "Circle", "Compas", "Cross", "Crossarrow",
                                        "Cube", "Cubewithpeak", "Cylinder", "Diamond", "Flower",
                                        "Null", "Pyramid", "Sphere", "Square"]:
                                        pm.menuItem(label=item)
                                    pm.optionMenuGrp("controlShapeSelector", e=True, v="Cube")

                                with pm.frameLayout(label="Keyable", lv=True, bgs=True):
                                    with pm.horizontalLayout():
                                        with pm.columnLayout(adj=1, rs=5):
                                            pm.button(label="Translate")
                                            pm.checkBox(label="tx", value=True)
                                            pm.checkBox(label="ty", value=True)
                                            pm.checkBox(label="tz", value=True)
                                        with pm.columnLayout(adj=1, rs=5):
                                            pm.button(label="Rotate")
                                            pm.checkBox(label="rx", value=True)
                                            pm.checkBox(label="ry", value=True)
                                            pm.checkBox(label="rz", value=True)
                                            pm.checkBox(label="ro", value=True)
                                            pm.optionMenu()
                                            for item in ["XYZ", "YZX", "ZXY", "ZXY", "YXZ", "ZYX"]:
                                                pm.menuItem(label=item)
                                        with pm.columnLayout(adj=1, rs=5):
                                            pm.button(label="Scale")
                                            pm.checkBox(label="sx", value=True)
                                            pm.checkBox(label="sy", value=True)
                                            pm.checkBox(label="sz", value=True)
                                with pm.frameLayout(label="IK Reference Array", lv=True, bgs=True):
                                    with pm.horizontalLayout():
                                        pm.textScrollList(h=150)
                                        with pm.columnLayout(adj=1, rs=5):
                                            pm.button(label="<<")
                                            pm.button(label=">>")

                    pm.tabLayout(
                        "moduleSettingTabLayout", edit=True,
                        tabLabel=(
                            ("mainSettingFrameLayout", 'Main Settings'),
                            ("componentSettingFrameLayout", 'Component Settings'),
                        ),
                        sti=1)

                    pm.button("moduleSettingCloseButton", label="Close")

                    pm.formLayout(
                        "moduleSettingWindowMainLayout", e=True,
                        attachForm=[
                            ("moduleSettingTabLayout", "top", 5),
                            ("moduleSettingTabLayout", "left", 5),
                            ("moduleSettingTabLayout", "right", 5),
                            ("moduleSettingCloseButton", "bottom", 5),
                            ("moduleSettingCloseButton", "left", 5),
                            ("moduleSettingCloseButton", "right", 5),
                        ],
                        attachControl=[
                            ("moduleSettingTabLayout", "bottom", 5, "moduleSettingCloseButton"),
                        ]
                    )

        pm.showWindow(self.toolName)
