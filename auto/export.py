# coding=utf-8

"""
自动输出工具类
"""

import os
from imp import reload

from pymel import core as pm
import maya.cmds as cmds
import maya.mel as mel

from animation import common

reload(common)

__version__ = "0.2.0"


class ExportFBXMaster(common.Singleton):
    def __init__(self):
        super(ExportFBXMaster, self).__init__()

        self.output_files = []
        self.output_path = ""

        self.auto_work_state = 1
        self.work_mode_selected = 1

        self.initialize()
        self.show()

    def show(self):
        if pm.window("autoExportFBXFileTool", ex=True):
            pm.deleteUI("autoExportFBXFileTool")

        pm.window(
            "autoExportFBXFileTool",
            t=u"自动输出 %s" % __version__,
            mb=True,
            cc=lambda *args: self._close_main_window())

        self.work_list_frame = pm.frameLayout(
            label=u"自动输出", mw=10, mh=5, bgs=True)
        self.form_layout = pm.formLayout()
        self.work_mode = pm.radioButtonGrp(
            label=u'工作类型：',
            labelArray3=[u'输出FBX', u'FBX优化', u'全流程'],
            cw4=[60, 80, 80, 80],
            sl=self.work_mode_selected,
            on1=lambda *args: self.fbx_optimize_state(state=False),
            on2=lambda *args: self.fbx_optimize_state(state=True),
            of2=lambda *args: self.fbx_optimize_state(state=False),
            on3=lambda *args: self.fbx_optimize_state(state=True),
            numberOfRadioButtons=3)
        fbx_optimize_layout = pm.columnLayout(adj=1)
        self.fbx_optimize = pm.checkBoxGrp(
            numberOfCheckBoxes=3,
            label=u"优化选项：",
            labelArray3=[u"清理头部动画", u"清理单个骨骼动画", u"清理模型组和控制器组"],
            cw4=[60, 100, 120, 100])
        self.face_make_node_check = pm.checkBox(label=u"优化捏脸骨骼")
        pm.setParent(fbx_optimize_layout)

        optimize_target_joint_layout = pm.columnLayout(p=self.form_layout)
        self.optimize_target = pm.textFieldGrp(
            label=u"骨骼名称：", cw2=[60, 300])
        self.offset_target = pm.floatFieldGrp(
            numberOfFields=3,
            cw4=[60, 100, 100, 100],
            label=u'偏移参数：',
            value1=0,
            value2=0,
            value3=0)
        pm.setParent("..")
        self.task_scroll_label = pm.text(
            label=u"任务列表：", al="left")
        self.task_scroll = pm.textScrollList(ams=True, w=200)
        pm.popupMenu()
        pm.menuItem(label=u"添加文件",
                    c=lambda *args: self._append_file())
        pm.menuItem(label=u"移除选择",
                    c=lambda *args: self.remove_select_item())

        self.output_scroll_label = pm.text(label=u"输出列表：", al="left")
        self.output_scroll = pm.textScrollList(ams=True, w=200)
        pm.popupMenu()
        pm.menuItem(label=u"清空列表",
                    c=lambda *args: self.clean_output_scroll())
        pm.menuItem(label=u"转移到任务列表",
                    c=lambda *args: self.move_to_task_scroll())

        self.ouput_path_field = pm.textFieldButtonGrp(
            adj=2,
            label=u"存放路径：",
            bl=u"指定路径",
            cw3=[60, 100, 100],
            text=self.output_path,
            bc=lambda *args: self._set_output_location())
        self.excute_btn = pm.button(
            label=u"开始输出",
            c=lambda *args: self.start_export())

        pm.formLayout(
            self.form_layout,
            edit=True,
            attachForm=[
                (self.work_mode, 'top', 0),
                (self.work_mode, 'left', 0),
                (self.work_mode, 'right', 0),
                (fbx_optimize_layout, 'left', 0),
                (fbx_optimize_layout, 'right', 0),
                (optimize_target_joint_layout, 'left', 0),
                (optimize_target_joint_layout, 'right', 0),
                (self.ouput_path_field, 'left', 0),
                (self.ouput_path_field, 'right', 0),
                (self.excute_btn, 'left', 0),
                (self.excute_btn, 'right', 0),
                (self.excute_btn, 'bottom', 10)
            ],
            attachControl=[
                (fbx_optimize_layout, 'top', 5, self.work_mode),
                (optimize_target_joint_layout, 'top', 5, fbx_optimize_layout),
                (self.task_scroll_label, 'top', 5,
                 optimize_target_joint_layout),
                (self.task_scroll, 'top', 5, self.task_scroll_label),
                (self.task_scroll, 'bottom', 5, self.ouput_path_field),
                (self.output_scroll_label, 'top', 5,
                 optimize_target_joint_layout),
                (self.output_scroll_label, 'left', 5, self.task_scroll),
                (self.output_scroll, 'top', 5, self.output_scroll_label),
                (self.output_scroll, 'left', 5, self.task_scroll),
                (self.output_scroll, 'bottom', 5, self.ouput_path_field),
                (self.ouput_path_field, 'bottom', 5, self.excute_btn),
            ]
        )

        pm.showWindow("autoExportFBXFileTool")

        if self.work_mode_selected == 2:
            self.fbx_optimize_state(state=True)
        elif self.work_mode_selected == 1:
            self.fbx_optimize_state(state=False)

    def initialize(self):
        if pm.optionVar(q='autoExportFBXFileToolOutputPath'):
            self.output_path = pm.optionVar(
                q='autoExportFBXFileToolOutputPath')

        if pm.optionVar(q='autoExportFBXFileToolAutoChecked'):
            self.auto_work_state = pm.optionVar(
                q='autoExportFBXFileToolAutoChecked')

        if pm.optionVar(q='autoExportFBXFileToolWorkMode'):
            self.work_mode_selected = int(pm.optionVar(
                q='autoExportFBXFileToolWorkMode'))

    def _close_main_window(self):
        pm.optionVar(sv=('autoExportFBXFileToolOutputPath', self.output_path))
        pm.optionVar(
            sv=("autoExportFBXFileToolWorkMode",
                pm.radioButtonGrp(self.work_mode, q=True, sl=True)))
        return

    def _append_file(self):
        multiple_filters = (
            "Maya Files (*.ma *.mb);;"
            "Maya ASCII (*.ma);;"
            "Maya Binary (*.mb);;"
            "FBX Files (*.fbx);;"
        )
        current_export_list = pm.textScrollList(
            self.task_scroll, q=True, ai=True)
        export_files = pm.fileDialog2(
            fileFilter=multiple_filters,
            dialogStyle=2, fileMode=4, okc=u"添加")
        if export_files:
            for export_file in export_files:
                if export_file not in current_export_list:
                    pm.textScrollList(
                        self.task_scroll, edit=True, append=export_file)

        self.output_files = pm.textScrollList(
            self.task_scroll, q=True, ai=True)
        return True

    def remove_select_item(self):
        pm.textScrollList(
            self.task_scroll,
            e=True,
            ri=pm.textScrollList(self.task_scroll, q=True, si=True))
        self.output_files = pm.textScrollList(
            self.task_scroll, q=True, ai=True)
        return

    def _set_output_location(self):
        output_location = pm.fileDialog2(
            dialogStyle=2, fileMode=3, okc=u"选择文件夹")
        if output_location:
            pm.textFieldButtonGrp(
                self.ouput_path_field,
                e=True,
                text=output_location[0])
            self.output_path = output_location[0]
        return

    def start_export(self):
        model_selected = pm.radioButtonGrp(self.work_mode, q=True, sl=True)

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        if len(self.output_files) < 1:
            pm.error(u"任务列表不能为空")
        else:
            if model_selected == 1:  # 输出FBX
                self.export_to_fbx(self.output_files)
            if model_selected == 2:  # FBX优化
                self.start_optimize_fbx(self.output_files)
            if model_selected == 3:  # 全流程
                if self.export_to_fbx(self.output_files):
                    self.move_to_task_scroll()
                    self.output_files = pm.textScrollList(
                        self.task_scroll, q=True, ai=True)
                    self.start_optimize_fbx(self.output_files)

        print(u"输出成功")

        return

    def start_optimize_fbx(self, export_files):
        """
        优化FBX文件

        主要功能：
        1.清除命名空间
        2.清理头部的动画曲线

        :param export_files: 需要输出的文件列表
        :return: True
        """
        # export_grp = ["character_root", "final_model_grp"]
        system_namespace = ['UI', 'shared']

        for export_file in export_files:
            # 新建场景，打开指定场景
            cmds.file(new=True, force=True)
            cmds.file(export_file, o=True)
            file_name = cmds.file(
                q=1, sceneName=True, shortName=True).split('.')[0]
            print(file_name + ' already open!')

            # 将MAYA的时间格式改成ntsc(30帧每秒)
            common.set_time_unit(unit='ntsc')

            # 命名空间列表
            all_namespace_list = pm.namespaceInfo(lon=True)
            for name in system_namespace:
                all_namespace_list.remove(name)
            # 清楚命名空间
            for namespace in all_namespace_list:
                pm.namespace(removeNamespace=":%s" % namespace,
                             mergeNamespaceWithParent=True)

            if pm.objExists("character_Group"):
                pm.delete("character_Group")

            # 清理头部动画
            if pm.checkBoxGrp(self.fbx_optimize, q=True, v1=True):
                pm.select("head_JNT", hi=True)
                for jnt in pm.ls(sl=True):
                    anim_attrs = pm.listAttr(jnt, k=True)
                    for anim_attr in anim_attrs:
                        cmd = '''cutKey -cl -t ":" -f ":" -at %s %s;''' % (
                            anim_attr, jnt.controller_name())
                        mel.eval(cmd)

            # 清理指定骨骼的动画
            if pm.checkBoxGrp(self.fbx_optimize, q=True, v2=True):
                target_joint = pm.textFieldGrp(
                    self.optimize_target, q=True, text=True)
                if pm.objExists(target_joint):
                    # pm.select(target_joint)
                    anim_attrs = pm.listAttr(target_joint, k=True)
                    for anim_attr in anim_attrs:
                        cmd = '''cutKey -cl -t ":" -f ":" -at %s %s;''' % (
                            anim_attr, target_joint)
                        mel.eval(cmd)
                    offset_value = pm.floatFieldGrp(
                        self.offset_target, q=True, value=True)
                    pm.PyNode(target_joint).translate.set(offset_value)

            export_file_name = "%s/%s.fbx" % (self.output_path, file_name)

            # 清理模型组
            if pm.checkBoxGrp(self.fbx_optimize, q=True, v3=True):
                if pm.objExists("MotionSystem"):
                    pm.delete("MotionSystem")
                if pm.objExists("Geometry"):
                    pm.delete("Geometry")
                if len(pm.ls(type="mesh")) > 0:
                    for item in pm.ls(type="mesh"):
                        parent_node = item.getParent()
                        pm.delete(parent_node)

            # 清理捏脸骨骼动画
            if pm.checkBox(self.face_make_node_check, q=True, value=True):
                faceMakeSets = []
                extraSets = []

                extraSets = ["L_eyeBall_socket", "L_eyeBall_socket_sdk",
                             "R_eyeBall_socket", "R_eyeBall_socket_sdk",
                             "headTipEnd_JNT", "facial_C_Nose_JNT",
                             "facial_C_NoseBase_JNT", "head_JNT",
                             "L_browMid_JNT", "L_browIn_JNT", "L_browOut_JNT",
                             "L_brow_JNT",
                             "R_browMid_JNT", "R_browIn_JNT", "R_browOut_JNT",
                             "R_brow_JNT", ]

                pm.select("head_JNT", hi=True)

                for item in pm.ls(sl=True):
                    if "definition_" in item.controller_name() and item.type() == "joint":
                        faceMakeSets.append(item)

                for item in extraSets:
                    if pm.objExists(item):
                        faceMakeSets.append(item)

                pm.select(faceMakeSets)

                for jnt in pm.ls(sl=True):
                    anim_attrs = pm.listAttr(jnt, k=True)
                    for anim_attr in anim_attrs:
                        cmd = '''cutKey -cl -t ":" -f ":" -at %s %s;''' % (
                            anim_attr, jnt.controller_name())
                        mel.eval(cmd)

            cmds.file(export_file_name,
                      force=True,
                      pr=True,
                      ea=True,
                      typ="FBX export",
                      options="v=0")

            pm.textScrollList(
                self.output_scroll, e=True, a=export_file_name)
            pm.textScrollList(
                self.task_scroll, e=True, ri=export_file)

        return True

    def export_to_fbx(self, export_files):
        """
        将maya文件中的角色输出为FBX文件

        :param export_files: 需要输出的文件列表
        :return: True
        """
        for export_file in export_files:
            # 新建场景，打开指定场景
            cmds.file(new=True, force=True)
            cmds.file(export_file, o=True)
            file_name = cmds.file(
                q=1, sceneName=True, shortName=True).split('.')[0]
            print(file_name + ' already open!')

            # 将MAYA的时间格式改成ntsc(30帧每秒)
            common.set_time_unit(unit='ntsc')

            min_time = pm.playbackOptions(q=True, minTime=True)
            max_time = pm.playbackOptions(q=True, maxTime=True)
            time_range = (min_time, max_time)

            system_namespace = ['UI', 'shared']
            # 命名空间列表
            all_namespace_list = pm.namespaceInfo(lon=True)
            for name in system_namespace:
                all_namespace_list.remove(name)

            print(u"所有的命名空间：%s" % all_namespace_list)

            fbx_files = []
            # 角色输出时需要包含的两个组
            export_grp = ["character_root", "final_model_grp"]

            for cha_name in all_namespace_list:
                print("cha name: %s" % cha_name)
                scene_export_grp = []
                # 制作过程中有可能引用非角色对象，例如道具，
                # 这个时候就需要用程序来判断使用该命名空间的对象是否为一个角色
                if pm.objExists("%s:character_root" % cha_name):
                    # 根据命名空间来获取场景中有多少角色
                    for export_item in export_grp:
                        scene_export_grp.append(
                            "%s:%s" % (cha_name, export_item))
                    print(u"%s需要输出的组：%s" % (cha_name, scene_export_grp))
                    pm.select("%s:character_root" % cha_name, hi=True)
                    bake_nodes = pm.ls(sl=True)

                    print(u"--------- 开始烘焙动画开始 --------------")

                    pm.bakeResults(
                        bake_nodes,
                        simulation=True,
                        t=time_range,
                        sb=1,
                        dic=True,
                        preserveOutsideKeys=False,
                        sparseAnimCurveBake=False,
                        removeBakedAttributeFromLayer=False,
                        bakeOnOverrideLayer=False,
                        controlPoints=False,
                        shape=False)

                    export_file_name = ""
                    if len(all_namespace_list) == 1:
                        export_file_name = "%s/%s.fbx" % (
                            self.output_path, file_name)
                    elif len(all_namespace_list) > 1:
                        export_file_name = "%s/%s_%s.fbx" % (
                            self.output_path, file_name, cha_name)

                    pm.select(scene_export_grp)
                    cmds.file(
                        export_file_name,
                        force=True,
                        pr=True,
                        es=True,
                        typ="FBX export",
                        options="v=0")

                    fbx_files.append(export_file_name)
                    pm.textScrollList(
                        self.output_scroll, e=True, a=export_file_name)

            pm.textScrollList(self.task_scroll, e=True, ri=export_file)

        return True

    def fbx_optimize_state(self, state):
        if state == True:
            pm.checkBoxGrp(self.fbx_optimize, e=True, en=True)
        elif state == False:
            pm.checkBoxGrp(self.fbx_optimize, e=True, en=False)

    def clean_output_scroll(self):
        pm.textScrollList(self.output_scroll, e=True, ra=True)
        return

    def move_to_task_scroll(self):
        output_list = pm.textScrollList(self.output_scroll, q=True, ai=True)
        pm.textScrollList(self.task_scroll, e=True, ra=True)
        pm.textScrollList(self.task_scroll, e=True, a=output_list)
        pm.textScrollList(self.output_scroll, e=True, ra=True)
        return
