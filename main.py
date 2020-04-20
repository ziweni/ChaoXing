# /usr/bin/python3
# coding=utf8

import os
import re
import time
import hashlib
from ChaoXing import ChaoXing
from alive_progress import alive_bar
from Util import print_list, print_tree

if __name__ == "__main__":

    obj = ChaoXing()

    print("正在登陆……")

    # 先判断有没有缓存Cookie
    if os.path.exists("cookies.json"):
        with open("cookies.json", "r", encoding='utf-8') as f:
            js = f.read()
        obj.set_cookie(js)
    # 登陆
    elif obj.login_m("user", "pass"):
        ck = json.dumps(obj.s.cookies.items())

        f = open("cookies.json", "w", encoding='utf-8')
        f.write(ck)
        f.close()
    else:
        print("登陆失败！")
        exit(-1)

    print("正在获取课程列表……")
    # 获取课程列表
    list = obj.get_list()
    # 输出
    print_list(list)

    while True:
        # 要求输入
        id = int(input("课程id: "))

        if id >= len(list) or id < 0:
            print("课程id不存在！")
            continue
        break

    # 输出选中的课程名称
    print("%s\n" % list[id]['courseName'])

    # 获取课程目录
    course = obj.get_course_cata(
        list[id]['url'])

    print("<课程目录>")
    # 输出课程目录
    print_tree(course)

    print("开始执行刷课代码……")
    # 遍历目录; 判断是否有需要进行的课程
    # 定义个索引
    i1 = 0
    while i1 < len(course):
        # 定义个索引
        i2 = 0
        while i2 < len(course[i1]['data']):
            # 取出数据
            item2 = course[i1]['data'][i2]
            # 判断这个课程是否有任务点
            if item2['complete'] == 0:
                i2 = i2 + 1
                continue

            # 有任务点，就来提取并自动化完成
            # 如果有任务点; 那么url参数就一定不为空
            # 从课程目录中选取一个： 提取其数据
            z = re.findall(r'chapterId=(.*?)&|courseId=(.*?)&|clazzid=(.*?)&', item2['url'])

            # 获取该子目录的分页数目
            s = obj.get_course_page(z[1][1], z[2][2], z[0][0], list[id]['cpi'])

            # 遍历分页; 逐个执行
            for item3 in s:
                # 获取分页内的任务点
                mArg = obj.get_course_page_level(item3['url'])

                # 提取任务点
                # 除文字分页外，其他类型的分页均存在数据
                for item4 in mArg['attachments']:
                    # 判断该任务点的完成状态
                    finish = not ("job" in item4 and item4['job'])
                    # 如果完成; 就跳转到下一个任务
                    if finish:
                        continue

                    print("课程 %s 正在自动完成" % item2['title'])
                    # 没完成; 就给模拟操作完成
                    # 先获取任务的类型
                    task_type = item4['type']

                    # 再通过判断; 根据不同的任务进行不同的操作
                    if task_type == 'video':
                        print("视频类任务")
                        # 获取视频任务的对象ID
                        objectId = item4['objectId']
                        # 获取视频的详细信息
                        c_data = obj.get_course_data(objectId)
                        # 获取视频的长度; 单位秒
                        duration = c_data['duration']
                        print("视频时长: %.2f 分钟" % (duration / 60))

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
                        print("任务点完成！")

                        continue
                    elif task_type == 'document':
                        print("文档/课件 观看任务")

                        # 先提取相关数据
                        jobid = item4['jobid']
                        jtoken = item4['jtoken']
                        knowledgeid = str(mArg['defaults']['knowledgeid'])
                        clazzId = str(mArg['defaults']['clazzId'])
                        courseid = str(mArg['defaults']['courseid'])
                        
                        # 上报数据
                        obj.updata_log_ppt(jobid, knowledgeid, courseid, clazzId, jtoken)
                        # 输出;  跳转到下一个循环
                        print("任务点完成！")

                        continue
                    elif task_type == 'workid':
                        # 如果是题目;
                        print("试题任务: 无法自动操作")
                    else:
                        # 不支持的任务类型
                        print("不支持的任务类型")

            # 刷新课程目录
            # 避免部分课程设置的锁的机制
            course = obj.get_course_cata(list[id]['url'])
            i2 = i2 + 1
        i1 = i1 + 1