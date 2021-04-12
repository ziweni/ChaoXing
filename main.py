# /usr/bin/python3
# coding=utf-8

import os
import re
import sys
import yaml
import json
import math
import time
import getopt
import random

from ChaoXing import ChaoXing
from alive_progress import alive_bar
from Util import print_list, print_tree, get_timestamp

# 初始化网课操作对象
obj = ChaoXing()

# 配置文件常量
config = {}

# 读取配置并登陆
def login():

    try:
        global config
        # 读取配置文件
        with open("config.yml", "r", encoding='utf-8') as f:
            data = f.read()
        # 加载配置文件
        config = yaml.safe_load(data)
    except IOError:
        print("❌ 初始化时出现错误：没找到配置文件！")
        exit(-1)
    except yaml.YAMLError:
        print("❌ 初始化时出现错误：配置文件异常！")
        exit(-2)

    # 登陆MChaoXing平台
    # 先判断有没有缓存Cookie
    if os.path.exists("cookies.json"):
        with open("cookies.json", "r", encoding='utf-8') as f:
            js = f.read()
        # 设置 Cookies
        obj.set_cookie(js)

    # 取一下数据，查看 Cookies 是否有效
    if len(obj.s.cookies.items()) == 0 or obj.get_user_info() == None:
        # 清空Cookies
        obj.s.cookies.clear()
        # 登陆
        if obj.login_m(str(config['member']['user']), str(config['member']['pass'])):
            if config['saveCookies']:
                # 获取 Cookies
                ck = json.dumps(obj.s.cookies.items())
                # 保存到文件
                f = open("cookies.json", "w", encoding='utf-8')
                f.write(ck)
                f.close()
        else:
            print("🚫 登陆失败！")
            exit(-3)

# 获取课程列表
def getCourseList():
    # 登陆
    login()
    # 获取
    course = obj.get_course_list()
    # 输出
    print_list(course, False)

# 遍历目录执行自动化操作
def eachProcessList(course, cata, cpi, clazzid, courseId):

    # 遍历目录; 判断是否有需要进行的课程
    # 定义个索引
    for key, item in cata.items():
        # 只取子节点
        if key > 1:
            for key, item2 in enumerate(item):
                # 查询剩余任务数量
                if item2['data']['unfinishcount'] <= 0:
                    continue
                # 取任务节点任务分页
                page = obj.get_task_page(item2['id'], courseId)
                # 遍历分页
                for item3 in page:
                    mArg = obj.get_task_page_level(clazzid, courseId, item2['id'], cpi, item3['cardorder'])
                    # 如果提取失败, 则跳转到下一个任务
                    if mArg == None:
                        continue
                    # 提取任务点
                    # 除文字分页外，其他类型的分页均存在数据
                    for item4 in mArg['attachments']:
                        # 判断该任务点的完成状态
                        finish = not ("job" in item4 and item4['job'])
                        # 如果完成; 就跳转到下一个任务
                        if finish:
                            continue

                        # 没完成; 就给模拟操作完成
                        # 先获取任务的类型
                        task_type = item4['type']

                        print("\n💼 任务类型: %s" % task_type)

                        if task_type == "video":
                            # 获取视频任务的对象ID
                            objectId = item4['objectId']
                            # 获取视频的详细信息
                            c_data = obj.get_course_data(objectId)
                            # 获取视频的长度; 单位秒
                            duration = c_data['duration']
                            print("📺 视频类任务 《%s - %s [%s]》" % (item2['name'], item3['title'], c_data['filename']))
                            print("⏰ 视频时长: %.2f 分钟" % (duration / 60))
                            print("⏳ 正在自动完成……")

                            # 开始进行模拟上报数据
                            # 计数变量
                            index = 0
                            # 上报间隔时间
                            delay = 30

                            # 进度条
                            with alive_bar(duration) as bar:
                                while True:
                                    # 加个判断; 避免数据上报的时间溢出视频本身的长度
                                    if index * delay > duration:
                                        times = duration
                                    else:
                                        times = index * delay

                                    c_res = obj.update_log_video(mArg['defaults']['reportUrl'], mArg['defaults']['clazzId'], times, c_data['duration'], c_data['dtoken'], objectId, item4['otherInfo'], item4['jobid'], mArg['defaults']['userid'])
                                    if c_res and index * delay > duration:
                                        break

                                    if duration - times < delay:
                                        items = range(duration - times)
                                        for item in items:
                                            bar()
                                            time.sleep(1)
                                    else:
                                        items = range(delay)
                                        for item in items:
                                            bar()
                                            time.sleep(1)
                                    index = index + 1
                            # 输出;  跳转到下一个循环
                            print("🎉 视频 任务完成！")
                            continue
                        elif task_type == 'document':
                            print("📽 文档/课件 观看任务")
                            # 上报数据
                            obj.updata_log_ppt(item4['jobid'], str(mArg['defaults']['knowledgeid']), str(mArg['defaults']['courseid']), str(mArg['defaults']['clazzId']), item4['jtoken'])
                            # 输出;  跳转到下一个循环
                            print("🎉 文档/课件 任务完成！")
                        elif task_type == "workid":
                            print("📃 测验 《%s - %s》" % (item2['name'], item3['title']))
                            print("⚠️  已自动跳过!")
                            pass
                        else:
                            print("❌ 不支持的任务类型!")
                            print("⚠️  已自动跳过!")
                        
                        time.sleep(2)
    
    print("\n🎉 你已完成了本课的所有任务！")

# 执行自动化代码
def chaoxingAuto(i):
    # 登陆
    login()
    # 获取
    course = obj.get_course_list()
    # 验证
    try:
        # 转换
        id = int(i)
    except ValueError:
        print("🚫 您输入的数据不符合规范！")
        exit(-4)
    if id >= len(course) or id < 0:
        print("🚫 课程id不存在！")
        exit(-5)

    # 输出选中的课程名称
    print("\n<%s>" % course[id]['courseName'])

    # 获取课程目录
    cata = obj.get_course_cata(course[id]['clazzid'], course[id]['cpi'])
    # 执行自动化
    eachProcessList(course, cata, course[id]['cpi'], course[id]['clazzid'], course[id]['courseId'])

# 执行默认程序
def chaoxingDefault():
    
    # 登陆
    login()

    print("✅ 登陆成功!")
    print("⏳ 正在获取课程列表……")
    course = obj.get_course_list()

    # 输出
    print_list(course)

    while True:
        # 异常输入判断
        try:
            # 要求输入
            id = int(input("课程id: "))
        except ValueError:
            print("🚫 您输入的数据不符合规范！")
            continue
        if id == -1:
            exit(0)
        if id >= len(course) or id < 0:
            print("🚫 课程id不存在！")
            continue
        break
    # 输出选中的课程名称
    print("\n<%s>" % course[id]['courseName'])
    # 获取课程目录
    cata = obj.get_course_cata(course[id]['clazzid'], course[id]['cpi'])
    # 输出目录
    print_tree(cata)
    # 执行自动化
    eachProcessList(course, cata, course[id]['cpi'], course[id]['clazzid'], course[id]['courseId'])

if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:l", ["id=", "list"])
    except getopt.GetoptError:
        print(
"""usage: main.py --id <courseId>
               --list ...get course list"""
               )
        exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('main.py --id <courseId> \
                           --list')
            exit(-1)
        elif opt in ("-i", "--id"):
            chaoxingAuto(arg)
            exit(0)
        elif opt in ("-l", "--list"):
            getCourseList()
            exit(0)

    chaoxingDefault()