# coding: utf-8

from pymel import core as pm

from animation import common


def mirror_position(source_field="LF_", target_field="RT_"):
    if len(pm.ls(sl=True)) < 1:
        pm.error("")
    else:
        for item in pm.ls(sl=True):
            target = ""
            translate = item.translate.get()
            target = item.replace(source_field, target_field)
            pm.PyNode(target).translate.set(translate)
    return


def mouth_bind_jnt_grp_translate_bc_connect(bind_jnt_grp="", old_min=0.0, old_max=0.0):
    lf_lip_sew_ctrl_follicle_shape = pm.PyNode(
        "LF_Mouth_01_LipSew_Ctrl_FollicleShape")
    rt_lip_sew_ctrl_follicle_shape = pm.PyNode(
        "RT_Mouth_01_LipSew_Ctrl_FollicleShape")

    set_range = pm.createNode(
        "setRange", name=bind_jnt_grp.replace("_Grp", "_LipSew_SR"))
    lf_lip_sew_ctrl_follicle_shape.attr("parameterU").connect(
        "{}.value.valueX".format(set_range.controller_name()))
    rt_lip_sew_ctrl_follicle_shape.attr("parameterU").connect(
        "{}.value.valueY".format(set_range.controller_name()))
    set_range.attr("oldMinX").set(old_min)
    set_range.attr("oldMinY").set(old_min)
    set_range.attr("oldMaxX").set(old_max)
    set_range.attr("oldMaxY").set(old_max)

    adl_node = pm.createNode(
        "addDoubleLinear", name=bind_jnt_grp.replace("_Grp", "_Jnt_ADL"))
    set_range.attr("outValueX").connect(adl_node.attr("input1"))
    set_range.attr("outValueY").connect(adl_node.attr("input2"))

    cmp_node = pm.createNode(
        "clamp", name=bind_jnt_grp.replace("_Grp", "_LipSew_CMP"))
    adl_node.attr("output").connect(cmp_node.attr("inputR"))

    pma_node = pm.createNode(
        "plusMinusAverage", name=bind_jnt_grp.replace("_Grp", "_LipSew_PMA"))
    cmp_node.attr("outputR").connect(pma_node.attr("input1D[1]"))
    pma_node.attr("input1D[0]").set(1.0)
    pma_node.attr("output1D").connect("{}.blender".format(
        bind_jnt_grp.replace("_Grp", "_Translate_BC")))
    return


def connect_targets_spec_attr(source="", source_attr="", targets=None, target_attrs=None):
    if target_attrs is None:
        target_attrs = []
    if targets is None:
        targets = []

    for target in targets:
        for target_attr in target_attrs:
            pm.PyNode(source).attr(source_attr).connect("{}.{}".format(target, target_attr))
    return


def follicle_shape_out_for_parent(follicle_shape):
    u"""将毛囊形节点的两个属性：输出平移和输出旋转，
    连接到它的父节点（位移节点）的平移和旋转属性上

    :param follicle_shape: 毛囊形节点
    :return: None
    """
    parent = pm.PyNode(follicle_shape).getParent()
    pm.PyNode(follicle_shape).attr("outTranslate").connect(parent.translate)
    pm.PyNode(follicle_shape).attr("outRotate").connect(parent.rotate)
    return


def check_constraint(target, source):
    u"""检查约束状态

    :param target: 被约束目标
    :param source: 约束目标
    :return: bool True or False
    """
    target_inputs = list(set(pm.PyNode(target).inputs()))
    if target_inputs:
        for target_input in target_inputs:
            if target_input.type() in ["parentConstraint", "pointConstraint", "scaleConstraint", "aimConstraint",
                                       "orientConstraint"]:
                if target in list(set(target_input.inputs())) and source in list(set(target_input.inputs())):
                    return True
                else:
                    return False
    else:
        return False


def make_follicle_work_on_surface(surface, follicle, param_u=0.0, param_v=0.0):
    u"""让毛囊在曲面上能够起作用（工作）

    :param surface: 曲面
    :param follicle: 毛囊
    :param param_u: 参数 U
    :param param_v: 参数 V
    :return: None
    """
    surface_shape = pm.PyNode(surface).getShape()
    follicle_shape = pm.PyNode(follicle).getShape()
    surface_shape.attr("local").connect(follicle_shape.attr("inputSurface"))
    surface_shape.attr("worldMatrix[0]").connect(follicle_shape.attr("inputWorldMatrix"))
    follicle_shape.attr("parameterU").set(param_u)
    follicle_shape.attr("parameterV").set(param_v)
    return


