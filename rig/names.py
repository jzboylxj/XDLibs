#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/11/21 22:22
# @Author  : Li XiaoJun
# @Site    : 
# @File    : names.py
# @Software: PyCharm
import os
from pymel.util import path

# 系统路径
cur_dir = os.path.abspath(__file__)
# 模板存放路径
template_dir = path(cur_dir).parent.parent.joinpath("template")


