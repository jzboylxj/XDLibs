#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/9/21 20:36
# @Author  : Li XiaoJun
# @Site    :
# @File    : mouth.py

from pymel import core as pm
import maya.OpenMaya as om
from itertools import izip

import os
from imp import reload
from animation import common

reload(common)


def get_selection():
    # check if nurbsSurface is selected
    sel = pm.ls(sl=True)

    if not sel:
        pm.warning("select a nurbs surface to ribbonize")
        return

    shapes = sel[0].getShape()

    if shapes and shapes[0].type() == "nurbsSurface":
        surf_tr = sel[0]
    # after changing attributes on "makeNurbPlane" node it stays selected.
    # so instead of raising an error we just get the connected surface
    elif pm.objectType(sel[0]) == "makeNurbPlane" or pm.objectType(
            sel[0]) == "makeNurbCylinder":
        surf_tr = pm.listConnections(
            sel[0] + ".outputSurface", d=True, s=False)[0]
    else:
        pm.warning("dude, that isn't a nurbs surface")
        return

    return surf_tr


def get_bbox_center(obj):
    # get bb of the shape in case there are children
    shapes = pm.listRelatives(obj, s=True)
    cvs = []
    for shape in shapes:
        num_of_cvs = pm.getAttr(shape + ".controlPoints", size=True)
        cvs.append("{}.cv[0:{}]".format(shape, num_of_cvs - 1))

    bbmin = pm.exactWorldBoundingBox(cvs)[:3]
    bbmax = pm.exactWorldBoundingBox(cvs)[3:7]

    mid_point = [(b_max + b_min) / 2 for b_min, b_max in izip(bbmin, bbmax)]

    return mid_point


def param_from_length(curve, count, curve_type="open", space="uv",
                      normalized=True):
    if curve_type == "periodic":
        divider = count
    else:
        divider = count - 1

    if divider == 0:
        divider = 1

    dag = om.MDagPath()
    obj = om.MObject()
    crv = om.MSelectionList()
    crv.add(curve)
    crv.getDagPath(0, dag, obj)

    curve_fn = om.MFnNurbsCurve(dag)
    length = curve_fn.length()

    param = [curve_fn.findParamFromLength(
        i * ((1 / float(divider)) * length)) for i in range(count)]

    if space == "world":
        data = []
        space = om.MSpace.kWorld
        point = om.MPoint()
        for p in param:
            curve_fn.getPointAtParam(p, point, space)
            data.append([point[0], point[1], point[2]])  # world space points
    elif normalized:
        def normalizer(value, old_range, new_range):
            return (value - old_range[0]) * (new_range[1] - new_range[0]) / (
                    old_range[1] - old_range[0]) + new_range[0]

        max_v = pm.getAttr(curve + ".minMaxValue.maxValue")
        min_v = pm.getAttr(curve + ".minMaxValue.minValue")

        # normalized parameters (before i was just dividing p to max_v. but
        # with weird ranges (ie. 1.4281 to 6.98214) the result is of is not
        # as expected. this also could have been fixed by just rebuilding
        # the surface uniformly)
        data = [normalizer(p, [min_v, max_v], [0, 1]) for p in param]
    else:
        data = param

    return data


def set_color(objects, color):
    color_dict = {
        "blue": 6,
        "red": 13,
        "green": 14,
        "mid_blue": 15,
        "yellow": 22,
        "light_green": 23
    }

    if isinstance(objects, list):
        for obj in objects:
            if pm.listRelatives(obj, f=True, s=True) != None:
                shapes = pm.listRelatives(obj, f=True, s=True)
                for shape in shapes:
                    pm.setAttr(shape + ".ove", 1)
                    pm.setAttr(shape + ".ovc", color_dict[color])
            else:
                pm.setAttr(obj + ".ove", 1)
                pm.setAttr(obj + ".ovc", color_dict[color])
    else:
        if pm.listRelatives(objects, f=True, s=True) != None:
            shapes = pm.listRelatives(objects, f=True, s=True)
            for shape in shapes:
                pm.setAttr(shape + ".ove", 1)
                pm.setAttr(shape + ".ovc", color_dict[color])
        else:
            pm.setAttr(objects + ".ove", 1)
            pm.setAttr(objects + ".ovc", color_dict[color])
    return