def imported_object(file_path):
    u"""返回导入到场景里面的新对象

    :return: list of new object
    """
    imported = cmds.file(file_path, ignoreVersion=True, i=True, type="mayaBinary", rnn=True)
    for transform_node in imported:
        if pm.PyNode(transform_node).type() == "transform":
            return transform_node


def point_on_curve_position(curve, parameter):
    u"""获取曲线上cv点的位置信息

    :param curve: 曲线的名字
    :param parameter: 曲线上的参数值
    :return: Returns the (x,y,z) position of curve at parameter.
    """
    return pm.pointOnCurve(curve, pr=parameter, p=True)


def yellow_component(name="", shape_type="", translate=(0, 0, 0), parent_node=None, have_loc=False, have_jnt=False):
    u"""黄色的基础控制器组件

    黄色的控制器一般用来作为模块的细节控制器或次级控制器

    :param name: 名字
    :param shape_type: 控制器的节点类型，例如nurbsPlane，locator, joint, sphere, cone
    :param translate: 位移
    :param parent_node: 父节点
    :param have_loc: 在父节点下是否创建loc
    :return: grp
    """
    if shape_type == "nurbsPlane":
        pm.nurbsPlane(name=name, p=[0, 0, 0], ax=[0, 0, 1], w=1, lr=1, d=3, u=1, v=1, ch=1)
    if shape_type == "locator":
        pm.spaceLocator(name=name)
    if shape_type == "joint":
        pm.select(cl=True)
        pm.joint(name=name)
    if shape_type == "sphere":
        pm.sphere(name=name, p=[0, 0, 0], ax=[0, 1, 0],
                  ssw=0, esw=360, r=0.3, d=3, ut=0, tol=0.01, s=4, nsp=2, ch=1)
    if shape_type == "cone":
        pm.cone(name=name, p=[0, 0, 0], ax=[-1, 0, 0],
                ssw=0, esw=360, r=0.45, hr=2, d=1, ut=0, tol=0.01, s=4, nsp=1, ch=0)

    pm.parent(
        pm.createNode("transform", name="{}_02_Grp".format(name)),
        pm.createNode("transform", name="{}_Grp".format(name))
    )

    pm.parent(name, "{}_02_Grp".format(name))

    if have_loc:
        pm.parent(pm.spaceLocator(name="{}_Roll_Loc".format(name)), "{}_Grp".format(name))

    if have_jnt:
        pm.select(cl=True)
        jnt = pm.joint(name="{}_Jnt".format(name))
        pm.parent(jnt, name)

    pm.PyNode("{}_Grp".format(name)).translate.set(translate)

    if parent_node is not None:
        if pm.objExists(parent_node):
            pm.parent("{}_Grp".format(name), parent_node)

    return "{}_Grp".format(name)


def cyan_control(name="", shape_type="sphere", translate=(0, 0, 0), parent_node=None):
    u"""蓝色的基础控制器组件

    蓝色的控制器一般用来作为模块的主控制器

    :return:
    """
    base_ctrl = None
    if shape_type == "sphere":
        base_ctrl = pm.sphere(name=name, p=[0, 0, 0], ax=[0, 1, 0],
                              ssw=0, esw=360, r=1, d=1, ut=0, tol=0.01, s=4, nsp=2, ch=0)
    pm.parent(base_ctrl, pm.createNode("transform", name="{}_Grp".format(name)))

    pm.PyNode("{}_Grp".format(name)).translate.set(translate)

    if parent_node is not None:
        if pm.objExists(parent_node):
            pm.parent("{}_Grp".format(name), parent_node)

    return "{}_Grp".format(name)


def cyan_locator_grp(name, translate=(0, 0, 0), parent_node=None):
    u"""子层级为locator的组

    :param name: locator的名字
    :param translate: 组的位移信息
    :param parent_node: 父节点
    :return: grp
    """
    loc = pm.spaceLocator(name=name)
    grp = pm.createNode("transform", name="{}_Grp".format(name))
    pm.PyNode(grp).translate.set(translate)
    pm.parent(loc, grp)

    if parent_node is not None:
        if pm.objExists(parent_node):
            pm.parent(grp, parent_node)

    return grp


