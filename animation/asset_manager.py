#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/8/18 14:53
# @Author  : Li XiaoJun
# @Site    : 
# @File    : asset_manager.py
# @Software: PyCharm
'''
ASSET MANAGER

Author: Peppe Russo
All rights reserved (c) 2017

pepperusso.uk
contact.pepperusso@gmail.com

---------------------------------------------------------------------------------------------

INSTALLATION:

Place the assetManager.py in your maya scripts folder and run this code (in python):

import assetManager as am
am.install()

It will ask you to create an icon in the current shelf

To run it simply click the shelf button or run this code (python):

import assetManager as am
am.start("C:/")

You can also put a custom path between the quotes


---------------------------------------------------------------------------------------------

You are using this script on you own risk.
Things can always go wrong, and under no circumstances the author
would be responsible for any damages caused from the use of this software.

---------------------------------------------------------------------------------------------

The coded instructions, statements, computer programs, and/or related
material (collectively the "Data") in these files are subject to the terms
and conditions defined by
Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License:
   http://creativecommons.org/licenses/by-nc-nd/4.0/
   http://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
   http://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.txt

---------------------------------------------------------------------------------------------
'''

__version__ = '1.0.1'
__author__ = 'Peppe Russo'

#############################################################################################

import maya.cmds as cmds
import os
from os.path import dirname
import shutil
from glob import glob
import maya.mel as mel
import urllib
import random

# Qt
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

# Logger
import logging

logging.basicConfig()
logger = logging.getLogger('AssetManager')
logger.setLevel(logging.INFO)

MAYA_APP_DIR = os.environ['MAYA_APP_DIR']


def start(path=MAYA_APP_DIR):
    if path == "":
        path = MAYA_APP_DIR

    try:
        checkUpdates()
    except:
        logger.debug("Can't check updates")
        pass


    logger.debug("Starting")

    ### DOWNLOAD FOLDER ICON
    url = "http://pepperusso.uk/scripts/assetManager/"

    # Get current maya version
    version = cmds.about(version=True)

    # Download Icon
    appPath = MAYA_APP_DIR

    folderImg = os.path.join(appPath, version, "prefs/icons", "AM_folder.png")
    unknownImg = os.path.join(appPath, version, "prefs/icons", "AM_unknown.png")

    try:
        if not os.path.isfile(folderImg):
            urllib.urlretrieve(url+"AM_folder.png", folderImg)
        if not os.path.isfile(unknownImg):
            urllib.urlretrieve(url+"AM_unknown.png", unknownImg)
    except:
        logger.info("Can't download icons. Please download them manually from the following links and paste them in Documents\maya\VERSION\prefs\icons")
        logger.info("http://pepperusso.uk/scripts/assetManager/AM_folder.png")
        logger.info("http://pepperusso.uk/scripts/assetManager/AM_unknown.png")


    ## START
    w = AssetManager(path)
    w.show()

def isHiDPI():
    screenH = QtWidgets.QDesktopWidget().screenGeometry().height()
    screenW = QtWidgets.QDesktopWidget().screenGeometry().width()
    if screenH < 1081 or screenW < 1921:  # Non HIDPI
        return False
    else:
        return True

