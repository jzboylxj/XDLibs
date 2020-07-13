# coding=utf-8
import os

import common
from pymel import core as pm

reload(common)


class TransferAnimTool(common.Singleton):
    """
    动画传递工具

    将旧版的表情动画传递到新版表情控制器面板上面的一次性工具

    """

    def __init__(self):
        super(TransferAnimTool, self).__init__()

        self.template_path = ""
        self.namespace = ""

        self.initialize()
        self.show()

    def show(self):
        if pm.window("transferAnimTool", ex=True):
            pm.deleteUI("transferAnimTool")
        pm.window(
            "transferAnimTool",
            title=u"动画传递助手",
            cc=lambda *args: self.close_main_window())
        form_layout = pm.formLayout()

        layout = pm.columnLayout(adj=1, rs=5)
        pm.textFieldButtonGrp(
            "templateTextField",
            label=u"模板文件",
            bl=u"指定文件",
            cw3=[70, 200, 100],
            adj=2,
            text=self.template_path,
            bc=lambda *args: self.load_template_file())
        pm.textFieldGrp(
            "namespaceTextField",
            label="Namespace:",
            cw2=[70, 200],
            adj=2,
            text=self.namespace,
            cc=lambda *args: self.set_namespace())
        pm.button(label=u"传递动画!", c=lambda *args: self.transfer_anim())
        pm.setParent("..")

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (layout, 'top', 10),
                (layout, 'left', 10),
                (layout, 'right', 10),
                (layout, 'bottom', 10),
                # (btn, 'left', 10),
                # (btn, 'right', 10),

                # (output_frame, 'left', 10),
                # (output_frame, 'right', 10),
                # (output_frame, 'bottom', 10),
            ],
            attachControl=[
                # (btn, 'top', 5, layout),
                # (output_frame, 'top', 5, btn),
                # (file_export_list_frame, 'bottom', 5, export_options_frame),
                # (export_options_frame, 'bottom', 5, execute_button),
            ])

        pm.showWindow("transferAnimTool")

    def close_main_window(self):
        pm.optionVar(sv=('transferAnimToolTemplatePath', self.template_path))
        pm.optionVar(sv=('transferAnimToolNamespace', self.namespace))

    def initialize(self):
        """
        初始化数据

        从MAYA的保存的属性数据里面获取一些值

        :return:
        """
        if pm.optionVar(q='transferAnimToolTemplatePath'):
            self.template_path = pm.optionVar(
                q='transferAnimToolTemplatePath')

        if pm.optionVar(q='transferAnimToolNamespace'):
            self.namespace = pm.optionVar(
                q='transferAnimToolNamespace')

    def load_template_file(self):
        json_location = pm.fileDialog2(
            dialogStyle=2, fileMode=1, okc=u"选择模板配置文件")
        if json_location:
            pm.textFieldButtonGrp(
                'templateTextField', e=True, text=json_location[0])
            self.template_path = json_location[0]
        return

    def set_namespace(self):
        self.namespace = pm.textFieldGrp(
            "namespaceTextField", q=True, text=True)

    def transfer_anim(self):
        dict_data = common.read_json(file_path=self.template_path)
        print dict_data
        # print self.namespace
        source_attrs = dict_data.keys()
        print source_attrs
        for source_attr in source_attrs:
            source_anim_curves = pm.PyNode(
                "%s%s" % (self.namespace, source_attr)).inputs()
            if len(source_anim_curves)>0:
                target_anim_curve = source_anim_curves[0].name()
                # print target_anim_curve
                # print source_attr.split(".")[0]
                # print dict_data[source_attr].split(".")[0]
                target_anim_curve = target_anim_curve.replace(
                    source_attr.split(".")[0],
                    dict_data[source_attr].split(".")[0])

                new_anim_curve = pm.duplicate(
                    source_anim_curves[0],
                    name=target_anim_curve)

                pm.connectAttr(
                    "%s.output" % new_anim_curve[0],
                    "%s%s" % (self.namespace, dict_data[source_attr]),
                    f=True)

                print "Done!"

        return