def xd_follicle_node(name, worldMatrixInput=None, surfaceInput=None, paramUInput=None, paramVInput=None,
                     outTranslateToParent=True, outRotateToParent=True, parentNode=None):
    u"""毛囊体

    :param name:
    :param worldMatrixInput:
    :param surfaceInput:
    :param paramUInput:
    :param paramVInput:
    :param outTranslateToParent:
    :param outRotateToParent:
    :param parentNode:
    :return:
    """
    follicle = pm.rename(pm.createNode("follicle").getParent(), name)

    if worldMatrixInput is not None:
        pm.connectAttr(worldMatrixInput, follicle.getShape().attr("inputWorldMatrix"))

    if surfaceInput is not None:
        pm.connectAttr(surfaceInput, follicle.getShape().attr("inputSurface"))

    if paramUInput is not None:
        pm.connectAttr(paramUInput, follicle.getShape().attr("parameterU"))

    if paramVInput is not None:
        pm.connectAttr(paramVInput, follicle.getShape().attr("parameterV"))

    if outTranslateToParent:
        pm.PyNode(follicle).getShape().attr("outTranslate").connect(pm.PyNode(follicle).translate)

    if outRotateToParent:
        pm.PyNode(follicle).getShape().attr("outRotate").connect(pm.PyNode(follicle).rotate)

    if parentNode is not None:
        if not pm.objExists(parentNode):
            pm.createNode("transform", name=parentNode)

        pm.parent(follicle, parentNode)

    return follicle


def jnt_or_control_grp(name, object_type="joint", parent_node=None, have_loc=False, have_jnt=False):
    u"""骨骼组或控制器组

    :param name:
    :param object_type: 可选项：joint,plane,tours,locator,sphere,cylinder
    :param parent_node:
    :param have_loc:
    :return: grp
    """
    pm.select(cl=True)

    if object_type == "joint":
        pm.joint(name=name),
    if object_type == "plane":
        pm.nurbsPlane(name=name, p=[0, 0, 0], ax=[0, 0, 1], w=1, lr=0.6, d=1, u=1, v=1, ch=0),
    if object_type == "tours":
        pm.torus(name=name, p=[0, 0, 0], ax=[0, 0, 1],
                 ssw=0, esw=360, msw=360, r=1, hr=0.5, d=3, ut=0, tol=0.01, s=8, nsp=4, ch=1),
    if object_type == "locator":
        pm.spaceLocator(name=name)
    if object_type == "sphere":
        pm.sphere(name=name, p=[0, 0, 0], ax=[0, 1, 0], ssw=0, esw=360, r=1, d=3, ut=0, tol=0.01, s=4, nsp=2, ch=1)
    if object_type == "cylinder":
        pm.cylinder(name=name, p=[0, 0, 0], ax=[0, 0, 1],
                    ssw=0, esw=360, r=1, hr=2, d=3, ut=0, tol=0.01, s=8, nsp=1, ch=1)

    pm.parent(name, pm.createNode("transform", name="{}_Grp".format(name)))

    if have_loc:
        loc = pm.spaceLocator(name=name.replace('_Jnt', "_Loc"))
        pm.parent(loc, name)

    if have_jnt:
        pm.select(cl=True)
        pm.joint(name="{}_Jnt".format(name))
        pm.parent("{}_Jnt".format(name), name)

    if parent_node is not None:
        pm.parent("{}_Grp".format(name), parent_node)
        pm.PyNode("{}_Grp".format(name)).translate.set([0, 0, 0])
        pm.PyNode("{}_Grp".format(name)).rotate.set([0, 0, 0])
    return pm.PyNode("{}_Grp".format(name))


def control_grp_have_joint(name, object_type="plane", parent_node=None, jnt_vis=False):
    u"""包含子骨骼的控制器组

    :param name: 控制器名
    :param object_type: 控制器的样式
    :param parent_node: 父节点
    :return: 控制器组
    """
    grp = pm.createNode("transform", name="{}_Grp".format(name))
    if object_type == "plane":
        pm.parent(pm.nurbsPlane(name=name, p=[0, 0, 0], ax=[0, 0, 1], w=1, lr=1, d=1, u=1, v=1, ch=0), grp)
    pm.select(cl=True)
    jnt = pm.joint(name="{}_Jnt".format(name))
    jnt.visibility.set(jnt_vis)
    pm.parent(jnt, name)
    if parent_node is not None:
        pm.parent(grp, parent_node)
        grp.translate.set([0, 0, 0])
        grp.rotate.set([0, 0, 0])
        grp.scale.set([1, 1, 1])
    return grp