def ctrl_maker(prefix, ctrl_type, count, deg, sp, name=""):
    if ctrl_type == "cube":
        c1 = pm.curve(p=[(-1.0, 1.0, 1.0), (-1.0, 1.0, -1.0), (1.0, 1.0, -1.0),
                         (1.0, 1.0, 1.0), (-1.0, 1.0, 1.0), (-1.0, -1.0, 1.0),
                         (1.0, -1.0, 1.0), (1.0, -1.0, -1.0),
                         (-1.0, -1.0, -1.0),
                         (-1.0, -1.0, 1.0), (-1.0, -1.0, -1.0),
                         (-1.0, 1.0, -1.0),
                         (1.0, 1.0, -1.0), (1.0, -1.0, -1.0), (1.0, -1.0, 1.0),
                         (1.0, 1.0, 1.0)],
                      k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                      d=1)
    elif ctrl_type == "sphere":
        c1 = pm.circle(d=deg, s=sp, nr=(1, 0, 0), r=1, ch=0)[0]
        c2 = pm.circle(d=deg, s=sp, nr=(0, 1, 0), r=1, ch=0)[0]
        c3 = pm.circle(d=deg, s=sp, nr=(0, 0, 1), r=1, ch=0)[0]
        pm.parent(pm.listRelatives(c2, s=True),
                  pm.listRelatives(c3, s=True), c1, r=True, s=True)
        pm.delete(c2, c3)
    elif ctrl_type == "circle":
        c1 = pm.circle(d=deg, s=sp, nr=(1, 0, 0), r=1, ch=0)[0]

    if name != "":
        name = name + "_"

    controls = [c1]
    for x in range(count - 1):
        controls.append(pm.duplicate(c1))

    for x, ctrl in enumerate(controls):
        controls[x] = pm.rename(ctrl,
                                "{}{}ctrl_{:02d}".format(prefix, name, x + 1))
        shapes = pm.listRelatives(controls[x], f=True, s=True)
        for y, shape in enumerate(shapes):
            pm.rename(shape, "{}Shape{:02d}".format(controls[x], y + 1))

    pm.select(cl=True)

    return controls


def lock_hide(objs, attrs):
    for obj in objs:
        for attr in attrs:
            pm.setAttr(obj + attr, l=True, k=False, cb=False)


def make_fk_controls(prefix, num_of_controls):
    fk_controls = []
    fk_ctrl_off_groups = []

    fk_controls = ctrl_maker(
        prefix, ctrl_type="circle",
        count=num_of_controls - 1, deg=3, sp=8, name="fk")
    fk_ctrl_off_groups = [pm.group(fk_ctrl, n=fk_ctrl + "_offset")
                          for fk_ctrl in fk_controls]
    [pm.xform(fk_ctrl_off_grp, piv=(0, 0, 0), os=True)
     for fk_ctrl_off_grp in fk_ctrl_off_groups]

    for (o, f) in izip(fk_ctrl_off_groups[1:], fk_controls[:-1]):
        pm.parent(o, f)

    return fk_controls, fk_ctrl_off_groups


class XDObject:
    def __init__(self, name):
        self.name = name

    def build(self):
        pass


class RibbonController:
    def __init__(self):
        self.name = None
        self.radius = 1.0
        self.controller = None
        self.constraint_grp = None
        self.controller_grp = None

    def build(self, name, radius=1.0, shape_type='sphere'):
        self.name = name
        self.radius = radius
        if shape_type == 'sphere':
            self.controller = pm.sphere(
                name=self.name,
                p=[0, 0, 0],
                ax=[0, 1, 0],
                ssw=0,
                esw=360,
                r=self.radius,
                d=3, ut=0, tol=0.01, s=4, nsp=1, ch=1)[0]
        self.constraint_grp = pm.createNode(
            "transform",
            name="{}_02_Grp".format(self.name))
        self.controller_grp = pm.createNode(
            "transform",
            name="{}_Grp".format(self.name))
        pm.parent(self.controller, self.constraint_grp)
        pm.parent(self.constraint_grp, self.controller_grp)
        return self.controller_grp


