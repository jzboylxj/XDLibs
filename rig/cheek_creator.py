from pymel import core as pm
from rig.main import Creator, yellow_component


class CheekCreator(Creator):
    def __init__(self):
        super(CheekCreator, self).__init__()

        self.module_name = "Cheek_01"

    def update_init(self):
        pass

    def proxy(self):
        if not pm.objExists("Proxy_Grp"):
            pm.createNode("transform", name="Proxy_Grp")

        if pm.objExists("Proxy_Cheek_Grp"):
            pm.error("Proxy_Cheek_Grp was exists!")
        else:
            pm.createNode("transform", name="Proxy_Cheek_Grp", p="Proxy_Grp")

        seg = 5
        for index in range(1, seg + 1):
            pm.parent(pm.spaceLocator(name="LF_proxyCheek{}Loc".format(
                "{0:02d}".format(index))), "Proxy_Cheek_Grp")

        pm.PyNode("LF_proxyCheek01Loc").translate.set([3, 1.2, -1.4])
        pm.PyNode("LF_proxyCheek02Loc").translate.set([1.9, 3.1, -0.23])
        pm.PyNode("LF_proxyCheek03Loc").translate.set([3.81, 4.0, -1.3])
        pm.PyNode("LF_proxyCheek04Loc").translate.set([1.156, 0.181, 0])
        pm.PyNode("LF_proxyCheek05Loc").translate.set([0.229, 4, -0.469])

        print("Build proxy done!")
        return

    def mirror_proxy(self):
        seg = 5
        for index in range(0, 5):
            lf_proxy_loc = "LF_proxyCheek{}Loc".format(
                "{0:02d}".format(index + 1))
            translate = pm.PyNode(lf_proxy_loc).translate.get()
            rotate = pm.PyNode(lf_proxy_loc).rotate.get()

            rt_proxy_loc = lf_proxy_loc.replace("LF", "RT")
            pm.spaceLocator(name=rt_proxy_loc)
            pm.parent(rt_proxy_loc, "Proxy_Cheek_Grp")
            pm.PyNode(rt_proxy_loc).translate.set(
                [translate[0] * -1, translate[1], translate[2]])
            pm.PyNode(rt_proxy_loc).rotate.set(
                [rotate[0], rotate[1] * -1, rotate[2] * -1])
            pm.PyNode(rt_proxy_loc).scale.set([-1, 1, 1])

            pm.textFieldButtonGrp("xdMouthCreatorRightCheek{}ProxyField".format("{0:02d}".format(index + 1)),
                                  e=True,
                                  text=rt_proxy_loc)
        return

    def build_module(self):
        self.build_deformer_grp()

        # todo 缺少微表情

        return

    def build_deformer_grp(self):
        cheeck_num = 5
        for side in ["LF", "RT"]:
            prefix = "{}_{}".format(side, self.module_name)

            deformer_grp = "{}_Deformer_Grp".format(prefix)
            if not pm.objExists(deformer_grp):
                pm.createNode("transform", name=deformer_grp, p="Deformer_Grp")

            cheek_jnt_group = "{}_Jnt_Grp".format(prefix)
            if not pm.objExists(cheek_jnt_group):
                pm.createNode("transform", name=cheek_jnt_group, p=deformer_grp)

            control_grp = "{}_Grp".format(prefix)
            if not pm.objExists(control_grp):
                pm.createNode("transform", name=control_grp, p="Head_02_Grp")

            control_main_grp = "{}_Main_Grp".format(prefix)
            if not pm.objExists(control_main_grp):
                pm.createNode("transform", name=control_main_grp, p=control_grp)

            for index in range(1, cheeck_num + 1):
                proxy_loc = "{}_proxyCheek{}Loc".format(side, "{0:02d}".format(index))

                cheek_ctrl = "{}_{}_Ctrl".format(prefix, "{0:02d}".format(index))
                cheek_ctrl_grp = yellow_component(name=cheek_ctrl, shape_type="sphere", parent_node=control_main_grp)
                pm.delete(pm.parentConstraint(proxy_loc, cheek_ctrl_grp, mo=False))
                pm.delete(pm.scaleConstraint(proxy_loc, cheek_ctrl_grp, mo=False))

                cheek_jnt = "{}_{}_Ctrl_Jnt".format(prefix, "{0:02d}".format(index))
                cheek_jnt_grp = yellow_component(name=cheek_jnt, shape_type="joint", parent_node=cheek_jnt_group)
                pm.delete(pm.parentConstraint(cheek_ctrl_grp, cheek_jnt_grp, mo=False))
                if side == "RT":
                    pm.PyNode(cheek_jnt_grp).scaleZ.set(-1)
                    pm.rotate(cheek_jnt_grp, 180, 0, 180, r=True, os=True, fo=True)

                pm.PyNode(cheek_ctrl).translate.connect(pm.PyNode(cheek_jnt).translate)
                pm.PyNode(cheek_ctrl).rotate.connect(pm.PyNode(cheek_jnt).rotate)
                pm.PyNode(cheek_ctrl).scale.connect(pm.PyNode(cheek_jnt).scale)

        return