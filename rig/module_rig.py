#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/20 11:03
# @Author  : Li XiaoJun
# @Site    :
# @File    : module_rig.py

from pymel import core as pm
import maya.mel as mel

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
        self.face_pre_layout()

        pm.setParent("..")
        return scroll_layout

    def face_pre_layout(self):
        face_pre_layout = pm.frameLayout(
            label=u"Pre",
            cll=True,
            cl=False,
            bgs=True,
            mw=5, mh=5)

        pm.text(label=u"Polygons:", al="left")
        pm.rowColumnLayout(nc=3)
        pm.button(
            label="Mask",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceMaskTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceMaskTextField", w=120, en=False)
        pm.button("?")
        pm.setParent("..")

        pm.text(label=u"Objects:", al="left")
        pm.rowColumnLayout(nc=3)
        pm.button(
            label="Face",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceFaceTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceFaceTextField", w=120, en=False)
        pm.button("?")
        pm.setParent("..")

        pm.rowColumnLayout(nc=3)
        pm.button(
            label="All Head",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceAllHeadTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceAllHeadTextField", w=120, en=False)
        pm.button("?")
        pm.setParent("..")

        pm.rowColumnLayout(nc=3)
        pm.button(
            label="Right Eye",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceRightEyeTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceRightEyeTextField", w=120, en=False)
        pm.button("?")
        pm.setParent("..")

        pm.rowColumnLayout(nc=3)
        pm.button(
            label="Left Eye",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceLeftEyeTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceLeftEyeTextField", w=120, en=False)
        pm.button("?")
        pm.setParent("..")

        pm.text(label=u"Optional:", al="left")
        pm.rowColumnLayout(nc=3)
        pm.button(
            label="Upper Teeth",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceUpperTeethTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceUpperTeethTextField", w=120, en=False)
        pm.button("?")
        pm.setParent("..")

        pm.rowColumnLayout(nc=3)
        pm.button(
            label="Lower Teeth",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceLowerTeethTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceLowerTeethTextField", w=120, en=False)
        pm.button("?")
        pm.setParent("..")

        pm.rowColumnLayout(nc=3)
        pm.button(
            label="Tongue",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceTongueTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceTongueTextField", w=120, en=False)
        pm.button("?")
        pm.setParent("..")

        pm.rowColumnLayout(nc=3)
        pm.button(
            label="Eyebrow",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceEyebrowTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceEyebrowTextField", w=120, en=False)
        pm.button("?")
        pm.setParent("..")

        pm.rowColumnLayout(nc=3)
        pm.button(
            label="Eyelash",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceEyelashTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceEyelashTextField", w=120, en=False)
        pm.button("?")
        pm.setParent("..")

        pm.rowColumnLayout(nc=3)
        pm.button(
            label="Extras",
            w=120,
            c=lambda *args: self.choose_input(
                text_field="xdFaceExtrasTextField"))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.textField("xdFaceExtrasTextField", w=120, en=False)
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
        pm.setParent("..")

        return face_pre_layout

    def choose_input(self, text_field):
        head_joint = "Head_M"
        sel = pm.ls(sl=True)

        print "text_field: %s" % text_field

        if not pm.objExists("FaceFitSkeleton"):
            self.create_face_fit_skeleton()

        if text_field == "xdFaceMaskTextField":
            print "Clicked Mask Button!"
            # self.create_face_fit_mask()
        if (text_field == "xdFaceFaceTextField" or
                text_field == "xdFaceAllHeadTextField"):
            for index in range(0, len(sel)):
                if mel.eval(' gmatch %s "*[.]*" ' % sel[index]):
                    pm.error("Only select Object, not vertices, edges or faces")

        return

    def create_face_fit_skeleton(self):
        face_group = pm.createNode("transform", n="FaceGroup")
        common.lock_and_hide_attr(face_group)

        if pm.objExists("|Group"):
            pm.parent(face_group, "|Group")
        if pm.objExists("FaceFitSkeleton"):
            pm.delete("FaceFitSkeleton")

        face_fit_skeleton = pm.createNode("transform",
                                          n="FaceFitSkeleton", p=face_group)
        common.lock_and_hide_attr(face_fit_skeleton)

        return

    def create_face_fit_mask(self):
        print "mask"
        # global string $gMainProgressBar;
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
        # float $faceScale;
        # float $bb[];
        # string $tempString[];
        sel = pm.ls(sl=True)
        if not mel.eval(' gmatch %s "*.f*" ' % sel[0]):
            pm.error(u"没有选择多边形元素，角色脸部的多边形元素必须被选择.")

        # progressBar -e -st "Storing Mask" -bp -ii 1 -min 0 -max 9 $gMainProgressBar;
        pm.progressBar(gMainProgressBar,
                       edit=True,
                       beginProgress=True,
                       isInterruptable=True,
                       status='Example Calculation ...',
                       maxValue=5000)
        pm.evalDeferred("pm.progressBar(gMainProgressBar, e=True, ep=True)")
        # evalDeferred ("progressBar -e -ep "+$gMainProgressBar);

        # $tempString=`listRelatives -s FaceFitSkeleton`;
        # if (size($tempString))
        #     delete $tempString;

        # $tempString=`circle -c 0 0 0 -nr 0 1 0 -sw 360 -r 0.5 -d 3 -ut 0 -tol 0.000393701 -s 8 -ch 0`;
        # rename $tempString[0] TempCircle;
        # parent -add -s TempCircleShape FaceFitSkeleton;
        # delete TempCircle;
        # rename TempCircleShape FaceFitSkeletonShape;
        # setAttr FaceFitSkeletonShape.overrideEnabled 1;
        # setAttr FaceFitSkeletonShape.overrideColor 13;
        # //scale -r -p 0 0 0 0.5 0.5 0.5 FaceFitSkeleton.cv[0:99];
        # rotate -r -p 0 0 0 -os 0 -90 0 FaceFitSkeleton.cv[0:99];
        # duplicate -n FaceFitSkeletonHeight FaceFitSkeleton;
        # duplicate -n FaceFitSkeletonCircle FaceFitSkeleton;
        # duplicate -n FaceFitSkeletonHeightCircle FaceFitSkeleton;
        # parent -add -s FaceFitSkeletonHeightShape FaceFitSkeleton;
        # parent -add -s FaceFitSkeletonCircleShape FaceFitSkeleton;
        # parent -add -s FaceFitSkeletonHeightCircleShape FaceFitSkeleton;
        # delete FaceFitSkeletonHeight FaceFitSkeletonCircle FaceFitSkeletonHeightCircle;
        # move -r 0 1.0 0 FaceFitSkeletonHeightShape.cv[0:99]  FaceFitSkeletonHeightCircleShape.cv[0:99];

        # if ($sel[0]!="")
        #     {
        #     select $sel;
        #     $bb=`xform -q -ws -bb`;
        #     $tempString=`listRelatives -s FaceFitSkeleton`;
        #     for ($i=0;$i<size($tempString);$i++)
        #         {
        #         scale -r -p 0 0 0 ($bb[3]-$bb[0]) ($bb[4]-$bb[1]) ($bb[5]-$bb[2]) ($tempString[$i]+".cv[0:99]");
        #         move -r -os -wd 0 $bb[1] (($bb[2]+$bb[5])/2.0) ($tempString[$i]+".cv[0:99]");
        #         }
        #     //FaceFitSkeleton.faceScale
        #     $faceScale=$bb[4]-$bb[1];
        #     if (!`attributeExists faceScale FaceFitSkeleton`)
        #         addAttr -k 0 -ln faceScale -at double FaceFitSkeleton;
        #     setAttr FaceFitSkeleton.faceScale $faceScale;
        #     }

        # print "// Mask stored.\n";
        return
