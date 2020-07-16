# coding=utf-8
"""
安装器

# Author: Li Xiao Jun
# Create Date: 2019/12/10 17:25
# Project: baladodo
# Version: 0.1

"""
from __future__ import absolute_import, division, print_function

__author__ = 'Li Xiao Jun'
__version__ = '0.1'

import os
import sys

try:
    import maya.cmds as cmds
    import maya.mel as mel

    isMaya = True
except ImportError:
    isMaya = False


def onMayaDroppedPythonFile(*args, **kwargs):
    """for Maya2017.3+"""
    pass


def _onMayaDropped():
    # srcPath = os.path.join(os.path.dirname(__file__), 'scripts')
    srcPath = os.path.join(os.path.dirname(__file__))

    # iconPath = os.path.join(srcPath, 'studiolibrary', 'resource', 'icons',
    #                         'icon.png')

    srcPath = os.path.normpath(srcPath)
    # iconPath = os.path.normpath(iconPath)

    # if not os.path.exists(iconPath):
    #     raise IOError('Cannot find ' + iconPath)

    for path in sys.path:
        if os.path.exists(path + '/__init__.py'):
            cmds.warning('Bak Library is already installed at ' + path)

    command = '''
# -----------------------------------
# XiuDan Technology Library
# -----------------------------------

import os
import sys

if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')

if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')

from animation import helper
reload(helper)
helper.JsonManager()
'''.format(path=srcPath)

    shelf = mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = cmds.tabLayout(shelf, query=True, selectTab=True)

    cmds.shelfButton(
        command=command,
        annotation='Json管理器',
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"Json管理器",
        label=u'Json管理器'
    )

    cmds.shelfButton(
        command=('''
# -----------------------------------
# XiuDan Technology Library
# -----------------------------------
import os
import sys

if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')

if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')

from animation import helper

reload(helper)

helper.ExportFBXMaster()
''').format(path=srcPath),
        annotation='Export FBX Master',
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"ExportFBX",
        label=u'ExpFBX'
    )

    cmds.shelfButton(
        command=('''
# -----------------------------------
# Bak Studio Library
# -----------------------------------
import os
import sys

if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')

if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')

from animation import helper

reload(helper)

helper.ChannelBoxSaver().show()
''').format(path=srcPath),
        annotation='将控制器的一些属性写入JSON文件保存',
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"写JSON",
        label=u'写JSON'
    )

    cmds.shelfButton(
        command=('''
# -----------------------------------
# Bak Studio Library
# -----------------------------------
import os
import sys

if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')
if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')

from animation import common

reload(common)

common.set_time_unit(unit='ntsc')
''').format(path=srcPath),
        annotation='将场景的时间制式修改为NTSC',
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"NTSC",
        label=u'NTSC'
    )

    cmds.shelfButton(
        command=('''
# -----------------------------------
# Bak Studio Library
# -----------------------------------
import os
import sys

if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')

if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')

from animation import helper

reload(helper)

helper.ChannelBoxWriter()

''').format(path=srcPath),
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"读Json",
        annotation=u"读取JSON文件数据的工具",
        label=u"读Json",
    )

    cmds.shelfButton(
        command=('''
# -----------------------------------
# Bak Studio Library
# -----------------------------------
import os
import sys

if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')

if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')

from animation import helper

reload(helper)

helper.CustomAttrHelper()
''').format(path=srcPath),
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"strData",
        annotation=u"为控制器添加自定义信息的工具",
        label=u"strData",
    )

#     cmds.shelfButton(
#         command=('''
# # -----------------------------------
# # Bak Studio Library
# # -----------------------------------
# import os
# import sys

# if not os.path.exists(r'{path}'):
#     raise IOError(r'The source path "{path}" does not exist!')

# if r'{path}' not in sys.path:
#     sys.path.insert(0, r'{path}')

# from pymel import core as pm
# from doPipline import doFace

# reload(doFace)

# doFace.ConnectorBuilder()

# ''').format(path=srcPath),
#         sourceType='Python',
#         parent=parent,
#         image="pythonFamily.png",
#         image1="pythonFamily.png",
#         style="iconOnly",
#         imageOverlayLabel=u"表情增强",
#         annotation=u"比克非凡工具集",
#         label=u"比克工具集",
#     )

#     cmds.shelfButton(
#         command=('''
# # -----------------------------------
# # Bak Studio Library
# # -----------------------------------
# import os
# import sys

# if not os.path.exists(r'{path}'):
#     raise IOError(r'The source path "{path}" does not exist!')

# if r'{path}' not in sys.path:
#     sys.path.insert(0, r'{path}')

# from pymel import core as pm
# from doManager import doBatchHelper

# reload(doBatchHelper)

# try:
#     batch_playblast.close()
# except:
#     pass

# batch_playblast = doBatchHelper.BatchPlayblast()
# batch_playblast.show()

#     ''').format(path=srcPath),
#         sourceType='Python',
#         parent=parent,
#         image="pythonFamily.png",
#         image1="pythonFamily.png",
#         style="iconOnly",
#         imageOverlayLabel=u"拍频",
#         annotation=u"比克非凡工具集",
#         label=u"比克工具集",
#     )

    # print("\n// Studio Library has been added to current shelf.")


if isMaya:
    _onMayaDropped()
