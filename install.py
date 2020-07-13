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
    import pymel.core as pm

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
# Bak Studio Library
# -----------------------------------

import os
import sys

if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')

if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')
    
from XDLibs.animation import helper
reload(helper)
helper.JsonManager()
'''.format(path=srcPath)

    shelf = mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = cmds.tabLayout(shelf, query=True, selectTab=True)

    cmds.shelfButton(
        command=command,
        annotation='Batch Helper',
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"自动",
        label=u'自动'
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
    
from doManager import doBatchHelper
reload(doBatchHelper)

global export_manager

try:
    export_manager.close()
except:
    pass

export_manager = doBatchHelper.AnimExportWnd()
export_manager.show()
''').format(path=srcPath),
        annotation='Animation Export Helper',
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"出画",
        label=u'出画'
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
   
from doManager import doBox

reload(doBox)

doBox.clean_unknown_node()
''').format(path=srcPath),
        annotation='Animation Export Helper',
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"优化",
        label=u'优化'
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

from v1.baladodo import doExportManager

reload(doExportManager)

doExportManager.ExportManager()
''').format(path=srcPath),
        annotation='角色输出工具',
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"角色输出",
        label=u'角色输出'
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
    
from doManager import doAnimatorHelper
reload(doAnimatorHelper)

global animator_helper

try:
    animator_helper.close()
except:
    pass

animator_helper = doAnimatorHelper.AnimatorHelper()
animator_helper.show()

''').format(path=srcPath),
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"动画助手",
        annotation=u"包含了一些提供给动画师的工具集",
        label=u"动画助手",
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
   
from pymel import core as pm
from doManager import doToolBox

reload(doToolBox)

doToolBox.ToolBox()
''').format(path=srcPath),
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"比克",
        annotation=u"比克非凡工具集",
        label=u"比克工具集",
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
   
from pymel import core as pm
from doPipline import doFace

reload(doFace)

doFace.ConnectorBuilder()

''').format(path=srcPath),
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"表情增强",
        annotation=u"比克非凡工具集",
        label=u"比克工具集",
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

from pymel import core as pm
from doManager import doBatchHelper

reload(doBatchHelper)

try:
    batch_playblast.close()
except:
    pass

batch_playblast = doBatchHelper.BatchPlayblast()
batch_playblast.show()

    ''').format(path=srcPath),
        sourceType='Python',
        parent=parent,
        image="pythonFamily.png",
        image1="pythonFamily.png",
        style="iconOnly",
        imageOverlayLabel=u"拍频",
        annotation=u"比克非凡工具集",
        label=u"比克工具集",
    )

    # print("\n// Studio Library has been added to current shelf.")


if isMaya:
    _onMayaDropped()
