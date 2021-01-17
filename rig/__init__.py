#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/20 11:01
# @Author  : Li XiaoJun
# @Site    : 
# @File    : __init__.py.py


import os
from pymel.util import path

# 系统路径
cur_dir = os.path.abspath(__file__)
# 模板存放路径
template_dir = path(cur_dir).parent.parent.joinpath("template")


