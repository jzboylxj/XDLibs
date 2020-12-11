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


def ar_export():
    # 新建一个空组作为代理loc的根目录
    anim_proxy_grp = "ARAnimProxyGrp"
    if pm.objExists(anim_proxy_grp):
        pm.error(u"场景中已经存在{}".format(anim_proxy_grp))
    else:
        pm.createNode("transform", name=anim_proxy_grp)

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

        if "Shape" in item.name():
            source = item.replace("Eye", "Eye_01")
            source = source.replace("Anim", "Ctrl")
            pm.parentConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

        if "Eye" in item.name() and "Shape" not in item.name() and "Eyeball" not in item.name():
            source = item.replace("Eye", "Eye_01")
            source = source.replace("Anim", "Jnt")
            print(source, pm.PyNode(proxy[1]).getParent())
            print(pm.objExists(source), pm.objExists(pm.PyNode(proxy[1]).getParent()))
            pm.orientConstraint(source, pm.PyNode(proxy[1]).getParent(), mo=True)

    return
