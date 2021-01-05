#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/12/11 15:36
# @Author  : Li XiaoJun
# @Site    :
# @File    : ar_export.py

from pymel import core as pm

bake_anim_set = "bake_anim_set"


def loc_grp(name):
    # 创建一个空节点作为组
    pm.createNode("transform", name="{}_Grp".format(name))
    pm.createNode("transform", name="{}_Con".format(name), p="{}_Grp".format(name))
    # 创建一个loc
    pm.spaceLocator(name=name)
    # 调整层级关系
    pm.parent(name, "{}_Con".format(name))
    return ["{}_Grp".format(name), name]


def UI():
    if pm.window("AnimationProxyUI", ex=True):
        pm.deleteUI("AnimationProxyUI")

    pm.window("AnimationProxyUI", mb=True)
    pm.columnLayout(adj=1)

    pm.showWindow("AnimationProxyUI")

    return


def animation_proxy():
    u"""为AR2.0版本的头部绑定创建代理体组，用来连接绑定动画用绑定组和导出到引擎里面的绑定组
    """

    # 新建一个空组作为代理loc的根目录
    anim_proxy_grp = "ARAnimProxyGrp"
    if pm.objExists(anim_proxy_grp):
        pm.error(u"场景中已经存在{}".format(anim_proxy_grp))
    else:
        pm.createNode("transform", name=anim_proxy_grp)
        pm.setAttr("{}.visibility".format(anim_proxy_grp), 0)

    # 获取输出动画的集，然后遍历集的成员为它们创建locator，并建立约束
    if not pm.objExists(bake_anim_set):
        pm.error(u"场景中缺少{}，这个集里面包含了需要驱动骨骼所要的locator")

    head_proxy = "Head_Anim_Proxy"
    all_item = pm.sets(bake_anim_set, q=True)
    if "Head_Anim" in all_item:
        head_proxy = loc_grp(name=head_proxy)
        pm.parent(head_proxy[0], anim_proxy_grp)
        pm.delete(pm.parentConstraint("Head_Anim", head_proxy[0], mo=False))
        pm.parentConstraint(head_proxy[1], "Head_Anim", mo=True)
        pm.scaleConstraint(head_proxy[1], "Head_Anim", mo=True)

        pm.parentConstraint("MD_Neck_01_Head_Ctrl", pm.PyNode(head_proxy[1]).getParent(), mo=True)
        pm.scaleConstraint("MD_Neck_01_Head_Ctrl", pm.PyNode(head_proxy[1]).getParent(), mo=True)

        all_item.remove("Head_Anim")

    for item in all_item:
        print(u"开始构建{}的代理体".format(item))
        proxy = loc_grp(name="{}_Proxy".format(item))
        pm.parent(proxy[0], head_proxy[1])
        pm.delete(pm.parentConstraint(item, proxy[0], mo=False))
        pm.parentConstraint(proxy[1], item, mo=True)
        pm.scaleConstraint(proxy[1], item, mo=True)

        if "LF_Brow" in item.name() or "RT_Brow" in item.name():
            source = item.replace("Brow", "Brow_01_Sub")
            source = source.replace("Anim", "Ctrl")
            pm.parentConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

        if "LF_Cheek" in item.name() or "RT_Cheek" in item.name():
            source = item.replace("Cheek", "Cheek_01")
            source = source.replace("Anim", "Ctrl")
            pm.parentConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

        if "Nose" in item.name():
            source = item.replace("Nose", "Nose_01")
            source = source.replace("Anim", "Ctrl")
            pm.parentConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

        if "Low_Teeth" in item.name():
            source = item.replace("Low_Teeth", "Mouth_01_Low_Teeth")
            source = source.replace("Anim", "Ctrl")
            pm.parentConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

        if "Up_Teeth" in item.name():
            source = item.replace("Up_Teeth", "Mouth_01_Up_Teeth")
            source = source.replace("Anim", "Ctrl")
            pm.parentConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

        if "Jaw" in item.name() and "Low" not in item.name() and "Line" not in item.name():
            source = item.replace("Jaw", "Mouth_01_Jaw")
            source = source.replace("Anim", "Ctrl")
            pm.parentConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

        if "LowJaw" in item.name():
            source = item.replace("LowJaw", "Mouth_01_Jaw")
            source = source.replace("Anim", "Ctrl")
            print(u"{}存在:{}".format(source, pm.objExists(source)))
            pm.parentConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

        if "Shape" in item.name():
            source = item.replace("Eye", "Eye_01")
            source = source.replace("Anim", "Ctrl")
            pm.parentConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

        if "Eye" in item.name() and "Shape" not in item.name() and "Eyeball" not in item.name():
            source = item.replace("Eye", "Eye_01")
            source = source.replace("Anim", "Jnt")
            local_proxy = loc_grp(name="{}_Proxy".format(source))
            pm.parent(local_proxy[0], anim_proxy_grp)
            pm.delete(pm.parentConstraint(item, local_proxy[0], mo=False))
            pm.parentConstraint(source, local_proxy[1], mo=True)
            pm.PyNode(local_proxy[1]).rotate.connect(pm.PyNode(proxy[1]).rotate)

        if "Eyeball" in item.name():
            source = item.replace("Eyeball_Anim", "Eye_01_Aim_01_Ctrl")
            pm.orientConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

        if "LowLip" in item.name():
            source = item.replace("LowLip", "Mouth_01_LowLip")
            source = source.replace("Anim", "Jnt")
            # print(u"{}存在:{}".format(source, pm.objExists(source)))

            local_proxy = loc_grp(name="{}_Proxy".format(source))
            pm.parent(local_proxy[0], anim_proxy_grp)
            pm.delete(pm.parentConstraint(item, local_proxy[0], mo=False))
            pm.parentConstraint(source, local_proxy[1], mo=True)
            pm.PyNode(local_proxy[1]).translate.connect(pm.PyNode(proxy[1]).translate)

        if "UpLip" in item.name():
            source = item.replace("UpLip", "Mouth_01_UpLip")
            source = source.replace("Anim", "Jnt")
            # print(u"{}存在:{}".format(source, pm.objExists(source)))

            local_proxy = loc_grp(name="{}_Proxy".format(source))
            pm.parent(local_proxy[0], anim_proxy_grp)
            pm.delete(pm.parentConstraint(item, local_proxy[0], mo=False))
            pm.parentConstraint(source, local_proxy[1], mo=True)
            pm.PyNode(local_proxy[1]).translate.connect(pm.PyNode(proxy[1]).translate)

        if "Lip" in item.name() and "Low" not in item.name() and "Up" not in item.name():
            source = item.replace("Lip", "Mouth_01_Lip")
            source = source.replace("Anim", "Jnt")
            # print(u"{}存在:{}".format(source, pm.objExists(source)))

            local_proxy = loc_grp(name="{}_Proxy".format(source))
            pm.parent(local_proxy[0], anim_proxy_grp)
            pm.delete(pm.parentConstraint(item, local_proxy[0], mo=False))
            pm.parentConstraint(source, local_proxy[1], mo=True)
            pm.PyNode(local_proxy[1]).translate.connect(pm.PyNode(proxy[1]).translate)

        # if "Tongue" in item.name():
        #     source = item.replace("Tongue", "Tongue_01")
        #     print("source:{} is existe? {}".format(source, pm.objExists(pm.PyNode(source))))
        #     source = source.replace("FK_Ctrl", "Ctrl")
        #     pm.parentConstraint("MD_LowJaw_Anim_Proxy", pm.PyNode(proxy[1]).getParent(), mo=True)

        if "MD_Brow" in item.name():
            if not pm.isConnected('MD_Brow_01_Sub_01_Jnt.ty', 'MD_Brow_Jnt.ty'):
                pm.PyNode("MD_Brow_01_Sub_01_Jnt").translateY.connect(pm.PyNode("MD_Brow_Jnt").translateY)

    for item in all_item:
        print(u"开始构建{}的代理体".format(item))

        if "Tongue" in item.name():
            # source = item.replace("Tongue", "Tongue_01")
            # source = source.replace("FK_Ctrl", "Ctrl")
            print("tongue source:{}".format(item.name()))
            # MD_Tongue_01_01_FK_Ctrl
            # print("source:{} is existe? {}".format(source, pm.objExists(pm.PyNode(source))))
        #     pm.parentConstraint("MD_LowJaw_Anim_Proxy", pm.PyNode(proxy[1]).getParent(), mo=True)

    return
