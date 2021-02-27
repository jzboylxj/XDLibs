# coding: utf-8

#############################################
# GLOBAL
#############################################
import pymel.core as pm
from pymel.core import datatypes
import json

import maya.OpenMaya as om


def addCurve(parent,
             name,
             points,
             close=False,
             degree=3,
             m=datatypes.Matrix()):
    u"""Create a NurbsCurve with a single subcurve.

    Arguments:
        parent (dagNode): Parent object.
        name (str): Name
        positions (list of float): points of the curve in a one dimension array
            [point0X, point0Y, point0Z, 1, point1X, point1Y, point1Z, 1, ...].
        close (bool): True to close the curve.
        degree (bool): 1 for linear curve, 3 for Cubic.
        m (matrix): Global transform.

    Returns:
        dagNode: The newly created curve.
    """
    if close:
        points.extend(points[:degree])
        knots = range(len(points) + degree - 1)
        node = pm.curve(n=name, d=degree, p=points, per=close, k=knots)
    else:
        node = pm.curve(n=name, d=degree, p=points)

    if m is not None:
        node.setTransformation(m)

    if parent is not None:
        parent.addChild(node)

    return node


def set_color(node, color):
    u"""Set the color in the Icons.

    Arguments:
        node(dagNode): The object
        color (int or list of float): The color in index base or RGB.


    """
    # on Maya version.
    # version = mgear.core.getMayaver()

    if isinstance(color, int):

        for shp in node.listRelatives(shapes=True):
            shp.setAttr("overrideEnabled", True)
            shp.setAttr("overrideColor", color)
    else:
        for shp in node.listRelatives(shapes=True):
            shp.overrideEnabled.set(1)
            shp.overrideRGBColors.set(1)
            shp.overrideColorRGB.set(color[0], color[1], color[2])
