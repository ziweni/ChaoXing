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

def print_list(obj, isExit = True):
    if len(obj) == 0:
        return
    print("------------------------------------")
    print("| id | 课程名称")
    index = 0
    for item in obj:
        print("| %2d | %-s" % (index, item['courseName']))
        index = index + 1
    print("------------------------------------")
    if isExit:
        print("| 退出请输入 -1")
        print("------------------------------------")

def print_tree(obj):
    if len(obj) == 0:
        return

    index = 0
    kv = {}
    print_list = []
    for key, value in obj.items():
        index2 = 0
        for key2, value2 in enumerate(value):
            head_list = [ " " for i in range(key) ]
            endi = len(obj[1]) - 1
            if index == 0 and index2 + 1 == len(obj[1]):
                head_list[0] = "└"
            elif index == 0 and index2 == 0:
                head_list[0] = "┌"
            elif key == 1:
                head_list[0] = "├"
            elif value2['parentnodeid'] != obj[1][endi]['id']:
                head_list[0] = "|"
            if key > 1:
                if key2 + 1 >= len(value) or value2['parentnodeid'] != value[key2+1]['parentnodeid']:
                    head_list[key-1] = "└"
                else:
                    head_list[key-1] = "├"
            head = "  ".join(head_list)
            
            if key == 1:
                print_list.insert(len(print_list), {
                    "title": "%s %s、%s" % (head, value2['label'], value2['name']),
                    "data": []
                })
                kv[value2['id']] = len(print_list)
            else:
                length = len(print_list[kv[value2['parentnodeid']] - 1]['data'])
                if value2['data']['totalcount'] == 0:
                    emoji = "🔒"
                elif value2['data']['unfinishcount'] == value2['data']['totalcount']:
                    emoji = "❌ %d" % value2['data']['totalcount']
                elif value2['data']['unfinishcount'] == 0:
                    emoji = "✅"
                else:
                    emoji = "⏳ %d" % value2['data']['unfinishcount']
                print_list[kv[value2['parentnodeid']] - 1]['data'].insert(length, {
                    "title": "%s %s、%s (%s)" % (head, value2['label'], value2['name'], emoji)
                })

            index2 = index2 + 1
        index = index + 1
    for item in print_list:
        print(item['title'])
        for item2 in item['data']:
            print(item2['title'])