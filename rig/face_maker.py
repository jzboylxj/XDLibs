#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/20 11:03
# @Author  : Li XiaoJun
# @Site    : 
# @File    : face_maker.py

from animation import common

reload(common)


class FaceMaker(common.Singleton):

    def __init__(self):
        super(FaceMaker, self).__init__()

        self.initialize()
        self.show()

    def initialize(self):
        pass

    def show(self):
        pass