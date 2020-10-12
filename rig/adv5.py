#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/8/27 20:02
# @Author  : Li XiaoJun
# @Site    :
# @File    : adv5.py
# @Software: PyCharm

from imp import reload
from pymel import core as pm
from animation import common

reload(common)


class AdvancedSkeleton(common.Singleton):
    def __init__(self):
        super(AdvancedSkeleton, self).__init__()

        # 当前TabLayout选择状态的选择索引
        self.current_tab_index = 2

        self.show()
        self.initialize()

    def show(self):
        if pm.window("pyAdvancedSkeleton5", ex=True):
            pm.deleteUI("pyAdvancedSkeleton5")
        pm.window(
            "pyAdvancedSkeleton5",
            t=u"AdvancedSkeleton5",
            mb=True,
            cc=lambda *args: self._closed_window_cmd())
        self.menu_bar()

        self.main_layout()

        pm.showWindow("pyAdvancedSkeleton5")

    def menu_bar(self):
        pm.menu(label="Pose", tearOff=False)
        pm.menu(label="Tools", tearOff=False)
        pm.menu(label="Display", tearOff=False)
        pm.menu(label="Optimize", tearOff=False)
        pm.menu(label="Publish", tearOff=False)
        pm.menu(label="Export", tearOff=False)
        pm.menu(label="About", tearOff=False)

        return

    def main_layout(self):
        main_layout = pm.formLayout()
        module_tab_widget = pm.tabLayout(
            innerMarginWidth=5,
            innerMarginHeight=5,
            p=main_layout)
        pre_tab = self.pre_tab(parent=module_tab_widget)
        face_tab = self.face_tab(parent=module_tab_widget)
        # add_controls_tab = self.tab_add_controls(parent=tool_tab_bar)
        pm.tabLayout(
            module_tab_widget,
            edit=True,
            tabLabel=(
                (pre_tab, u"Pre"),
                (face_tab, u"Face"),
                # (add_controls_tab, u"Add Controls"),
            ),
            sti=self.current_tab_index)
        pm.formLayout(
            main_layout, edit=True,
            attachForm=[
                (module_tab_widget, "top", 0),
                (module_tab_widget, "left", 0),
                (module_tab_widget, "right", 0),
                (module_tab_widget, "bottom", 0),
            ],
            attachControl=[
                # (data_form, 'top', 2, tool_tab_bar),
            ])

        return main_layout

    def initialize(self):
        pass

    def _closed_window_cmd(self):
        pass

    def pre_tab(self, parent):
        frame = pm.frameLayout(lv=False, mw=10, mh=10, p=parent)
        pm.columnLayout(adj=1, rs=2, p=frame)
        pm.text(
            label='''This \"Preparation\" section is optional, \nbut recommended for clean file and workflow''',
            al='left', fn="smallBoldLabelFont")
        pm.separator(h=10, style="none")
        pm.text(label="Clean:", al='left')
        pm.text(
            label='''Group your model, so that you have 1 top node.\nAnd name this group \"geo\"\nThen use the model-cleaner tool:''',
            al='left')
        pm.button(label=u"Model Clean")
        pm.separator(h=10, style="none")
        pm.text(label="Then save your cleaned model.", al='left')
        pm.text(label="Also, you can check the symmetry:", al='left')
        pm.button(label=u"Model Check")
        pm.separator(h=10, style="none")
        pm.text(label="Create rig file:", al='left')
        pm.button(label=u"New Scene")
        pm.text(label="Reference-in the model:", al='left')
        pm.button(label=u"Reference")
        pm.setParent("..")
        pm.setParent(frame)
        return frame

    def face_tab(self, parent):
        layout = pm.formLayout(p=parent)
        scroll_widget = pm.scrollLayout(cr=True, vsb=True)

        self.face_init_frame(parent=scroll_widget)
        self.face_fit_frame(parent=scroll_widget)

        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (scroll_widget, "top", 0),
                (scroll_widget, "left", 0),
                (scroll_widget, "right", 0),
                (scroll_widget, "bottom", 0),
            ],
            attachControl=[
                # (data_form, 'top', 2, tool_tab_bar),
            ])

        pm.setParent(layout)
        return layout

    def face_init_frame(self, parent):
        cw3 = [80, 120, 100]
        init_widget = pm.frameLayout(
            label="Init", cl=False, cll=True, mw=5, mh=5, parent=parent)
        pm.text(label="Polygons:")
        pm.textFieldButtonGrp("xdFaceMaskTextField",
                              label="Mask",
                              bl=" Get ",
                              cw3=cw3,
                              adj=2,
                              bc=lambda *args: self.xdChooseInput(
                                  textField="xdFaceMaskTextField"))
        pm.text(label="Objects:")
        pm.textFieldButtonGrp(
            label="Face", bl=" Get ", cw3=cw3, adj=2)
        pm.textFieldButtonGrp(
            label="All Head", bl=" Get ", cw3=cw3, adj=2)
        pm.textFieldButtonGrp(
            label="Right Eye", bl=" Get ", cw3=cw3, adj=2)
        pm.textFieldButtonGrp(
            label="Left Eye", bl=" Get ", cw3=cw3, adj=2)
        pm.text(label="Optional:")
        pm.textFieldButtonGrp(
            label="Upper Teeth", bl=" Get ", cw3=cw3, adj=2)
        pm.textFieldButtonGrp(
            label="Lower Teeth", bl=" Get ", cw3=cw3, adj=2)
        pm.textFieldButtonGrp(
            label="Tongue", bl=" Get ", cw3=cw3, adj=2)
        pm.textFieldButtonGrp(
            label="Eyebrow", bl=" Get ", cw3=cw3, adj=2)
        pm.textFieldButtonGrp(
            label="Eyelash", bl=" Get ", cw3=cw3, adj=2)
        pm.textFieldButtonGrp(
            label="Extras", bl=" Get ", cw3=cw3, adj=2)
        pm.separator(style="in", h=5)
        pm.optionMenuGrp(label="Rig-type", cw2=[50, 120], cat=[2, "left", 29])
        pm.menuItem(label="Joints")
        pm.menuItem(label="BlendShapes")
        pm.menuItem(label="Mixed")
        pm.checkBox(label="Non symmetrical")
        pm.checkBox(label="Game engine")
        pm.checkBox(label="Advanced")
        pm.setParent(init_widget)  # end of frameLayout

        return init_widget

    def face_fit_frame(self, parent):
        fit_widget = pm.frameLayout(
            label="Fit", cl=True, cll=True, mw=5, mh=5, parent=parent)
        pm.setParent(fit_widget)
        return fit_widget

    def xdChooseInput(self, textField):
        confirmed = 0
        connectedToDeformer = 0
        tempFloat = []
        pos1 = []
        pos2 = []
        headJoint = "Head_M"
        # Default name for auto-created HeadJoint, to match AdvSkel headJoint
        skinCluster = ""
        txt = ""
        dialog = ""
        m = ""
        ffd = ""
        sel = pm.ls(sl=1)
        restoreSel = sel
        tempString = []
        tempString2 = []
        tempString3 = []
        selGeos = []
        self.xdFaceUpgradeFaceFitCheck()

        if not pm.objExists('FaceFitSkeleton'):
            self.xdCreateFaceFitSkeleton()

        if textField == "xdFaceMaskTextField":
            self.asCreateFaceFitMask()

        if textField == "asFaceFaceTextField" or textField == "asFaceAllHeadTextField":
            for i in range(0, len(sel)):
                if pm.mel.gmatch(sel[i], "*[.]*"):
                    pm.error(
                        "Only select Object, not vertices, edges or faces")

        for i in range(0, len(sel)):
            if pm.mel.gmatch(sel[i], "*|*"):
                pm.select(sel[i])
                pm.error("Selected object: \"" + sel[
                    i] + "\" does not have a unique name, rename to a unique name.")

        if pm.mel.gmatch(textField, "*Joint*"):
            if pm.objectType(sel[0]) != "joint":
                pm.error("A joint must be selected")

            txt = sel[0]

        else:
            pm.select(cl=1)
            # Include children
            children = []
            for i in range(0, len(sel)):
                if not pm.mel.gmatch(sel[i], "*[.]*"):
                    pm.select(
                        pm.listRelatives(sel[i], type='transform', ad=1, f=1),
                        add=1)

            addedSel = pm.ls(sl=1)
            sel = sel + addedSel
            sel = pm.mel.stringArrayRemoveDuplicates(sel)
            # Not include non-mesh || non-nurbs (unless choose joint)
            shapes = []
            for i in range(0, len(sel)):
                if pm.mel.gmatch(sel[i], "*[.]*"):
                    selGeos = sel
                else:
                    nodeType = ""
                    shapes = pm.listRelatives(sel[i], ni=1, s=1, f=1)
                    if len(shapes):
                        nodeType = pm.nodeType(shapes[0])
                    if nodeType == "nurbsSurface" or nodeType == "mesh":
                        selGeos.append(sel[i])
            txt = selGeos[0]

        pm.select(restoreSel)
        if len(selGeos) > 1:
            for i in range(1, len(selGeos)):
                txt += " " + selGeos[i]
            # Everything must have skinCluster
        for i in range(0, len(selGeos)):
            if (textField == "asFaceHeadJointTextField"
                    or textField == "asFaceMaskTextField"):
                continue
            if not pm.objExists('FaceFitSkeletonShape'):
                pm.pm.mel.error("Start with choosing Mask")
            tempString = pm.listHistory(selGeos[i])
            skinCluster = ""
            for y in range(0, len(tempString)):
                if pm.objectType(tempString[y]) == "skinCluster":
                    skinCluster = tempString[y]
            if skinCluster == "":
                if dialog != "Create New SkinCluster":
                    dialog = str(pm.confirmDialog(
                        db="Create New SkinCluster",
                        b=["Create New SkinCluster", "Cancel"],
                        m=("No SkinCluster found on this geometry:\n" +
                           selGeos[i]),
                        t="Confirm",
                        ds="Cancel"))
                if dialog != "Create New SkinCluster":
                    return
                pm.select(cl=1)
                if not pm.objExists(headJoint):
                    pm.joint(n=headJoint)
                    if pm.objExists('FaceFitSkeleton'):
                        pos1 = pm.xform(
                            'FaceFitSkeletonShape.cv[0]', q=1, ws=1, t=1)
                        pos2 = pm.xform(
                            'FaceFitSkeletonHeightShape.cv[0]', q=1, ws=1, t=1)
                        pm.xform(
                            headJoint, ws=1,
                            t=(0, (pos1[1] + ((pos2[1] - pos1[1]) / 3.0)), 0))
                pm.textField('asFaceHeadJointTextField', e=1, tx=headJoint)
                pm.select(selGeos[i], headJoint)
                tempString = pm.mel.newSkinCluster(
                    "-toSelectedBones -mi 1 -dr 4 -rui false")
                skinCluster = tempString[0]
                pm.select(selGeos[i])

            if textField == "asFaceFaceTextField":
                pm.textField('asFaceSkinClusterTextField', e=1, tx=skinCluster)
                pm.textField('asFaceHeadJointTextField', e=1, tx=headJoint)

        if pm.mel.gmatch(textField, "asFace*EyeTextField"):
            # If there is a Lattice on the Eye, this might be for non-spherical eyes
            for i in range(0, len(selGeos)):
                tempString = pm.listHistory(selGeos[i])
                skinCluster = ""
                for y in range(0, len(tempString)):
                    if pm.objectType(tempString[y]) == "ffd":
                        ffd = tempString[y]
                    if pm.objectType(tempString[y]) == "skinCluster":
                        skinCluster = tempString[y]
                if ffd != "":
                    if dialog != "Detected Lattice":
                        dialog = str(
                            pm.confirmDialog(
                                db="Yes",
                                b=["Yes", "No"],
                                m=(
                                    "Lattice detected.\nUse this Lattice for non-spherical eyes ?"),
                                t="Confirm",
                                ds="No"))

                    if dialog == "Yes":
                        tempString = pm.listAttr(ffd, ud=1)
                        for y in range(0, len(tempString)):
                            if pm.mel.gmatch(
                                    tempString[y], "asNonSphereLattice_*"):
                                pm.deleteAttr(ffd + "." + tempString[y])
                        if textField == "asFaceRightEyeTextField":
                            pm.addAttr(
                                ffd,
                                ln='asNonSphereLattice_R',
                                dv=True,
                                k=0, at='bool')
                        if textField == "asFaceLeftEyeTextField":
                            pm.addAttr(
                                ffd,
                                ln='asNonSphereLattice_L',
                                dv=True,
                                k=0, at='bool')
                        pm.reorderDeformers(ffd, skinCluster, selGeos[i])
                        if pm.getAttr(ffd + ".outsideLattice") != 1:
                            pm.setAttr((ffd + ".outsideLattice"), 1)

        pm.textField(textField, e=1, tx=txt)
        # optionVar -sv $textField $txt;
        pm.mel.asFaceUpdateInfo(0)

    def xdFaceUpgradeFaceFitCheck(self):
        oldVersion = 0.0
        faceScale = 0.0
        geometry = ""
        allFaceGeoString = ""
        rightEye = ""
        leftEye = ""
        upperTeeth = ""
        lowerTeeth = ""
        tongue = ""
        headJoint = ""
        skinCluster = ""
        rightPupil = ""
        rightIris = ""
        dialog = ""
        tempString = []
        if pm.objExists('FaceGroup'):
            if pm.attributeQuery('version', node='FaceGroup'):
                oldVersion = float(pm.getAttr('FaceGroup.version'))
        elif pm.objExists('FaceFitSkeleton'):
            if pm.getAttr('FaceFitSkeleton.ty') > 1:
                oldVersion = 5.0
            # could be old Face-Fit, never built, so no version info stored
            else:
                return
        else:
            return

        if oldVersion > 5.743:
            return

        dialog = str(pm.confirmDialog(
            db="Yes", b=["Yes", "Cancel"],
            m="FaceFitSkeleton is from a older version.\nCreate New FaceFitSkeleton ?",
            t="Confirm",
            ds="Cancel"))
        if dialog != "Yes":
            pm.error(
                "FaceFitSkeleton is from a older version. Delete this, and create a new FaceFitSkeleton.")

        if pm.objExists('FaceFitCheekRaiser'):
            pm.delete('FaceFitCheekRaiser')

        if pm.objExists('FaceFitSmileBulge'):
            pm.delete('FaceFitSmileBulge')

        if pm.objExists('FaceFitFrownBulge'):
            pm.delete('FaceFitFrownBulge')

        if pm.objExists('FaceMotionSystem'):
            if not pm.getAttr('FaceFitSkeleton.v'):
                pm.mel.asToggleFitFace()

            pm.mel.asDeleteAdvancedFace()

        geometry = str(pm.getAttr('FaceFitSkeleton.Geometry'))
        # changed in 5.743
        allFaceGeoString = str(pm.getAttr('FaceFitSkeleton.AllFaceGeo'))
        # changed in 5.743
        rightEye = str(pm.getAttr('FaceFitSkeleton.Eye_R'))
        # changed in 5.743
        leftEye = str(pm.getAttr('FaceFitSkeleton.Eye_L'))
        # changed in 5.743
        upperTeeth = str(pm.getAttr('FaceFitSkeleton.UpperTeeth'))
        lowerTeeth = str(pm.getAttr('FaceFitSkeleton.LowerTeeth'))
        tongue = str(pm.getAttr('FaceFitSkeleton.Tongue'))
        headJoint = str(pm.getAttr('FaceFitSkeleton.HeadJoint'))
        skinCluster = str(pm.getAttr('FaceFitSkeleton.SkinCluster'))
        faceScale = float(pm.getAttr('FaceFitSkeleton.sy') * 1.5)
        if pm.mel.attributeExists('Pupil_R', 'FaceFitSkeleton'):
            rightPupil = str(pm.getAttr('FaceFitSkeleton.Pupil_R'))

        if pm.mel.attributeExists('Pupil_R', 'FaceFitSkeleton'):
            rightIris = str(pm.getAttr('FaceFitSkeleton.Iris_R'))
        # OldFaceFitSkeletonHolder

        pm.createNode('transform', n='OldFaceFitSkeletonHolder')
        tempString = pm.listRelatives('FaceFitSkeleton', c=1, type='transform')
        for i in range(0, len(tempString)):
            pm.parent(tempString[i], 'OldFaceFitSkeletonHolder')
            # turn On .inheritsTransform
            tempString2 = pm.listRelatives(tempString[i], c=1,
                                           type='transform')
            for y in range(0, len(tempString2)):
                pm.mel.asLockAttr(tempString2[y], 0, 0, 0, 0)

            pm.parent(tempString2, w=1)
            for y in range(0, len(tempString2)):
                pm.setAttr((str(tempString2[y]) + ".inheritsTransform"),
                           1)

            pm.xform(tempString[i], s=(1, 1, 1), ro=(0, 0, 0), os=1,
                     t=(0, 0, 0))
            pm.parent(tempString2, tempString[i])

        pm.delete('FaceGroup')
        pm.select(geometry)
        pm.mel.xdChooseInput('asFaceFaceTextField')
        pm.setAttr('FaceFitSkeleton.Face', geometry, type="string")
        pm.setAttr('FaceFitSkeleton.AllHead', allFaceGeoString, type="string")
        pm.setAttr('FaceFitSkeleton.RightEye', rightEye, type="string")
        pm.setAttr('FaceFitSkeleton.LeftEye', leftEye, type="string")
        pm.setAttr('FaceFitSkeleton.UpperTeeth', upperTeeth, type="string")
        pm.setAttr('FaceFitSkeleton.LowerTeeth', lowerTeeth, type="string")
        pm.setAttr('FaceFitSkeleton.HeadJoint', headJoint, type="string")
        pm.setAttr('FaceFitSkeleton.SkinCluster', skinCluster, type="string")
        # temporarily use old version scale
        pm.addAttr('FaceFitSkeleton', ln='faceScale', dv=faceScale, k=0,
                   at='double')
        if rightPupil != "":
            if not pm.catch(lambda: pm.mel.eval('select')):
                pm.mel.asCreateFaceFit('Pupil', "", 0, 0, 0, "asRedSG")

        if rightIris != "":
            if not pm.catch(lambda: pm.mel.eval('select')):
                pm.mel.asCreateFaceFit('Iris', "", 0, 0, 0, "asGreenSG")

        pm.deleteAttr('FaceFitSkeleton.faceScale')
        tempString = pm.listRelatives('OldFaceFitSkeletonHolder', c=1,
                                      type='transform')
        for i in range(0, len(tempString)):
            pm.parent(tempString[i], 'FaceFitSkeleton')

        pm.delete('OldFaceFitSkeletonHolder')
        tempString = pm.listRelatives('FaceFitSkeleton', type='transform',
                                      ad=1)
        for i in range(0, len(tempString)):
            if pm.mel.gmatch(tempString[i], "*EyeBrowMiddle*"):
                pm.rename(tempString[i],
                          tempString[i].replace("EyeBrowMiddle",
                                                "EyeBrowCenter"))

        pm.mel.asFaceUpdateInfo(1)
        pm.error(
            "FaceFitSkeleton updated.\nNext complete the \"Pre\" and \"Fit\" section, before building the FaceSetup.\n")

    def xdCreateFaceFitSkeleton(self):
        bb = []
        sel = pm.ls(sl=1)
        tempString = []
        # asFitModeEnsureShaders;
        # if (`objExists FaceGroup`)
        #  delete FaceGroup;
        pm.createNode('transform', n='FaceGroup')
        # setAttr -l 1 FaceGroup.inheritsTransform 0;
        asLockAttr('FaceGroup', 1, 1, 1, 0)
        if pm.objExists("|Group"):
            pm.parent('FaceGroup', "|Group")

        if pm.objExists('FaceFitSkeleton'):
            pm.delete('FaceFitSkeleton')

        pm.createNode('transform', p='FaceGroup', n='FaceFitSkeleton')
        asLockAttr('FaceFitSkeleton', 1, 1, 1, 0)
        # self.asUpdateButtonEnables()
        # self.asFaceUpdateInfo(1)
        pm.select(sel)

    def asUpdateButtonEnables(self):
        if not pm.columnLayout('asColumnLayout', q=1, ex=1):
            return

        gameEngine = 0
        rigTypeInt = 0
        displayPoleVector = 0
        displayJointOrient = 0
        displayJointAxis = 0
        lockCenterJoints = 0
        hasBodySetup = int(pm.objExists("Group"))
        hasFaceSetup = int(pm.objExists('FaceMotionSystem'))
        hasVisualizers = int(pm.objExists('FitSkeletonVisualizers'))
        hasGeometryVisualizers = int(
            pm.objExists('FitSkeletonVisualizers') and pm.objExists('Aims'))
        showDelteAdvButton = 0
        showDelteAdvFaceButton = 0
        if hasBodySetup and pm.getAttr('FitSkeleton.v'):
            showDelteAdvButton = 1

        if hasFaceSetup and pm.getAttr('FaceFitSkeleton.v'):
            showDelteAdvFaceButton = 1

        buildLabel = ""
        skinLayerButtons = []
        if pm.mel.attributeExists('visPoleVector', 'FitSkeleton'):
            displayPoleVector = int(pm.getAttr('FitSkeleton.visPoleVector'))

        if pm.mel.attributeExists('visJointOrient', 'FitSkeleton'):
            displayJointOrient = int(pm.getAttr('FitSkeleton.visJointOrient'))

        if pm.mel.attributeExists('visJointAxis', 'FitSkeleton'):
            displayJointAxis = int(pm.getAttr('FitSkeleton.visJointAxis'))

        if pm.mel.attributeExists('lockCenterJoints', 'FitSkeleton'):
            lockCenterJoints = int(pm.getAttr('FitSkeleton.lockCenterJoints'))
        # Body

        pm.checkBox('asVisGeo', e=1, v=hasGeometryVisualizers)
        pm.optionMenu('asVisGeoType', en=hasVisualizers, e=1)
        pm.floatSliderGrp('asVisGap', en=hasVisualizers, e=1)
        pm.checkBox('asVisPoleVector', e=1, v=displayPoleVector)
        pm.checkBox('asVisJointOrient', e=1, v=displayJointOrient)
        pm.checkBox('asVisJointAxis', e=1, v=displayJointAxis)
        pm.checkBox('asLockCenterJoints', e=1, v=lockCenterJoints)
        pm.button('asDelteAdvButton', m=showDelteAdvButton, e=1)
        pm.checkBox('asKeepAllCheckBox', m=hasBodySetup, e=1)
        if not hasBodySetup:
            pm.columnLayout('asBodyKeepColumnLayout', m=0, e=1)

        pm.button('asToggleFitSkeletonButton', m=hasBodySetup, e=1)
        buildLabel = "Build AdvancedSkeleton"
        if hasBodySetup:
            buildLabel = "ReBuild AdvancedSkeleton"

        pm.button('asBuildAdvancedSkeletonButton', e=1, l=buildLabel)
        # Face (Face-Fit section done in "asFaceUpdateInfo")
        pm.button('asDelteAdvFaceButton', m=showDelteAdvFaceButton, e=1)
        pm.checkBox('asFaceKeepAllCheckBox', m=hasFaceSetup, e=1)
        if not hasFaceSetup:
            pm.columnLayout('asFaceKeepColumnLayout', m=0, e=1)

        pm.button('asToggleFitFaceButton', m=hasFaceSetup, e=1)
        buildLabel = "Build AdvancedFace"
        if hasFaceSetup:
            buildLabel = "ReBuild AdvancedFace"

        pm.button('asBuildAdvancedFaceButton', m=1, e=1, l=buildLabel)
        if pm.objExists('FaceBuildInProgress'):
            pm.checkBox('asFaceKeepAllCheckBox', m=0, e=1)
            pm.columnLayout('asFaceKeepColumnLayout', m=0, e=1)
            pm.button('asBuildAdvancedFaceButton', m=0, e=1)
            pm.button('asDelteAdvFaceButton', m=0, e=1)

        tempString = pm.ls("asDSEdit_*", type='animCurve')
        # Pose
        if len(tempString):
            pm.rowLayout('asDsEditApplyCancelRowLayout', en=1, e=1)

        if pm.mel.attributeExists('GameEngine', 'FaceFitSkeleton'):
            gameEngine = int(pm.getAttr('FaceFitSkeleton.GameEngine'))

        pm.frameLayout('asFaceDeltaMushFrameLayout', en=(not gameEngine), e=1)
        pm.frameLayout('asFaceSquashFrameLayout', en=(not gameEngine), e=1)
        pm.frameLayout('asFaceCustomControlsFrameLayout', en=(not gameEngine),
                       e=1)
        if pm.mel.attributeExists('RigType', 'FaceFitSkeleton'):
            rigTypeInt = int(pm.getAttr('FaceFitSkeleton.RigType'))

        pm.frameLayout('asFaceTweaksFrameLayout', en=(not rigTypeInt), e=1)
        pm.text('asBodyText', m=hasFaceSetup, e=1)
        pm.text('asFaceText', m=hasFaceSetup, e=1)
        pm.button('asGoToBuildPoseFaceButton', m=hasFaceSetup, e=1)

    def asFaceUpdateInfo(self, read):
        """info between UI and FitSkeleton"""

        if not pm.columnLayout('asColumnLayout', q=1, ex=1):
            return

        vtxsFromLipToNose = 3
        # int $vtxsFromLipCornerToNoseCorner=6;
        stepBuild = 0
        nextStep = 0
        headerEn = 0
        bodyEn = 0
        m = 0
        nonSymFace = 0
        leftFaceFitting = 0
        inputNr = 0
        value = 0
        disableSteps = []
        text = ""
        obj = ""
        fitType = ""
        savedFitType = ""
        leftSuffix = ""
        parent = ""
        stepBuildText = ""
        type = ""
        ctrl = ""
        optionEnums = ""
        valueAsString = ""
        avaiableBuiltTypes = []
        tempString = []
        tempString2 = []
        tempString3 = []
        inputs = []
        inputTypes = []
        ctrls = []
        # 3-level recursive searching layots for textFields,etc ($ctrls)
        tempString = pm.layout('asFacePreColumnLayout', q=1, ca=1)
        for a in range(0, len(tempString)):
            if not pm.layout(tempString[a], q=1, ex=1):
                ctrls.append(tempString[a])
                continue

            tempString2 = pm.layout(tempString[a], q=1, ca=1)
            for b in range(0, len(tempString2)):
                if not pm.layout(tempString2[b], q=1, ex=1):
                    ctrls.append(tempString2[b])
                    continue

                tempString3 = pm.layout(tempString2[b], q=1, ca=1)
                for c in range(0, len(tempString3)):
                    if not pm.layout(tempString3[c], q=1, ex=1):
                        ctrls.append(tempString3[c])
                        continue

        for i in range(0, len(ctrls)):
            if pm.mel.gmatch(ctrls[i], "*TextField"):
                type = "TextField"

            if pm.mel.gmatch(ctrls[i], "*CheckBox"):
                type = "CheckBox"

            if pm.mel.gmatch(ctrls[i], "*OptionMenu"):
                type = "OptionMenu"

            if pm.mel.gmatch(ctrls[i], ("asFace*" + type)):
                tempString[0] = ctrls[i].replace("asFace", "")
                tempString[0] = tempString[0].replace(type, "")
                inputs[inputNr] = tempString[0]
                inputTypes[inputNr] = type
                inputNr += 1

        if pm.mel.attributeExists('NonSym', 'FaceFitSkeleton'):
            if pm.getAttr('FaceFitSkeleton.NonSym', type=1) == "string":
                pm.deleteAttr('FaceFitSkeleton.NonSym')
            # backwards compability

        if read:
            if pm.mel.attributeExists('NonSym', 'FaceFitSkeleton'):
                if pm.getAttr('FaceFitSkeleton.NonSym'):
                    nonSymFace = 1

                if pm.getAttr('FaceFitSkeleton.NonSymSide') == "Left":
                    leftSuffix = "Left"
                    leftFaceFitting = 1

            pm.columnLayout('asFaceNonSymColumnLayout', m=nonSymFace, e=1)
            if nonSymFace:
                if leftFaceFitting:
                    pm.frameLayout('asFaceFitFrameLayout', e=1,
                                   l=(" Fit                      (Left)"))
                else:
                    pm.frameLayout('asFaceFitFrameLayout', e=1,
                                   l=(" Fit                      (Right)"))

            else:
                pm.frameLayout('asFaceFitFrameLayout', e=1, l=" Fit")

        for i in range(0, len(inputs)):
            ctrl = "asFace" + inputs[i] + inputTypes[i]
            # print ($i+" : "+$inputs[$i]+" : "+$inputTypes[$i]+"\n");
            if not pm.control(ctrl, q=1, ex=1):
                continue

            if read:
                text = ""
                value = 0
                if inputTypes[i] == "TextField":
                    if pm.mel.attributeExists(inputs[i], 'FaceFitSkeleton'):
                        text = str(pm.getAttr("FaceFitSkeleton." + inputs[i]))

                    pm.textField(ctrl, e=1, tx=text)

                if inputTypes[i] == "CheckBox":
                    if pm.mel.attributeExists(inputs[i], 'FaceFitSkeleton'):
                        value = int(pm.getAttr("FaceFitSkeleton." + inputs[i]))

                    pm.checkBox(ctrl, e=1, v=value)

                if inputTypes[i] == "OptionMenu":
                    pm.optionMenu(ctrl, e=1, sl=1)
                    # default to first option
                    if pm.mel.attributeExists(inputs[i], 'FaceFitSkeleton'):
                        valueAsString = str(
                            pm.getAttr(("FaceFitSkeleton." + inputs[i]),
                                       asString=1))
                        pm.optionMenu(ctrl, e=1, v=valueAsString)

            elif not pm.mel.attributeExists(inputs[i], 'FaceFitSkeleton'):
                if inputTypes[i] == "TextField":
                    pm.addAttr('FaceFitSkeleton', ln=inputs[i], dt="string")

                if inputTypes[i] == "CheckBox":
                    pm.addAttr('FaceFitSkeleton', ln=inputs[i], at='bool')

                if inputTypes[i] == "OptionMenu":
                    pm.addAttr('FaceFitSkeleton', ln=inputs[i],
                               en=pm.mel.asFaceOptionMenuItemsAsEnums(
                                   inputs[i]), at="enum")

            if inputTypes[i] == "TextField":
                pm.setAttr(("FaceFitSkeleton." + inputs[i]),
                           pm.textField(ctrl, q=1, tx=1),
                           type="string")

            if inputTypes[i] == "CheckBox":
                pm.setAttr(("FaceFitSkeleton." + inputs[i]),
                           pm.checkBox(ctrl, q=1, v=1))

            if inputTypes[i] == "OptionMenu":
                pm.setAttr(("FaceFitSkeleton." + inputs[i]),
                           (pm.optionMenu(ctrl, q=1, sl=1) - 1))

        checkBoxes = pm.lsUI(type='checkBox')
        # Update CheckBoxes
        for i in range(0, len(checkBoxes)):
            value = 0
            if pm.mel.gmatch(checkBoxes[i], "asFaceFit*"):
                obj = checkBoxes[i].replace("asFaceFit",
                                            "FaceFit") + leftSuffix
                if pm.objExists(obj):
                    value = 1

                pm.checkBox(checkBoxes[i], ed=value, e=1, v=value)

            if pm.mel.gmatch(checkBoxes[i], "asFaceFitLip*") or checkBoxes[
                    i] == "asFaceFitEyeBrowCenter" or checkBoxes[
                    i] == "asFaceFitNose" or checkBoxes[
                    i] == "asFaceFitNoseCenter" or checkBoxes[
                    i] == "asFaceFitNoseUnder" or checkBoxes[
                    i] == "asFaceFitJaw" or checkBoxes[i] == "asFaceFitThroat" or \
                checkBoxes[i] == "asFaceFitTongue" or checkBoxes[
                    i] == "asFaceFitUpMidLo" or checkBoxes[
                    i] == "asFaceFitJawCurves":
                parent = str(pm.checkBox(checkBoxes[i], q=1, p=1))
                # Not all checkBoxes to be used for Left side Fitting
                pm.layout(parent, en=(not leftFaceFitting), e=1)

        if pm.mel.attributeExists('buildStep', 'FaceFitSkeleton'):
            stepBuild = int(pm.getAttr('FaceFitSkeleton.buildStep'))
        # BuildStep

        nextStep = stepBuild + 1
        for i in range(0, 99):
            if not pm.columnLayout(("asStepBuildColumnLayout" + str(i)),
                                   q=1, ex=1):
                break

            headerEn = 0
            bodyEn = 0
            m = 0
            if i > (nextStep - 2):
                m = 1

            if pm.text(("stepBuild" + str(i) + "Text"),
                       q=1, ex=1):
                stepBuildText = str(pm.text(("stepBuild" + str(i) + "Text"),
                                            q=1, l=1))
                if pm.mel.gmatch(stepBuildText, "*RebuildRestore"):
                    if not pm.objExists('prefix_FaceGroup'):
                        m = 0

            if i == (nextStep - 1):
                bodyEn = 1

            if i == nextStep:
                headerEn = 1

            pm.rowLayout(("asStepBuildRowLayout" + str(i)),
                         m=m, en=headerEn, e=1)
            pm.columnLayout(("asStepBuildColumnLayout" + str(i)),
                            m=m, en=bodyEn, e=1)

        if pm.mel.attributeExists('vtxsFromLipToNose', 'FaceFitSkeleton'):
            vtxsFromLipToNose = int(
                pm.getAttr('FaceFitSkeleton.vtxsFromLipToNose'))
        # vtxsFromLipToNose

        if pm.intField('lipFalloffOuterIntField', q=1, ex=1):
            pm.intField('lipFalloffOuterIntField', e=1, v=vtxsFromLipToNose)
        # BuildType

        if pm.optionMenu('asFaceBuildTypeOptionMenu', q=1, ex=1):
            fitType = "Full"
            if pm.mel.attributeExists('buildType', 'FaceFitSkeleton'):
                avaiableBuiltTypes = pm.optionMenu('asFaceBuildTypeOptionMenu',
                                                   q=1, ils=1)
                savedFitType = str(pm.getAttr('FaceFitSkeleton.buildType'))
                if avaiableBuiltTypes.count(savedFitType):
                    fitType = savedFitType

            pm.optionMenu('asFaceBuildTypeOptionMenu', e=1, v=fitType)

    def asCreateFaceFitMask(self):
        pm.melGlobals.initVar('string', 'gMainProgressBar')
        faceScale = 0.0
        bb = []
        sel = pm.ls(sl=1)
        tempString = []

        pm.mel.eval(" string $sel[]=`ls -sl`; ")
        if not pm.mel.eval(' gmatch $sel[0] "*.f*" '):
            pm.error(
                "No poly-faces selected, The polygons of the characters`s face must be selected.")

        pm.progressBar(pm.melGlobals['gMainProgressBar'], e=1, min=0, max=9,
                       st="Storing Mask", ii=1, bp=1)
        pm.evalDeferred(
            "progressBar -e -ep " + pm.melGlobals['gMainProgressBar'])
        tempString = pm.listRelatives('FaceFitSkeleton', s=1)
        if len(tempString):
            pm.delete(tempString)

        tempString = pm.circle(c=(0, 0, 0), ch=0, d=3, ut=0, sw=360, s=8,
                               r=0.5, tol=0.000393701, nr=(0, 1, 0))
        pm.rename(tempString[0], 'TempCircle')
        pm.parent('TempCircleShape', 'FaceFitSkeleton', add=1, s=1)
        pm.delete('TempCircle')
        pm.rename('TempCircleShape', 'FaceFitSkeletonShape')
        pm.setAttr('FaceFitSkeletonShape.overrideEnabled', 1)
        pm.setAttr('FaceFitSkeletonShape.overrideColor', 13)

        pm.mel.eval(
            ' rotate -r -p 0 0 0 -os 0 -90 0 FaceFitSkeleton.cv[0:99]; ')
        pm.duplicate('FaceFitSkeleton', n='FaceFitSkeletonHeight')
        pm.duplicate('FaceFitSkeleton', n='FaceFitSkeletonCircle')
        pm.duplicate('FaceFitSkeleton', n='FaceFitSkeletonHeightCircle')
        pm.parent('FaceFitSkeletonHeightShape', 'FaceFitSkeleton', add=1, s=1)
        pm.parent('FaceFitSkeletonCircleShape', 'FaceFitSkeleton', add=1, s=1)
        pm.parent('FaceFitSkeletonHeightCircleShape', 'FaceFitSkeleton', add=1,
                  s=1)
        pm.delete('FaceFitSkeletonHeight', 'FaceFitSkeletonCircle',
                  'FaceFitSkeletonHeightCircle')
        pm.mel.eval(
            ' move -r 0 1.0 0 FaceFitSkeletonHeightShape.cv[0:99]  FaceFitSkeletonHeightCircleShape.cv[0:99]; ')

        mel = ''' 
        if ($sel[0]!="")
		{
            select $sel;
            $bb=`xform -q -ws -bb`;
            //string $tempString[];
            $tempString=`listRelatives -s FaceFitSkeleton`;
            print $tempString;
            for ($i=0;$i<size($tempString);$i++)
			{
			scale -r -p 0 0 0 ($bb[3]-$bb[0]) ($bb[4]-$bb[1]) ($bb[5]-$bb[2]) ($tempString[$i]+".cv[0:99]");
			move -r -os -wd 0 $bb[1] (($bb[2]+$bb[5])/2.0) ($tempString[$i]+".cv[0:99]");
			}
            //FaceFitSkeleton.faceScale
            $faceScale=$bb[4]-$bb[1];
            if (!`attributeExists faceScale FaceFitSkeleton`)
                addAttr -k 0 -ln faceScale -at double FaceFitSkeleton;
            setAttr FaceFitSkeleton.faceScale $faceScale;
		}
        print "// Mask stored.\n"; 
    '''
        # pm.mel.eval(mel)


def asLockAttr(object, trans, rot, scale, vis):
    pm.setAttr((object + ".translateX"),
               k=(not trans), l=trans)
    pm.setAttr((object + ".translateY"),
               k=(not trans), l=trans)
    pm.setAttr((object + ".translateZ"),
               k=(not trans), l=trans)
    pm.setAttr((object + ".rotateX"),
               k=(not rot), l=rot)
    pm.setAttr((object + ".rotateY"),
               k=(not rot), l=rot)
    pm.setAttr((object + ".rotateZ"),
               k=(not rot), l=rot)
    pm.setAttr((object + ".scaleX"),
               k=(not scale), l=scale)
    pm.setAttr((object + ".scaleY"),
               k=(not scale), l=scale)
    pm.setAttr((object + ".scaleZ"),
               k=(not scale), l=scale)
    pm.setAttr((object + ".visibility"),
               k=(not vis), l=vis)
    return
