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

    token = "4faa8662c59590c6f43ae9fe5b002b42"

    uid = ""

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

        if a['status']:
            print("✅ %s" % a['mes'])
        else:
            print("❌ %s" % a['mes'])

        return a['status']

    # 获取用户信息
    def get_user_info(self):
        r = self.s.get("https://sso.chaoxing.com/apis/login/userLogin4Uname.do")
        if r.text != "":
            o = json.loads(r.text)
            if o['result'] == 1:
                puid = o['msg']['puid']
                _time = str(get_timestamp())
                enc = "token={0}&_time={1}&puid={2}&myPuid={3}&DESKey={4}".format(
                    self.token, _time, puid, puid, "Z(AfY@XS")
                enc = hashlib.md5(enc.encode("utf-8")).hexdigest()
                url = "https://useryd.chaoxing.com/apis/user/getUser?token={0}&_time={1}&puid={2}&myPuid={3}&inf_enc={4}".format(self.token, _time, puid, puid, enc)
                r = self.s.get(url)
                if r.text != "":
                    o = json.loads(r.text)
                    if o['result'] == 1:
                        self.uid = o['msg']['puid']
                        return o['msg']
        
        return None

    # 获取课程列表
    def get_course_list(self):
        if self.uid == "":
            self.get_user_info()
        r = self.s.get("http://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&rss=1")
        if r.text != "":
            o = json.loads(r.text)
            if o['result'] == 1:
                ret = []
                for item in o['channelList']:
                    for item2 in item['content']['course']['data']:
                        ret.insert(0, {
                            "id": item['id'],
                            "courseId": item2['id'],
                            "courseName": item2['name'],
                            "cpi": item['cpi'],
                            "cataName": item['cataName'],
                            "clazzid": item['key'],
                            "isstart": item['content']['isstart'],
                            "state": item['content']['state']
                        })

                return ret
        return None

    # 获取课程目录
    def get_course_cata(self, clazzid, cpi):

        url = "https://mooc1-api.chaoxing.com/gas/clazz?id={0}&personid={1}&fields=id,bbsid,classscore,isstart,allowdownload,chatid,name,state,isthirdaq,isfiled,information,discuss,visiblescore,begindate,coursesetting.fields(id,courseid,hiddencoursecover,hiddenwrongset,coursefacecheck),course.fields(id,name,infocontent,objectid,app,bulletformat,mappingcourseid,imageurl,knowledge.fields(id,name,indexOrder,parentnodeid,status,layer,label,begintime,endtime,attachment.fields(id,type,objectid,extension).type(video)))&view=json" \
            .format(clazzid, cpi)
        
        r = self.s.get(url)

        if r.text != "":
            o = json.loads(r.text)

            ret = {}
            for item in o['data'][0]['course']['data'][0]['knowledge']['data']:
                if not item['layer'] in ret:
                    ret[item['layer']] = []
                ret[item['layer']].insert(len(ret[item['layer']]), {
                    'id': item['id'],
                    'parentnodeid': item['parentnodeid'],
                    'name': item['name'],
                    'label': item['label'],
                    'data': {
                        "clickcount": 0,
                        "finishcount": 0,
                        "totalcount": 0,
                        "openlock": 0,
                        "unfinishcount": 0
                    }
                })
            
            
            nodes = []
            for item in o['data'][0]['course']['data'][0]['knowledge']['data']:
                if item['layer'] > 1:
                    nodes.insert(0, item['id'])
            taskInfo = self.get_task_finish_status(o['data'][0]['id'], cpi, nodes, o['data'][0]['course']['data'][0]['id'])
            for key, value in taskInfo.items():
                for key2, value2 in ret.items():
                    for key3, value3 in enumerate(value2):
                        if str(value3['id']) == key:
                            ret[key2][key3]['data']['clickcount'] = value['clickcount']
                            ret[key2][key3]['data']['finishcount'] = value['finishcount']
                            ret[key2][key3]['data']['totalcount'] = value['totalcount']
                            ret[key2][key3]['data']['openlock'] = value['openlock']
                            ret[key2][key3]['data']['unfinishcount'] = value['unfinishcount']

            return ret
            
        return None

    # 获取任务完成数量
    def get_task_finish_status(self, clazzid, cpi, nodes, courseid):

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': "http://i.mooc.chaoxing.com/",
            'Referer': "http://passport2.chaoxing.com/login?fid=&refer=http://i.mooc.chaoxing.com"
        }

        node = ','.join([str(i) for i in nodes])

        data = obj2str({
            'clazzid': clazzid,
            'userid': self.uid,
            'view': 'json',
            'cpi': cpi,
            'nodes': node,
            'courseid': courseid
        })

        r = self.s.post("https://mooc1-api.chaoxing.com/job/myjobsnodesmap", headers=headers, data=data)
        if r.text != "":
            return json.loads(r.text)
        return None

    # 获取子节点任务分页
    def get_task_page(self, id, courseid):

        _time = str(get_timestamp())
        enc = "token={0}&_time={1}&DESKey={2}".format(
            self.token, _time, "Z(AfY@XS")
        enc = hashlib.md5(enc.encode("utf-8")).hexdigest()

        url = "https://mooc1-api.chaoxing.com/gas/knowledge?id={0}&courseid={1}&fields=name,id,card.fields(id,title,cardorder,description)&view=json&token={2}&_time={3}&inf_enc={4}" \
            .format(id, courseid, self.token, _time, enc)

        r = self.s.get(url)

        if r.text != "":
            o = json.loads(r.text)
            if len(o['data']) != 0:
                return o['data'][0]['card']['data']

        return None

    # 获取分页的分级
    # 有时一个分页不止一个任务点
    def get_task_page_level(self, clazzid, courseId, knowledgeid, cpi, n):

        url = "https://mooc1-api.chaoxing.com/knowledge/cards?clazzid={0}&courseid={1}&knowledgeid={2}&num={3}&isPhone=1&control=true&cpi={4}" \
            .format(clazzid, courseId, knowledgeid, n, cpi)

        r = self.s.get(url)

        mArg = re.findall(r'mArg = (.*?)\;', r.text)

        for d in mArg:
            if d != "\"\"":
                mArg = d
                break
        try:
            mArg = json.loads(mArg)
        except TypeError:
            return None
        except json.JSONDecodeError:
            return None
        
        return mArg

    #  获取课程资源信息
    def get_course_data(self, objectid):

        uri = "https://mooc1-1.chaoxing.com/ananas/status/%s?k=2041&flag=normal&_dc=%d" % (
            objectid, get_timestamp())

        r = self.s.get(uri)
        if r.text != "":
            return json.loads(r.text)
        return None

    # 上报数据; 用于表示用户正在播放视频
    def update_log_video(self, reportUrl, clazzId, playingTime, duration, dtoken, objectId, otherInfo, jobId, userid):
        clipTime = "0_%s" % duration
        enc = "[{0}][{1}][{2}][{3}][{4}][{5}][{6}][{7}]".format(
            clazzId, userid, jobId, objectId, playingTime * 1000, "d_yHJ!$pdA~5", duration * 1000, clipTime)
        
        uri = "{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}{13}{14}{15}{16}{17}{18}{19}{20}{21}{22}{23}{24}{25}{26}{27}{28}".format(
            reportUrl, "/", dtoken, "?clazzId=", clazzId, "&playingTime=", playingTime, "&duration=", duration, "&clipTime=", clipTime, "&objectId=", objectId, "&otherInfo=", otherInfo, "&jobid=", jobId, "&userid=", userid, "&isdrag=", 0, "&view=pc", "&enc=", hashlib.md5(enc.encode(encoding='UTF-8')).hexdigest(), "&rt=", 0.9, "&dtype=Video", "&_t=", get_timestamp())
        
        r = self.s.get(uri)

        if r.text != "":
            ret = json.loads(r.text)
            return ret['isPassed']

        return None

    # 数据上报完成; 用于pptx
    def updata_log_ppt(self, jobId, knowledgeid, courseId, clazzid, jtoken):

        uri = "https://mooc1-1.chaoxing.com/ananas/job/document?jobid=%s&knowledgeid=%s&courseid=%s&clazzid=%s&jtoken=%s&_dc=%d" % (
            jobId, knowledgeid, courseId, clazzid, jtoken, get_timestamp())

        r = self.s.get(uri)
        if r.text != "":
            o = json.loads(r.text)
            print(o['msg'])
            return o['status']
        return None