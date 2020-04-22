# /usr/bin/python3
# coding=utf8

"""
工具集
"""

import time

# 获取时间戳
def get_timestamp():
    timestamp = time.time()
    return int(timestamp * 1000)

# json转字符
def obj2str(obj):
    ret = ""
    for key in obj:
        if ret == "":
            ret = key + "=" + str(obj[key])
        else:
            ret = ret + "&" + key + "=" + str(obj[key])
    return ret

def print_list(obj):
    if len(obj) == 0:
        return
    print("------------------------------------")
    print("| id | 课程名称")
    index = 0
    for item in obj:
        print("| %2d | %-s" % (index, item['courseName']))
        index = index + 1
    print("------------------------------------")
    print("| 退出请输入 -1")
    print("------------------------------------")

def print_tree(obj):
    if len(obj) == 0:
        return

    oc = 0

    index = 0
    for item in obj:
        if index == 0:
            print("┌ %s" % item['title'])
        elif index == len(obj) - 1:
            print("└ %s" % item['title'])
        else:
            print("├ %s" % item['title'])

        index2 = 0
        for item2 in item['data']:

            if item2['complete'] != 0:
                c = "  ❌（%d）" % item2['complete']
                oc = oc + item2['complete']
            else:
                c = ""

            if index + 1 == len(obj):
                if len(item['data']) - 1 != index2:
                    print("  ├ %s" % item2['title'] + c)
                else:
                    print("  └ %s" % item2['title'] + c)
            else:
                if len(item['data']) - 1 != index2:
                    print("│ ├ %s" % item2['title'] + c)
                else:
                    print("│ └ %s" % item2['title'] + c)

            index2 = index2 + 1

        index = index + 1

    if oc != 0:
        print("您一共有 %d 个未完成的项目!" % oc)