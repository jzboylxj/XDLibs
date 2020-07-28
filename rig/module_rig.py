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

        self.main_tab = pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        child1 = self.tab_body()
        child2 = self.tab_face()

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

    def tab_body(self):
        form_layout = pm.formLayout()
        pm.setParent("..")
        return form_layout

    def tab_face(self):
        layout = self.face_pre_layout()
        return layout

    def face_pre_layout(self):
        layout = pm.columnLayout(adj=1)
        pm.frameLayout(
            label=u"Pre",
            cll=True,
            cl=False,
            bgs=True,
            bgc=[0.2, 0.2, 0.2],
            mw=5, mh=5)

        face_component = ["Mask", "Face"]

        pm.columnLayout(adj=1)
        for component in face_component:
            if component == "Mask":
                pm.text(label=u"Polygons:", al="left")
            elif component == "Face":
                pm.separator(h=7, st="none")
                pm.text(label=u"Objects:", al="left")
            self.text_field_widget(component)
        pm.setParent("..")  # end of pre_form_layout

        pm.separator(h=5, style="in")

        # form_layout = pm.formLayout()
        # rig_type_options = pm.optionMenuGrp(
        #     label=u"Rig-type:", cw2=[52, 300], adj=2)
        # rig_type_options_help = pm.button("?")
        # symmetrical_check_box = pm.checkBox(label=u"Non symmetrical")
        # symmetrical_check_help = pm.button(label="?")
        # game_engine_check_box = pm.checkBox(label=u"Game engine")
        # game_engine_check_help = pm.button(label="?")
        # advanced_check_box = pm.checkBox(label=u"Advanced")
        # advanced_check_help = pm.button(label="?")
        #
        # pm.formLayout(
        #     form_layout,
        #     edit=True,
        #     attachForm=[
        #         (rig_type_options, 'top', 2),
        #         (rig_type_options, 'left', 0),
        #         (rig_type_options_help, 'right', 0),
        #         (symmetrical_check_box, 'left', 0),
        #         (symmetrical_check_help, 'right', 0),
        #         (game_engine_check_help, 'right', 0),
        #         (advanced_check_help, 'right', 0),
        #     ],
        #     attachControl=[
        #         (rig_type_options, 'right', 5, rig_type_options_help),
        #         (symmetrical_check_box, 'top', 9, rig_type_options),
        #         (game_engine_check_box, 'top', 12, symmetrical_check_box),
        #         (advanced_check_box, 'top', 12, game_engine_check_box),
        #         (symmetrical_check_help, 'top', 6, rig_type_options),
        #         (game_engine_check_help, 'top', 2, symmetrical_check_help),
        #         (advanced_check_help, 'top', 2, game_engine_check_help),
        #     ]
        # )
        # pm.setParent("..")  # end of form_layout
        pm.setParent("..")  # end of face_pre_layout
        pm.setParent("..")  # end of layout

        return layout

    def text_field_widget(self, label):
        pm.formLayout("facePreComponent%sLayout" % label)
        pm.textFieldButtonGrp(
            "face%sTextField" % label,
            label=label,
            cw3=[40, 100, 60],
            adj=2,
            bl="    Get    ",
            bc=lambda *args: self.choose_input(
                text_field="face%sTextField" % label))
        pm.popupMenu()
        pm.menuItem(label=u"re-select")
        pm.button(
            "face%sHelp" % label,
            label=u"?")
        pm.formLayout(
            "facePreComponent%sLayout" % label,
            edit=True,
            attachForm=[
                ("face%sTextField" % label, 'top', 2),
                ("face%sTextField" % label, 'left', 5),
                ("face%sHelp" % label, 'top', 2),
                ("face%sHelp" % label, 'right', 5),
            ],
            attachControl=[
                ("face%sTextField" % label, 'right', 5, "face%sHelp" % label),
            ])
        pm.setParent("..")

    def choose_input(self, text_field):
        value = None

        head_joint = "Head_M"
        sel = pm.ls(sl=True)

        if not pm.objExists("FaceFitSkeleton"):
            self.create_face_fit_skeleton()

        if text_field == "faceMaskTextField":
            self.create_face_fit_mask()
        if (text_field == "faceFaceTextField" or
                text_field == "faceAllHeadTextField"):
            for index in range(0, len(sel)):
                if mel.eval(' gmatch %s "*[.]*" ' % sel[index]):
                    pm.error(
                        "Only select Object, not vertices, edges or faces")

        # pm.textFieldButtonGrp(text_field, e=True, text=value)

        return

    def create_face_fit_skeleton(self):
        face_group = pm.createNode("transform", n="FaceGroup")
        common.lock_and_hide_attr(face_group)

        if pm.objExists("|Group"):
            pm.parent(face_group, "|Group")
        if pm.objExists("FaceFitSkeleton"):
            pm.delete("FaceFitSkeleton")

        face_fit_skeleton = pm.createNode(
            "transform", n="FaceFitSkeleton", p=face_group)
        common.lock_and_hide_attr(face_fit_skeleton)

        temp_circle = pm.circle(
            nr=(0, 1, 0), c=(0, 0, 0), sw=360,
            r=0.5, d=3, ut=0, tol=0.000393701, s=8, ch=0)

        pm.rename(temp_circle[0], "TempCircle")
        pm.parent(
            temp_circle[0].getShape().name(),
            "FaceFitSkeleton",
            add=True, s=True)
        pm.delete("TempCircle")
        pm.rename("TempCircleShape", "FaceFitSkeletonShape")
        pm.setAttr("FaceFitSkeletonShape.overrideEnabled", 1)
        pm.setAttr("FaceFitSkeletonShape.overrideColor", 13)
        pm.rotate(
            "FaceFitSkeleton.cv[0:99]",
            0, -90, 0, r=True, p=[0, 0, 0], os=True, fo=True)
        pm.duplicate("FaceFitSkeleton", n="FaceFitSkeletonHeight")
        pm.duplicate("FaceFitSkeleton", n="FaceFitSkeletonCircle")
        pm.duplicate("FaceFitSkeleton", n="FaceFitSkeletonHeightCircle")
        pm.parent("FaceFitSkeletonHeightShape", "FaceFitSkeleton", add=True,
                  s=True)
        pm.parent("FaceFitSkeletonCircleShape", "FaceFitSkeleton", add=True,
                  s=True)
        pm.parent("FaceFitSkeletonHeightCircleShape", "FaceFitSkeleton",
                  add=True, s=True)
        pm.delete(["FaceFitSkeletonHeight",
                   "FaceFitSkeletonCircle",
                   "FaceFitSkeletonHeightCircle"])
        pm.move("FaceFitSkeletonHeightShape.cv[0:99]", 0, 1.0, 0, r=True)
        pm.move("FaceFitSkeletonHeightCircleShape.cv[0:99]", 0, 1.0, 0, r=True)

        return

    def create_face_fit_mask(self):
        # global string $gMainProgressBar;
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
        # float $faceScale;
        # float $bb[];
        # string $tempString[];

        # sel = pm.ls(sl=True)
        # if not mel.eval(' gmatch %s "*.f*" ' % sel[0]):
        #     pm.error(u"没有选择多边形元素，角色脸部的多边形元素必须被选择.")

        sel = pm.ls(sl=True)
        list = [item.name() for item in sel]
        if ".f[" not in list[0]:
            pm.error(u"没有选择多边形元素，角色脸部的多边形元素必须被选择.")

        # pm.progressBar(gMainProgressBar,
        #                edit=True,
        #                st="Storing Mask",
        #                beginProgress=True,
        #                isInterruptable=True,
        #                status='Example Calculation ...',
        #                minValue=0,
        #                maxValue=9)
        # pm.evalDeferred("progressBar -e -ep " + gMainProgressBar)

        # 检查线圈有没有形节点，如果有的话就删除
        # face_fit_skeleton_shapes = pm.listRelatives("FaceFitSkeleton", s=True)
        # if len(face_fit_skeleton_shapes):
        #     pm.delete(face_fit_skeleton_shapes)

        # temp_circle = pm.circle(
        #     nr=(0, 1, 0), c=(0, 0, 0), sw=360,
        #     r=0.5, d=3, ut=0, tol=0.000393701, s=8, ch=0)
        #
        # pm.rename(temp_circle[0], "TempCircle")
        # pm.parent(
        #     temp_circle[0].getShape().name(),
        #     "FaceFitSkeleton",
        #     add=True, s=True)
        # pm.delete("TempCircle")
        # pm.rename("TempCircleShape", "FaceFitSkeletonShape")
        # pm.setAttr("FaceFitSkeletonShape.overrideEnabled", 1)
        # pm.setAttr("FaceFitSkeletonShape.overrideColor", 13)
        # pm.rotate(
        #     "FaceFitSkeleton.cv[0:99]",
        #     0, -90, 0, r=True, p=[0, 0, 0], os=True, fo=True)
        # pm.duplicate("FaceFitSkeleton", n="FaceFitSkeletonHeight")
        # pm.duplicate("FaceFitSkeleton", n="FaceFitSkeletonCircle")
        # pm.duplicate("FaceFitSkeleton", n="FaceFitSkeletonHeightCircle")
        # pm.parent("FaceFitSkeletonHeightShape", "FaceFitSkeleton", add=True,
        #           s=True)
        # pm.parent("FaceFitSkeletonCircleShape", "FaceFitSkeleton", add=True,
        #           s=True)
        # pm.parent("FaceFitSkeletonHeightCircleShape", "FaceFitSkeleton",
        #           add=True, s=True)
        # pm.delete(["FaceFitSkeletonHeight",
        #            "FaceFitSkeletonCircle",
        #            "FaceFitSkeletonHeightCircle"])
        # pm.move("FaceFitSkeletonHeightShape.cv[0:99]", 0, 1.0, 0, r=True)
        # pm.move("FaceFitSkeletonHeightCircleShape.cv[0:99]", 0, 1.0, 0, r=True)

        if len(sel)>0:
            pm.select(sel)
            bb = pm.xform(q=True, ws=True, bb=True)
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
