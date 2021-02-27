# coding: utf-8

import pymel.core as pm
import maya.OpenMaya as om
from pymel.core import datatypes

from core import curve, attribute


def cube(parent=None,
         name="cube",
         width=1,
         height=1,
         depth=1,
         color=[0, 0, 0],
         m=datatypes.Matrix(),
         pos_offset=None,
         rot_offset=None):
    """Create a curve with a CUBE shape.

    Arguments:
        parent (dagNode): The parent object of the newly created curve.
        name (str): Name of the curve.
        width (float): Width of the shape.
        height (float): Height of the shape.
        depth (float): Depth of the shape.
        color (int or list of float): The color in index base or RGB.
        m (matrix): The global transformation of the curve.
        pos_offset (vector): The xyz position offset of the curve
            from its center.
        rot_offset (vector): The xyz rotation offset of the curve
            from its center. xyz in radians

    Returns:
        dagNode: The newly created icon.
    """
    lenX = width * 0.5
    lenY = height * 0.5
    lenZ = depth * 0.5

    # p is positive, N is negative
    ppp = datatypes.Vector(lenX, lenY, lenZ)
    ppN = datatypes.Vector(lenX, lenY, lenZ * -1)
    pNp = datatypes.Vector(lenX, lenY * -1, lenZ)
    Npp = datatypes.Vector(lenX * -1, lenY, lenZ)
    pNN = datatypes.Vector(lenX, lenY * -1, lenZ * -1)
    NNp = datatypes.Vector(lenX * -1, lenY * -1, lenZ)
    NpN = datatypes.Vector(lenX * -1, lenY, lenZ * -1)
    NNN = datatypes.Vector(lenX * -1, lenY * -1, lenZ * -1)

    v_array = [ppp, ppN, NpN, NNN, NNp, Npp, NpN, Npp, ppp, pNp, NNp, pNp, pNN,
               ppN, pNN, NNN]

    points = getPointArrayWithOffset(v_array,
                                     pos_offset,
                                     rot_offset)

    node = curve.addCurve(parent, name, points, False, 1, m)

    setcolor(node, color)

    return node


def null(parent=None,
         name="null",
         width=1,
         color=[0, 0, 0],
         m=datatypes.Matrix(),
         pos_offset=None,
         rot_offset=None):
    """Create a curve with a NULL shape.

    Arguments:
        parent (dagNode): The parent object of the newly created curve.
        name (str): Name of the curve.
        width (float): Width of the shape.
        color (int or list of float): The color in index base or RGB.
        m (matrix): The global transformation of the curve.
        pos_offset (vector): The xyz position offset of the curve from
            its center.
        rot_offset (vector): The xyz rotation offset of the curve from
            its center. xyz in radians

    Returns:
        dagNode: The newly created icon.

    """
    dlen = width * .5

    v0 = datatypes.Vector(dlen, 0, 0)
    v1 = datatypes.Vector(-dlen, 0, 0)
    v2 = datatypes.Vector(0, dlen, 0)
    v3 = datatypes.Vector(0, -dlen, 0)
    v4 = datatypes.Vector(0, 0, dlen)
    v5 = datatypes.Vector(0, 0, -dlen)

    points = getPointArrayWithOffset([v0, v1], pos_offset, rot_offset)
    node = curve.addCurve(parent, name, points, False, 1, m)

    points = getPointArrayWithOffset([v2, v3], pos_offset, rot_offset)
    crv_0 = curve.addCurve(parent, name, points, False, 1, m)

    points = getPointArrayWithOffset([v4, v5], pos_offset, rot_offset)
    crv_1 = curve.addCurve(parent, name, points, False, 1, m)

    for crv in [crv_0, crv_1]:
        for shp in crv.listRelatives(shapes=True):
            node.addChild(shp, add=True, shape=True)
        pm.delete(crv)

    setcolor(node, color)

    return node


def guideRootIcon(parent=None,
                  name="root",
                  width=.5,
                  color=[0, 0, 0],
                  m=datatypes.Matrix(),
                  pos_offset=None,
                  rot_offset=None):
    """Create a curve with a ROOT GUIDE shape.

    Note:
        This icon is specially design for **Shifter** root guides

    Arguments:
        parent (dagNode): The parent object of the newly created curve.
        name (str): Name of the curve.
        width (float): Width of the shape.
        color (int or list of float): The color in index base or RGB.
        m (matrix): The global transformation of the curve.
        pos_offset (vector): The xyz position offset of the curve from
            its center.
        rot_offset (vector): The xyz rotation offset of the curve from
            its center. xyz in radians

    Returns:
        dagNode: The newly created icon.

    """
    rootIco = null(parent, name, width, color, m, pos_offset, rot_offset)
    cubeWidth = width / 2.0
    cubeIco = cube(parent,
                   name,
                   cubeWidth,
                   cubeWidth,
                   cubeWidth,
                   color,
                   m,
                   pos_offset,
                   rot_offset)

    for shp in cubeIco.listRelatives(shapes=True):
        rootIco.addChild(shp, add=True, shape=True)
    pm.delete(cubeIco)

    attribute.setNotKeyableAttributes(rootIco)
    rootIco.addAttr("isGearGuide", at="bool", dv=True)
    # Set the control shapes isHistoricallyInteresting
    for oShape in rootIco.getShapes():
        oShape.isHistoricallyInteresting.set(False)

    return rootIco


def getPointArrayWithOffset(point_pos, pos_offset=None, rot_offset=None):
    """Get Point array with offset

    Convert a list of vector to a List of float and add the position and
    rotation offset.

    Arguments:
        point_pos (list of vector): Point positions.
        pos_offset (vector):  The position offset of the curve from its
            center.
        rot_offset (vector): The rotation offset of the curve from its
            center. In radians.

    Returns:
        list of vector: the new point positions

    """
    points = []
    for v in point_pos:
        if rot_offset:
            mv = om.MVector(v.x, v.y, v.z)
            mv = mv.rotateBy(om.MEulerRotation(rot_offset.x,
                                               rot_offset.y,
                                               rot_offset.z,
                                               om.MEulerRotation.kXYZ))
            v = datatypes.Vector(mv.x, mv.y, mv.z)
        if pos_offset:
            v = v + pos_offset

        points.append(v)

    return points


def setcolor(node, color):
    """Set the color in the Icons.

    Arguments:
        node(dagNode): The object
        color (int or list of float): The color in index base or RGB.


    """
    # TODO: configure this funcion to work with RGB or Index color base
    # on Maya version.
    # version = mgear.core.getMayaver()

    curve.set_color(node, color)