class AssetManager(QtWidgets.QMainWindow):
    def __init__(self, path=MAYA_APP_DIR):
        super(AssetManager, self).__init__()
        windowName = 'AssetManagerWindow'
        # Delete if exists
        if cmds.window(windowName, exists=True):
            cmds.deleteUI(windowName)
            logger.debug('Deleted previous UI')
        else:
            logger.debug('No previous UI exists')
            pass

        # Get Maya window and parent the controller to it
        mayaMainWindow = {o.objectName(): o for o in QtWidgets.qApp.topLevelWidgets()}["MayaWindow"]
        self.setParent(mayaMainWindow)
        self.setWindowFlags(QtCore.Qt.Window)

        self.setWindowTitle('Asset Manager')
        self.setObjectName(windowName)
        if isHiDPI():
            self.resize(600, 600)
        else:
            self.resize(300, 300)
        self.buildUI()
        self.populate(path)



    def buildUI(self):
        # Main widget
        widget = QtWidgets.QWidget(self)
        self.setCentralWidget(widget)

        # Main Layout
        layout = QtWidgets.QGridLayout()
        widget.setLayout(layout)



        # Directory above button
        upBtn = QtWidgets.QPushButton()
        upBtn.setIcon(upBtn.style().standardIcon(QtWidgets.QStyle.SP_FileDialogToParent))
        upBtn.clicked.connect(self.getParentDir)
        layout.addWidget(upBtn,0,0,1,1)

        # Current directory
        self.currentDirTxt = QtWidgets.QLineEdit()
        self.currentDirTxt.setStyleSheet("border: 2px groove black; border-radius: 4px;")
        self.currentDirTxt.returnPressed.connect(lambda: self.populate(self.currentDirTxt.text()))
        layout.addWidget(self.currentDirTxt,0,1,1,1)

        # New Folder button
        newDirBtn = QtWidgets.QPushButton()
        newDirBtn.setIcon(newDirBtn.style().standardIcon(QtWidgets.QStyle.SP_FileDialogNewFolder))
        newDirBtn.clicked.connect(self.newFolder)
        layout.addWidget(newDirBtn,0,2)



        # Search field
        self.searchFld = QtWidgets.QLineEdit()
        self.searchFld.setPlaceholderText('Search...')
        self.searchFld.textChanged.connect(self.search)
        layout.addWidget(self.searchFld,1,0,1,2)
        self.searchFld.setFocus()

        # New Asset button
        newBtn = QtWidgets.QPushButton()
        newBtn.setIcon(newBtn.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton))
        newBtn.clicked.connect(self.save)
        layout.addWidget(newBtn,1,2)

        # List Widget

        ## HiDPI Fix
        if isHiDPI():
            size = 128
            padding = 4
        else:
            size = 64
            padding = 16

        self.listWidget = QtWidgets.QListWidget()

        self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)
        self.listWidget.setIconSize(QtCore.QSize(size, size))
        self.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.listWidget.setMovement(QtWidgets.QListWidget.Static) # disable drag and drop
        self.listWidget.setGridSize(QtCore.QSize(size + padding, size + padding))

        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # enable multiple selection
        self.listWidget.itemDoubleClicked.connect(self.load)

        layout.addWidget(self.listWidget,2,0,1,3)

        # RIGHT CLICK MENU
        self.listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.openMenu)

    def changeListStyle(self):
        listStyle = self.listWidget.viewMode()
        if listStyle == QtWidgets.QListWidget.IconMode:
            self.listWidget.setViewMode(QtWidgets.QListWidget.ListMode)
        elif listStyle == QtWidgets.QListWidget.ListMode:
            self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)

    def getParentDir(self):
        parentDir = dirname(self.userPath)
        self.populate(parentDir)

    def populate(self, userPath=MAYA_APP_DIR):

        if not os.path.isdir(userPath):
            logger.error("Directory doesn't exist: "+ self.userPath)
            self.populate(self.userPath)
            return

        self.userPath = os.path.abspath(userPath)

        logger.debug("Reading path: " + userPath)


        self.currentDirTxt.setText(self.userPath)

        # FINDING ASSETS
        self.assets = {}
        folders = {}
        files = {}

        ## FIND FOLDERS
        path = os.path.join(userPath, "*/")

        for folder in glob(path):
            name = os.path.basename(os.path.normpath(folder))
            folders = {'name': name, 'path': folder, 'type': 'folder'}

            self.assets[name] = folders

        ## FIND MAYA FILES
        for f in os.listdir(userPath):
            if f.endswith(".ma"):
                name = os.path.splitext(f)[0]
                path = os.path.join(userPath, f)
                screenshot = os.path.join(userPath, name + ".jpg")

                if not os.path.isfile(screenshot):
                    screenshot = os.path.join(os.environ['MAYA_APP_DIR'], cmds.about(version=True), "prefs/icons", "AM_unknown.png")

                files = {'name': name, 'path': path, 'screenshot': screenshot, 'type': 'maya'}

                self.assets[name] = files


        # POPULATING LISTWIDGET

        self.listWidget.clear()

        for name in self.assets:
            item = QtWidgets.QListWidgetItem(name)

            if self.assets[name]['type'] == 'folder':
                item.setIcon(QtGui.QIcon(os.path.join(os.environ['MAYA_APP_DIR'], cmds.about(version=True), "prefs/icons", "AM_folder.png"))) # Folder icon
                item.setData(QtCore.Qt.UserRole, 'folder')

            elif self.assets[name]['type'] == 'maya':
                icon = QtGui.QIcon(self.assets[name]['screenshot'])
                item.setIcon(icon)
                item.setData(QtCore.Qt.UserRole, 'maya')


            self.listWidget.addItem(item)

        self.listWidget.sortItems()
        self.listWidget.setCurrentRow(0) # select first item, to fix right click not showing at startup

        # if directory empty
        if self.listWidget.count() == 0:
            pass
            # TODO: show text saying empty

    def openMenu(self, position):
        currentItem = self.listWidget.currentItem()
        if not currentItem:
            return

        menu = QtWidgets.QMenu(self)

        importAction = menu.addAction("Import")
        moveAction = menu.addAction("Move to")
        renameAction = menu.addAction("Rename")
        deleteAction = menu.addAction("Delete")
        menu.addSeparator()
        newFileAction = menu.addAction("New Asset")
        newFolderAction = menu.addAction("New Folder")
        menu.addSeparator()
        browseAction = menu.addAction("Browse Folder")
        refreshAction = menu.addAction("Refresh List")
        changeStyleAction = menu.addAction("Change list style")

        if currentItem.data(QtCore.Qt.UserRole) == 'folder':
            importAction.setVisible(False)
            #moveAction.setVisible(False)

        action = menu.exec_(self.listWidget.mapToGlobal(position))

        if action == importAction:
            self.load()
        elif action == moveAction:
            self.moveItem()
        elif action == renameAction:
            self.rename()
        elif action == deleteAction:
            self.delete()
        elif action == newFileAction:
            self.save()
        elif action == newFolderAction:
            self.newFolder()
        elif action == refreshAction:
            self.populate(self.userPath)
        elif action == changeStyleAction:
            self.changeListStyle()
        elif action == browseAction:
            self.openExplorer()

    def search(self):
        items = self.listWidget.findItems(self.searchFld.text(), QtCore.Qt.MatchContains)

        # Find all items in self.listWidget and store them in allItems
        allItems = []
        for index in xrange(self.listWidget.count()):
             allItems.append(self.listWidget.item(index))

        # hide all items found
        for each in allItems:
            self.listWidget.setItemHidden(each, True)

        # Show only the ones that match the search
        for found in items:
            self.listWidget.setItemHidden(found, False)

    def save(self):
        result = cmds.promptDialog(
                title='Save asset',
                message='Enter asset name:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

        if result == 'OK':
            name = cmds.promptDialog(query=True, text=True)
            if name == "":
                logger.warning("Please enter a name for your asset")
                self.save()
            else:
                if self.doesItExist(name):
                    # OVERWRITE DIALOG
                    response = cmds.confirmDialog(
                        title='Overwrite...',
                        message='An asset with the same name already exists, overwrite?',
                        button=['Yes','No'],
                        defaultButton='No',
                        cancelButton='No',
                        dismissString='No')

                    if response == "No":
                        return


                #### SAVE HERE
                currentScene = cmds.file(query=True, sceneName=True)

                savePath = os.path.join(self.userPath, '%s.ma' % name)
                cmds.file(rename=savePath)

                if cmds.ls(selection=True):
                    cmds.file(force=True, type='mayaAscii', exportSelected=True)
                else:
                    cmds.file(force=True, save=True, type='mayaAscii')

                cmds.file(rename=currentScene) # restore previous scene name

                # SAVE SCREENSHOT
                self.saveScreenshot(name)
                logger.info("Asset saved in " + savePath)
                self.populate(self.userPath)

    def saveScreenshot(self, name):
        path = os.path.join(self.userPath, '%s.jpg' % name)
        activePanel = cmds.paneLayout('viewPanes', q=True, pane1=True)


        cmds.viewFit()
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)

        # Isolate selection
        if cmds.ls(selection=True):
            cmds.isolateSelect(activePanel, update=1)
            cmds.isolateSelect(activePanel, state=1)
            cmds.isolateSelect(activePanel, addSelected=1)

        cmds.modelEditor(activePanel, edit=True, sel=False)


        cmds.playblast(completeFilename=path, forceOverwrite=True, format='image', width=200, height= 200,
                       showOrnaments=False, startTime=1, endTime=1, viewer=False)


        cmds.modelEditor(activePanel, edit=True, sel=True)

        cmds.isolateSelect(activePanel, state=0)

        #return path

    def load(self):
        """This loads the currently selected assets, or opens the folder"""
        for item in self.listWidget.selectedItems():
            itemType = item.data(QtCore.Qt.UserRole)

            if itemType == 'maya':
                path = self.assets[item.text()]['path']
                logger.info("Importing: " + path)
                cmds.file(path, i=True, usingNamespaces=False)

            elif itemType == 'folder':
                newPath = os.path.join(self.userPath, item.text())
                logger.debug("Populating list with this path: " + newPath)
                self.populate(newPath)

    def delete(self):
        # CONFIRMATION DIALOG
        response = cmds.confirmDialog(
            title='Deleting...',
            message='Are you sure?',
            button=['Yes','No'],
            defaultButton='No',
            cancelButton='No',
            dismissString='No')

        if response == "No":
            return

        for item in self.listWidget.selectedItems():
            itemType = item.data(QtCore.Qt.UserRole)

            if itemType == 'maya':
                path = os.path.join(self.userPath, '%s.ma' % item.text())
                screenshot = os.path.join(self.userPath, '%s.jpg' % item.text())
                try:
                    os.remove(path)
                    os.remove(screenshot)
                except OSError:
                    logger.error("Error deleting: "+item.text())


            elif itemType == 'folder':
                # CONFIRMATION DIALOG
                response = cmds.confirmDialog(
                    title='Deleting...',
                    message='Deleting the folder ' + item.text()+ ' will delete all of its contents, are you sure?',
                    button=['Yes','No'],
                    defaultButton='No',
                    cancelButton='No',
                    dismissString='No')

                if response == "Yes":
                    path = os.path.join(self.userPath, item.text())

                    try:
                        shutil.rmtree(path, ignore_errors=False, onerror=None)
                        logger.info("Directory deleted: " + item.text())
                    except OSError:
                        logger.error("Error deleting: "+ item.text())
                elif response == "No":
                    logger.info("Directory not deleted: " + item.text())

        self.populate(self.userPath)

    def rename(self):
        for item in self.listWidget.selectedItems():
            result = cmds.promptDialog(
                title='Rename Object',
                message='Enter new name for:\n'+item.text(),
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

            if result == 'OK':
                newName = cmds.promptDialog(query=True, text=True)

                if not newName: # Empty field
                    logger.error("Please insert a name")
                    self.populate(self.userPath)
                    #return

                elif newName==item.text(): # New name == old name
                    logger.error("Please choose a different name")
                    self.populate(self.userPath)
                    return

                elif newName in self.assets:# New name already exists

                    if item.data(QtCore.Qt.UserRole) != self.assets[newName]['type']: # if different type stop script
                        logger.error("An element of a different type with the same name already exist, please choose a different name")
                        return

                    response = cmds.confirmDialog(
                        title='Attention',
                        message='An element with the same name already exists, do you want to overwrite it?',
                        button=['Yes','No'],
                        defaultButton='No',
                        cancelButton='No',
                        dismissString='No')
                    if response == "No":
                        return
                    elif response == "Yes":
                        if item.data(QtCore.Qt.UserRole) == "maya":
                            os.remove(os.path.join(self.userPath, newName + ".ma"))
                            os.remove(os.path.join(self.userPath, newName + ".jpg"))
                        elif item.data(QtCore.Qt.UserRole) == "folder":
                            shutil.rmtree(os.path.join(self.userPath, newName))

                if item.data(QtCore.Qt.UserRole) == "maya":
                    os.rename(os.path.join(self.userPath, item.text() + ".ma"), os.path.join(self.userPath, newName + ".ma"))
                    os.rename(os.path.join(self.userPath, item.text() + ".jpg"), os.path.join(self.userPath, newName + ".jpg"))
                elif item.data(QtCore.Qt.UserRole) == "folder":
                    shutil.move(os.path.join(self.userPath, item.text()), os.path.join(self.userPath, newName))

        self.populate(self.userPath)

    def moveItem(self):
        destination = cmds.fileDialog2(caption='Move to:', fileMode=2, okCaption='Move', startingDirectory=self.userPath)[0]
        if not destination:
            return
        for item in self.listWidget.selectedItems():
            try:
                shutil.move(self.assets[item.text()]['path'], destination)

                # copy screenshot too if maya file
                itemType = item.data(QtCore.Qt.UserRole)
                if itemType == 'maya':
                    shutil.move(self.assets[item.text()]['screenshot'], destination)
            except:
                logger.error("Error copying " + item.text() + " to: " + destination + "\nThe file/folder already exists")

        self.populate(destination)

    def doesItExist(self, getName):
        if getName in self.assets:
            return True
        else:
            return False

    def newFolder(self):
        result = cmds.promptDialog(
                title='Folder name',
                message='Enter a name for the new folder',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

        if result == 'OK':
            newName = cmds.promptDialog(query=True, text=True)
            newPath = os.path.join(self.userPath, newName)

            if not os.path.exists(newPath):
                os.makedirs(newPath)
                self.populate(newPath)
            else:
                logger.error("A directory with the same name already exists, please choose a different name.")
                self.newFolder()

    def openExplorer(self):
        path = self.userPath
        import subprocess
        try:
            os.startfile(path)
        except:
            subprocess.Popen(['xdg-open', path])

    def test(self, *args):
        print "test"

##################################

def install():
    # ask for directory
    try:
        userPath = cmds.fileDialog2(caption='Choose an asset folder', fileMode=2, okCaption='Select')[0]
    except:
        return
    logger.debug(userPath)

    ############
    url = 'http://pepperusso.uk/scripts/assetManager/icon.png' # Url of the icon
    imageName = 'assetManager.png'

    name = 'Asset Manager: ' + os.path.basename(userPath) # Name to use for the shelf button
    tooltip = "AM: " + userPath # Tooltip to use for the shelf button
    iconLabel = os.path.basename(userPath)

    # Command of the shelf button.
    command = "import assetManager as am\nam.start(\""+userPath+"\")"
    doubleClickCmd = "import assetManager as am\nam.install()"

    ############

    response = cmds.confirmDialog(
            title='Shelf icon',
            message='Do you want to create an icon in the current shelf?',
            button=['Yes','No'],
            defaultButton='No',
            cancelButton='No',
            dismissString='No')

    if response == "Yes":
        ## Get current maya version
        version = cmds.about(version=True)

        ## Download Icon

        appPath = os.environ['MAYA_APP_DIR']
        iconPath = os.path.join(appPath, version, "prefs/icons", imageName)

        try:
            urllib.urlretrieve(url, iconPath)
        except:
            iconPath = "empty.png"


        ## Add to current shelf
        topShelf = mel.eval('$nul = $gShelfTopLevel')
        currentShelf = cmds.tabLayout(topShelf, q=1, st=1)
        cmds.shelfButton(parent=currentShelf, i=iconPath, c=command, dcc=doubleClickCmd, label=name, annotation=tooltip, imageOverlayLabel=iconLabel, overlayLabelColor=(1,1,1), overlayLabelBackColor=(random.random(), random.random(), random.random(), .5))

    # START SCRIPT
    logger.info("To start the script in the same folder execute this python script:\nimport assetManager as am\nam.start(\""+userPath+"\")")
    start(userPath)

def checkUpdates():
    url = "http://pepperusso.uk/scripts/assetManager/update.txt" # Current version of the script
    update = urllib.urlopen(url).read()

    if update.split("\n")[0] > __version__:
        logger.info("\n".join(update.split("\n")[1:]))