def custom_show_channel(target, attr_list=None):
    u"""自定义通道栏里面的属性，

    :param target:
    :param attr_list:
    :return:
    """
    if attr_list is None:
        attr_list = []
    attrs_in_cb = pm.listAttr(pm.PyNode(target), k=True)
    for attr in attrs_in_cb:
        if attr not in attr_list:
            pm.PyNode(target).attr(attr).set(lock=True, k=False, cb=False)
    return True


def ctrl_null_grp(name, parent_node=None):
    null = pm.createNode("transform", name=name)
    null_grp = pm.createNode("transform", name="{}_Grp".format(name))
    pm.parent(null, null_grp)

    if parent_node is not None:
        pm.parent(null_grp, parent_node)
        null_grp.translate.set([0, 0, 0])

    return null_grp


def chain_ctrl_null_grp(name, segment=3, parent_node=None):
    u"""子节点包含3个空节点的组

    :param name:
    :param segment:
    :param parent_node:
    :return: null grp
    """
    null = pm.createNode("transform", name=name)
    null_grp = pm.createNode("transform", name="{}_Grp".format(name))
    pm.parent(null, null_grp)

    for index in range(1, segment):
        null_seg = pm.createNode("transform", name="{}_{}_Grp".format(name, "{0:02d}".format(index + 1)))
        if index == 1:
            pm.parent(null_seg, null_grp)
        else:
            pm.parent(null_seg, "{}_{}_Grp".format(name, "{0:02d}".format(index)))

    if parent_node is not None:
        pm.parent(null_grp, parent_node)
        null_grp.translate.set([0, 0, 0])

    return null_grp


def symmetry_surface(source, target):
    u"""对称surface

    :param source:
    :param target:
    :return:
    """
    num_u = pm.PyNode(source).getShape().attr("degreeU").get() + pm.PyNode(source).getShape().attr("spansU").get()
    num_v = pm.PyNode(source).getShape().attr("degreeV").get() + pm.PyNode(source).getShape().attr("spansV").get()

    for index_u in range(0, num_u):
        for index_v in range(0, num_v):
            source_position = pm.pointPosition('{}.cv[{}][{}]'.format(source, index_u, index_v), w=True)
            pm.move(source_position[0] * -1, source_position[1], source_position[2],
                    pm.PyNode("{}.cv[{}][{}]".format(target, index_u, index_v)))
    return True


def drag_to_group_and_field(target, field="", group=None):
    pm.textFieldButtonGrp(field, e=True, text=target)
    if group is not None:
        pm.parent(target, group)
    return


def dm_node(node_name, matrix_input="", translate_output="", rotate_output=""):
    u"""decomposeMatrix节点

    :param node_name: 节点名字
    :param matrix_input: 输入矩阵的属性
    :param translate_output: output_translate输出的属性
    :param rotate_output: out_rotate输出的属性
    :return: dm_node
    """
    dm_node = pm.createNode("decomposeMatrix", name=node_name)
    pm.Attribute(matrix_input).connect(dm_node.attr("inputMatrix"), f=True)
    dm_node.attr("outputTranslate").connect(translate_output)
    dm_node.attr("outputRotate").connect(rotate_output)
    return dm_node


def mp_node(node_name, geometry_path_input="", all_coordinates_output=""):
    u"""motion path节点

    :param node_name: 节点名字
    :param geometry_path_input: 连接geometryPath属性的外部属性
    :param all_coordinates_output: allCoordinates属性输出的外部属性
    :return: mp_node
    """
    mp_node = pm.createNode("motionPath", name=node_name)
    mp_node.attr("uValue").set(0)

    u'''
    关掉参数化长度。1位关闭，0为开启
    如果处于开启状态，motion path节点输出的对象位置会根据曲线的实际弧长进行计算
    如果处于关闭状态，motion path节点输出的对象位置会根据曲线的实际弧长乘以参数的百分比进行计算
    '''
    mp_node.attr("fractionMode").set(1)

    pm.Attribute(geometry_path_input).connect(mp_node.attr('geometryPath'))
    pm.PyNode(mp_node).attr("allCoordinates").connect(all_coordinates_output)
    return mp_node


class Creator(common.Singleton):

    def __init__(self):
        super(Creator, self).__init__()

        self.module_name = ""

    def proxy(self):
        pass

    def build_module(self):
        pass


def get_object_in_field(field):
    sel_object = pm.ls(sl=True)[0]
    pm.textFieldButtonGrp(field, e=True, text=sel_object)
    return