class RibbonJoint:
    def __init__(self):
        self.name = None
        self.joint = None
        self.connect_out_grp = None
        self.roll_out_loc = None
        self.joint_grp = None

    def build(self, name, radius=1.0):
        self.name = name
        pm.select(cl=True)
        self.joint = pm.createNode("joint", n=self.name)
        self.joint.attr("radius").set(radius)
        self.connect_out_grp = pm.group(
            n="{}_connect_Grp".format(self.name),
            em=True)
        self.roll_out_loc = pm.spaceLocator(
            name="{}_RollOut_Loc".format(self.name))
        self.roll_out_loc.getShape().attr("localScaleX").set(0.2)
        self.roll_out_loc.getShape().attr("localScaleY").set(0.2)
        self.roll_out_loc.getShape().attr("localScaleZ").set(0.2)
        self.joint_grp = pm.group(
            n="{}_Grp".format(self.name),
            em=True)
        pm.parent(self.joint, self.connect_out_grp)
        pm.parent(self.roll_out_loc, self.connect_out_grp, self.joint_grp)

        return self.joint

    @staticmethod
    def from_joint_get_connect_grp(joint_name):
        connect_grp = "{}_connect_Grp".format(joint_name)
        return pm.PyNode(connect_grp)

    @staticmethod
    def from_joint_get_controller(joint_name):
        controller = joint_name.replace("_ctrl_jnt", "_ctrl")
        return pm.PyNode(controller)


class RibbonPlane:
    def __init__(self):
        self.name = None
        self.num_of_controls = 0
        self.num_of_joints = 0
        self.length = 0
        self.surface = None
        self.param_controls = []
        self.param_joints = []
        self.divider_for_controls = 0

    def build(self, name, num_of_controls, num_of_joints):
        """
        构建一个nurbs用于创建ribbon骨骼和控制器
        :param name: nurbs的名字
        :param num_of_controls: 曲面控制器的数量
        :param num_of_joints: 曲面可以控制的骨骼数量（即：毛囊的数量）
        :return: nurbs
        """
        self.name = name
        self.num_of_controls = num_of_controls
        self.num_of_joints = num_of_joints
        self.surface = pm.nurbsPlane(
            name=self.name,
            p=[0, 0, 0],
            ax=[0, 0, 1],
            w=5,
            lr=0.1,
            d=3,
            u=5,
            v=1,
            ch=1)
        tweak_surface_shapes = self.surface[0].getShapes()[0]
        # 冻结位移变换并删除surface的创造历史节点
        pm.makeIdentity(self.surface[0],
                        t=True, r=True, s=True, apply=True)
        pm.delete(self.surface[0], ch=True)
        # 复制表面曲线以确定方向
        u_curve = pm.duplicateCurve(
            self.surface[0] + ".v[.5]", local=True, ch=0)
        v_curve = pm.duplicateCurve(
            self.surface[0] + ".u[.5]", local=True, ch=0)
        # 删除历史以防万一
        pm.delete(self.surface[0], ch=True)
        u_length = pm.arclen(u_curve)
        v_length = pm.arclen(v_curve)
        # print("u_length:{}".format(u_length))
        # print("v_length:{}".format(v_length))
        if u_length < v_length:
            pm.reverseSurface(self.surface[0], d=3, ch=False, rpo=True)
            pm.reverseSurface(self.surface[0], d=0, ch=False, rpo=True)
        parameter = ".parameterU"
        other_param = ".parameterV"
        u_curve_corr = pm.duplicateCurve(
            self.surface[0] + ".v[.5]", local=True, ch=0)[0]
        # 选择的曲面是周期的还是开放的?(圆柱体或平面)
        curve_type = None
        if (pm.getAttr(tweak_surface_shapes + ".formU") == 2 or
                pm.getAttr(tweak_surface_shapes + ".formV") == 2):
            curve_type = "periodic"
            self.divider_for_controls = self.num_of_controls
        elif (pm.getAttr(tweak_surface_shapes + ".formU") == 0 or
              pm.getAttr(tweak_surface_shapes + ".formV") == 0):
            curve_type = "open"
            self.divider_for_controls = self.num_of_controls - 1
        # -------------------------------------------
        self.param_controls = param_from_length(
            u_curve_corr, self.num_of_controls, curve_type, "uv")
        self.param_joints = param_from_length(
            u_curve_corr, self.num_of_joints, curve_type, "uv")
        self.length = pm.arclen(u_curve_corr)
        pm.delete(u_curve, v_curve, u_curve_corr)

        return self.surface


