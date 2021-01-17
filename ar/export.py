#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/22 13:56
# @Author  : Li XiaoJun
# @Site    :
# @File    : export.py

from imp import reload

import maya.cmds as cmds
from pymel import core as pm
from animation import common

reload(common)


manager_version = 0.1


class ExportUI(common.Singleton):

    def __init__(self):
        super(ExportUI, self).__init__()

        self.output_files = None
        self.output_path = ""

        self.anim_set = None

        self.create_window()
        self.create_menu()
        self.create_layout()

    def create_window(self):
        window = "ARExporter"

        if pm.window(window, ex=True):
            pm.deleteUI(window)
        pm.window(window, t=u"ARExporter %s" % manager_version, mb=True,
                  cc=lambda *args: self._closed_window_cmd())

        pm.formLayout("ExportUIMainLayout")
        pm.setParent("ExportUIMainLayout")

        pm.showWindow(window)
        return window

    def _closed_window_cmd(self):
        pass

    def create_menu(self):
        pm.menu(label=u"File", tearOff=True)
        pm.menuItem(label=u"Append Export Files", c=lambda *args: self._append_file())

    def create_layout(self):
        label = pm.text(label="File list", al="left", p="ExportUIMainLayout", w=200)
        self.file_list_control = pm.textScrollList(p="ExportUIMainLayout", w=200)
        bake_field = pm.textFieldButtonGrp("ARExporterBakeField",
                                           label="Bake Anim Set",
                                           bl="Anim Set", adj=2, cw3=[82, 100, 100],
                                           cat=[(2, "left", 5), (3, "left", 5)],
                                           text="bake_anim_set",
                                           bc=lambda *args: self._set_anim_set_field())
        output_path = pm.textFieldButtonGrp("ARExporterOutputPath",
                                            label="Output Path",
                                            bl=u"Setting Path",
                                            adj=2,
                                            cw3=[82, 100, 100],
                                            cat=[(2, "left", 5), (3, "left", 5)],
                                            text=self.output_path,
                                            bc=lambda *args: self._set_output_location())
        add_btn = pm.button(label=u"Export Files", p="ExportUIMainLayout", w=200,
                            c=lambda *args: self._export_file())

        pm.formLayout(
            "ExportUIMainLayout", edit=True,
            attachForm=[
                (label, 'top', 10),
                (label, 'left', 10),
                (label, 'right', 10),
                (self.file_list_control, 'left', 10),
                (self.file_list_control, 'right', 10),
                (bake_field, 'left', 10),
                (bake_field, 'right', 10),
                (output_path, 'left', 10),
                (output_path, 'right', 10),
                (add_btn, 'left', 10),
                (add_btn, 'right', 10),
                (add_btn, 'bottom', 10),
            ],
            attachControl=[
                (self.file_list_control, 'top', 5, label),
                (self.file_list_control, 'bottom', 5, bake_field),
                (bake_field, 'bottom', 5, output_path),
                (output_path, 'bottom', 5, add_btn),
            ])

        return

    def _append_file(self):
        multiple_filters = (
            "Maya Files (*.ma *.mb);;"
            "Maya ASCII (*.ma);;"
            "Maya Binary (*.mb);;"
            "FBX Files (*.fbx);;"
        )
        current_export_list = pm.textScrollList(self.file_list_control, q=True, ai=True)
        export_files = pm.fileDialog2(
            fileFilter=multiple_filters, dialogStyle=2, fileMode=4, okc=u"添加")
        if export_files:
            for export_file in export_files:
                if export_file not in current_export_list:
                    pm.textScrollList(
                        self.file_list_control, edit=True, append=export_file)

        self.output_files = pm.textScrollList(self.file_list_control, q=True, ai=True)
        return True

    def _set_anim_set_field(self):
        pm.textFieldButtonGrp("ARExporterBakeField", e=True, text=pm.ls(sl=True)[0])
        self.anim_set = pm.textFieldButtonGrp("ARExporterBakeField", q=True, text=True)
        return self.anim_set

    def _set_output_location(self):
        output_location = pm.fileDialog2(
            dialogStyle=2, fileMode=3, okc=u"选择文件夹")
        if output_location:
            pm.textFieldButtonGrp('ARExporterOutputPath', e=True, text=output_location[0])
            self.output_path = output_location[0]
        return

    def _export_file(self):
        for export_file in self.output_files:
            # 新建场景，打开指定场景
            cmds.file(new=True, force=True)
            # cmds.file(export_file, o=True)
            cmds.file(export_file, o=True)
            file_name = cmds.file(q=1, sceneName=True, shortName=True).split('.')[0]
            print (file_name + ' already open!')

            defaults = ['UI', 'shared']

            def num_children(ns):
                return ns.count(':')

            namespaces = [ns for ns in cmds.namespaceInfo(lon=True, r=True) if ns not in defaults]
            # We want to reverse the list, so that namespaces with more children are at the front of the list.
            namespaces.sort(key=num_children, reverse=True)
            for ns in namespaces:
                print("{}:export".format(ns))

                if not pm.objExists("{}:export".format(ns)):
                    print(u"没有找到{}:export，即将跳过循环".format(ns))
                    continue

                # todo 导入文件
                # refs = cmds.ls(type='reference')
                # if "sharedReferenceNode" in refs:
                #     refs.remove('sharedReferenceNode')
                # for i in refs:
                #     if "_UNKNOWN_REF_NODE_" not in i:
                #         rFile = cmds.referenceQuery(i, f=True)
                #         print i, rFile
                #     cmds.file(rFile, importReference=True)
                rFile = cmds.referenceQuery("{}RN".format(ns), f=True)
                print(u"即将导入文件:{}".format(rFile))
                cmds.file(rFile, importReference=True)

                print(u"开始烘焙动画")
                self.bake_anim(namespace=ns)

                del_set = "{}:Del".format(ns)
                del_items = pm.sets(del_set, q=True)
                # 删除相关节点
                for item in del_items:
                    print(u"删除元素{}".format(item))
                    pm.delete(item)

                # todo 删除命名空间前缀
                if namespaces.index(ns)+1 < len(namespaces):
                    parent_ns = namespaces[namespaces.index(ns)+1]
                    cmds.namespace(mv=[ns, parent_ns], f=True)
                    cmds.namespace(rm=ns)
                else:
                    cmds.namespace(mv=[ns, ":"], f=True)
                    cmds.namespace(rm=ns)

                # 导出文件
                if len(namespaces) > 1:
                    output_file = "{}/{}_{}.fbx".format(self.output_path, file_name, ns)
                else:
                    output_file = "{}/{}.fbx".format(self.output_path, file_name)

                pm.select("export")
                cmds.file(output_file, f=True, options="v=0;", type="FBX export", pr=True, es=True)

        pm.log()
        return

    def bake_anim(self, namespace=None):
        # 烘焙动画
        bake_sets = []
        set_name = pm.textFieldButtonGrp("ARExporterBakeField", q=True, text=True)

        anim_set = "{}:{}".format(namespace, set_name)

        if pm.objExists(anim_set):
            bake_sets = pm.sets(anim_set, q=True)
            if len(bake_sets) < 1:
                pm.error(u"选择集{}里面为空".format(anim_set))
            else:
                time_range = self.anim_range()
                pm.bakeResults(bake_sets, simulation=True,
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
        else:
            pm.error(u"缺少{}".format(anim_set))

    def anim_range(self):
        start_time = pm.playbackOptions(q=True, min=True)
        end_time = pm.playbackOptions(q=True, max=True)
        return [start_time, end_time]

    def get_namespace(self):
        namespace_list = pm.namespaceInfo(an=True, lon=True)
        namespace_list.remove(":UI")
        namespace_list.remove(":shared")
        namespace_item = namespace_list[0]
        return namespace_item.split(":")[1]


def show_window():
    export_window = ExportUI()
    return export_window
