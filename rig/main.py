# coding: utf-8

from imp import reload
from animation import common
from rig import face_creator_ui

reload(common)
reload(face_creator_ui)

creator_version = 0.21


def open_creator_ui():
    ui = face_creator_ui.FaceCreatorUI()