class MouthModule(common.Singleton):
    def __init__(self):
        super(MouthModule, self).__init__()
        self.prefix = None
        self.num_of_controls = 8
        self.num_of_joints = 12
        self.equal = 1
        self.constrain = 0

        self.deformer_grp = "Mouth_Deformer_Grp"
        self.robbin_surface_grp = "Mouth_Ribbon_Surface_Grp"
        self.up_tweak_surface = "Mouth_Up_Tweak_Surface"
        self.low_tweak_surface = "Mouth_Low_Tweak_Surface"
        self.tweak_jnt_grp = "Mouth_Tweak_Jnt_Grp"
        self.bind_jnt_grp = "Mouth_Bind_Jnt_Grp"
        self.bind_jnt_follicles_grp = "Mouth_Bind_Jnt_Follicles_Grp"

    def build(self, prefix="LF", num_of_controls=8, num_of_joints=12,
              equal=1, constrain=0):
        if not pm.objExists(self.deformer_grp):
            pm.createNode("transform", name=self.deformer_grp)

        self.prefix = prefix
        self.num_of_controls = num_of_controls
        self.num_of_joints = num_of_joints
        self.equal = equal
        self.constrain = constrain

        attrs = [".tx", ".ty", ".tz", ".rx", ".ry",
                 ".rz", ".sx", ".sy", ".sz", ".v"]

        # 开始构建空的组，用于后面整理各类节点
        self._init_framework()

        # -----------------------------------------------------
        # 开始构建嘴唇部分
        # ["Mouth_Up_Tweak_Surface", "Mouth_Low_Tweak_Surface"]
        for mouth_lip in ["Up", "Low"]:
            # surface_name = "Mouth_{}_Tweak_Surface".format(mouth_lip)
            tweak_surface = RibbonPlane()
            tweak_surface.build(
                name="Mouth_{}_Tweak_Surface".format(mouth_lip),
                num_of_controls=self.num_of_controls,
                num_of_joints=self.num_of_joints)

            # -------------------------------------------------------------
            # 在nurbs表面创建毛囊，这些毛囊会关联蒙皮骨骼的位移旋转，实现次级控制
            fols = []  # 包含表面上所有的follicle shape的列表
            fols_tr = []  # 包含表面上所有的follicle shape的位移节点（父节点）的列表
            bind_joints = []  # bind joint list
            # 骨骼的半径
            bnd_joints_rad = (tweak_surface.length / 60) / (
                    float(self.num_of_joints) / 40)

            for index in range(0, self.num_of_joints):
                if index == 0:
                    fol_name = "LF_Mouth_Lip_jnt_follicle"
                    bind_name = "LF_Mouth_Lip_jnt"
                    if pm.objExists(fol_name):
                        continue
                elif index == num_of_joints - 1:
                    fol_name = "RT_Mouth_Lip_jnt_follicle"
                    bind_name = "RT_Mouth_Lip_jnt"
                    if pm.objExists(fol_name):
                        continue
                elif 0 < index < num_of_joints / 2:
                    fol_name = "LF_Mouth_{}Lip_{:02d}_jnt_follicle".format(
                        mouth_lip, int(num_of_joints / 2) - index
                    )
                    bind_name = "LF_Mouth_{}Lip_{:02d}_jnt".format(
                        mouth_lip, int(num_of_joints / 2) - index)
                else:
                    fol_name = "RT_Mouth_{}Lip_{:02d}_jnt_follicle".format(
                        mouth_lip, abs(int(num_of_joints / 2 - 1) - index)
                    )
                    bind_name = "RT_Mouth_{}Lip_{:02d}_jnt".format(
                        mouth_lip, abs(int(num_of_joints / 2 - 1) - index))

                # fol的节点类型是毛囊的形节点，如果需要对其进行改名，
                # 就需要获取它的位移节点，也就是它的父节点，然后进行重命名
                fol, temp_follicle = self._skin_follicle(
                    fol_name, tweak_surface, index)

                fols_tr.append(temp_follicle)
                fols.append(fol)

                # 在表面创建蒙皮骨骼, 并将骨头放到包囊体的子层级下面，
                # nurbs plane被它的蒙皮骨骼驱动后，这些骨骼也会受到影响，产生位移，
                # 这样就达到了驱动嘴唇的目的
                self._ribbon_joint(bind_joints, bind_name, bnd_joints_rad,
                                   temp_follicle, tweak_surface)

            # ----------------------------------------
            # 创建临时控制偏移用的毛囊组并对齐, 这些毛囊是用来为控制骨骼做定位用的
            temp_follicles_transform_list = self._location_tweak_jnt_follicles(
                equal, tweak_surface)

            # ------------ 建控件和控制关节 -----------------
            self._build_ribbon_controls_and_bind_joints(
                bnd_joints_rad,
                constrain,
                mouth_lip,
                temp_follicles_transform_list,
                tweak_surface)

        self._build_base_ctrl_grp()

        return

    def _ribbon_joint(self, bind_joints, bind_name, bnd_joints_rad,
                      temp_follicle, tweak_surface):
        bind_joint = RibbonJoint()
        bind_joint.build(name=bind_name)
        pm.PyNode(bind_joint.joint).attr("radius").set(bnd_joints_rad)
        bind_joints.append(bind_joint.joint_grp)
        pm.delete(
            pm.parentConstraint(
                temp_follicle,
                bind_joint.joint_grp,
                mo=False))
        pm.parent(bind_joints, self.bind_jnt_grp)
        set_color(bind_joints, "mid_blue")
        pm.parent(tweak_surface.controller_name, self.robbin_surface_grp)

    def _init_framework(self):
        if not pm.objExists(self.robbin_surface_grp):
            pm.group(n=self.robbin_surface_grp, em=True)
        if not pm.objExists(self.tweak_jnt_grp):
            pm.group(n=self.tweak_jnt_grp, em=True)
        if not pm.objExists(self.bind_jnt_grp):
            pm.group(n=self.bind_jnt_grp, em=True)
        if not pm.objExists(self.bind_jnt_follicles_grp):
            pm.group(n=self.bind_jnt_follicles_grp, em=True)

    def _build_ribbon_controls_and_bind_joints(self, bnd_joints_rad, constrain,
                                               mouth_lip,
                                               temp_follicles_transform_list,
                                               tweak_surface):
        tweak_ctrl_grp = None
        if pm.objExists("Mouth_Tweak_Ctrl_Grp"):
            tweak_ctrl_grp = pm.PyNode("Mouth_Tweak_Ctrl_Grp")
        else:
            tweak_ctrl_grp = pm.group(n="Mouth_Tweak_Ctrl_Grp", em=True)
        ctrl_joints = []
        tweak_ctrl_list = []
        tweak_controller_group = []  # 包含嘴唇上的所有次级控制器的组
        tweak_skin_joints = []
        ik_ctrl_scale = (tweak_surface.length / 35) / (
                float(self.num_of_controls) / 5)
        for index in range(0, self.num_of_controls):
            if index == 0:
                controller_name = "LF_Mouth_Tweak_ctrl"
                tweak_skin_joints.append("{}_jnt".format(controller_name))
                if pm.objExists(controller_name):
                    continue
            elif index == self.num_of_controls - 1:
                controller_name = "RT_Mouth_Tweak_ctrl"
                tweak_skin_joints.append("{}_jnt".format(controller_name))
                if pm.objExists(controller_name):
                    continue
            elif 0 < index < self.num_of_controls / 2:
                controller_name = "LF_Mouth_{}Tweak_{:02d}_ctrl".format(
                    mouth_lip,
                    int(self.num_of_controls / 2) - index)
                tweak_skin_joints.append("{}_jnt".format(controller_name))
            else:
                controller_name = "RT_Mouth_{}Tweak_{:02d}_ctrl".format(
                    mouth_lip,
                    abs(int(self.num_of_controls / 2 - 1) - index))
                tweak_skin_joints.append("{}_jnt".format(controller_name))
            # controller_name = (
            #     "{}{}_index:{}".format(prefix, mouth_lip, index))
            controller = RibbonController()
            controller.build(
                name=controller_name,
                radius=ik_ctrl_scale)
            tweak_ctrl_list.append(controller.controller_grp)
            tweak_controller_group.append(controller_name)

            pm.delete(
                pm.parentConstraint(
                    temp_follicles_transform_list[index],
                    controller.controller_grp
                )
            )

            ctrl_joints_rad = bnd_joints_rad
            control_joint = RibbonJoint()
            control_joint.build(
                name="{}_jnt".format(controller_name),
                radius=ctrl_joints_rad)
            pm.delete(
                pm.parentConstraint(
                    temp_follicles_transform_list[index],
                    control_joint.joint_grp
                )
            )
            ctrl_joints.append(control_joint.joint_grp)
        pm.parent(tweak_ctrl_list, tweak_ctrl_grp)
        pm.parent(ctrl_joints, self.tweak_jnt_grp)
        #
        # set_color(controls, "green")
        # set_color(ctrl_joints, "red")
        # pm.parent(ctrl_ofs_grps, ctrl_grp)
        # pm.parent(ctrl_jnt_ofs_grps, ctrl_joints_grp)
        # lock_hide(ctrl_ofs_grps, attrs[:9])
        # lock_hide(ctrl_jnt_ofs_grps, attrs[:9])
        pm.delete(temp_follicles_transform_list)
        # bind the surface to the joints
        nurbs_skin_cluster = pm.skinCluster(
            tweak_skin_joints,
            tweak_surface.controller_name,
            dr=2,
            mi=(self.num_of_controls - 1),
            ns=(self.num_of_controls * 5),
            bm=0,
            n="{}_SC".format(tweak_surface.controller_name))
        pm.skinPercent(
            nurbs_skin_cluster, tweak_surface.controller_name, pruneWeights=0.2
        )
        for skin_joint in tweak_skin_joints:
            skin_joint_grp = RibbonJoint().from_joint_get_connect_grp(
                skin_joint)
            tweak_ctrl = RibbonJoint().from_joint_get_controller(skin_joint)
            if constrain == 1:
                if not skin_joint_grp.translate.isConnected():
                    tweak_ctrl.translate.connect(skin_joint_grp.translate)
            elif constrain == 0:
                if not skin_joint_grp.translate.isConnected():
                    pm.pointConstraint(tweak_ctrl, skin_joint_grp)

    def _location_tweak_jnt_follicles(self, equal, tweak_surface):
        follicle_shape_list = []
        follicles_transform_list = []
        for index in range(self.num_of_controls):
            temp_follicle_shape = pm.createNode("follicle")
            follicle_shape_list.append(temp_follicle_shape)
            follicles_transform_list.append(
                temp_follicle_shape.getParent())

            temp_follicle_shape.attr("outTranslate").connect(
                temp_follicle_shape.getParent().attr("translate"),
                f=True,
            )
            temp_follicle_shape.attr("outRotate").connect(
                temp_follicle_shape.getParent().attr("rotate"),
                f=True,
            )

            tweak_surface.surface[0].getShapes()[0].attr(
                "worldMatrix[0]"
            ).connect(
                temp_follicle_shape.attr("inputWorldMatrix"))

            tweak_surface.surface[0].getShapes()[0].attr(
                "local"
            ).connect(
                temp_follicle_shape.attr("inputSurface"))
        # 骨头的间隔是否等距
        if equal == 1:
            for index, temp_follicle in enumerate(follicle_shape_list):
                pm.setAttr(
                    temp_follicle + ".parameterU",
                    tweak_surface.param_controls[index])
                pm.setAttr(temp_follicle + ".parameterV", 0.5)
        if equal == 0:
            v = 0
            for temp_follicle in follicle_shape_list:
                pm.setAttr(temp_follicle + ".parameterU", v)
                pm.setAttr(temp_follicle + ".parameterV", 0.5)
                v = v + (1.0 / tweak_surface.divider_for_controls)
        return follicles_transform_list

    def _skin_follicle(self, fol_name, tweak_surface, x):
        fol = pm.createNode("follicle")
        fol.visibility.set(1)
        # temp_follicle = pm.listRelatives(fol, p=True)[0]
        temp_follicle = fol.getParent()
        temp_follicle.rename(fol_name)
        # 将毛囊的形节点与它的位移节点连接起来
        # pm.connectAttr(fols[-1] + ".outTranslate",
        #                fols_tr[-1] + ".translate", f=True)
        fol.attr("outTranslate").connect(
            temp_follicle.attr("translate"), f=True)
        # pm.connectAttr(fols[-1] + ".outRotate",
        #                fols_tr[-1] + ".rotate", f=True)
        fol.attr("outRotate").connect(
            temp_follicle.attr("rotate"), f=True)
        # 将毛囊的形节点附着在表面
        pm.connectAttr(
            tweak_surface.surface[0].getShapes()[
                0] + ".worldMatrix[0]",
            # fols[-1] + ".inputWorldMatrix"
            fol.attr("inputWorldMatrix")
        )
        pm.connectAttr(
            tweak_surface.surface[0].getShapes()[0] + ".local",
            # fols[-1] + ".inputSurface"
            fol.attr("inputSurface")
        )
        pm.setAttr(
            # fols[-1] + parameter,
            fol.controller_name() + ".parameterU",
            tweak_surface.param_joints[x])
        pm.setAttr(fol.controller_name() + ".parameterV", 0.5)
        pm.parent(fol, self.bind_jnt_follicles_grp)
        return fol, temp_follicle

    def _build_base_ctrl_grp(self):
        base_ctrl_grp = "Mouth_Base_Ctrl_Grp"
        if not pm.objExists(base_ctrl_grp):
            base_ctrl_grp = pm.group(n=base_ctrl_grp, em=True)
        else:
            base_ctrl_grp = pm.PyNode(base_ctrl_grp)

        # lip_sew_surface = RibbonPlane()
        # lip_sew_surface.build(name=)

        ctrl_list = []
        for ctrl in ["Up", "Low", "LF", "RT"]:
            base_ctrl = RibbonController()
            base_ctrl.build(name="{}_Mouth_01_Ctrl".format(ctrl))
            ctrl_list.append(base_ctrl.controller_grp)

        pm.parent(ctrl_list, base_ctrl_grp)
        return

    def proxy_locator(self, num_of_controls):
        if pm.objExists("proxy_locator_grp"):
            proxy_locator_grp = pm.PyNode("proxy_locator_grp")
        else:
            proxy_locator_grp = pm.createNode(
                "transform", name="proxy_locator_grp")

        self.num_of_controls = num_of_controls

        locator_list = []
        for mouth_lip in ["UpTweak", "LowTweak"]:
            for side in ["LF", "RT"]:
                for index in range(1, int(self.num_of_controls / 2)):
                    locator_list.append(
                        pm.spaceLocator(
                            name="{}_{}_{:02d}_loc".format(
                                side, mouth_lip, index)))
        locator_list.append(pm.spaceLocator(n="LF_Tweak_loc"))
        locator_list.append(pm.spaceLocator(n="RT_Tweak_loc"))

        pm.parent(locator_list, proxy_locator_grp)

        return proxy_locator_grp


