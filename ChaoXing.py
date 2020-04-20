# /usr/bin/python3
# coding=utf8

import re
import html
import json
import base64
import hashlib
import requests
from urllib.parse import quote
from Util import get_timestamp, obj2str

""" 
超星学习通操作类
"""
class ChaoXing:

    s = requests.session()

    def __init__(self):
        # 设置全局Http协议头
        self.s.headers.update(
            {
                'Accept': "*/*",
                'Accept-Language': "zh-Hans-CN;q=1",
                'Connection': "keep-alive",
                'Accept-Encoding': "gzip, deflate, br",
                'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ChaoXingStudy/ChaoXingStudy_3_4.4_ios_phone_202004071850_39 (@Kalimdor)_15167665855436465586 ChaoXingStudy/ChaoXingStudy_3_4.4_ios_phone_202004071850_39 (@Kalimdor)_15167665855436465586"
            })

    # 设置Cookie
    def set_cookie(self, ck):
        obj = json.loads(ck)

        cookies = {}
        for o in obj:
            cookies[o[0]] = o[1]

        self.s.cookies.update(cookies)

    # 获得验证码
    def getCode(self, name):
        uri = "http://passport2.chaoxing.com/num/code?" + str(get_timestamp())

        r = self.s.get(uri)

        with open(name, 'wb') as fd:
            for chunk in r.iter_content():
                fd.write(chunk)

    # 执行登陆; Web网页接口
    def login(self, u_name, u_pass, code):

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': "http://i.mooc.chaoxing.com/",
            'Referer': "http://passport2.chaoxing.com/login?fid=&refer=http://i.mooc.chaoxing.com"
        }

        uri = "http://passport2.chaoxing.com/login?refer=" + \
            quote("http://i.mooc.chaoxing.com", "utf-8")

        data = obj2str({
            'refer_0x001': quote("http://i.mooc.chaoxing.com", "utf-8"),
            'pid': "-1",
            'pidName': "",
            'fid': "-1",
            'fidName': "",
            'allowJoin': "0",
            'isCheckNumCode': "1",
            'f': "0",
            'productid': "",
            't': "true",
            'uname': u_name,
            'password': base64.b64encode(u_pass.encode("utf-8")).decode('ascii'),
            'numcode': code,
            'verCode': ""
        })

        r = self.s.post(uri, headers=headers, data=data, allow_redirects=False)

        if r.status_code != 302:
            rule = r'id=\"show_error\">(.*?)</td>'
            d = re.findall(rule, r.text)
            print(d[0])
            return False
        else:
            return True

    # 执行登陆: Mobile端
    # 优点是可以免验证码登陆
    def login_m(self, u_name, u_pass):

        uri = "https://passport2-api.chaoxing.com/v11/loginregister?code=" + u_pass + \
            "&cx_xxt_passport=json&uname=" + u_name + "&loginType=1&roleSelect=true"

        r = self.s.get(uri)

        a = json.loads(r.text)

        print(a['mes'])

        return a['status']

    # 验证码识别; 联众打码接口
    def code(self, imagePath):
        uri = "http://v1-http-api.jsdama.com/api.php?mod=php&act=upload"

        user_name = "*********"
        user_pw = "*********"

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Connection': 'keep-alive',
            'Host': 'v1-http-api.jsdama.com',
            'Upgrade-Insecure-Requests': '1'
        }

        files = {
            'upload': (imagePath, open(imagePath, 'rb'), 'image/png')
        }

        data = {
            'user_name': user_name,
            'user_pw': user_pw,
            'yzm_type': '1001'
        }

        s = requests.session()
        r = s.post(uri, headers=headers,
                   data=data, files=files, verify=False)
        a = json.loads(r.text)

        return a['data']['val']

    # 获取课程列表
    def get_list(self):
        uri = "http://i.mooc.chaoxing.com/space/index?t=" + \
            str(get_timestamp())

        r = self.s.get(uri)

        rule = r'<iframe src=\"(.*?)\"'
        d = re.findall(rule, r.text)

        for it in d:
            if it != "":
                uri = it
                break

        r = self.s.get(uri)

        rule = r'<li style=\"position:relative\">(.*?)</li>'
        d = re.findall(rule, r.text, re.DOTALL)

        ret = []

        for item in d:
            item = html.unescape(item)

            url = re.findall(r'href=\'(.*?)\'', item)
            courseId = re.findall(r'courseId" value=\"(.*?)\"', item)
            classId = re.findall(r'classId" value=\"(.*?)\"', item)
            cpi = re.findall(r'cpi=(.*?)&', url[0])
            title = re.findall(
                r'<div class=\"Mconright httpsClass\">(.*?)</div>', item, re.DOTALL)

            infomation = re.findall(r'title=\"(.*?)\"', title[0])

            course = {
                'courseId': courseId[0],
                'classId': classId[0],
                'cpi': cpi[0],
                'url': "https://mooc1-1.chaoxing.com" + url[0],
                'courseName': infomation[0],
                'teachar': infomation[1],
                'school': infomation[2],
                'class': infomation[3]
            }

            ret.insert(len(ret), course)

        return ret

    # 获取课程目录
    def get_course_cata(self, url):

        r = self.s.get(url)

        d = re.findall(
            r'<div class=\"units\">(.*?)\n                            </div>', r.text, re.DOTALL)
        bul = re.findall(r'bulletFormat = \"(.*?)\"', r.text)

        ret = []
        for item in d:
            root = re.findall(r'<h2 (.*?)</h2>', item, re.DOTALL)
            ic = re.findall(
                r'<span class=\"chapterNumber\">(.*?)</span>', root[0], re.DOTALL)
            title = re.findall(r'title=\"(.*?)\"', root[0])
            title[0] = title[0].replace("\ufeff", "")

            order = re.findall(
                r'<div class=\"leveltwo\">(.*?)</div>', item, re.DOTALL)
            data = []
            for node in order:
                t = re.findall(r'title=\"(.*?)\"', node)
                s = re.findall(
                    r'<span class=\"chapterNumber\">(.*?)</span>', node)
                u = re.findall(r'href=\'(.*?)\'', node)
                c = re.findall(r'<em class=\"orange\">(.*?)</em>', node)
                if len(c) == 0:
                    c = 0
                else:
                    c = int(c[0])

                if len(u) == 0:
                    u = ""
                else:
                    u = "https://mooc1-1.chaoxing.com" + u[0]

                i = len(t) - 1
                if len(s) == 0 or bul[0] == "Dot":
                    t = t[i]
                else:
                    t = "%s %s" % (s[0], t[i])

                if u == "":
                    t = t + " 🔒"

                data.insert(len(data), {
                    'title': t,
                    'url': u,
                    'complete': c
                })

            if len(ic) == 0:
                title = title[0]
            else:
                title = "%s %s" % (ic[0].replace(
                    "\n", "").replace("\t", ""), title[0])
            ret.insert(len(ret), {
                'title': title,
                'data': data
            })

        return ret

    # 获取课程分页
    def get_course_page(self, courseId, clazzid, chapterId, cpi):

        uri = "https://mooc1-1.chaoxing.com/mycourse/studentstudyAjax"

        data = obj2str({
            'courseId': courseId,
            'clazzid': clazzid,
            'chapterId': chapterId,
            'cpi': cpi,
            'verificationcode': ""
        })

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': "http://i.mooc.chaoxing.com/",
        }

        r = self.s.post(uri, headers=headers, data=data)

        rc = re.findall(r'<span (.*?)</span>', r.text, re.DOTALL)

        ret = []
        # 判断是否只有一页
        if len(rc) == 0:
            title = re.findall(r'<h1>(.*?)</h1>', r.text, re.DOTALL)
            url = re.findall(r'/knowledge/cards\?(.*?)\"', r.text, re.DOTALL)
            ret.insert(len(ret), {
                'title': title[0],
                'url': "https://mooc1-1.chaoxing.com/knowledge/cards?%s" % url[0]
            })
        else:
            for item in rc:
                title = re.findall(r'title=\"(.*?)\"', item)
                paras = re.findall(r'\d{1,}', item)
                num = int(paras[0]) - 1
                totalnum = paras[1]
                chapterId = paras[2]
                courseId = paras[3]
                clazzid = paras[4]
                ret.insert(len(ret), {
                    'title': title[0],
                    'url': "https://mooc1-1.chaoxing.com/knowledge/cards?clazzid=%s&courseid=%s&knowledgeid=%s&num=%d&ut=s&cpi=%s&v=20160407-1"
                    % (clazzid, courseId, chapterId, num, cpi)
                })
        return ret

    # 获取分页的分级
    # 有时一个分页不止一个任务点
    def get_course_page_level(self, url):

        r = self.s.get(url)

        mArg = re.findall(r'mArg = (.*?)\;', r.text)

        for d in mArg:
            if d != "\"\"":
                mArg = d
                break

        mArg = json.loads(mArg)
        return mArg

    #  获取课程分页分级的资源
    def get_course_data(self, objectid):

        uri = "https://mooc1-1.chaoxing.com/ananas/status/%s?k=2041&flag=normal&_dc=%d" % (
            objectid, get_timestamp())

        r = self.s.get(uri)

        return json.loads(r.text)

    # 数据上报完成; 用于pptx
    def updata_log_ppt(self, jobId, knowledgeid, courseId, clazzid, jtoken):

        uri = "https://mooc1-1.chaoxing.com/ananas/job/document?jobid=%s&knowledgeid=%s&courseid=%s&clazzid=%s&jtoken=%s&_dc=%d" % (
            jobId, knowledgeid, courseId, clazzid, jtoken, get_timestamp())

        r = self.s.get(uri)

        j = json.loads(r.text)
        print(j['msg'])
        return j['status']

    # 上报数据; 用于表示用户正在播放视频
    def update_log_video(self, reportUrl, clazzId, playingTime, duration, dtoken, objectId, otherInfo, jobId, userid):
        clipTime = "0_%s" % duration
        enc = "[{0}][{1}][{2}][{3}][{4}][{5}][{6}][{7}]".format(
            clazzId, userid, jobId, objectId, playingTime * 1000, "d_yHJ!$pdA~5", duration * 1000, clipTime)
        
        uri = "{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}{13}{14}{15}{16}{17}{18}{19}{20}{21}{22}{23}{24}{25}{26}{27}{28}".format(
            reportUrl, "/", dtoken, "?clazzId=", clazzId, "&playingTime=", playingTime, "&duration=", duration, "&clipTime=", clipTime, "&objectId=", objectId, "&otherInfo=", otherInfo, "&jobid=", jobId, "&userid=", userid, "&isdrag=", 0, "&view=pc", "&enc=", hashlib.md5(enc.encode(encoding='UTF-8')).hexdigest(), "&rt=", 0.9, "&dtype=Video", "&_t=", get_timestamp())
        
        r = self.s.get(uri)
        
        ret = json.loads(r.text)
        
        return ret['isPassed']