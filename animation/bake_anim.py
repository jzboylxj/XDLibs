# coding=utf-8
"""
数据自动转换工具

功能描述：
将从3dsMax导出的FBX动画数据，应用到Maya的绑定文件（控制器）上。
以批处理的形式自动处理，快速提高效率。

"""
import os
import maya.cmds as cmds
from pymel.core import mel

from pymel import core as pm

import common

reload(common)

__author__ = 'Li Xiao Jun'
__version__ = '0.1'


class MainWindow:
    def __init__(self):
        self.template_file = ''
        self.output_files = []
        self.output_path = ''
        self.clean_file = True
        self.export_atom = True

        self.rig_file = ''
        self.atom_file = ''
        self.changeNTSC = True

        self.initialize()

    def initialize(self):
        """
        初始化数据

        从MAYA的保存的属性数据里面获取一些值

        :return:
        """
        if pm.optionVar(q='doBakeAnimOutputPath'):
            self.output_path = pm.optionVar(
                q='doBakeAnimOutputPath')
        if pm.optionVar(q='doBakeAnimTemplateFile'):
            self.template_file = pm.optionVar(
                q='doBakeAnimTemplateFile')
        if pm.optionVar(q='doBakeAnimCleanFileChecked'):
            if pm.optionVar(q='doBakeAnimCleanFileChecked') == "False":
                self.clean_file = False
            elif pm.optionVar(q='doBakeAnimCleanFileChecked') == "True":
                self.clean_file = True
        if pm.optionVar(q='doBakeAnimExportAtomChecked'):
            if pm.optionVar(q='doBakeAnimExportAtomChecked') == "False":
                self.export_atom = False
            elif pm.optionVar(q='doBakeAnimExportAtomChecked') == "True":
                self.export_atom = True

        if pm.optionVar(q='doBakeAnimRigFile'):
            self.rig_file = pm.optionVar(
                q='doBakeAnimRigFile')
        if pm.optionVar(q='doBakeAnimAtomFile'):
            self.atom_file = pm.optionVar(
                q='doBakeAnimAtomFile')
        if pm.optionVar(q='doBakeChangeNTSCChecked'):
            if pm.optionVar(q='doBakeChangeNTSCChecked') == "False":
                self.changeNTSC = False
            elif pm.optionVar(q='doBakeChangeNTSCChecked') == "True":
                self.changeNTSC = True

    def _close_main_window(self):
        pm.optionVar(sv=('doBakeAnimOutputPath', self.output_path))
        pm.optionVar(sv=('doBakeAnimTemplateFile', self.template_file))
        pm.optionVar(sv=('doBakeAnimCleanFileChecked', self.clean_file))
        pm.optionVar(sv=('doBakeAnimExportAtomChecked', self.export_atom))

        pm.optionVar(sv=('doBakeAnimRigFile', self.rig_file))
        pm.optionVar(sv=('doBakeAnimAtomFile', self.atom_file))
        pm.optionVar(sv=('doBakeChangeNTSCChecked', self.changeNTSC))

    def show(self):
        if pm.window("dataConvertWin", ex=True):
            pm.deleteUI("dataConvertWin")
        pm.window(
            "dataConvertWin",
            t=u"自动输出 %s" % __version__,
            mb=True,
            cc=lambda *args: self._close_main_window())

        self.menu_list()

        tabs = pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        child1 = self.child_tab_export()
        child2 = self.child_tab_import()

        pm.tabLayout(
            tabs,
            edit=True,
            tabLabel=((child1, u'输出'), (child2, u'导入')))

        pm.showWindow("dataConvertWin")

    def child_tab_export(self):
        layout = pm.formLayout(numberOfDivisions=100)
        file_export_list_frame = pm.frameLayout(
            label=u"数据文件列表：", mw=10, mh=10, bgs=True)
        pm.textFieldButtonGrp(
            'template_file_setter',
            label=u"模板文件",
            bl=u"指定",
            adj=2,
            cw3=[52, 100, 60],
            cat=[(2, "left", 5), (3, "left", 5)],
            text=self.template_file,
            bc=lambda *args: self._set_template_file())
        pm.textScrollList('export_list_input', ams=True)
        pm.popupMenu()
        pm.menuItem(label=u"移除选择",
                    c=lambda *args: self._remove_selected_item())
        pm.menuItem(label=u"移除所有",
                    c=lambda *args: self._remove_all_item())
        pm.setParent("..")

        export_options_frame = pm.frameLayout(
            label=u"输出选项：", mw=10, mh=10, bgs=True)
        pm.textFieldButtonGrp(
            'output_path_setter',
            label=u"存放路径",
            bl=u"设置",
            adj=2,
            cw3=[52, 100, 60],
            cat=[(2, "left", 5), (3, "left", 5)],
            text=self.output_path,
            bc=lambda *args: self._set_output_location())
        pm.rowColumnLayout(nr=1)
        pm.checkBoxGrp(
            'cleanFileChecked',
            label=u"清理文件",
            value1=self.clean_file,
            cw2=[52, 30], cat=[(2, "left", 5)],
            cc=lambda *args: self._set_clean_file_check()
        )
        pm.checkBoxGrp(
            'exportAtomFileChecked',
            label=u"输出Atom动画数据",
            value1=self.export_atom,
            cw2=[120, 30], cat=[(2, "left", 5)],
            cc=lambda *args: self._set_export_atom_check()
        )
        pm.setParent("..")
        pm.setParent("..")
        execute_button = pm.button(
            label=u"输出！",
            c=lambda *args: self.start_export_work())
        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (file_export_list_frame, 'top', 10),
                (file_export_list_frame, 'left', 10),
                (file_export_list_frame, 'right', 10),
                (export_options_frame, 'left', 10),
                (export_options_frame, 'right', 10),
                (execute_button, 'left', 10),
                (execute_button, 'right', 10),
                (execute_button, 'bottom', 10)],
            attachControl=[
                # (file_export_list_frame, 'top', 5, project_store_path_frame),
                (file_export_list_frame, 'bottom', 5, export_options_frame),
                (export_options_frame, 'bottom', 5, execute_button)],
            # attachPosition=[(b1, 'right', 5, 75),
            #                                 (column, 'left', 0, 75)],
            #                 attachNone=(b2, 'top'))
        )
        pm.setParent("..")
        return layout

    def child_tab_import(self):
        layout = pm.formLayout(numberOfDivisions=100)
        import_atom_frame = pm.frameLayout(
            label=u"数据文件列表：", mw=10, mh=10, bgs=True)
        pm.columnLayout(adj=1)
        pm.textFieldButtonGrp(
            'rig_file_setter',
            label=u"绑定文件",
            bl=u"指定",
            adj=2,
            cw3=[52, 100, 60],
            cat=[(2, "left", 5), (3, "left", 5)],
            text=self.rig_file,
            bc=lambda *args: self._set_rig_file()
        )
        pm.textFieldButtonGrp(
            'atom_file_setter',
            label=u"动画数据",
            bl=u"指定",
            adj=2,
            cw3=[52, 100, 60],
            cat=[(2, "left", 5), (3, "left", 5)],
            text=self.atom_file,
            bc=lambda *args: self._set_atom_file()
        )
        pm.checkBoxGrp(
            'unitToNTSC',
            label=u"NTSC制式",
            value1=self.changeNTSC,
            cw2=[60, 30], cat=[(2, "left", 5)],
            cc=lambda *args: self._set_change_unit_check()
        )
        pm.setParent("..")
        pm.setParent("..")
        execute_button = pm.button(
            label=u"读取！",
            c=lambda *args: self.start_import_work()
        )
        pm.formLayout(
            layout, edit=True,
            attachForm=[
                (import_atom_frame, 'top', 10),
                (import_atom_frame, 'left', 10),
                (import_atom_frame, 'right', 10),
                # (export_options_frame, 'left', 10),
                # (export_options_frame, 'right', 10),
                (execute_button, 'left', 10),
                (execute_button, 'right', 10),
                (execute_button, 'bottom', 10)
            ],
            attachControl=[
                # (file_export_list_frame, 'top', 5, project_store_path_frame),
                # (file_export_list_frame, 'bottom', 5, export_options_frame),
                (import_atom_frame, 'bottom', 5, execute_button)
            ],
            # attachPosition=[(b1, 'right', 5, 75),
            #                                 (column, 'left', 0, 75)],
            #                 attachNone=(b2, 'top'))
        )
        return layout

    def menu_list(self):
        pm.menu(label=u"文件", tearOff=True)
        pm.menuItem(label=u"添加数据文件", c=lambda *args: self._append_file())

    def _append_file(self):
        multiple_filters = ("FBX Files (*.fbx);;"
                            "Maya Files (*.ma *.mb);;"
                            "Maya ASCII (*.ma);;"
                            "Maya Binary (*.mb);;")
        current_export_list = pm.textScrollList(
            'export_list_input', q=True, ai=True)
        export_files = pm.fileDialog2(
            fileFilter=multiple_filters,
            dialogStyle=2, fileMode=4, okc=u"添加")
        if export_files:
            for export_file in export_files:
                if export_file not in current_export_list:
                    pm.textScrollList(
                        'export_list_input', edit=True, append=export_file)

        self.output_files = pm.textScrollList(
            'export_list_input', q=True, ai=True)
        return

    def _remove_selected_item(self):
        selected_item = pm.textScrollList('export_list_input', q=True, si=True)
        for item in selected_item:
            pm.textScrollList('export_list_input', e=True, ri=item)
        self.output_files = pm.textScrollList(
            'export_list_input', q=True, ai=True)

    def _remove_all_item(self):
        pm.textScrollList('export_list_input', e=True, ra=True)
        self.output_files = pm.textScrollList(
            'export_list_input', q=True, ai=True)

    def _set_output_location(self):
        output_location = pm.fileDialog2(
            dialogStyle=2, fileMode=3, okc=u"选择文件夹")
        if output_location:
            pm.textFieldButtonGrp(
                'output_path_setter', e=True,
                text=output_location[0])
            self.output_path = output_location[0]
        return

    def _set_template_file(self):
        template_location = pm.fileDialog2(
            dialogStyle=2, fileMode=1, okc=u"选择模板文件")
        if template_location:
            pm.textFieldButtonGrp(
                'template_file_setter', e=True,
                text=template_location[0])
            self.template_file = template_location[0]
        return

    def _set_rig_file(self):
        rig_location = pm.fileDialog2(
            dialogStyle=2, fileMode=1, okc=u"选择绑定文件")
        if rig_location:
            pm.textFieldButtonGrp(
                'rig_file_setter', e=True,
                text=rig_location[0])
            self.rig_file = rig_location[0]
        return

    def _set_atom_file(self):
        atom_location = pm.fileDialog2(
            dialogStyle=2, fileMode=1, okc=u"选择Atom动画文件")
        if atom_location:
            pm.textFieldButtonGrp(
                'atom_file_setter', e=True,
                text=atom_location[0])
            self.atom_file = atom_location[0]
        return

    def _set_clean_file_check(self):
        self.clean_file = pm.checkBoxGrp(
            'cleanFileChecked', q=True, value1=True)

    def _set_export_atom_check(self):
        self.export_atom = pm.checkBoxGrp(
            'exportAtomFileChecked', q=True, value1=True)

    def _set_change_unit_check(self):
        self.changeNTSC = pm.checkBoxGrp(
            'unitToNTSC', q=True, value1=True)

    def start_export_work(self):
        if self.template_file == '':
            pm.error(u"模板文件不能为空")
        if not os.path.exists(self.template_file):
            pm.error(u"模板文件不存在或不是有效文件")

        if len(self.output_files) < 1:
            pm.error(u"数据文件不能为空")

        if self.output_path == '':
            pm.error(u"输出路径不能为空")
        if not os.path.exists(self.output_path):
            pm.error(u"输出路径不存在")

        for export_file in self.output_files:
            # 新建场景，打开指定场景
            cmds.file(new=True, force=True)
            # cmds.file(export_file, o=True)
            cmds.file(self.template_file, o=True)
            file_name = cmds.file(
                q=1, sceneName=True, shortName=True).split('.')[0]
            print (file_name + ' already open!')

            cmds.file(export_file, loadReference="chaCRN",
                      type="FBX", options="fbx")

            # 将MAYA的时间格式改成ntsc(30帧每秒)
            common.set_time_unit(unit='ntsc')

            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)

            time_range = common.get_anim_range_from_node("chaC:Bip001")
            print time_range

            fk_controllers = []
            if pm.objExists("FKControllers"):
                fk_controllers = pm.sets("FKControllers", q=True)
            else:
                pm.error(u"缺少FK控制器的选择集")
            if len(fk_controllers) < 1:
                pm.error(u"FK控制器的选择集里面为空")
            else:
                pm.bakeResults(fk_controllers, simulation=True,
                               t=time_range,
                               sb=1,
                               # at=pm.listAttr(cam, k=True),
                               dic=True,
                               preserveOutsideKeys=False,
                               sparseAnimCurveBake=False,
                               removeBakedAttributeFromLayer=False,
                               bakeOnOverrideLayer=False,
                               controlPoints=False,
                               shape=False)

            # 清理场景文件
            if self.clean_file:
                # 将参考文件从场景中移除
                cmds.file(export_file, removeReference=True)
                if pm.objExists("delete_grp"):
                    pm.delete("delete_grp")

            if self.export_atom:
                # 将所有FK动画以Atom的格式输出
                atom_name = export_file.split("/")[
                    len(export_file.split("/")) - 1].strip(".fbx")
                atom_file = "%s/%s" % (self.output_path, atom_name)
                pm.select(fk_controllers)
                mel_command = ('doExportAtom(1,{ "%s" });' % atom_file)
                mel.eval(mel_command)
                options = (
                    "precision=8;"
                    "statics=1;"
                    "baked=1;"
                    "sdk=0;"
                    "constraint=0;"
                    "animLayers=0;"
                    "selected=selectedOnly;"
                    "whichRange=2;"
                    "range=%d:%d;"
                    "hierarchy=none;"
                    "controlPoints=0;"
                    "useChannelBox=1;"
                    "options=keys;"
                    "copyKeyCmd=-animation objects "
                    "-time >%d:%d> "
                    "-float >%d:%d> "
                    "-option keys "
                    "-hierarchy none "
                    "-controlPoints 0 " % (
                        time_range[0], time_range[1], time_range[0],
                        time_range[1], time_range[0], time_range[1]))

                cmds.file(atom_file, force=True,
                          options=options,
                          typ="atomExport", es=True)

            # 另存maya文件
            new_file_name = ""
            if ".fbx" in export_file:
                new_file_name = export_file.replace(".fbx", ".mb")
            elif ".FBX" in export_file:
                new_file_name = export_file.replace(".FBX", ".mb")
            cmds.file(rename=new_file_name)
            cmds.file(f=True, save=True, options="v=0;")

            print (u"%s输出工作全部完成" % export_file)

    def start_import_work(self):
        if self.rig_file == '':
            pm.error(u"模型文件不能为空")
        if not os.path.exists(self.rig_file):
            pm.error(u"模型文件不存在或不是有效文件")

        if self.atom_file == '':
            pm.error(u"动画数据文件不能为空")
        if not os.path.exists(self.atom_file):
            pm.error(u"动画数据文件不存在或不是有效文件")

        namespace_prefix = 'chaA'
        # 新建场景，打开指定场景
        cmds.file(new=True, force=True)
        cmds.file(
            self.rig_file,
            r=True,
            ignoreVersion=True,
            mergeNamespacesOnClash=False,
            namespace=namespace_prefix,
            options="v=0;")

        if self.changeNTSC:
            common.set_time_unit(unit='ntsc')

        fk_controllers = []
        if pm.objExists("%s:FKControllers" % namespace_prefix):
            fk_controllers = pm.sets("%s:FKControllers" % namespace_prefix,
                                     q=True)
        else:
            pm.error(u"缺少FK控制器的选择集")
        if len(fk_controllers) < 1:
            pm.error(u"FK控制器的选择集里面为空")

        pm.select(fk_controllers)

        options = (";;"
                   "targetTime=3;"
                   "option=insert;"
                   "match=string;;"
                   "selected=selectedOnly;"
                   "search=;"
                   "replace=;"
                   "prefix=%s:;"
                   "suffix=;" % namespace_prefix)

        atom_namespace = self.atom_file.split("/")[
            len(self.atom_file.split("/")) - 1].strip(".atom")

        cmds.file(
            self.atom_file,
            i=True,
            type="atomImport",
            ra=True,
            namespace=atom_namespace,
            options=options)

        print "Done!"