def base_window():
    if pm.window("moduleKitCreator", ex=True):
        pm.showWindow("moduleKitCreator")
    else:
        window = pm.window("moduleKitCreator", title="Kit Creator")
        main_layout = pm.columnLayout("moduleKitMainLayout", adj=True)
        pm.showWindow("moduleKitCreator")
        return window, main_layout


class KitCreator(common.Singleton):
    def __init__(self):
        super(KitCreator, self).__init__()

    @staticmethod
    def ribbon_surface():
        main_window, root_layout = base_window()
        layout_list = pm.layout(root_layout, q=True, ca=True)

        if layout_list == 'None':
            pm.deleteUI(layout_list)

        ribbon_frame = pm.frameLayout(
            "moduleKitCreatorRibbonFrame",
            label=u"Ribbon surface options:",
            mw=5,
            mh=5,
            p=root_layout)
        pm.textFieldGrp(label=u"Name: ", p=ribbon_frame)
        pm.intSliderGrp(label=u"Segment: ", p=ribbon_frame)
        pm.setParent(ribbon_frame)
        # layouts = pm.layout(main_window, q=True, ca=True)
        # if type(layouts) != "NoneType":
        #     pm.deleteUI(layouts)
        # else:

        # pm.showWindow(main_window)
        return


class Creator(common.Singleton):
    def __init__(self):
        super(Creator, self).__init__()

        self.module = MouthModule()

        self.show()

    def pre_build_window(self):
        pass

    def menu_list(self):
        """
        工具菜单栏

        :return:
        """
        pm.menu(label=u"Controllers", tearOff=False)
        pm.menuItem(
            label=u"new",
            c=lambda *args: self.new_controller())
        pm.menuItem(divider=True)

        pm.menu(label=u"Kits", tearOff=False)
        pm.menuItem(
            label=u"New Ribbon Surface",
            c=lambda *args: KitCreator().ribbon_surface())
        pm.menuItem(divider=True)

    def show(self):
        """
        显示工具窗口

        :return: window
                """
        self.pre_build_window()

        if pm.window("mouthModuleCreator", ex=True):
            pm.deleteUI("mouthModuleCreator")
        pm.window(
            "mouthModuleCreator",
            t=u"Mouth Module Creator",
            mb=True,
            cc=lambda *args: self._closed_window_cmd())
        self.menu_list()
        main_layout = pm.frameLayout(lv=False, mw=5, mh=5)
        form_layout = pm.formLayout(p=main_layout)
        step1 = pm.text(
            p=form_layout,
            label=u"Step 1: 创建嘴唇控制定位器",
            al="left")
        num_of_control_slider = pm.intSliderGrp(
            "num_of_control_slider",
            p=form_layout,
            field=True,
            label='Number of controls:',
            minValue=5,
            maxValue=10,
            fieldMinValue=4,
            fieldMaxValue=10,
            value=8,
            s=2,
            cw3=[115, 60, 100],
            adj=3)
        num_of_joint_slider = pm.intSliderGrp(
            "num_of_joint_slider",
            p=form_layout,
            field=True,
            label='Number of joints:',
            minValue=4,
            maxValue=24,
            fieldMinValue=4,
            fieldMaxValue=10,
            value=12,
            s=2,
            cw3=[115, 60, 100],
            adj=3)
        location_btn = pm.button(
            p=form_layout,
            label=u"创建定位器",
            c=lambda *args: self.build_proxy_locator())
        sep1 = pm.separator(h=10, p=form_layout)
        step2 = pm.text(
            p=form_layout,
            label=u"Step 2: 调整定位器的控件位置",
            al="left")
        sep2 = pm.separator(h=10, p=form_layout)
        build_btn = pm.button(
            p=form_layout,
            label="Build!",
            c=lambda *args: self.build_module())

        pm.formLayout(
            form_layout, edit=True,
            attachForm=[
                (step1, 'top', 5),
                (step1, 'left', 2),
                (step1, 'right', 2),
                (num_of_control_slider, 'left', 2),
                (num_of_control_slider, 'right', 2),
                (num_of_joint_slider, 'left', 2),
                (num_of_joint_slider, 'right', 2),
                (location_btn, 'left', 2),
                (location_btn, 'right', 2),
                (sep1, 'left', 2),
                (sep1, 'right', 2),
                (step2, 'left', 2),
                (step2, 'right', 2),
                (sep2, 'left', 2),
                (sep2, 'right', 2),
                (build_btn, 'left', 2),
                (build_btn, 'right', 2),
                (build_btn, 'bottom', 2),
            ],
            attachControl=[
                (num_of_control_slider, 'top', 5, step1),
                (num_of_joint_slider, 'top', 5, num_of_control_slider),
                (location_btn, 'top', 5, num_of_joint_slider),
                (sep1, 'top', 5, location_btn),
                (step2, 'top', 5, sep1),
                (sep2, 'top', 5, step2),
                (build_btn, 'top', 5, sep2),
            ])
        pm.showWindow("mouthModuleCreator")

        self.init_system()
        return

    def init_system(self):
        pass

    def _closed_window_cmd(self):
        pass

    def build_proxy_locator(self):
        num_of_controls = pm.intSliderGrp(
            "num_of_control_slider", q=True, v=True)
        self.module.proxy_locator(num_of_controls=num_of_controls)
        return

    def build_module(self):
        # 控制器的数量
        num_of_controls = pm.intSliderGrp(
            "num_of_control_slider", q=True, v=True)
        # 嘴巴蒙皮骨骼的数量
        num_of_joints = 12
        prefix = "Mouth"
        equal = 1
        constrain = 0
        wire = 0
        add_fk = 0

        self.module.build(
            prefix=prefix,
            num_of_controls=num_of_controls,
            num_of_joints=num_of_joints,
            equal=1,
            constrain=0,
        )

        return

    def new_controller(self):
        pass