class TemplateBuilder(common.Singleton):
    """
    属性传递模板创建工具

    传递属性工具依赖属性模板（JSON）文件，
    这个模板文件里面包含数据来源（source）对象控制器的名字和属性，
    接受数据的目标（target）对象控制器的名字和属性

    """

    def __init__(self):
        super(TemplateBuilder, self).__init__()

        self.output_path = ""
        self.namespace = ""
        self.output_items = []

        self.initialize()
        self.show()

    def initialize(self):
        """
        初始化数据

        从MAYA的保存的属性数据里面获取一些值

        :return:
        """
        if pm.optionVar(q='transferOutputPath'):
            self.output_path = pm.optionVar(
                q='transferOutputPath')

        if pm.optionVar(q='transferNamespace'):
            self.namespace = pm.optionVar(
                q='transferNamespace')

    def show(self):
        if pm.window("templateBuilder", ex=True):
            pm.deleteUI("templateBuilder")
        pm.window(
            "templateBuilder",
            title=u"模板创建助手", cc=lambda *args: self.close_main_window())
        form_layout = pm.formLayout()

        mode_options_grp = self.mode_options_grp()

        layout = pm.rowColumnLayout(nc=2, w=520)
        self.source_attr_list_column()
        self.target_attr_list_column()
        pm.setParent("..")

        btn = pm.button(
            label=u"自动比对", w=504,
            c=lambda *args: self.comparison_attrs())

        output_frame = self.template_item_list()

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (mode_options_grp, 'top', 10),
                (mode_options_grp, 'left', 10),
                (layout, 'left', 10),
                (btn, 'left', 10),
                (output_frame, 'left', 10),
                (output_frame, 'bottom', 10)],
            attachControl=[
                (layout, 'top', 5, mode_options_grp),
                (btn, 'top', 5, layout),
                (output_frame, 'top', 5, btn)])

        pm.showWindow("templateBuilder")

    def template_item_list(self):
        frame_layout = pm.frameLayout(label="Output Frame", mh=5, w=504)
        pm.textFieldGrp(
            "namespaceField",
            adj=2, label="Namespace:",
            cw2=[80, 200],
            text=self.namespace,
            cc=lambda *args: self.set_namespace())
        pm.textFieldButtonGrp(
            "outputPathField",
            label="Output Path:",
            bl="Set Path",
            adj=2,
            text=self.output_path,
            cw3=[80, 200, 100],
            bc=lambda *args: self.set_output_location())
        pm.textScrollList("outputItemScrollList", a=self.output_items)
        pm.popupMenu()
        pm.menuItem(
            label=u"载入数据", c=lambda *args: self.load_dict_data())
        pm.menuItem(
            label=u"移除选择", c=lambda *args: self.remove_selected_item())
        pm.menuItem(
            label=u"移除所有", c=lambda *args: self.remove_all_item())
        pm.button(label="Build", c=lambda *args: self.write_output())
        pm.setParent("..")
        return frame_layout

    def mode_options_grp(self):
        options_grp = pm.optionMenuGrp(
            label=u'模式', cw2=[24, 200], adj=2)
        pm.menuItem(label=u'属性——属性')
        pm.menuItem(label=u'属性——对象')
        return options_grp

    def target_attr_list_column(self):
        pm.columnLayout(adj=1, rs=5)
        pm.text(label=u"Target Object:",
                al="left")
        pm.textField("targetObjectField", w=250)
        pm.textScrollList(
            "targetObjectAttrScrollList",
            sc=lambda *args: self.print_selected_item(
                widget="targetObjectAttrScrollList"),
            dcc=lambda *args: self.append_output_item())
        pm.button(
            "loadTargetBtn",
            label=u"Load Object",
            c=lambda *args: self.load_controller(
                widget="targetObjectField",
                extra_widget="targetObjectAttrScrollList"))
        pm.setParent("..")

    def source_attr_list_column(self):
        pm.columnLayout(adj=1, rs=5)
        pm.text(label=u"Source Object:",
                al="left")
        pm.textField("sourceObjectField", w=250)
        pm.textScrollList(
            "sourceObjectAttrScrollList",
            sc=lambda *args: self.print_selected_item(
                widget="sourceObjectAttrScrollList"))
        pm.button(
            "loadSourceBtn",
            label=u"Load Object",
            c=lambda *args: self.load_controller(
                widget="sourceObjectField",
                extra_widget="sourceObjectAttrScrollList"))
        pm.setParent("..")

    @staticmethod
    def remove_selected_item():
        selected_item = pm.textScrollList('outputItemScrollList', q=True,
                                          si=True)
        for item in selected_item:
            pm.textScrollList('outputItemScrollList', e=True, ri=item)
        # self.output_files = pm.textScrollList(
        #     'outputItemScrollList', q=True, ai=True)

    @staticmethod
    def remove_all_item():
        pm.textScrollList('outputItemScrollList', e=True, ra=True)
        # self.output_files = pm.textScrollList(
        #     'outputItemScrollList', q=True, ai=True)

    @staticmethod
    def load_controller(widget=None, extra_widget=None):
        controller = pm.ls(sl=True)
        if len(controller) > 1 or len(controller) < 1:
            pm.error(u"请选择单个控制器")
        else:
            pm.textField(widget, e=True, text=controller[0])

        attr_list = pm.listAttr(controller[0], k=True)
        pm.textScrollList(extra_widget, e=True, ra=True)
        pm.textScrollList(extra_widget, e=True, a=attr_list)

    @staticmethod
    def append_output_item():
        # todo: bug fix - 属性应该是一对一，当前是一对多，后续版本应该强制验证

        namespace = pm.textFieldGrp("namespaceField", q=True, text=True)

        source_controller = pm.textField(
            "sourceObjectField", q=True, text=True)
        if namespace in source_controller:
            source_controller = source_controller.split(":")[1]
        key = "%s.%s" % (
            source_controller,
            pm.textScrollList(
                "sourceObjectAttrScrollList", q=True, si=True)[0]
        )

        target_controller = pm.textField(
            "targetObjectField", q=True, text=True)
        if namespace in target_controller:
            target_controller = target_controller.split(":")[1]
        value = "%s.%s" % (
            target_controller,
            pm.textScrollList(
                "targetObjectAttrScrollList", q=True, si=True)[0]
        )

        item = "%s:%s" % (key, value)
        print item

        current_items = pm.textScrollList(
            "outputItemScrollList", q=True, ai=True)
        if item not in current_items:
            pm.textScrollList("outputItemScrollList", e=True, a=item)

        print "--------------"

    def set_namespace(self):
        self.namespace = pm.textFieldGrp("namespaceField", q=True, text=True)

    def set_output_location(self):
        output_path = pm.fileDialog2(
            dialogStyle=2,
            fileFilter="JSON File (*.json);;",
            fileMode=0, okc=u"保存文件")
        if output_path:
            pm.textFieldButtonGrp(
                "outputPathField", e=True,
                text=output_path[0])
            self.output_path = output_path[0]
        return

    def close_main_window(self):
        pm.optionVar(sv=('transferOutputPath', self.output_path))
        pm.optionVar(sv=('transferNamespace', self.namespace))

    def write_output(self):
        output_map = {}

        output_items = pm.textScrollList(
            "outputItemScrollList", q=True, ai=True)
        for output_item in output_items:
            key, value = output_item.split(":")
            print key, value
            output_map[key] = value

        common.write_json(dict_data=output_map, file_path=self.output_path)

        print "Done!"

    def load_dict_data(self):
        item_list = []
        if os.path.isfile(self.output_path):
            dict_data = common.read_json(file_path=self.output_path)
            for item_key in dict_data.keys():
                item_list.append("%s%s:%s%s" % (
                    self.namespace,
                    item_key,
                    self.namespace,
                    dict_data[item_key]))
            pm.textScrollList("outputItemScrollList", e=True, a=item_list)

    @staticmethod
    def print_selected_item(widget=None):
        print pm.textScrollList(widget, q=True, si=True)

    @staticmethod
    def comparison_attrs():
        source_attrs = pm.textScrollList(
            "sourceObjectAttrScrollList", q=True, ai=True)
        target_attrs = pm.textScrollList(
            "targetObjectAttrScrollList", q=True, ai=True)

        comparison_attrs = list(
            set(source_attrs).intersection(set(target_attrs)))
        print comparison_attrs

        current_items = pm.textScrollList(
            "outputItemScrollList", q=True, ai=True)

        namespace = pm.textFieldGrp("namespaceField", q=True, text=True)

        source_controller = pm.textField(
            "sourceObjectField", q=True, text=True)
        if namespace in source_controller:
            source_controller = source_controller.split(":")[1]

        target_controller = pm.textField(
            "targetObjectField", q=True, text=True)
        if namespace in target_controller:
            target_controller = target_controller.split(":")[1]

        for attr in comparison_attrs:
            key = "%s.%s" % (source_controller, attr)
            value = "%s.%s" % (target_controller, attr)
            item = "%s:%s" % (key, value)
            if item not in current_items:
                pm.textScrollList("outputItemScrollList", e=True, a=item)
