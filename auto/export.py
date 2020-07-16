# coding=utf-8

"""
自动输出工具类
"""

from pymel import core as pm
from animation import common

reload(common)


class ExportFBXMaster(common.Singleton):
    def __init__(self):
        super(ExportFBXMaster, self).__init__()

        self.output_files = []
        self.output_path = ""

        self.work_mode_selected = 1

        self.initialize()
        self.show()

    def show(self):
        if pm.window("autoExportFBXFileTool", ex=True):
            pm.deleteUI("autoExportFBXFileTool")
        pm.window(
            "autoExportFBXFileTool",
            # t=u"自动输出 %s" % __version__,
            mb=True,
            cc=lambda *args: self._close_main_window())

        # self.menu_list()

        self.form_layout = pm.formLayout()

        self.work_list_frame = pm.frameLayout(
            label=u"工作模式", mw=10, mh=5)

        self.auto_checked = pm.checkBoxGrp(label=u"全自动")
        # self.work_mode = pm.radioButtonGrp(
        #     label=u'工作类型：',
        #     labelArray2=[u'骨骼输出', u'FBX优化'],
        #     cw3=[60, 80, 80],
        #     sl=self.work_mode_selected,
        #     numberOfRadioButtons=2)

        self.scroll_label = pm.text(
            label=u"输出文件列表：", al="left")
        self.output_scroll = pm.textScrollList(ams=True)
        pm.popupMenu()
        pm.menuItem(label=u"添加文件",
                    c=lambda *args: self._append_file())
        pm.menuItem(label=u"移除选择",
                    c=lambda *args: self.remove_select_item())
        pm.setParent("..")

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
                (self.work_list_frame, 'top', 10),
                (self.work_list_frame, 'left', 10),
                (self.work_list_frame, 'right', 10),
                (self.ouput_path_field, 'left', 10),
                (self.ouput_path_field, 'right', 10),
                (self.excute_btn, 'left', 10),
                (self.excute_btn, 'right', 10),
                (self.excute_btn, 'bottom', 10)
            ],
            attachControl=[
                (self.work_list_frame, 'bottom', 0, self.ouput_path_field),
                (self.ouput_path_field, 'bottom', 5, self.excute_btn),
            ],
        )

        pm.showWindow("autoExportFBXFileTool")

    def initialize(self):
        if pm.optionVar(q='autoExportFBXFileToolOutputPath'):
            self.output_path = pm.optionVar(
                q='autoExportFBXFileToolOutputPath')

    def _close_main_window(self):
        pm.optionVar(sv=('autoExportFBXFileToolOutputPath', self.output_path))

    def menu_list(self):
        """
        工具菜单栏
        """
        pm.menu(label=u"设置", tearOff=True)
        pm.menuItem(
            label=u"设置捏脸配置文件存放目录",
            c=lambda *args: self.setting_dedinition())
        # pm.menuItem(
        #     label=u"调试模式", cb=False)

    def _append_file(self):
        multiple_filters = (
            "Maya Files (*.ma *.mb);;"
            "Maya ASCII (*.ma);;"
            "Maya Binary (*.mb);;"
            "FBX Files (*.fbx);;"
        )
        current_export_list = pm.textScrollList(
            self.output_scroll, q=True, ai=True)
        export_files = pm.fileDialog2(
            fileFilter=multiple_filters,
            dialogStyle=2, fileMode=4, okc=u"添加")
        if export_files:
            for export_file in export_files:
                if export_file not in current_export_list:
                    pm.textScrollList(
                        self.output_scroll, edit=True, append=export_file)

        self.output_files = pm.textScrollList(
            self.output_scroll, q=True, ai=True)
        return True

    def remove_select_item(self):
        pm.textScrollList(
            self.output_scroll,
            e=True,
            ri=pm.textScrollList(self.output_scroll, q=True, si=True))
        self.output_files = pm.textScrollList(
            self.output_scroll, q=True, ai=True)
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

        if model_selected == 1:
            self.export_to_fbx()
        if model_selected == 2:
            self.clean_definition_anim()

        print u"输出成功"

        return

    def clean_definition_anim(self):
        # export_grp = ["character_root", "final_model_grp"]

        system_namespace = ['UI', 'shared']

        print self.output_files

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        if len(self.output_files) > 0:
            for export_file in self.output_files:
                # scence_export_grp = []

                # 新建场景，打开指定场景
                cmds.file(new=True, force=True)
                cmds.file(export_file, o=True)
                file_name = cmds.file(
                    q=1, sceneName=True, shortName=True).split('.')[0]
                print (file_name + ' already open!')

                # 将MAYA的时间格式改成ntsc(30帧每秒)
                common.set_time_unit(unit='ntsc')

                # min_time = pm.playbackOptions(q=True, minTime=True)
                # max_time = pm.playbackOptions(q=True, maxTime=True)
                # time_range = (min_time, max_time)

                # 命名空间列表
                all_namespace_list = pm.namespaceInfo(lon=True)
                for name in system_namespace:
                    all_namespace_list.remove(name)

                for namespace in all_namespace_list:
                    pm.namespace(
                        removeNamespace=":%s" % namespace,
                        mergeNamespaceWithParent=True)
                pm.select("head_JNT", hi=True)
                for jnt in pm.ls(sl=True, type="joint"):
                    if "definition_" in jnt.name():
                        anim_attrs = pm.listAttr(jnt, k=True)
                        for anim_attr in anim_attrs:
                            cmd = '''cutKey -cl -t ":" -f ":" -at %s %s;''' % (
                                anim_attr, jnt.name())
                            mel.eval(cmd)

                # export_file_name = ""
                # if len(all_namespace_list) == 1:
                export_file_name = "%s/%s.fbx" % (self.output_path, file_name)

                # pm.select(scence_export_grp)
                cmds.file(
                    export_file_name,
                    force=True,
                    pr=True,
                    ea=True,
                    typ="FBX export",
                    options="v=0")

    def export_to_fbx(self):
        export_grp = ["character_root", "final_model_grp"]

        system_namespace = ['UI', 'shared']

        print self.output_files

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        if len(self.output_files) > 0:
            for export_file in self.output_files:
                scence_export_grp = []

                # 新建场景，打开指定场景
                cmds.file(new=True, force=True)
                cmds.file(export_file, o=True)
                file_name = cmds.file(
                    q=1, sceneName=True, shortName=True).split('.')[0]
                print (file_name + ' already open!')

                # 将MAYA的时间格式改成ntsc(30帧每秒)
                common.set_time_unit(unit='ntsc')

                min_time = pm.playbackOptions(q=True, minTime=True)
                max_time = pm.playbackOptions(q=True, maxTime=True)
                time_range = (min_time, max_time)

                # 命名空间列表
                all_namespace_list = pm.namespaceInfo(lon=True)
                for name in system_namespace:
                    all_namespace_list.remove(name)

                # print all_namespace_list

                fbx_files = []
                export_file_name = ""
                for namespace in all_namespace_list:
                    if pm.objExists("%s:character_root" % namespace):
                        # 根据命名空间来获取场景中有多少角色
                        print "namespace: %s" % namespace
                        for export_item in export_grp:
                            scence_export_grp.append(
                                "%s:%s" % (namespace, export_item))

                        pm.select("%s:character_root" % namespace, hi=True)
                        bake_nodes = pm.ls(sl=True)

                        print u"烘焙动画开始"
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
                                self.output_path, file_name, namespace)

                        pm.select(scence_export_grp)
                        cmds.file(
                            export_file_name,
                            force=True,
                            pr=True,
                            es=True,
                            typ="FBX export",
                            options="v=0")

                        fbx_files.append(export_file_name)

        else:
            pm.error(u"数据文件和输出路径不能为空")
