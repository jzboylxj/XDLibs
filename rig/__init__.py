#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020/7/20 11:01
# @Author  : Li XiaoJun
# @Site    : 
# @File    : __init__.py.py


# imports
import os
import sys

from pymel.util import path
import exceptions

# 系统路径
cur_dir = os.path.abspath(__file__)
# 模板存放路径
template_dir = path(cur_dir).parent.parent.joinpath("template")

# 用于日志的 Debug 模式
logDebug = False

# 用于日志信息里面描述严重程度的代码
sev_fatal = 1
sev_error = 2
sev_warning = 4
sev_info = 8
sev_verbose = 16
sev_comment = 32


def log(message, severity=sev_comment, infos=False):
    u"""根据严重程度和文件本身的附加信息记录一条日志

    严重程度参照:
        * 1. Fatal 重大
        * 2. Error 错误
        * 4. Warning 警告
        * 8. Info 信息
        * 16. Verbose 长信息
        * 32. Comment 建议

    Args:
        messages(str): 信息
        severity (int): 严重程度.
        infos (bool):  添加来自模块、类、方法和行号的额外信息

    """
    message = str(message)

    if infos or logDebug:
        message = getInfos(1) + "\n" + message

    sys.stdout.write(message + "\n")


class FakeException(exceptions.Exception):
    pass


def getInfos(level):
    u"""从方法被触发的位置获取信息。例如模块名、方法、行号...

    Args:
        level (int): 级别程度

    Returns:
        str: 信息
    """
    try:
        raise FakeException("this is fake")
    except Exception:
        # get the current execution frame
        f = sys.exc_info()[2].tb_frame

    # go back as many call-frames as was specified
    while level >= 0:
        f = f.f_back
        level = level - 1

    infos = ""

    # Module Name
    moduleName = f.f_globals["__name__"]
    if moduleName != "__ax_main__":
        infos += moduleName + " | "

    # Class Name
    # if there is a self variable in the caller's local namespace then
    # we'll make the assumption that the caller is a class method
    obj = f.f_locals.get("self", None)
    if obj:
        infos += obj.__class__.__name__ + "::"

    # Function Name
    functionName = f.f_code.co_name
    if functionName != "<rig_classic_components>":
        infos += functionName + "()"

    # Line Number
    lineNumber = str(f.f_lineno)
    infos += " line " + lineNumber + ""

    if infos:
        infos = "[" + infos + "]"

    return infos
