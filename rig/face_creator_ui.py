# coding: utf-8
from imp import reload

from animation import common
from pymel import core as pm
from pymel.util import path

from rig import template_dir

from rig_classic_components import nose_creator, mouth_creator, eye_creator, neck_ear_creator

reload(eye_creator)

reload(mouth_creator)

reload(neck_ear_creator)

reload(nose_creator)

from core.utils import imported_object, jnt_or_control_grp, symmetry_surface, drag_to_group_and_field

VERSION = 0.21


def draw_component(comp_type, parent=None, showSettingWnd=False):
    u"""Draw a new component of a given name

    :return:
    """
    pass


class FaceCreatorUI(common.Singleton):
    def __init__(self):
        super(FaceCreatorUI, self).__init__()

        self.version = VERSION

        # self.rig_root_node = ""  # group "World"

        # # neck and ear rig_classic_components
        # self.neck_ear_creator = neck_ear_creator.NeckEarCreator()

        # # eye rig_classic_components
        # self.eye_module = "Eye_01"
        # self.eye_creator = eye_creator.EyeCreator()

        # self.left_master_ctrl_surface = ""
        # self.right_master_ctrl_surface = ""

        # # mouth rig_classic_components
        # self.mouth_module = "Mouth_01"
        # self.mouth_creator = mouth_creator.MouthCreator()

        # self.up_base_curve = ""
        # self.low_base_curve = ""
        # self.up_tweak_surface = ""
        # self.low_tweak_surface = ""
        # self.up_out_curve = ""
        # self.low_out_curve = ""

        # self.mouth_surface = ""
        # self.mouth_lip_sew_surface = ""

        # # cheek rig_classic_components
        # self.cheek_module = "Cheek_01"
        # self.cheek_creator = cheek_creator.CheekCreator()

        self.show_window()

    def show_window(self):
        template = pm.uiTemplate('ModuleRigWindowTemplate', force=True)
        template.define(pm.button, width=100, height=30, align='left')
        template.define(pm.frameLayout, labelVisible=False, mw=5, mh=5)

        if pm.window("xdFaceCreatorWnd", exists=True):
            pm.deleteUI("xdFaceCreatorWnd")

        with pm.window("xdFaceCreatorWnd",
                       title="Biped Creator dev {}".format(self.version),
                       mb=True) as win:
            with template:
                with pm.formLayout(en=False) as self.root_layout:
                    with pm.tabLayout(p=self.root_layout, cr=True) as module_tab_layout:
                        with pm.paneLayout(configuration='vertical2', swp=1) as module_sub_tab:
                            with pm.frameLayout(label=u"Models Tree", mw=0, mh=0, bgs=True, w=250):
                                pm.treeView(vis=True, abr=False)
                            with pm.tabLayout() as setting_sub_tab:
                                main_setting_sub = pm.columnLayout(adj=1)
                                pm.setParent("..")
                                component_setting_sub = pm.columnLayout(adj=1)
                                pm.setParent("..")

                            pm.tabLayout(
                                setting_sub_tab, edit=True,
                                tabLabel=(
                                    (main_setting_sub, 'Main Setting'),
                                    (component_setting_sub, 'Component Setting'),
                                ),
                                sti=1,
                            )

                        control_sub_tab = pm.columnLayout(adj=1, p=module_tab_layout)

                    pm.tabLayout(
                        module_tab_layout, edit=True,
                        tabLabel=(
                            (module_sub_tab, 'Module'),
                            (control_sub_tab, 'Control'),
                        ),
                        sti=1,
                    )

                pm.formLayout(
                    self.root_layout, edit=True,
                    attachForm=[
                        (module_tab_layout, "top", 5),
                        (module_tab_layout, "left", 10),
                        (module_tab_layout, "right", 10),
                        (module_tab_layout, "bottom", 10),
                    ],
                    attachControl=[
                        # (data_form, 'top', 2, tool_tab_bar),
                    ])

            # pre_tab = pm.columnLayout(adj=1, p=tab_layout)
            # self.rig_pre_frame(pre_tab)
            # pm.setParent(pre_tab)

            # neck_ear_tab = pm.columnLayout(adj=1, p=tab_layout)
            # self.neck_ear_module_frame(neck_ear_tab)
            # pm.setParent(neck_ear_tab)

            # eye_tab = pm.columnLayout(adj=1, p=tab_layout)
            # self.eye_module_frame(eye_tab)
            # pm.setParent(eye_tab)

            # mouth_tab = pm.columnLayout(adj=1, p=tab_layout)
            # self.mouth_module_frame(mouth_tab)
            # pm.setParent(mouth_tab)

            # face_tab = pm.columnLayout(adj=1, p=tab_layout)
            # self.cheek_module_frame(face_tab)
            # pm.setParent(face_tab)

            # linkage_tab = pm.columnLayout(adj=1, p=tab_layout)
            # self.linkage_frame(linkage_tab)
            # pm.setParent(linkage_tab)

        with win:
            with pm.menu(label="Rig"):
                pm.menuItem(label='New', c=lambda *args: self.new_rig_structure())
                pm.menuItem(label='Delete')
                pm.menuItem(divider=True)
                pm.menuItem(label='Publish Rig')
            with pm.menu(label="Templates"):
                pm.menuItem(label='Save Template')
                pm.menuItem(divider=True)
                pm.menuItem(label='Human')
            with pm.menu(label="Modules"):
                pm.menuItem(label=u"Mouth surface", c=lambda *args: self.build_base_loc())
                pm.menuItem(label=u"Mouth tweak surface", c=lambda *args: self.build_base_loc())
            with pm.menu(label="Components"):
                pm.menuItem(label=u"control_01",
                            c=lambda *args: draw_component(comp_type="control_01", parent=None, showSettingWnd=True))
            with pm.menu(label="Tools"):
                pm.menuItem(label=u"Symmetry surface", c=lambda *args: self.symmetry_surface())

        pm.showWindow(win)

        if pm.objExists("World"):
            pm.formLayout(self.root_layout, e=True, en=True)

        # self.eye_control_location_frame_init()
        # self.cheek_proxy_frame_init()

        return

    def _closed_window_cmd(self):

        # mouth rig_classic_components
        pm.optionVar(
            sv=('mouth_01_Up_Base_Curve', pm.textFieldButtonGrp("xdMouthCreatorUpBaseCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Low_Base_Curve', pm.textFieldButtonGrp("xdMouthCreatorLowBaseCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Up_Tweak_Surface',
                pm.textFieldButtonGrp("xdMouthCreatorUpTweakSurfaceField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Low_Tweak_Surface',
                pm.textFieldButtonGrp("xdMouthCreatorLowTweakSurfaceField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Up_Out_Curve',
                pm.textFieldButtonGrp("xdMouthCreatorUpOutCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_Low_Out_Curve',
                pm.textFieldButtonGrp("xdMouthCreatorLowOutCurveField", q=True, text=True)))
        pm.optionVar(
            sv=('mouth_01_mouth_surface',
                pm.textFieldButtonGrp("xdMouthCreatorMouthSurfaceField", q=True, text=True)))

        pm.optionVar(
            sv=('mouth_01_lip_sew_surface',
                pm.textFieldButtonGrp("xdMouthCreatorMouthLipSewSurfaceField", q=True, text=True)))
        return

    def initialize(self):
        u"""初始化数据

        从MAYA的保存的属性数据里面获取一些值

        :return:
        """

        # mouth rig_classic_components
        if pm.optionVar(q='mouth_01_Up_Base_Curve'):
            self.up_base_curve = pm.optionVar(q='mouth_01_Up_Base_Curve')
        if pm.optionVar(q='mouth_01_Low_Base_Curve'):
            self.low_base_curve = pm.optionVar(q='mouth_01_Low_Base_Curve')
        if pm.optionVar(q='mouth_01_Up_Tweak_Surface'):
            self.up_tweak_surface = pm.optionVar(q='mouth_01_Up_Tweak_Surface')
        if pm.optionVar(q='mouth_01_Low_Tweak_Surface'):
            self.low_tweak_surface = pm.optionVar(
                q='mouth_01_Low_Tweak_Surface')
        if pm.optionVar(q='mouth_01_Up_Out_Curve'):
            self.up_out_curve = pm.optionVar(q='mouth_01_Up_Out_Curve')
        if pm.optionVar(q='mouth_01_Low_Out_Curve'):
            self.low_out_curve = pm.optionVar(q='mouth_01_Low_Out_Curve')
        if pm.optionVar(q='mouth_01_mouth_surface'):
            self.mouth_surface = pm.optionVar(q='mouth_01_mouth_surface')
        if pm.optionVar(q='mouth_01_lip_sew_surface'):
            self.mouth_lip_sew_surface = pm.optionVar(
                q='mouth_01_lip_sew_surface')
        return

    def rig_pre_frame(self, parent):
        layout = pm.frameLayout(p=parent, lv=False, mw=10, mh=5, bgs=True)
        pm.button("xdMouthCreatorNewRigBtn", label=u"New", c=lambda *args: self.new_rig_structure())
        pm.setParent(layout)

        return layout

    def neck_ear_module_frame(self, parent):
        frame = pm.frameLayout(p=parent, label="Preparatory Work", mh=5, mw=10)
        proxy_grp_frame = pm.frameLayout(p=frame, label=u"Proxy", mh=10, mw=10, bgs=True)
        pm.button(label=u"Build Proxy", c=lambda *args: self.proxy_neck_ear())
        pm.setParent(proxy_grp_frame)

        pm.button(label=u"Build Module", c=lambda *args: self.build_neck_head_module())

        pm.setParent(frame)
        return frame

    def eye_module_frame(self, parent):
        frame = pm.frameLayout(p=parent, label="Preparatory Work", mh=5, mw=10)

        pm.frameLayout(label=u"Eye Guid Curve",
                       ann=u"这些曲线将会约束眼皮的蒙皮骨骼", mh=10, mw=10, bgs=True, cll=True, cl=True)
        pm.text(label="Left side:", al="left")

        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpMasterCurveField",
            label=u"Left Up Master Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(
                field="xdMouthCreatorLeftUpMasterCurveField", group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowMasterCurveField",
            label=u"Left Low Master Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(
                field="xdMouthCreatorLeftLowMasterCurveField", group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpBlinkCurveField",
            label=u"Left Up Blink Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(
                field="xdMouthCreatorLeftUpBlinkCurveField", group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowBlinkCurveField",
            label=u"Left Low Blink Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(
                field="xdMouthCreatorLeftLowBlinkCurveField", group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpOutCurveField",
            label=u"Left Up Out Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(
                field="xdMouthCreatorLeftUpOutCurveField", group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowOutCurveField",
            label=u"Left Low Out Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(
                field="xdMouthCreatorLeftLowOutCurveField", group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpTweakCurveField",
            label=u"Left Up Tweak Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(
                field="xdMouthCreatorLeftUpTweakCurveField", group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowTweakCurveField",
            label=u"Left Low Tweak Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftLowTweakCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpFreshyCurveField",
            label=u"Left Up Freshy Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftUpFreshyCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowFreshyCurveField",
            label=u"Left Low Freshy Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftLowFreshyCurveField",
                                                         group="LF_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpShapeSurfaceField",
            label=u"Left Up Shape Surface", bl=u"Get Object", adj=2,
            bc=lambda *args: self.import_eye_up_shape_surface(vertical="Up", side="LF",
                                                              field="xdMouthCreatorLeftUpShapeSurfaceField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowShapeSurfaceField",
            label=u"Left Low Shape Surface", bl=u"Get Object", adj=2,
            bc=lambda *args: self.import_eye_up_shape_surface(vertical="Low", side="LF",
                                                              field="xdMouthCreatorLeftLowShapeSurfaceField"))

        pm.separator(style="in", h=5)

        pm.text(label="Right side:", al="left")

        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpMasterCurveField",
            label=u"Right Up Master Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpMasterCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowMasterCurveField",
            label=u"Right Low Master Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightLowMasterCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpBlinkCurveField",
            label=u"Right Up Blink Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpBlinkCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowBlinkCurveField",
            label=u"Right Low Blink Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightLowBlinkCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpOutCurveField",
            label=u"Right Up Out Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpOutCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowOutCurveField",
            label=u"Right Low Out Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpOutCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpTweakCurveField",
            label=u"Right Up Tweak Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpTweakCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowTweakCurveField",
            label=u"Right Low Tweak Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightLowTweakCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpFreshyCurveField",
            label=u"Right Up Freshy Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpFreshyCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowFreshyCurveField",
            label=u"Right Low Freshy Curve", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightLowFreshyCurveField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpShapeSurfaceField",
            label=u"Right Up Shape Surface", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightUpShapeSurfaceField",
                                                         group="RT_Eye_01_Curve_Grp"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowShapeSurfaceField",
            label=u"Right Low Shape Surface", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightLowShapeSurfaceField",
                                                         group="RT_Eye_01_Curve_Grp"))

        pm.setParent("..")

        pm.frameLayout(label=u"Eye Control location", mh=10, mw=10, bgs=True, cll=True, cl=False)
        pm.text(label=u"* is optional", al='left')
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftEyeGeoField",
            label=u"Left eye geo", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftEyeGeoField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightEyeGeoField",
            label=u"Right eye geo", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightEyeGeoField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftEyeProxyField",
            label=u"Left eye proxy(*)", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorLeftEyeProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightEyeProxyField",
            label=u"Right eye proxy(*)", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_component_in_field(field="xdMouthCreatorRightEyeProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftMasterCtrlField",
            label=u"Left master control", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_master_ctrl_field(side="LF", field="xdMouthCreatorLeftMasterCtrlField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightMasterCtrlField",
            label=u"Right master control", bl=u"Get Object", adj=2,
            bc=lambda *args: self.eye_master_ctrl_field(side="RT", field="xdMouthCreatorRightMasterCtrlField"))
        pm.setParent("..")

        pm.button(label=u"Build Module", c=lambda *args: self.build_eye_module())

        pm.setParent(frame)
        return frame

    def cheek_module_frame(self, parent):
        frame = pm.frameLayout(p=parent, label=u"Preparatory Work", mh=5, mw=10)

        proxy_grp_frame = pm.frameLayout(p=frame, label=u"Proxy", mh=10, mw=10, bgs=True)
        pm.button(label=u"Build Proxy", c=lambda *args: self.proxy_cheek())
        pm.frameLayout(p=proxy_grp_frame, label=u"component detail", cl=True, cll=True, mh=10, mw=10)

        pm.text(label="Left side:", al="left")

        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftCheek01ProxyField",
            label=u"Left cheek 01", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftCheek01ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftCheek02ProxyField",
            label=u"Left cheek 02", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftCheek02ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftCheek03ProxyField",
            label=u"Left cheek 03", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftCheek03ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftCheek04ProxyField",
            label=u"Left cheek 04", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftCheek04ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLeftCheek05ProxyField",
            label=u"Left cheek 05", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLeftCheek05ProxyField"))

        pm.separator(style="in", h=5)

        pm.rowColumnLayout(numberOfColumns=2, adj=1)
        pm.text(label="Right side:", al="left")
        pm.button(label=u"Mirror Proxy", c=lambda *args: self.mirror_cheek_proxy())
        pm.setParent("..")

        pm.textFieldButtonGrp(
            "xdMouthCreatorRightCheek01ProxyField",
            label=u"Right cheek 01", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightCheek01ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightCheek02ProxyField",
            label=u"Right cheek 02", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightCheek02ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightCheek03ProxyField",
            label=u"Right cheek 03", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightCheek03ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightCheek04ProxyField",
            label=u"Right cheek 04", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightCheek04ProxyField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorRightCheek05ProxyField",
            label=u"Right cheek 05", adj=2, bl="Get object",
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorRightCheek05ProxyField"))

        pm.setParent("..")
        pm.setParent(proxy_grp_frame)

        pm.button(label=u"Build Module", p=frame, c=lambda *args: self.build_cheek_module())
        pm.setParent(frame)
        return frame

    def linkage_frame(self, parent):
        frame = pm.frameLayout(p=parent, label=u"Preparatory Work", mh=5, mw=10)
        pm.button(label=u"Build", p=frame, c=lambda *args: self.build_linkage())
        pm.setParent(frame)
        return frame

    def eye_control_location_frame_init(self):
        for side in ["LF", "RT"]:
            if side == "LF":
                side_alias = "Left"
            else:
                side_alias = "Right"

            for vertical in ["Up", "Low"]:
                prefix = "{}_{}_{}".format(side, self.eye_module, vertical)
                for item in ["Master", "Blink", "Out", "Tweak", "Freshy"]:
                    curve = "{}_{}_Curve".format(prefix, item)
                    if pm.objExists(curve):
                        pm.textFieldButtonGrp(
                            "xdMouthCreator{}{}{}CurveField".format(side_alias, vertical, item), e=True, text=curve)
                surface = "{}_Shape_Surface".format(prefix)
                # print("surface:{}".format(surface))
                if pm.objExists(surface):
                    pm.textFieldButtonGrp(
                        "xdMouthCreator{}{}ShapeSurfaceField".format(side_alias, vertical), e=True, text=surface)
            # control location frame上面的字段
            eye_geo = "{}_Eye_Geo".format(side)
            if pm.objExists(eye_geo):
                pm.textFieldButtonGrp("xdMouthCreator{}EyeGeoField".format(side_alias), e=True, text=eye_geo)

            eye_proxy = "{}_proxy_eye".format(side)
            if pm.objExists(eye_proxy):
                pm.textFieldButtonGrp("xdMouthCreator{}EyeProxyField".format(side_alias), e=True, text=eye_proxy)

            master_ctrl = "{}_{}_Master_Ctrl".format(side, self.eye_module)
            if pm.objExists(master_ctrl):
                pm.textFieldButtonGrp("xdMouthCreator{}MasterCtrlField".format(side_alias), e=True, text=master_ctrl)

        return

    def cheek_proxy_frame_init(self):
        for side in ["LF", "RT"]:
            for index in range(0, 5):
                proxy_loc = "{}_proxyCheek{}Loc".format(side, "{0:02d}".format(index + 1))

                if side == "LF":
                    sider = "Left"
                else:
                    sider = "Right"

                if pm.objExists(proxy_loc):
                    pm.textFieldButtonGrp(
                        "xdMouthCreator{}Cheek{}ProxyField".format(sider, "{0:02d}".format(index + 1)),
                        e=True, text=proxy_loc)
        return

    def mouth_module_frame(self, parent):
        frame = pm.frameLayout(p=parent, label=u"Preparatory Work", mh=5, mw=10)

        curve_grp_frame = pm.frameLayout(p=frame, label=u"Mouth Curve Grp", cll=True, cl=True, mh=10, mw=10, bgs=True)
        pm.textFieldButtonGrp(
            "xdMouthCreatorUpBaseCurveField",
            label=u"Up base curve",
            bl=u"Get Object",
            adj=2,
            text=self.up_base_curve,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorUpBaseCurveField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLowBaseCurveField",
            label=u"Low base curve",
            bl=u"Get Object",
            adj=2,
            text=self.low_base_curve,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLowBaseCurveField"))

        pm.textFieldButtonGrp(
            "xdMouthCreatorUpTweakSurfaceField",
            label=u"Up tweak surface",
            bl=u"Get Object",
            adj=2,
            text=self.up_tweak_surface,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorUpTweakSurfaceField"))

        pm.textFieldButtonGrp(
            "xdMouthCreatorLowTweakSurfaceField",
            label=u"Low tweak surface",
            bl=u"Get Object",
            adj=2,
            text=self.low_tweak_surface,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLowTweakSurfaceField"))

        pm.setParent(curve_grp_frame)

        out_curve_grp_frame = pm.frameLayout(p=frame, label=u"Out Curve Grp", cll=True, cl=True, mh=10, mw=10,
                                             bgs=True)
        pm.textFieldButtonGrp(
            "xdMouthCreatorUpOutCurveField",
            label=u"Up out curve",
            bl=u"Get Object",
            adj=2,
            text=self.up_out_curve,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorUpOutCurveField"))
        pm.textFieldButtonGrp(
            "xdMouthCreatorLowOutCurveField",
            label=u"Low out curve",
            bl=u"Get Object",
            adj=2,
            text=self.low_out_curve,
            bc=lambda *args: self.get_object_in_field("xdMouthCreatorLowOutCurveField"))
        pm.setParent(out_curve_grp_frame)

        pm.separator(h=5, style="in")

        pm.textFieldButtonGrp(
            "xdMouthCreatorMouthSurfaceField",
            label="mouth surface",
            adj=2,
            text=self.mouth_surface,
            bl="Get Object",
            bc=lambda *args: self.import_mouth_surface(
                "mouth_surface",
                "xdMouthCreatorMouthSurfaceField"))

        pm.textFieldButtonGrp(
            "xdMouthCreatorMouthLipSewSurfaceField",
            label="lip sew surface",
            adj=2,
            text=self.mouth_lip_sew_surface,
            bl="Get Object",
            bc=lambda *args: self.import_mouth_surface(
                "mouth_lip_sew_surface",
                "xdMouthCreatorMouthLipSewSurfaceField",
                module="Mouth_01_LipSew"))

        pm.separator(h=5, style="in")
        pm.intFieldGrp("xdMouthCreatorTweakSegmentField", label=u"tweak segment", numberOfFields=1, value1=6)

        jaw_frame = pm.frameLayout(p=frame, label="Jaw Control", cll=True, cl=True, mh=10, mw=10, bgs=True)
        pm.checkBoxGrp(label=u"Mouth cavity", numberOfCheckBoxes=1, label1='Teeth', value1=True)
        pm.button("xdMouthCreatorAddProxyJawBtn", label=u"Add proxy jaw", c=lambda *args: self.proxy_jaw())

        pm.setParent(jaw_frame)

        proxy_tongue_frame = pm.frameLayout(p=frame, label=u"Tongue Proxy", cll=True, cl=False, mh=10, mw=10, bgs=True)
        pm.button(label=u"Build Proxy", c=lambda *args: self.proxy_tongue())
        pm.setParent(proxy_tongue_frame)

        pm.button("xdMouthCreatorBuildMouthModuleBtn", p=frame, label=u"Build Module",
                  c=lambda *args: self.build_mouth_module())

        pm.setParent(frame)
        return frame

    @staticmethod
    def get_object_in_field(field):
        sel_object = pm.ls(sl=True)[0]
        pm.textFieldButtonGrp(field, e=True, text=sel_object)
        return

    def import_mouth_surface(self, template="", field="", module="Mouth_01"):
        template_file = path(template_dir).joinpath("{}.mb".format(template))
        import_object = pm.rename(imported_object(
            template_file), "MD_{}_Surface".format(module))
        deformer_grp = "MD_{}_Deformer_Grp".format(self.mouth_module)
        if pm.objExists(deformer_grp):
            pm.parent(import_object, deformer_grp)
        pm.textFieldButtonGrp(field, e=True, text=import_object)

        return True

    def import_tweak_surface(self, location, field):
        template_file = path(template_dir).joinpath("mouth_tweak_surface.mb")
        import_object = pm.rename(imported_object(template_file),
                                  "MD_{}_{}_Tweak_Surface".format(self.mouth_module, location))
        if pm.objExists("MD_Mouth_01_Curve_Grp"):
            pm.parent(import_object, "MD_Mouth_01_Curve_Grp")
        pm.textFieldButtonGrp(field, e=True, text=import_object)

        return True

    def import_eye_up_shape_surface(self, vertical="Up", side="LF", field=""):
        if vertical == "Up":
            template_file = path(template_dir).joinpath(
                "lf_eye_up_shape_surface.mb")
        else:
            template_file = path(template_dir).joinpath(
                "lf_eye_low_shape_surface.mb")

        import_object = pm.rename(imported_object(template_file),
                                  "{}_{}_{}_Shape_Surface".format(side, self.eye_module, vertical))
        if pm.objExists("{}_{}_Curve_Grp".format(side, self.eye_module)):
            pm.parent(import_object, "{}_{}_Curve_Grp".format(
                side, self.eye_module))

        pm.textFieldButtonGrp(field, e=True, text=import_object)

        return True

    def new_rig_structure(self):
        if not pm.objExists("World"):
            self.rig_root_node = pm.createNode("transform", name="World")
            deformer_grp = pm.createNode("transform", name="Deformer_Grp")
            pm.parent(deformer_grp, self.rig_root_node)
            master_ctrl = pm.createNode("transform", name="Master_Ctrl")
            pm.parent(master_ctrl, self.rig_root_node)
            # pm.button("xdMouthCreatorNewRigBtn", e=True, en=False)
            pm.formLayout(self.root_layout, e=True, en=True)
        else:
            pm.confirmDialog(title=u'提示', icn="warning",
                             message=u"场景中已存在绑定\n"
                                     u"提示：开始绑定前需要检查文件，确保场景中没有存在绑定结构")
        return

    def build_mouth_module(self):
        self.before_build_mouth()

        self.mouth_creator.build_module()
        return

    def build_base_loc(self):
        if pm.window("xdBaseLocCreatorWnd", ex=True):
            pm.deleteUI("xdBaseLocCreatorWnd")
        pm.window("xdBaseLocCreatorWnd", title="Base Loc Creator")
        pm.showWindow("xdBaseLocCreatorWnd")

    def before_build_mouth(self):
        u"""mouth creator执行创建命令之前，执行此方法，初始化所有的变量"""
        self.up_base_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorUpBaseCurveField", q=True, text=True)
        self.low_base_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLowBaseCurveField", q=True, text=True)
        self.mouth_creator.up_base_curve = self.up_base_curve
        self.mouth_creator.low_base_curve = self.low_base_curve

        self.up_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorUpOutCurveField", q=True, text=True)
        self.low_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLowOutCurveField", q=True, text=True)
        self.mouth_creator.up_out_curve = self.up_out_curve
        self.mouth_creator.low_out_curve = self.low_out_curve

        self.up_tweak_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorUpTweakSurfaceField", q=True, text=True)
        self.low_tweak_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorLowTweakSurfaceField", q=True, text=True)
        self.mouth_creator.up_tweak_surface = self.up_tweak_surface
        self.mouth_creator.low_tweak_surface = self.low_tweak_surface

        self.mouth_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorMouthSurfaceField", q=True, text=True)
        self.mouth_creator.mouth_surface = self.mouth_surface

        self.mouth_lip_sew_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorMouthLipSewSurfaceField", q=True, text=True)
        self.mouth_creator.mouth_lip_sew_surface = self.mouth_lip_sew_surface

        return

    def proxy_jaw(self):
        self.before_build_mouth()

        if pm.objExists("proxyJawRoot"):
            pm.error(u"代理Jaw已经创建了")
        if self.mouth_creator.proxy_jaw():
            pm.button("xdMouthCreatorAddProxyJawBtn", e=True, en=False)

    def proxy_neck_ear(self):
        self.neck_ear_creator.proxy()

    def proxy_tongue(self):
        self.mouth_creator.proxy_tongue()

    def proxy_cheek(self):
        self.cheek_creator.proxy()

    def mirror_cheek_proxy(self):
        self.cheek_creator.mirror_proxy()

    @staticmethod
    def symmetry_surface():
        u"""对称surface"""
        sel_list = pm.ls(sl=True)
        if len(sel_list) > 1:
            source = sel_list[0]
            for index in range(1, len(sel_list)):
                symmetry_surface(source, sel_list[index])
        else:
            pm.error(u"请选择两个或两个以上的对象")

    def build_neck_head_module(self):
        self.neck_ear_creator.build_module()

    def build_cheek_module(self):
        self.cheek_creator.build_module()

    def build_eye_module(self):
        self.eye_module_init()
        self.eye_creator.init_structure()
        self.eye_creator.build_module()
        return

    def eye_module_init(self):
        self.eye_creator.left_up_master_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpMasterCurveField", q=True, text=True)
        self.eye_creator.left_low_master_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowMasterCurveField", q=True, text=True)
        self.eye_creator.left_up_blink_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpBlinkCurveField", q=True, text=True)
        self.eye_creator.left_low_blink_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowBlinkCurveField", q=True, text=True)
        self.eye_creator.left_up_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpOutCurveField", q=True, text=True)
        self.eye_creator.left_low_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowOutCurveField", q=True, text=True)
        self.eye_creator.left_up_tweak_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpTweakCurveField", q=True, text=True)
        self.eye_creator.left_low_tweak_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowTweakCurveField", q=True, text=True)
        self.eye_creator.left_up_freshy_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpFreshyCurveField", q=True, text=True)
        self.eye_creator.left_low_freshy_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowFreshyCurveField", q=True, text=True)
        self.eye_creator.left_up_shape_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftUpShapeSurfaceField", q=True, text=True)
        self.eye_creator.left_low_shape_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftLowShapeSurfaceField", q=True, text=True)

        self.eye_creator.right_up_master_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpMasterCurveField", q=True, text=True)
        self.eye_creator.right_low_master_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowMasterCurveField", q=True, text=True)
        self.eye_creator.right_up_blink_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpBlinkCurveField", q=True, text=True)
        self.eye_creator.right_low_blink_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowBlinkCurveField", q=True, text=True)
        self.eye_creator.right_up_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpOutCurveField", q=True, text=True)
        self.eye_creator.right_low_out_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowOutCurveField", q=True, text=True)
        self.eye_creator.right_up_tweak_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpTweakCurveField", q=True, text=True)
        self.eye_creator.right_low_tweak_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowTweakCurveField", q=True, text=True)
        self.eye_creator.right_up_freshy_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpFreshyCurveField", q=True, text=True)
        self.eye_creator.right_low_freshy_curve = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowFreshyCurveField", q=True, text=True)
        self.eye_creator.right_up_shape_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorRightUpShapeSurfaceField", q=True, text=True)
        self.eye_creator.right_low_shape_surface = pm.textFieldButtonGrp(
            "xdMouthCreatorRightLowShapeSurfaceField", q=True, text=True)

        self.eye_creator.left_eye_geo = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftEyeGeoField", q=True, text=True)
        self.eye_creator.right_eye_geo = pm.textFieldButtonGrp(
            "xdMouthCreatorRightEyeGeoField", q=True, text=True)
        self.eye_creator.left_eye_proxy = pm.textFieldButtonGrp(
            "xdMouthCreatorLeftEyeProxyField", q=True, text=True)
        self.eye_creator.right_eye_proxy = pm.textFieldButtonGrp(
            "xdMouthCreatorRightEyeProxyField", q=True, text=True)

        return

    def eye_component_in_field(self, field, group=None):
        target = pm.ls(sl=True)[0]
        self.eye_creator.init_structure()
        drag_to_group_and_field(target, field=field, group=group)
        return

    def eye_master_ctrl_field(self, side, field):
        self.eye_creator.init_structure()

        prefix = "{}_{}".format(side, self.eye_module)
        master_ctrl = "{}_Master_Ctrl".format(prefix)
        jnt_or_control_grp(name=master_ctrl, object_type="tours", parent_node="{}_Grp".format(prefix))
        pm.textFieldButtonGrp(field, e=True, text=master_ctrl)

    def build_linkage(self):
        jaw_ctrl = "MD_Mouth_01_Jaw_Ctrl"
        jaw_ctrl_grp = pm.PyNode(jaw_ctrl).getParent()

        pm.parentConstraint(jaw_ctrl, "MD_Tongue_01_Main_Grp", mo=True)
        pm.scaleConstraint(jaw_ctrl, "MD_Tongue_01_Main_Grp", mo=True)

        mouth_master_ctrl_grp = "MD_Mouth_01_Master_Ctrl_Grp"
        constraint = pm.parentConstraint(jaw_ctrl, jaw_ctrl_grp, mouth_master_ctrl_grp, mo=True)

        driver_value = [-1, 0]
        value = [0, 1]
        for index in range(0, len(driver_value)):
            pm.setDrivenKeyframe(
                constraint,
                at="{}W1".format(jaw_ctrl_grp),
                cd="{}.{}".format(jaw_ctrl, "rotateX"),
                dv=driver_value[index],
                value=value[index],
                itt="linear",
                ott="linear",
            )

        for side in ["LF", "RT"]:
            pm.parentConstraint(jaw_ctrl, "{}_Cheek_01_04_Ctrl_Grp".format(side), mo=True)
            pm.PyNode("{}_Cheek_01_04_Ctrl_02_Grp".format(side)).translate.connect(
                pm.PyNode("{}_Cheek_01_04_Ctrl_Jnt_02_Grp".format(side)).translate)
        print("Done!")
        return
