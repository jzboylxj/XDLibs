# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:/work/XDLibs/ui/rs.ui'
#
# Created: Thu Oct 29 14:03:44 2020
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(716, 687)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_rig = QtGui.QWidget()
        self.tab_rig.setObjectName("tab_rig")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_rig)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame_5 = QtGui.QFrame(self.tab_rig)
        self.frame_5.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame_5.setObjectName("frame_5")
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.frame_5)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_10 = QtGui.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.pushButton_11 = QtGui.QPushButton(self.frame_5)
        self.pushButton_11.setObjectName("pushButton_11")
        self.verticalLayout_10.addWidget(self.pushButton_11)
        self.line = QtGui.QFrame(self.frame_5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setMinimumSize(QtCore.QSize(0, 2))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_10.addWidget(self.line)
        self.pushButton_12 = QtGui.QPushButton(self.frame_5)
        self.pushButton_12.setObjectName("pushButton_12")
        self.verticalLayout_10.addWidget(self.pushButton_12)
        self.verticalLayout_9.addLayout(self.verticalLayout_10)
        self.verticalLayout_3.addWidget(self.frame_5)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem)
        self.frame_4 = QtGui.QFrame(self.tab_rig)
        self.frame_4.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.frame_4)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_7 = QtGui.QPushButton(self.frame_4)
        self.pushButton_7.setObjectName("pushButton_7")
        self.gridLayout.addWidget(self.pushButton_7, 0, 0, 1, 2)
        self.pushButton_8 = QtGui.QPushButton(self.frame_4)
        self.pushButton_8.setObjectName("pushButton_8")
        self.gridLayout.addWidget(self.pushButton_8, 1, 0, 1, 2)
        self.pushButton_9 = QtGui.QPushButton(self.frame_4)
        self.pushButton_9.setObjectName("pushButton_9")
        self.gridLayout.addWidget(self.pushButton_9, 2, 0, 1, 1)
        self.pushButton_10 = QtGui.QPushButton(self.frame_4)
        self.pushButton_10.setObjectName("pushButton_10")
        self.gridLayout.addWidget(self.pushButton_10, 2, 1, 1, 1)
        self.verticalLayout_8.addLayout(self.gridLayout)
        self.verticalLayout_3.addWidget(self.frame_4)
        spacerItem1 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem1)
        self.frame_3 = QtGui.QFrame(self.tab_rig)
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.frame_3)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtGui.QLabel(self.frame_3)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.horizontalSlider = QtGui.QSlider(self.frame_3)
        self.horizontalSlider.setProperty("value", 1)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalLayout_2.addWidget(self.horizontalSlider)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(self.frame_3)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.horizontalLayout_2.addWidget(self.doubleSpinBox)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtGui.QLabel(self.frame_3)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.horizontalSlider_2 = QtGui.QSlider(self.frame_3)
        self.horizontalSlider_2.setProperty("value", 1)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.horizontalLayout_3.addWidget(self.horizontalSlider_2)
        self.doubleSpinBox_2 = QtGui.QDoubleSpinBox(self.frame_3)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.horizontalLayout_3.addWidget(self.doubleSpinBox_2)
        self.verticalLayout_6.addLayout(self.horizontalLayout_3)
        self.verticalLayout_7.addLayout(self.verticalLayout_6)
        self.verticalLayout_3.addWidget(self.frame_3)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.tabWidget.addTab(self.tab_rig, "")
        self.tab_modules = QtGui.QWidget()
        self.tab_modules.setObjectName("tab_modules")
        self.tabWidget.addTab(self.tab_modules, "")
        self.tab_add_controls = QtGui.QWidget()
        self.tab_add_controls.setObjectName("tab_add_controls")
        self.tabWidget.addTab(self.tab_add_controls, "")
        self.tab_twists = QtGui.QWidget()
        self.tab_twists.setObjectName("tab_twists")
        self.tabWidget.addTab(self.tab_twists, "")
        self.tab_inbetweens = QtGui.QWidget()
        self.tab_inbetweens.setObjectName("tab_inbetweens")
        self.tabWidget.addTab(self.tab_inbetweens, "")
        self.tab_object_spaces = QtGui.QWidget()
        self.tab_object_spaces.setObjectName("tab_object_spaces")
        self.tabWidget.addTab(self.tab_object_spaces, "")
        self.tab_controllers = QtGui.QWidget()
        self.tab_controllers.setObjectName("tab_controllers")
        self.tabWidget.addTab(self.tab_controllers, "")
        self.tab_tools = QtGui.QWidget()
        self.tab_tools.setObjectName("tab_tools")
        self.tabWidget.addTab(self.tab_tools, "")
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 716, 30))
        self.menubar.setObjectName("menubar")
        self.menuRig = QtGui.QMenu(self.menubar)
        self.menuRig.setObjectName("menuRig")
        self.menuDisplay = QtGui.QMenu(self.menubar)
        self.menuDisplay.setObjectName("menuDisplay")
        self.menuTools = QtGui.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setObjectName("menuOptions")
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionLoad = QtGui.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionDelete = QtGui.QAction(MainWindow)
        self.actionDelete.setObjectName("actionDelete")
        self.actionSave_Pose = QtGui.QAction(MainWindow)
        self.actionSave_Pose.setObjectName("actionSave_Pose")
        self.actionReset_Pose = QtGui.QAction(MainWindow)
        self.actionReset_Pose.setObjectName("actionReset_Pose")
        self.actionPosers = QtGui.QAction(MainWindow)
        self.actionPosers.setObjectName("actionPosers")
        self.actionControls = QtGui.QAction(MainWindow)
        self.actionControls.setObjectName("actionControls")
        self.actionJoints = QtGui.QAction(MainWindow)
        self.actionJoints.setObjectName("actionJoints")
        self.actionGeometry = QtGui.QAction(MainWindow)
        self.actionGeometry.setObjectName("actionGeometry")
        self.actionJoints_Template = QtGui.QAction(MainWindow)
        self.actionJoints_Template.setObjectName("actionJoints_Template")
        self.actionGeometry_Template = QtGui.QAction(MainWindow)
        self.actionGeometry_Template.setObjectName("actionGeometry_Template")
        self.actionGeometry_Reference = QtGui.QAction(MainWindow)
        self.actionGeometry_Reference.setObjectName("actionGeometry_Reference")
        self.actionPosers_Axises = QtGui.QAction(MainWindow)
        self.actionPosers_Axises.setObjectName("actionPosers_Axises")
        self.actionSkeleton_LRA = QtGui.QAction(MainWindow)
        self.actionSkeleton_LRA.setObjectName("actionSkeleton_LRA")
        self.actionControl_Sets = QtGui.QAction(MainWindow)
        self.actionControl_Sets.setObjectName("actionControl_Sets")
        self.actionHuman_IK_Transfer_Tool = QtGui.QAction(MainWindow)
        self.actionHuman_IK_Transfer_Tool.setObjectName("actionHuman_IK_Transfer_Tool")
        self.actionMudule_Builder = QtGui.QAction(MainWindow)
        self.actionMudule_Builder.setObjectName("actionMudule_Builder")
        self.actionDebug = QtGui.QAction(MainWindow)
        self.actionDebug.setObjectName("actionDebug")
        self.actionHome_Page = QtGui.QAction(MainWindow)
        self.actionHome_Page.setObjectName("actionHome_Page")
        self.actionTutorials = QtGui.QAction(MainWindow)
        self.actionTutorials.setObjectName("actionTutorials")
        self.actionHelp_Mode = QtGui.QAction(MainWindow)
        self.actionHelp_Mode.setObjectName("actionHelp_Mode")
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.menuRig.addAction(self.actionNew)
        self.menuRig.addAction(self.actionSave)
        self.menuRig.addAction(self.actionLoad)
        self.menuRig.addAction(self.actionDelete)
        self.menuRig.addSeparator()
        self.menuRig.addAction(self.actionSave_Pose)
        self.menuRig.addAction(self.actionReset_Pose)
        self.menuDisplay.addAction(self.actionPosers)
        self.menuDisplay.addAction(self.actionControls)
        self.menuDisplay.addAction(self.actionJoints)
        self.menuDisplay.addAction(self.actionGeometry)
        self.menuDisplay.addSeparator()
        self.menuDisplay.addAction(self.actionJoints_Template)
        self.menuDisplay.addAction(self.actionGeometry_Template)
        self.menuDisplay.addAction(self.actionGeometry_Reference)
        self.menuDisplay.addSeparator()
        self.menuDisplay.addAction(self.actionPosers_Axises)
        self.menuDisplay.addAction(self.actionSkeleton_LRA)
        self.menuTools.addAction(self.actionControl_Sets)
        self.menuTools.addAction(self.actionHuman_IK_Transfer_Tool)
        self.menuTools.addAction(self.actionMudule_Builder)
        self.menuOptions.addAction(self.actionDebug)
        self.menuHelp.addAction(self.actionHome_Page)
        self.menuHelp.addAction(self.actionTutorials)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionHelp_Mode)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuRig.menuAction())
        self.menubar.addAction(self.menuDisplay.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_11.setText(QtGui.QApplication.translate("MainWindow", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_12.setText(QtGui.QApplication.translate("MainWindow", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_7.setText(QtGui.QApplication.translate("MainWindow", "Publish Rig", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_8.setText(QtGui.QApplication.translate("MainWindow", "Select Skin Joint", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_9.setText(QtGui.QApplication.translate("MainWindow", "Save Pose", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_10.setText(QtGui.QApplication.translate("MainWindow", "Reset Pose", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Posers Size", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Joints Size", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_rig), QtGui.QApplication.translate("MainWindow", "Rig", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_modules), QtGui.QApplication.translate("MainWindow", "Modules", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_add_controls), QtGui.QApplication.translate("MainWindow", "Add Controls", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_twists), QtGui.QApplication.translate("MainWindow", "Twists", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_inbetweens), QtGui.QApplication.translate("MainWindow", "Inbetweens", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_object_spaces), QtGui.QApplication.translate("MainWindow", "ObjectSpaces", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_controllers), QtGui.QApplication.translate("MainWindow", "Controllers", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_tools), QtGui.QApplication.translate("MainWindow", "Tools", None, QtGui.QApplication.UnicodeUTF8))
        self.menuRig.setTitle(QtGui.QApplication.translate("MainWindow", "Rig", None, QtGui.QApplication.UnicodeUTF8))
        self.menuDisplay.setTitle(QtGui.QApplication.translate("MainWindow", "Display", None, QtGui.QApplication.UnicodeUTF8))
        self.menuTools.setTitle(QtGui.QApplication.translate("MainWindow", "Tools", None, QtGui.QApplication.UnicodeUTF8))
        self.menuOptions.setTitle(QtGui.QApplication.translate("MainWindow", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew.setText(QtGui.QApplication.translate("MainWindow", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad.setText(QtGui.QApplication.translate("MainWindow", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDelete.setText(QtGui.QApplication.translate("MainWindow", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_Pose.setText(QtGui.QApplication.translate("MainWindow", "Save Pose", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReset_Pose.setText(QtGui.QApplication.translate("MainWindow", "Reset Pose", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPosers.setText(QtGui.QApplication.translate("MainWindow", "Posers", None, QtGui.QApplication.UnicodeUTF8))
        self.actionControls.setText(QtGui.QApplication.translate("MainWindow", "Controls", None, QtGui.QApplication.UnicodeUTF8))
        self.actionJoints.setText(QtGui.QApplication.translate("MainWindow", "Joints", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGeometry.setText(QtGui.QApplication.translate("MainWindow", "Geometry", None, QtGui.QApplication.UnicodeUTF8))
        self.actionJoints_Template.setText(QtGui.QApplication.translate("MainWindow", "Joints Template", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGeometry_Template.setText(QtGui.QApplication.translate("MainWindow", "Geometry Template", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGeometry_Reference.setText(QtGui.QApplication.translate("MainWindow", "Geometry Reference", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPosers_Axises.setText(QtGui.QApplication.translate("MainWindow", "Posers Axises", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSkeleton_LRA.setText(QtGui.QApplication.translate("MainWindow", "Skeleton LRA", None, QtGui.QApplication.UnicodeUTF8))
        self.actionControl_Sets.setText(QtGui.QApplication.translate("MainWindow", "Control Sets", None, QtGui.QApplication.UnicodeUTF8))
        self.actionHuman_IK_Transfer_Tool.setText(QtGui.QApplication.translate("MainWindow", "Human IK Transfer Tool...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMudule_Builder.setText(QtGui.QApplication.translate("MainWindow", "Mudule Builder...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDebug.setText(QtGui.QApplication.translate("MainWindow", "Debug", None, QtGui.QApplication.UnicodeUTF8))
        self.actionHome_Page.setText(QtGui.QApplication.translate("MainWindow", "Home Page", None, QtGui.QApplication.UnicodeUTF8))
        self.actionTutorials.setText(QtGui.QApplication.translate("MainWindow", "Tutorials", None, QtGui.QApplication.UnicodeUTF8))
        self.actionHelp_Mode.setText(QtGui.QApplication.translate("MainWindow", "Help Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
